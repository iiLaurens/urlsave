# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from pychrome import Browser as PyChromeBrowser
from urlsave.service import Service


class Browser(PyChromeBrowser):
    def __init__(self, executable=None, headless = True, **kwargs):  
        
        self.service = Service(executable=executable, headless = headless, **kwargs)
        
        # Attach a DevTools python interface
        super().__init__(url="http://127.0.0.1:" + str(self.service.port))
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.__del__()
        
    def __del__(self):
        try:
            self.service.__del__()
        except Exception:
            pass
        