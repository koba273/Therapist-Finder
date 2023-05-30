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
def remove_dupes(input_array):
    return [*set(input_array)]
class ScrapeLinks():
    def psychology_today(zip):
        driver = init_driver()
        driver.get('https://www.psychologytoday.com/us/therapists/' + zip +'?page=1')
        i=1
        driver.implicitly_wait(4)
        if(driver.page_source.__contains__('The page you were looking for was not found.') == False & driver.page_source.__contains__("The specific page you were looking for has been moved or deleted. Please use the main menu at the top of this page to locate the resource you are searching for. To find a counselor or therapist in your location please feel free to use the ZIP Code Search form below:") == False):
            while(driver.current_url.__contains__('https://www.psychologytoday.com/us/therapists/' + zip + '?state=') == False):
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
        driver.implicitly_wait(4)
        driver.find_element(By.XPATH, '//*[@id="header-widget_button"]').click()
        driver.implicitly_wait(4)
        page_number = 1
        time.sleep(4)
        while(driver.page_source.__contains__('Unfortunately, no search results match the criteria you entered.') == False & driver.page_source.__contains__('The specific page you were looking for has been moved or deleted. Please use the main menu at the top of this page to locate the resource you are searching for. To find a counselor or therapist in your location please feel free to use the ZIP Code Search form below:') == False):
            if(driver.page_source.__contains__('The page you were looking for was not found. Please check the address and try again or start from the top.') == False):
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
                driver.implicitly_wait(10)
        driver.close()
    def better_help(zip):
        driver = init_driver()
        driver.get('https://www.betterhelp.com/therapists/')
        driver.implicitly_wait(4)
        driver.find_element(By.XPATH, '//*[@id="search"]').send_keys(zip)
        driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[1]/div/div/div/form/button').click()
        if(driver.page_source.__contains__("Sorry, we couldn't find any cities for") == False):
            driver.implicitly_wait(4)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for therapist_link_div in soup.find_all('div', {'class':'therapist-name'}):
                for therapist_link in therapist_link_div.find_all('a'):
                    all_links.append('https://www.betterhelp.com' + therapist_link['href'])
        driver.close()
class GetInfo():
    def call_links():
        driver = init_driver()
        links = remove_dupes(all_links)
        for i in range(len(links)-1):
            if(links[i].__contains__('psychologytoday')):
               _, name, insurance, endorsed, number = GetInfo.psychology_today(driver, links[i])
               print(name,insurance,endorsed,number)
               license = None
            elif(links[i].__contains__('goodtherapy')):
                name, insurance = GetInfo.good_therapy(driver, links[i])
                license = None
            elif(links[i].__contains__('betterhelp')):
                name, insurance, license = GetInfo.better_help(driver, links[i])
            print(db.insert({'name':name, 'insurance':insurance, 'license':license, 'link':links[i]}))
        driver.close()
    def psychology_today(driver, link):
        title_name, insurance, endorsed, number = None
        driver.get(link)
        if(driver.page_source.__contains__('Accepted Insurance Plans') == True):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for name_div in soup.find_all('div', {'class':'profile-heading-content'}):
                for name in name_div.find_all('h1'):
                    print('name' + name.text.strip())
                    title_name = name.text.strip()
            #get insurance
            insurance = []
            for insurance_div in soup.find_all('div', {'class':'insurance'}):
                for insurance_ul in insurance_div.find_all('ul', {'class':'section-list columns'}):
                    for insurance_li in insurance_ul.find_all('li'):
                        insurance.append(insurance_li.text.strip())
            if(driver.page_source.__contains__('endorsement-count profile-badge clickable')):
                endorsed = True
            else:
                endorsed = False
            for number in soup.find_all('a', {'class': 'lets-connect-phone-number'}):
                number = number.text.strip()
            return link, title_name, insurance, endorsed, number
        driver.close()
    def good_therapy(driver, link):
        insurance = []
        name = None
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for insurance_ul in soup.find_all('ul', {'class':'billingData'}):
            for insurance_li in insurance_ul.find_all('li'):
                insurance.append(insurance_li.text.strip())
        for user_name in soup.find_all('h1', {'id': 'profileTitle_id'}):
            name = user_name.text.strip()
        return name, insurance
    def better_help(driver, link):
        name = None
        license_id = None
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        license_id = []
        for name in soup.find_all('h1', {'class':'counselor-profile-header__name'}):
            name = name.text.strip()
        if(driver.page_source.__contains__('licensing')):
            for license_div in soup.find_all('div', {'id':'licensing'}):
                for license_text in license_div.find_all('p'):
                    license_id.append(license_text.text.strip())
        time.sleep(1.5)
        return name, None, license_id
def init_driver():
    PATH = "chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)
    return driver

def bulk_zip(zip):
    i=0
    while i <= len(zip):
        ScrapeLinks.psychology_today(str(zip[i]))
        ScrapeLinks.good_therapy(str(zip[i]))
        ScrapeLinks.better_help(str(zip[i]))
        GetInfo.call_links()
        i+=1
ct_zips = ["06144", "06150", "06161"]
bulk_zip(ct_zips)
#print(all_links)
#User = Query()
#print(db.search(User.insurance == "Aetna"))
#GetInfo.psychology_today('https://www.psychologytoday.com/us/therapists/steven-w-graham-lcsw-vernon-ct/257932')