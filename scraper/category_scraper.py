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
    base_delay = random.uniform(3, 10)
    additional_delay = random.uniform(-1, 1)
    total_delay = max(10, base_delay + additional_delay)
    time.sleep(total_delay)
    
def delay_fast():
    base_delay = random.uniform(0.3, 2)
    additional_delay = random.uniform(-1, 1)
    total_delay = max(0.5, base_delay + additional_delay)
    time.sleep(total_delay)

def login_and_save_cookies(driver, email, password):
    wait = WebDriverWait(driver, 30)
    print("Logging in...")
    wait.until(EC.element_to_be_clickable((By.NAME, 'loginKey'))).send_keys(email)
    delay()
    wait.until(EC.element_to_be_clickable((By.NAME, 'password'))).send_keys(password)
    delay()
    
    # click on LOG IN button
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))).click()
    
    # save cookies
    print("Saving cookies...")
    cookies = driver.get_cookies()
    with open("../cookies/shopee-cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    print("Login success, Cookies are saved")

def first_login_and_save_cookies(driver, email, password):
    url_login = "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F"
    driver.get(url_login)    
    wait = WebDriverWait(driver, 30)
    print("Logging in...")
    wait.until(EC.presence_of_element_located((By.NAME, 'loginKey'))).send_keys(email)
    delay()
    wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)
    delay()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))).click()
    
    time.sleep(5)
    
    # save cookies
    print("Saving cookies...")
    cookies = driver.get_cookies()
    with open("../cookies/shopee-cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)
    
    print("Login success, Cookies are saved")

def scrolling(total_steps):
    for i in tqdm(range(1, total_steps + 1), desc="Scrolling"):
        step = random.randint(600, 900)
        end = step * i
        script = "window.scrollTo(0," + str(end) + ")"
        delay_fast()
        driver.execute_script(script)
        
        delay()

        driver.execute_script("window.scrollBy(0, 1);")
        driver.execute_script("window.scrollBy(0, -1);")

        # Randomly pause the scrolling at different intervals
        if random.random() < 0.6:  # 60% chance to pause scrolling
            pause_duration = random.uniform(0.5, 4)
            time.sleep(pause_duration)

# ----------- SCRAPING FUNCTION ------------- #
            
# function to scrape search by category
def category_search_results(driver, base_url, page, category_link, email, password):
    """
    a function to scrape product lsit by category.
    - driver: selenium chrome driver
    - base_url: shopee url (home), STR
    - links: array of product link you want to scrape, ARR of STR
    - email: shopee email/username, STR
    - password: shopee password, STR
    """
    url = f"{category_link}" + f"?page={page}"
    driver.get(url)
    print(f"searching category {category_link}...")
    time.sleep(10)

    content_raw = driver.page_source

    if "<title>Login sekarang untuk mulai berbelanja! | Shopee Indonesia</title>" in content_raw:
        print("Login required")
        login_and_save_cookies(driver, email, password)
        delay()

        driver.get(url)
        delay()

        scrolling(6)
        delay()
        content_raw = driver.page_source
        delay()
    else:
        delay()
        scrolling(7)
        delay()
        content_raw = driver.page_source


    content = BeautifulSoup(content_raw,'html.parser')

    titles = []
    prices = []
    links = []
    solds = []
    locations = []

    for area in tqdm(content.find_all('li', class_="col-xs-2-4 shopee-search-item-result__item"), desc="Processing Items"):
        try:
            title = area.find('div',class_="DgXDzJ rolr6k Zvjf4O").get_text()
            # img = area.find('img')['src']
            price = area.find('span',class_="k9JZlv").get_text()
            link = base_url + area.find('a')['href']
            sold = area.find('div',class_="OwmBnn eumuJJ")
            if sold != None:
                sold = sold.get_text()
            location = area.find('div',class_="JVW3E2").get_text()
            
            titles.append(title)
            prices.append(price)
            links.append(link)
            solds.append(sold)
            locations.append(location)

        except:
            driver.save_screenshot('category_search_results_error.png')

    return pd.DataFrame({'title':titles, 'price':prices, 'sold':solds, 'location': locations, 'link':links, 'category':category_link})

if __name__ == '__main__':
    category_link = [
               'https://shopee.co.id/Makanan-Minuman-cat.11043451'
               # 'https://shopee.co.id/Makanan-Ringan-cat.11043451.11043453',
               # 'https://shopee.co.id/Bahan-Pokok-cat.11043451.11043467',
               # 'https://shopee.co.id/Menu-Sarapan-cat.11043451.11043496',
               # 'https://shopee.co.id/Minuman-cat.11043451.11043502',
               # 'https://shopee.co.id/Susu-Olahan-cat.11043451.11043517',
               # 'https://shopee.co.id/Makanan-Segar-Beku-cat.11043451.11043529',
               # 'https://shopee.co.id/Roti-Kue-cat.11043451.11043544',
               # 'https://shopee.co.id/Makanan-Kaleng-cat.11043451.11043557',
               # 'https://shopee.co.id/Makanan-Instan-cat.11043451.11043564',
               # 'https://shopee.co.id/Makanan-Minuman-Lainnya-cat.11043451.11043556'
    ]
    
    email = 'skripsirey'
    password = 'eehpoSispirks$'
    # email = 'reyfinalproject'
    # password = 'eehpoSispirks#'
    base_url = "https://shopee.co.id"
    
    
    # --- PRODUCT BY CATEGORY SCRAPING --- #

    df_all_cat = pd.DataFrame()
    
    for idx, category in enumerate(category_link):
        proxy = FreeProxy(country_id=['US', 'BR', 'IN', 'CA', 'SG', 'GB']).get().split('//')[1]
        ua = UserAgent(browsers='chrome', os='macos').random
        print(proxy,ua)
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f'proxy-server={proxy}')
        chrome_options.add_argument(f'--user-agent={ua}')

        driver = uc.Chrome(
            options=chrome_options, headless=True
        )
        
        print("New driver initialized")
        
        first_login_and_save_cookies(driver, email, password)
        
        delay()
        for page in range(9):
            delay()
            df = category_search_results(driver, base_url, page, category, email, password)
            if df.shape[0] < 60:
                print(f"WARNING: only {df.shape[0]} products scraped")
            df_all_cat = pd.concat([df_all_cat, df], ignore_index=True)
        
        df_all_cat.to_csv(f"../dataset/all_category_full_{idx}.csv", index=False)

        driver.quit()