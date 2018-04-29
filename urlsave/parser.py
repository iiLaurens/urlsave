# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from poyo import parse_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html
import re


#webdriver.Chrome(chrome_options=chrome_options, 
#                                       executable_path=chrome_driver)


class Parser(object):
    def __init__(self, job, driver=None, html=None):
        # If we have raw string, then transform it into a dictionary
        if type(job) == str:
            job = parse_string(job)
            
        # Store variables
        self.job = job
        self.driver = driver
        self.html = html
        
        if not driver and not html:
            raise Exception("No HTML provided and no webdriver found")
        elif driver and not self.job.get('Url'):
            raise Exception("No URL given in job config")
        
    def stop(self):
        # Neatly close the driver, if any
        if driver:
            self.driver.quit()
        
    def start(self):
        # Parse the URL. Either use a real webdriver (if available) to fetch
        # html from an url or fall back on provided html
        if self.driver and self.job.get('Url'):
            self.driver.get(self.job['Url'])
            self.html = self.driver.page_source
            
        self.page = html.fromstring(self.html)
        self.active_element = self.page
        
        # Parse list
        self.storage = self.save(self.job['Save'])
        
    def xpath(self, path):
        # Test validity of XPath
        path = path.strip()
        slash_pos = path.find("/")
        if slash_pos == -1 and path != ".":
            raise Exception(path + 'is not a valid XPath: requires a backslash')
            
        # Add a reference to the active element in scope with a leading dot
        if path[max(slash_pos - 1, 0)] != ".":
            path = path[:slash_pos] + "." + path[slash_pos:]
        
        return self.active_element.xpath(path)
        
    def save(self, job):
        if type(job) == str:
            # Seperate options from XPath string
            options = set(["-"+e for e in job.split(" -")[1:]])
            job = job.split(" -")[0]
            
            # Get results
            result = self.xpath(job)
            
            # Note that if the xpath delivers an element, the expression below
            # will extract all text contents and strip leading or trailing
            # whitespace. If not an element but already text, for example
            # because the xpath selects some attribute value such as class, 
            # then only stripping is required.
            result = [e.text_content().strip() if type(e) == html.HtmlElement
                      else e.strip() for e in result]
            
            # Keep only unique values if the unique option is set
            if len(set(["--unique", "-u"]) & options) > 0:
                seen = set()
                result = [x for x in result if not (x in seen or seen.add(x))]
            
            # If the result is a single value and not a list, then collapse
            # the list, unless this behaviour is turned off in the options
            if len(set(["--force-list", "-l"]) & options) == 0:
                result = result if len(result) != 1 else result[0]
                
                
            return result
            
        elif type(job) == dict:
            job = job.copy() # Prevent changes to original job by making copy
            
            results = []
            keys = []
            
            # Limit scope of XPath to certain elements if scope is given
            # or else fall back to current active element
            group_by = job.pop("Group by", ".")
            elements = self.xpath(group_by)
            for e in elements:
                self.active_element = e
                result = {}
                                   
                if "Save" in job.keys():
                    job = {key:job.get(key) for key in ["Keys", "Save"] if job.get(key)}

                for key, value in job.items():
                    result[key] = self.save(value)
                    
                if "Keys" in job.keys():
                    if group_by != ".":
                        if type(result["Keys"])!=str:
                            raise Exception("Keys XPath must return exactly one value per group")
                        keys.append(result.pop("Keys"))
                    else:
                        if not job.get("Save"):
                            raise Exception("'Keys' command requires 'Save' or 'Group by' command to match with")
                        elif type(result["Keys"]) == list and len(result["Keys"]) != len(result["Save"]):
                            raise Exception(f"Set returned by Save: {job['Save']} not same length as Keys: {job['Keys']}")
                        keys = result["Keys"]
                        results = result["Save"]
                        break
                            
                if "Save" in job.keys():
                    result = result["Save"]
                    
                results.append(result)        

            if len(keys) > 0:
                results = dict(zip(keys, results))
                
            return results

