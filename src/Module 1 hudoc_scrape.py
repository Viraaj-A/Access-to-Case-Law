import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pandas as pd
from random import uniform
from pickle import dump


def scroll():
    """Scrolls down page with Selenium, implementing 0.5 second pause.
        
    """
    scroll_pause = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



class Judgment:
    """Contains all essential information of the respective judgment.

    Args:
        title (str): Title of the Judgment.
        text (str): full text of the Judgment.
        url (str): url of the Judgment.
        case_details (dic): Dictionary of case_details.
    
    Attributes:
        title (str): Title of the Judgment.
        text (str): full text of the Judgment.
        url (str): url of the Judgment.
        case_details (dic): Dictionary of case_details.

    """
    def __init__(self, title: str, ident: str, text:str, url:str, case_details: dict):
        self.title = title
        self.ident = ident
        self.text = text
        self.url = url
        self.case_details = case_details


def get_judgement(url, judgment_dict: dict, n: int):
    """Scrapes individual pages to obtain raw text data from Judgements.

    It is also required to pass an empty judgement dictionary so that attributes can be assigned.

    Args:
        url (str): URL for individual judgment.
        judgment_dict (dict): Dictionary in which results are stored.
    
    """
    driver.get(url)
    sleep(uniform(4,6))
    if len(driver.find_elements_by_class_name("content")) > 1:
        text = driver.find_element_by_class_name("content").text
        title = driver.find_element_by_class_name("lineone").text
        ident = driver.find_element_by_class_name("linetwo").text.split("|")[0].strip()
        driver.find_element_by_id("notice").click()
        sleep(2)
        more = driver.find_elements_by_class_name('moreword')
        if len(more) > 0:
            [elem.click() for elem in more]
        sleep(uniform(2,3))
        raw_text = driver.find_element_by_xpath('//*[@id="notice"]/div').text
        sleep(uniform(1,2))
        url = url
        judgment_dict[n] = Judgment(
            title = title,
            ident = ident,
            text = text,
            url = url,
            case_details = raw_text
        )
    else:
        next

# initialize driver from downloads folder
driver = webdriver.Edge("C:/Users/julia/Downloads/msedgedriver.exe")
driver.implicitly_wait(5) # set implicit wait to 5 sec
driver.get("https://hudoc.echr.coe.int/eng#{%22documentcollectionid2%22:[%22GRANDCHAMBER%22]}")
scroll() # scroll index page down to load all further links

soup = BeautifulSoup(driver.page_source) # save index once scroll is finished

# save all urls
urls = list(set(["https://hudoc.echr.coe.int/eng#{" + elem['href'].partition('"GRANDCHAMBER"],')[2] for elem in soup.find_all(class_ = 'availableonlylink', href = True) if elem.text == 'English']))

# scrape all the data and store it in the attributes of the class instances, with each judgement as one instance
n = 1 
judgment_dict = {}
for url in urls:
    get_judgement(url, judgment_dict, n)
    sleep(uniform(0.5,1))
    print(f"judgement: #{n}")
    print(f"dict-length: #{len(judgment_dict)}")
    driver.back()
    n += 1

# save data
with open('all_data_finally.pickle', 'wb') as handle:
    dump(judgment_dict, handle)