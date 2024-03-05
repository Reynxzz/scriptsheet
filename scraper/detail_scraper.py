import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import os
import re
import json
import requests
import random
from tqdm import tqdm
from urllib.parse import quote
from fp.fp import FreeProxy
from fake_useragent import UserAgent

# ----------- COMMON FUNCTION ------------- #
def delay():
    base_delay = random.uniform(10, 20)
    additional_delay = random.uniform(-1, 1)
    total_delay = max(10, base_delay + additional_delay)
    time.sleep(total_delay)

def login_and_save_cookies(driver, email, password):
    wait = WebDriverWait(driver, 30)
    
    wait.until(EC.element_to_be_clickable((By.NAME, 'loginKey'))).send_keys(email)
    delay()
    wait.until(EC.element_to_be_clickable((By.NAME, 'password'))).send_keys(password)
    delay()
    
    # click on LOG IN button
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))).click()
    
    # save cookies
    cookies = driver.get_cookies()
    with open("../cookies/shopee-cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    print("Login success, Cookies are saved")

def first_login_and_save_cookies(driver, email, password):
    url_login = "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F"
    driver.get(url_login)    
    wait = WebDriverWait(driver, 30)

    wait.until(EC.presence_of_element_located((By.NAME, 'loginKey'))).send_keys(email)
    delay()
    wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)
    delay()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))).click()
    
    time.sleep(5)
    
    # save cookies
    cookies = driver.get_cookies()
    with open("../cookies/shopee-cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    print("Login success, Cookies are saved")

def scrolling(total_steps):
    for i in tqdm(range(1, total_steps + 1), desc="Scrolling"):
        step = random.randint(600, 900)
        end = step * i
        script = "window.scrollTo(0," + str(end) + ")"
        delay()
        driver.execute_script(script)
        
        delay()

        driver.execute_script("window.scrollBy(0, 1);")
        driver.execute_script("window.scrollBy(0, -1);")

        # Randomly pause the scrolling at different intervals
        if random.random() < 0.6:  # 60% chance to pause scrolling
            pause_duration = random.uniform(0.5, 4)
            time.sleep(pause_duration)

# ----------- SCRAPING FUNCTION ------------- #

# function to scrape detail for each products
def search_detail_per_product(driver, base_url, links, email, password):
    """
    a function to scrape detail each product by link.
    - driver: selenium chrome driver
    - base_url: shopee url (home), STR
    - links: array of product link you want to scrape, ARR of STR
    - email: shopee email/username, STR
    - password: shopee password, STR
    """
    
    descriptions = []
    seller_names = []
    seller_links = []
    reviews = []
    
    for url in links:
        try:
            driver.get(url)
            time.sleep(10)
            content_raw = driver.page_source
            
            if "<title>Login sekarang untuk mulai berbelanja! | Shopee Indonesia</title>" in content_raw:
                print("Login required")
                login_and_save_cookies(driver, email, password)
                delay()
                driver.get(url)
                scrolling(1)
                delay()
                content_raw = driver.page_source
                content = BeautifulSoup(content_raw, 'html.parser')
            else:
                delay()
                driver.get(url)
                scrolling(1)
                delay()
                content_raw = driver.page_source
                content = BeautifulSoup(content_raw, 'html.parser')
                
            description = content.find('p', class_='QN2lPu').text
            seller_name = content.find('div', class_='fV3TIn').text
            seller_link = base_url + content.find('a', class_="btn btn-light btn--s btn--inline btn-light--link Z6yFUs")['href']
            r = re.search(r'i\.(\d+)\.(\d+)', url)
            shop_id, item_id = r[1], r[2]
            
            params = {
                "filter": "0",
                "flag": "1",
                "itemid": f"{item_id}",
                "limit": "5",
                "offset": "0",
                "shopid": f"{shop_id}",
                "type": "0"
            }
            
            review_product = []
            ratings_url = 'https://shopee.co.id/api/v2/item/get_ratings'
            r = requests.get(ratings_url, params=params).json()
            for item in r['data']['ratings']:
                review_product.append(item['comment'])
            all_reviews = ' '.join(review_product)
            
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            description = ''
            seller_name = ''
            seller_link = ''
            all_reviews = ''
        
        descriptions.append(description)
        seller_names.append(seller_name)
        seller_links.append(seller_link)
        reviews.append(all_reviews)
        delay_fast()
            
    return pd.DataFrame({'seller':seller_names, 'seller_link':seller_links, 'description':descriptions, 'review':reviews, 'link': links})
            

if __name__ == '__main__':
    email = 'skripsirey'
    password = 'eehpoSispirks$'
    # email = 'reyfinalproject'
    # password = 'eehpoSispirks#'
    base_url = "https://shopee.co.id"
    
    
    # --- PRODUCT DETAIL SCRAPING --- #

    proxy = FreeProxy(country_id=['US', 'BR', 'IN', 'CA', 'SG', 'GB']).get().split('//')[1]
    ua = UserAgent(browsers='chrome', os='macos').random
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f'proxy-server={proxy}')
    chrome_options.add_argument(f'--user-agent={ua}')

    driver = uc.Chrome(
        options=chrome_options, headless=True
    )
        
    links = df_all["link"].values
    df = search_detail_per_product(driver, base_url, links[:10], email, password)
    df_final = pd.merge(df_all[:10], df, on='link', how='inner')

    driver.quit()