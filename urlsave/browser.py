# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from shutil import which

class Browser(WebDriver):
    def __init__(self, *args, **kwargs):  
        # Set default options
        if 'chrome_options' not in kwargs:
            chrome_options = Options()
            chrome_options.add_argument("--disable-infobars")
            if kwargs.pop('headless', True):
                chrome_options.add_argument("--headless")
            
        if 'executable_path' not in kwargs:
            # Search for chromedriver in path environment
            executable_path = which('chromedriver')
            if executable_path is None:
                raise Exception("Chromedriver could not be found! Please add location to system path.")
        
        kwargs['chrome_options'] = chrome_options
        kwargs['executable_path'] = executable_path
            
        super(Browser, self).__init__(*args, **kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.quit()
        