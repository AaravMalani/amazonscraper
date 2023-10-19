
import os
import selenium.webdriver
from selenium.webdriver.common.by import By
import argparse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
argparser = argparse.ArgumentParser(prog="AmazonScraper", description="Used to scrape Amazon pages")
argparser.add_argument('--job', help='The job value (0 to jobs-1). Defaults to 0', default=0)
argparser.add_argument('--jobs', help='The number of jobs. Defaults to 1', default=1)
argparser.add_argument('--remove-header', action='store_true', help='Does not add header row if set. Useful for concatenating CSV files. Defaults to not set', default=False)
argparser.add_argument('-o', '--output', help="Output file. Defaults to csv-dump.csv", default='csv-dump.csv')
args = argparser.parse_args()
options = selenium.webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--no-sandbox");
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}})
driver = selenium.webdriver.Chrome(options=options)
page = int(args.job)*20//int(args.jobs) + 1  # Get the page for the job

lst = []  # The list of entries
count = 0 
names = set() # Set of names
while len(lst) < 200/int(args.jobs) and count < (20 / int(args.jobs)) and count < 100:
    driver.get(f"https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1&page="+str(page))
    print(f'Page {count+1}')
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'puis-card-container')))  # Wait for containers to load
    except Exception as e:
        driver.refresh() # Ratelimited or slow
        continue
    for i in driver.find_elements(By.CLASS_NAME, 'puis-card-container'):
        if 'Sponsored' in i.text.split("\n"):  # Skip sponsored items
            continue
        try:
            prices = i.find_elements(By.CLASS_NAME, "a-price") 
            name = i.find_element(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal").get_attribute("innerText") # Find the span with medium text size in the card (the heading)
            if name in names:
                continue

            obj = {
                'name': name, 
                'reviews': int(i.find_element(By.CSS_SELECTOR, "span>a.a-link-normal.s-link-style").get_attribute("innerText").replace(',', '')), # Find the review count
                'price': int(prices[0].get_attribute("innerText")[1:].replace(',', '').split("\n")[0]), # Find the price (either the lower range of a range or the discounted price)
                'mrp': int((prices[0] if len(prices) == 1 else prices[1]).get_attribute("innerText")[1:].replace(',', '').split("\n")[0]), # Find the upper price (either the upper range of a price range or the MRP)
                'url': [x for x in i.find_elements(By.TAG_NAME, "a") if not x.get_attribute('href').startswith('https://www.amazon.in/gp/bestsellers')][0].get_attribute('href') # The URL
            }
            
            try:
                obj['rating'] = float(i.find_element(
                    By.CLASS_NAME, "a-icon-alt").get_attribute("innerText").split()[0]) # Find the rating
            except:
                obj['rating'] = None # There is no rating
            names.add(obj['name'])
        except:
            continue
        lst += [obj] # Add object
    count += 1
    page+=1
for c,i in enumerate(lst):
    driver.get(i['url']) # Get the page URL
    check = 0 # Check 10 times if the title is present (to prevent infinite ratelimited loops, its better to skip the page)
    while check<10:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.ID, 'productTitle')))
            break

        except Exception:
            pass
        driver.refresh()
        check+=1
    if check == 10:
        continue
    try:
        brand = {x.find_element(By.TAG_NAME, 'th').get_attribute("innerText").strip(): x for x in driver.find_elements(By.TAG_NAME, 'tr') if x.find_elements(
        By.TAG_NAME, 'th') and x.find_element(By.TAG_NAME, 'th').get_attribute("innerText").strip() in ['Manufacturer', 'Brand']} # Get the manufacturer and brand from the table
    except:
        
        brand = None
    if not brand:
        try:
            brand = driver.find_element(value='bylineInfo').get_attribute(
                "innerText").split(":")[1].strip() # Get the brand from the byline (Brand: <brand> below the title)
        except:
            try:
                brand = {x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip(): x.find_element(By.TAG_NAME, "span") for x in driver.find_element( 
                    value="detailBullets_feature_div").find_elements(By.TAG_NAME, 'li') if x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip().startswith(('Manufacturer', 'Brand'))} # Find from the bullet points (product details)
                if not brand:
                    brand = None
                else:
                    brand = (brand[next(x for x in brand if x.startswith('Manufacturer'))] if any(x.startswith('Manufacturer') for x in brand) else brand[next(
                        x for x in brand if x.startswith('Brand'))]).find_elements(By.TAG_NAME, 'span')[-1].get_attribute("innerText").strip() # Retrieve the manufacturer or brand
            except:
                brand = None
            if not brand:
                try:
                    brand = driver.find_element(By.CSS_SELECTOR,'.brand-snapshot-flex-badges-section span').get_attribute("innerText") # Get the brand from the customized Top Brand container
                except:
                    pass

    else:
        brand = (brand['Manufacturer'] if 'Manufacturer' in brand else brand['Brand']).find_element(
            By.TAG_NAME, 'td').get_attribute("innerText").strip() # Retrieve the manufacturer or brand
    try:
        description = driver.find_element(
            value="productDescription").get_attribute("innerText") # Check for the product description
    except:
        description = None # Not found
    asin = i['url'].find('/dp/') # Get the ASIN from the URL
    asin = i['url'][asin+4:i['url'].find('/', asin+4)]  
    try:
        featureBullets = driver.find_element(value='feature-bullets').get_attribute("innerText") # Check for the bullet points below the title
    except:
        featureBullets = None # Not found
    
    lst[c].update({
        'manufacturer': brand,
        'asin': asin,
        'description': featureBullets,
        'productDescription': description
    })

with open(args.output, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=lst[0].keys())
    if not args.remove_header:
        writer.writeheader()
    writer.writerows(lst) # Save the values
