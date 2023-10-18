
import selenium.webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
options = selenium.webdriver.ChromeOptions()
options.add_argument('--headless=new')
driver = selenium.webdriver.Chrome(options=options)
driver.get("https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1")
lst = []  # The list of entries
count = 0 
while len(lst) < 200 or count < 20:
    print(f'Page {count+1}')

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'puis-card-container')))  # Wait for containers to load
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
                'url': i.find_element(By.TAG_NAME, "a").get_attribute('href')
            }
            try:
                obj['rating'] = float(i.find_element(
                    By.CLASS_NAME, "a-icon-alt").get_attribute("innerText").split()[0])
            except:
                obj['rating'] = None
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
for c, i in enumerate(lst):
    driver.get(i['url'])
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
    else:
        brand = (brand['Manufacturer'] if 'Manufacturer' in brand else brand['Brand']).find_element(
            By.TAG_NAME, 'td').get_attribute("innerText").strip()
    try:
        description = driver.find_element(
            value="productDescription").get_attribute("innerText")
    except:
        description = None
    try:
        asin = [x for x in driver.find_elements(By.TAG_NAME, 'tr') if x.find_elements(By.TAG_NAME, 'th') and x.find_element(
            By.TAG_NAME, 'th').get_attribute("innerText").strip() == "ASIN"][0].find_element(By.TAG_NAME, 'td').get_attribute("innerText").strip()
    except:
        try:
            asin = {x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip(): x.find_element(By.TAG_NAME, "span") for x in driver.find_element(
                value="detailBullets_feature_div").find_elements(By.TAG_NAME, 'li') if x.find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").get_attribute("innerText").strip().startswith('ASIN')}
            if not asin:
                asin = None
            else:
                asin = (list(asin.values())[0]).find_elements(By.TAG_NAME, 'span')[-1].get_attribute("innerText").strip()
        except:
            asin = None
    try:
        featureBullets = driver.find_element(value='feature-bullets').get_attribute("innerText")
    except:
        featureBullets = None
    
    lst[c].update({
        'manufacturer': brand,
        'asin': asin,
        'description': featureBullets,
        'productDescription': description
    })
with open('csv-dump.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, lst[0].keys())
    writer.writeheader()
    writer.writerows(lst)
