# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from poyo import parse_string
from lxml import html
from time import sleep

class Parser(object):
    def __init__(self, job, driver=None, html=None, keep_driver = False, test_mode = False):
        # If we have raw string, then transform it into a dictionary
        if type(job) == str:
            job = parse_string(job)
            
        # Store variables
        self.job = job
        self.driver = driver
        self.html = html
        self.keep_driver = keep_driver
        
        if not driver and not html:
            raise Exception("No HTML provided and no webdriver found")
        elif driver and not self.job.get('Url') and not test_mode:
            raise Exception("No URL given in job config")
        
        
    def parse(self):
        # Parse the URL. Either use a real webdriver (if available) to fetch
        # html from an url or fall back on provided html
        if self.driver and self.job.get('Url'):
            self.driver.get(self.job['Url'])
        
        if self.driver:
            self.html = self.driver.page_source
            
        self.page = html.fromstring(self.html)
        self.active_element = self.page
        
        if self.driver and self.job.get('Navigate'):
            self.navigate(self.job['Navigate'])
        
        # Parse list
        if self.job.get("Multipage"):
            self.storage = self.multipage(self.job['Multipage'])
        elif self.job.get("Save"):
            self.storage = self.save(self.job['Save'])
            
        
        if self.driver and not self.keep_driver:
            self.driver.quit()
        
        return self.storage
    
    
    def navigate(self, jobs):
        jobs = jobs.copy() # Prevent changes to original job by making copy
        
        if type(jobs) != list:
            jobs = [jobs]
        
        for job in jobs:
            if job["Action"] == "Click":
                self.driver.implicitly_wait(job.get("Timeout", 1))
                try:
                    self.driver.find_element_by_xpath(job["Element"]).click()
                except:
                    if not job.get("Optional", False):
                        raise
        
        sleep(0.5)
        self.html = self.driver.page_source
        self.page = html.fromstring(self.html)
        self.active_element = self.page
        
        
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
    
    
    def multipage(self, job):
        max_pages = job.get("Max pages", 10)
        next_path = job.get("Next")
        
        if not next_path or not job.get("Save"):
            raise Exception("Multipage requires an XPath and Save")
        
        # Detect if the save in the multipage is grouped
        if type(job["Save"]) == dict and job["Save"].get("Group by"):
            is_grouped = True
        else: is_grouped = False
        
        results = []
        
        for page in range(max_pages):
            results.append(self.save(job["Save"]))
            
            if page < max_pages:
                self.driver.implicitly_wait(0)
                try:
                    e = self.driver.find_element_by_xpath(job["Next"])
                except:
                      break  
                self.driver.execute_script("return arguments[0].scrollIntoView();", e)
                
                # Give the browser some time to do it's thing
                sleep(0.5)
                e.click()
                sleep(0.5)
                
                self.html = self.driver.page_source
                self.page = html.fromstring(self.html)
                self.active_element = self.page
        
        if is_grouped:
            if type(results[0]) == dict:
                result = {}
                for i in results:
                    for k, v in i.items():
                        result[k] = v
            if type(results[0]) == list:
                result = []
                for i in results:
                    for v in i:
                        result.append(v)    
        else:
            if type(results[0]) == dict:
                result = {}
                for i in results:
                    for k in i.keys():
                        result[k] = result.get(k, []) + (i[k] if type(i[k]) == list else [i[k]])
            if type(results[0]) == list:
                raise Exception("This case is not programmed yet")
        
        return result
            

    def save_xpath(self, job):
        # Seperate options from XPath string
        options = [("-"+e).split(" ") for e in job.split(" -")[1:]]
        options = {x[0]:x[1:] for x in options}
        job = job.split(" -")[0]
        
        #
        if len(set(["--text", "-t"]) & set(options.keys())) > 0:
            return job
        
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
        if len(set(["--unique", "-u"]) & set(options.keys())) > 0:
            seen = set()
            result = [x for x in result if not (x in seen or seen.add(x))]
        
        # If the result is a single value and not a list, then collapse
        # the list, unless this behaviour is turned off in the options
        if len(set(["--force-list", "-l"]) & set(options.keys())) == 0:
            result = result if len(result) != 1 else result[0]
            
        return result
        
        
    def save(self, job):
        if type(job) == str:
            return self.save_xpath(job)
        
        if type(job) == dict:
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
                    break_outer = True if result[key] == None else False
                if break_outer: continue
                    
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
                
                if len(result) > 0:
                    results.append(result)

            if len(keys) > 0:
                results = dict(zip(keys, results))
                
            return results

