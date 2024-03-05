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

# search by keyword scraping function
def keyword_search_results(driver, base_url, keyword, page, email, password):
    """
    a function to scrape Shopee product list by search keyword.
    - driver: selenium chrome driver
    - base_url: shopee url (home), STR
    - keyword: product keyword(s), STR
    - page: how many page(s) you want to scrape, INT
    - email: shopee email/username, STR
    - password: shopee password, STR
    """

    keyword_quote = quote(keyword)
    keyword_url = f"{base_url}/search?keyword=" + keyword_quote + f"&page={page}"
    driver.get(keyword_url)
    print(f"Searching {keyword}...")
    delay()
          
    content_raw = driver.page_source
    
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
    images = []
    
    for area in tqdm(content.find_all('li', class_="col-xs-2-4 shopee-search-item-result__item"), desc="Processing Items"):
        try:
            title = area.find('div',class_="xA2DZd tYvyWM wupGTj").get_text()
            img = area.find('img')['src']
            price = area.find('span',class_="_7s1MaR").get_text()
            link = base_url + area.find('a')['href']
            sold = area.find('div',class_="L68Ib9 s3wNiK")
            if sold != None:
                sold = sold.get_text()
            location = area.find('div',class_="wZEyNc").get_text()
            
        except:
            pass
        
        titles.append(title)
        prices.append(price)
        links.append(link)
        solds.append(sold)
        locations.append(location)
        images.append(img)

    return pd.DataFrame({'title':titles, 'price':prices, 'sold':solds, 'location': locations, 'link':links, 'image':images})

if __name__ == '__main__':
    keyword_makanan_ilegal = [
    "makanan import luar negri", #Pangan Olahan tanpa izin edar
    "snack kiloan branded", #Pangan Olahan tanpa izin edar 
    "makanan expired", #melewati tanggal kedaluwarsa
    "susu formula penambah berat badan anak", #PKMK bayi/anak
    "susu formula bayi prematur", #PKMK bayi/anak
    "pangan olahan medis", #PKMK
    "bir", #Minuman beralkohol
    "whisky minuman alkohol", #Minuman beralkohol
    "tuak arak", #Minuman beralkohol
    "makanan sehat obat", #iklan/klaim menyehatkan
    "minuman pembesar", #iklan/klaim
    "minuman penambah stamina" #penambah stamina
    ]
    
    email = 'skripsirey'
    password = 'eehpoSispirks$'
    # email = 'reyfinalproject'
    # password = 'eehpoSispirks#'
    base_url = "https://shopee.co.id"
    
    
    # --- PRODUCT BY SEARCH KEYWORD SCRAPING --- #

    df_all = pd.DataFrame()

    for keyword in keyword_makanan_ilegal:
        proxy = FreeProxy(country_id=['US', 'BR', 'IN', 'CA', 'SG', 'GB']).get().split('//')[1]
        ua = UserAgent(browsers='chrome', os='macos').random
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f'proxy-server={proxy}')
        chrome_options.add_argument(f'--user-agent={ua}')

        driver = uc.Chrome(
            options=chrome_options, headless=True
        )
        
        print("new driver initialized")
        
        first_login_and_save_cookies(driver, email, password)
        
        for page in range(5):
            delay()
            df = keyword_search_results(driver, base_url, keyword, page, email, password)
            df_all = pd.concat([df_all, df], ignore_index=True)

        driver.quit()