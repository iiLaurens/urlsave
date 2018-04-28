# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 19:01:18 2018

@author: Laurens
"""

from selenium.webdriver.chrome.options import Options
from .parser import Parser
from pprint import pprint as print

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-infobars")

chrome_driver = 'c:\Windows\chromedriver.exe'

conf1 = """
Tweakers:
    Url: https://www.robeco.com/nl/carriere/vacatures/
    Save: //p/a[@class='arrow']
"""

conf2 = """
Tweakers:
    Url: https://www.robeco.com/nl/carriere/vacatures/
    Save:
        Elements: //p/a[@class='arrow']
        link: /@href
        name: .      
"""

conf2 = """
Tweakers:
    Url: https://www.robeco.com/nl/carriere/vacatures/
    Save:
        Elements: //p/a[@class='arrow']
        link: /@href
        name: .      
"""

conf3 = """
Tweakers:
    Url: https://www.robeco.com/nl/carriere/vacatures/
    Save:
        Elements: (//p/a[@class='arrow'])[1]
        link: /@href
        name: .  
"""


if __name__ == "__main__":
    print(Parser(conf1).storage)