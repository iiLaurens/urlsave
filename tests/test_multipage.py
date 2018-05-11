# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 21:47:09 2018

@author: Laurens
"""

from urlsave.parser import Parser
from textwrap import dedent
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def test_tweakers():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-infobars")

    chrome_driver = 'c:\Windows\chromedriver.exe'
    
    driver = webdriver.Chrome(chrome_options=chrome_options, 
                              executable_path=chrome_driver)
    
    ##################
    # First test job #
    ##################
    job = dedent("""
        Url: https://tweakers.net/nieuws/zoeken/
        Navigate:
            Action: Click
            Element: //*[@id="cookieAcceptForm"]//button
            Optional: True
            Timeout: 3
        Save:
            Group by: //div[@id="listingContainer"]//tr
            Title: //p[contains(@class, "title")]
            Replies: //td[@class="replies"]//a
     """).strip()
    
    test_obj = Parser(job, driver=driver, keep_driver=True)
    assert len(test_obj.parse()) == 25
        
    ##################
    # Second test job #
    ##################
    job = dedent("""
        Url: https://tweakers.net/nieuws/zoeken/
        Navigate:
            Action: Click
            Element: //*[@id="cookieAcceptForm"]//button
            Optional: True
            Timeout: 3
        Multipage:
            Next: //a[@class="next"]
            Max pages: 3
            Save:
                Group by: //div[@id="listingContainer"]//tr
                Title: //p[contains(@class, "title")]
                Replies: //td[@class="replies"]//a
     """).strip()
    
    test_obj = Parser(job, driver=driver, keep_driver=True)
    assert len(test_obj.parse()) == 75
    
    
   