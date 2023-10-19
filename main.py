
import os
import selenium.webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import csv
def check_page(count, sub):
    global lst
    print(f"Starting thread {count+1}")
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument("--no-sandbox");
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--disable-extensions")
    options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2, 
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}})
    driver = selenium.webdriver.Chrome(options=options)
    for c,i in enumerate(sub):
        driver.get(i['url'])
        while True:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.ID, 'productTitle')))
                break

            except Exception:
                pass
            driver.refresh()
        try:
            brand = {x.find_element(By.TAG_NAME, 'th').get_attribute("innerText").strip(): x for x in driver.find_elements(By.TAG_NAME, 'tr') if x.find_elements(
            By.TAG_NAME, 'th') and x.find_element(By.TAG_NAME, 'th').get_attribute("innerText").strip() in ['Manufacturer', 'Brand']}
        except:
            
            brand = None
        if not brand:
            try:
                brand = driver.find_element(value='bylineInfo').get_attribute(
                    "innerText").split(":")[1].strip()
            except:
                try:
                    brand = {x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip(): x.find_element(By.TAG_NAME, "span") for x in driver.find_element(
                        value="detailBullets_feature_div").find_elements(By.TAG_NAME, 'li') if x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip().startswith(('Manufacturer', 'Brand'))}
                    if not brand:
                        brand = None
                    else:
                        brand = (brand[next(x for x in brand if x.startswith('Manufacturer'))] if any(x.startswith('Manufacturer') for x in brand) else brand[next(
                            x for x in brand if x.startswith('Brand'))]).find_elements(By.TAG_NAME, 'span')[-1].get_attribute("innerText").strip()
                except:
                    brand = None
                if not brand:
                    try:
                        brand = driver.find_element(By.CSS_SELECTOR,'.brand-snapshot-flex-badges-section span').get_attribute("innerText")
                    except:
                        pass

        else:
            brand = (brand['Manufacturer'] if 'Manufacturer' in brand else brand['Brand']).find_element(
                By.TAG_NAME, 'td').get_attribute("innerText").strip()
        try:
            description = driver.find_element(
                value="productDescription").get_attribute("innerText")
        except:
            description = None
        asin = i['url'].find('/dp/')
        asin = i['url'][asin+4:i['url'].find('/', asin+4)]  
        try:
            featureBullets = driver.find_element(value='feature-bullets').get_attribute("innerText")
        except:
            featureBullets = None
        
        lst[c + (len(lst)*count)//os.cpu_count()].update({
            'manufacturer': brand,
            'asin': asin,
            'description': featureBullets,
            'productDescription': description
        })
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
driver.get("https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1")
lst = []  # The list of entries
count = 0 
names = []
while (len(lst) < 20 or count < 2) and count < 100:
    print(f'Page {count+1}')
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'puis-card-container')))  # Wait for containers to load
    except Exception as e:
        print(e)
        driver.refresh()
        continue
    for i in driver.find_elements(By.CLASS_NAME, 'puis-card-container'):
        if 'Sponsored' in i.text.split("\n"):  # Skip sponsored items
            continue
        try:
            prices = i.find_elements(By.CLASS_NAME, "a-price")
            obj = {
                'name': i.find_element(By.CSS_SELECTOR, "span.a-size-medium.a-color-base.a-text-normal").get_attribute("innerText"),
                'reviews': int(i.find_element(By.CSS_SELECTOR, "span>a.a-link-normal.s-link-style").get_attribute("innerText").replace(',', '')),
                'price': int(prices[0].get_attribute("innerText")[1:].replace(',', '').split("\n")[0]),
                'mrp': int((prices[0] if len(prices) == 1 else prices[1]).get_attribute("innerText")[1:].replace(',', '').split("\n")[0]),
                'url': [x for x in i.find_elements(By.TAG_NAME, "a") if not x.get_attribute('href').startswith('https://www.amazon.in/gp/bestsellers')][0].get_attribute('href')
            }
            if obj['name'] in names:
                continue
            
            try:
                obj['rating'] = float(i.find_element(
                    By.CLASS_NAME, "a-icon-alt").get_attribute("innerText").split()[0])
            except:
                obj['rating'] = None
            names+=[obj['name']]
        except:
            continue
        lst += [obj]
    count += 1
    k = False
    while True:
        try:
            if not driver.find_element(By.CLASS_NAME, "s-pagination-next").is_enabled():
                k = True
                break
            driver.find_element(By.CLASS_NAME, "s-pagination-next").click()
            break
        except:
            pass
        driver.refresh()
    if k:
        break
threads = [threading.Thread(target=check_page, args=(i, lst[(len(lst)*i)//os.cpu_count(): (len(lst)*(i+1))//os.cpu_count() ]), daemon=True) for i in range(os.cpu_count())]
for i in threads:
    i.start()
for i in threads:
    i.join()

with open('csv-dump.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, lst[0].keys())
    writer.writeheader()
    writer.writerows(lst)
