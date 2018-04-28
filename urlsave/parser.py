# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from poyo import parse_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html


class Parser(object):
    def __init__(self, dic, chrome_options, chrome_driver):
        self.driver = webdriver.Chrome(chrome_options=chrome_options, 
                                       executable_path=chrome_driver)
        dic = parse_string(dic)
        dic = list(dic.values())[0]
        self.parse(dic)
        self.driver.quit()
        
    def parse(self, dic):
        # Parse the URL
        self.driver.get(dic['Url'])
        self.page = html.fromstring(self.driver.page_source)
        self.active_element = self.page
        
        # Parse list
        self.storage = self.save(dic['Save'])
        
    def xpath(self, path):
        path = path.strip()
        slash_pos = path.find("/")
        if slash_pos == -1 and path != ".":
            print(path + 'is not a valid XPath: requires a backslash')
            return []
        
        if path[max(slash_pos - 1, 0)] != ".":
            path = path[:slash_pos] + "." + path[slash_pos:] 
        
        print(path)
        return self.active_element.xpath(path)
        
    def save(self, dic):
        if type(dic) not in [list, dict]:
            result = [e.text if type(e) == html.HtmlElement else e 
                     for e in self.xpath(dic)]
            return result if len(result) != 1 else result[0]
            
        elif type(dic) == dict:
            dic = dic.copy()
            elements = self.xpath(dic.pop("Elements", "."))
            
            results = []
            for e in elements:
                self.active_element = e
                result = {}
                for key, value in dic.items():
                    result[key] = self.save(value)
                results.append(result)
            return results
