import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup 
from tinydb import TinyDB, Query 
import time
import re
all_links = []
db = TinyDB('db.json')
class ScrapeLinks():
    def psychology_today(zip):
        driver = init_driver()
        driver.get('https://www.psychologytoday.com/us/therapists/' + zip +'?page=1')
        i=1
        print("ff")
        while(driver.current_url.__contains__('https://www.psychologytoday.com/us/therapists/' + zip + '?state=') == False):
            print("ff")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for link in soup.find_all('a', {'class': 'profile-title'}):
                #print(link.get('href'))
                all_links.append(link.get('href'))
            driver.get('https://www.psychologytoday.com/us/therapists/' + zip +'?page=' + str(i))
            i+=1
        driver.close()
    def good_therapy(zip):
        driver = init_driver()
        driver.get('https://www.goodtherapy.org/')
        time.sleep(4)
        driver.find_element(By.XPATH, '//*[@id="direccion_maps_header"]').send_keys(str(zip))
        driver.find_element(By.XPATH, '//*[@id="header-widget_button"]').click()
        time.sleep(4)
        page_number = 1
        while(driver.page_source.__contains__('Unfortunately, no search results match the criteria you entered.') == False):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            div_info = soup.find_all('div',attrs={'class':'col s8 m9 l5 xl6 therapist_middle_section'})
            for div in div_info:
                therapist_profile = div.find_all('a') 
                for a in therapist_profile:
                    #print(a['href'])
                    all_links.append(a['href'])
            page_number +=1        
            driver.get(str(driver.current_url) + "&search[p]=" + str(page_number))
            #page_number +=1
            time.sleep(5)
        print('done')
        driver.close()
class GetInfo():
    def call_links():
        for i in range(len(all_links)):
            if(all_links[i].__contains__('psychologytoday')):
               driver = init_driver()
               name, insurance = GetInfo.psychology_today(driver, all_links[i])
            elif(all_links[i].__contains__('goodtherapy')):
                driver = init_driver()
                name, insurance = GetInfo.good_therapy(driver, all_links[i])
            else:
                driver = init_driver()
            db.insert({'name':name, 'insurance':insurance})
        driver.close()
    def psychology_today(driver, link):
        driver.get(link)
        if(driver.page_source.__contains__('Accepted Insurance Plans') == True):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #get name
            for name_div in soup.find_all('div', {'class':'col-sm-6 col-md-7 col-lg-7 name-title-column'}):
                for name in name_div.find_all('h1'):
                    print('name' + name.text.strip())
                    title_name = name.text.strip()
            #get insurance
            insurance = []
            for insurance_div_one in soup.find_all('div', {'class': 'spec-list attributes-insurance'}):
                for insurance_div_two in insurance_div_one.find_all('div', {'class': 'col-split-xs-1 col-split-md-2'}):
                    for insurace_company in insurance_div_two.find_all('ul', {'class': 'attribute-list copy-small'}):
                        for li_company in insurace_company.find_all('li'):
                            insurance.append(li_company.text.strip())
            return title_name, insurance 
        driver.close()
    def good_therapy(driver, link):
        driver = init_driver()
        driver.get(link) 
        soup = BeautifulSoup(driver.page_sourc, 'html.parser')
        insurance = []
        for insurance_ul in soup.find_all('ul', {'class':'billingData'}):
            for insurance_li in insurance_ul.find_all('li'):
                print(insurance_li.text.strip())
                insurance.append(insurance_li.text.strip())
        for insurance_name in soup.find_all('h1', {'class', 'profileName'}):
            print(insurance_name.text.strip())
            name = insurance_name.text.strip()
        return name, insurance

def init_driver():
    PATH = "chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--window-size=1920,1080")
    #driver = webdriver.Chrome(options=options, executable_path=PATH)
    driver = uc.Chrome(options=options)
    return driver

#ScrapeLinks.psychology_today('06042')
#ScrapeLinks.good_therapy('06042')
#GetInfo.call_links()
#print(all_links)
User = Query()
print(db.search(User.insurance == "Aetna"))
#GetInfo.psychology_today('https://www.psychologytoday.com/us/therapists/steven-w-graham-lcsw-vernon-ct/257932')