# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from selenium.webdriver.chrome.webdriver import WebDriver

class Browser(WebDriver):
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.quit()
        