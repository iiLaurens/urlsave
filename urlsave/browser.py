# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

import os
import pychrome

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

from tempfile import TemporaryDirectory
from shutil import which
from re import search


class Browser(WebDriver):
    def __init__(self, *args, **kwargs):  
        # Set default options
        if 'chrome_options' not in kwargs:
            chrome_options = Options()
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--window-size=1920,1080")
            if kwargs.pop('headless', True):
                chrome_options.add_argument("--headless")
            
        if 'executable_path' not in kwargs:
            # Search for chromedriver in path environment
            executable_path = which('chromedriver')
            if executable_path is None:
                raise Exception("Chromedriver could not be found! Please add location to system path.")
        
        # Create temporary directory for logging
        self.tmpdir = TemporaryDirectory()
        
        kwargs['chrome_options'] = chrome_options
        kwargs['executable_path'] = executable_path
        kwargs['service_args'] = [f'--log-path={os.path.join(self.tmpdir.name, "driver.log")}']
            
        super(Browser, self).__init__(*args, **kwargs)


        # Extract DevTools port
        with open(os.path.join(self.tmpdir.name, "driver.log")) as f:
            match = search("remote-debugging-port=([0-9]+)", f.read())
            
        if match:
            # Isolote the capture group containg the port
            self.devToolsPort = match.group(1)
        else:
            raise Exception("Could not extract DevTools port from chromedriver log!")
        
        # Attach a DevTools python interface
        self.dt = pychrome.Browser(url="http://127.0.0.1:" + str(self.devToolsPort))
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.quit()
        self.tmpdir.cleanup()
        