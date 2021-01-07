import selenium
import options
from selenium import webdriver
from options import Options,attrs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json
import time
import os
import re
path_chromedriver = os.getcwd() + "/Tiki/chromedriver"
class Tiki :
    def __init__(self):
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        #options.add_argument("--headless") 
        # options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(executable_path = path_chromedriver,options = options)
        self.driver.maximize_window()


    # keo thanh cuon xuong cuoi cung
    def scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while (True) :
            self.driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height :
                break
            else :
                last_height = new_height      
        time.sleep(2)


    # lay ra comment , sao danh gia cua danh gia
    def get_comment(self):
        self.scroll()
        linkNX = self.driver.find_elements_by_class_name("-reviews-count")
        if linkNX != [] :
            try:
                totalNX = int(linkNX[0].text)
            except:
                return []
            linkNX[0].click()
            time.sleep(2)
            comments = []
            while True:
                comments_block = self.driver.find_elements_by_class_name("infomation")
                if comments_block != [] :
                    for comment_block in comments_block :
                        if comment_block.find_elements_by_class_name('review_detail') != []:
                            comment_text = comment_block.find_elements_by_class_name('review_detail')[0]
                            text = comment_text.find_elements_by_tag_name('span')[0].text
                            print(text)
                            comment_star = comment_block.find_elements_by_class_name('rating-content')[0]
                            star_text = comment_star.find_elements_by_tag_name('span')[0]
                            star_style = star_text.get_attribute("style")
                            star = int(''.join(re.findall("(\d+)",star_style))) // 20
                            print(star)
                            comments.append([text,star])
                if self.driver.find_elements_by_class_name("list-pager") != []:
                    list_next_tags = self.driver.find_element_by_class_name('list-pager')
                    if list_next_tags.find_elements_by_class_name('next') != []:
                        try :
                            list_next_tags.find_elements_by_class_name('next')[0].click()
                        except:
                            break
                    else : 
                        break
                else: break
                self.scroll()
            return comments
        else :
            return []


    # lay ra duong dan den cac san pham cua hang
    def get_link_products(self):
        products_link = []
        while True:
            products_content = self.driver.find_elements_by_class_name('product-item')
            if products_content != [] :
                for x in products_content:
                    products_link.append(x.find_element_by_tag_name("a").get_attribute('href'))
            list_pager = self.driver.find_elements_by_class_name('list-pager') if self.driver.find_elements_by_class_name('list-pager') != [] else []
            print(list_pager)
            if list_pager != [] and list_pager[0].find_elements_by_class_name('ico-arrow-next') != []:
                list_pager[0].find_element_by_class_name('ico-arrow-next').click()
            else :
                break       
        return products_link


    # lay ra thong tin cua tat ca san pham cua hang
    def get_Phones(self,url):
        self.driver.get(url)
        self.scroll()
        self.driver.implicitly_wait(5)
        links = self.get_link_products()
        items = []
        for x in links:
            tmp = self.get_Info(x)
            items.append(tmp)
        return items
    # lay ra thong tin 1 san pham     
    def get_Info(self,url):
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        imageURL =self.driver.find_element_by_id("product-magiczoom").get_attribute('src')
        try:
            store =  self.driver.find_element_by_class_name("current-seller").find_element_by_tag_name("span").text
        except:
            store = ""
        nm = self.driver.find_element_by_id("product-name").text
        item_rating = self.driver.find_elements_by_class_name("item-rating")
        sku_tag = self.driver.find_element_by_id('product-sku')
        span_list_tag = item_rating[0].find_elements_by_tag_name('span')  
        sku = "".join(re.findall("(\d+)",sku_tag.text))
        cmts =  self.get_comment()
        try :
            rating = float("".join(re.findall("(\d+)",span_list_tag[1].get_attribute('style')))) / 20
        except :
            rating = "0"
        try :
            sold = str(span_list_tag[2].text)
            if sold == "" :
                sold = "0"
        except :
            sold = "0"
        try :
            price = str("".join(re.findall("(\d+)",self.driver.find_element_by_id("span-price").text)))
        except:
            price = "0"
        return [nm,str(rating),sold,price,imageURL,url,"Tiki",store,cmts,sku]
    def get_SKU(self,url):
        self.driver.get(url)
        self.scroll()
        result = []
        links = self.get_link_products()
        for link in links:
            self.driver.get(link)
            sku_tag = self.driver.find_element_by_id('product-sku')
            sku = "".join(re.findall("(\d+)",sku_tag.text))
            result.append([sku,url])
        return result