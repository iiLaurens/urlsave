# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

import yaml
from lxml import html
from time import sleep

class Parser(object):
    def __init__(self, job, driver=None, html=None, keep_driver = False,
                 test_mode = False):
        # If we have raw string, then transform it into a dictionary
        if type(job) == str:
            job = yaml.load(job)
            
        # Store variables
        self.job = job
        self.driver = driver
        self.html = html
        self.keep_driver = keep_driver
        self.storage = None
        
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
            
        if self.driver and self.job.get('Navigate'):
            self.navigate(self.job['Navigate'])
            
        self.page = html.fromstring(self.html)
        self.active_element = self.page
        
        # Parse list
        if self.job.get("Multipage"):
            self.storage = self.multipage(self.job['Multipage'])
            
        elif self.job.get("Save"):
            self.storage = self.save(self.job['Save'])
        
        if self.driver and not self.keep_driver:
            self.driver.quit()
        
        return self.storage
    
    
    def navigate(self, jobs):
        # This function expects a list of dicts. Each dict corresponds to
        # some action that corresponds to navigating the page.
        jobs = jobs.copy() # Prevent changes to original job by making copy
        
        # Navigation will always expect a list. Dicts do not allow repeated
        # keys and are tricky to organize in the correct order. If we only
        # have one dict, then put it in a list
        if type(jobs) != list:
            jobs = [jobs]
        
        for job in jobs:
            if "Wait" in job:
                sleep(job["Wait"])
                
            elif "Scroll" in job:
                if type(job["Scroll"]) == int:
                    self.driver.execute_script(f"return window.scrollBy(0, {job['Scroll']});")
                    
            elif "Click" in job:
                self.driver.implicitly_wait(job.get("Timeout", 1))
                try:
                    self.driver.find_element_by_xpath(job["Click"]).click()
                except:
                    if not job.get("Optional", False):
                        raise Exception("Couldn't find XPath needed to click")
                
                
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
        pause_time = job.get("Pause", 0.5)
        next_path = job.get("Next")
        scroll_load = job.get("Scrolling", False)
        cumulative = job.get("Cumulative", False)
        
        if not next_path and not scroll_load:
            raise Exception("Multipage requires an XPath for next button")
            
        if scroll_load:
            cumulative = True
            last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        results = []
        
        for page in range(max_pages):           
            self.driver.implicitly_wait(0)
            
            # If each page contains new items only, then we have to accumulate
            # the results manually.
            if not cumulative:
                results.append(self.save(self.job["Save"]))
            
            if not scroll_load:
                # Try to find the next button in source, or stop if not found
                try:
                    e = self.driver.find_element_by_xpath(job["Next"])
                except:
                      break
                
                # Scroll into view of the newxt button
                self.driver.execute_script("return arguments[0].scrollIntoView();", e)
                
                # Give the browser some time to scroll and then press the button
                sleep(0.5)
                e.click()
                sleep(pause_time)
            else:
                # Scrolling is needed to load new elements, so scroll down and
                # check if we moved at all
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Set next page
            if not cumulative:
                self.html = self.driver.page_source
                self.page = html.fromstring(self.html)
                self.active_element = self.page
        
        if not cumulative:
            result = Parser.merge_results(results)
        else:
            self.html = self.driver.page_source
            self.page = html.fromstring(self.html)
        
            self.active_element = self.page.body
        
            result = self.save(self.job['Save'])
        
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
        
        if type(job) == list:
            return [self.save(x) for x in job]
        
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

    @staticmethod
    def merge_results(results):
        # This function takes saved objects from several pages and combines
        # them into a single object.
        
        if type(results[0]) == dict:
            # Case: we have a saved object that was not grouped and in dict
            # format. We should therefore combine all keys of the dicts, but
            # also combine among shared keys. This is tricky, since
            # the value of the dict can itself be a list, dict or scalar.
            result = results[0]
            for i in results[1:]:
                for k in i.keys():
                    if k not in result.keys():
                        result[k] = i[k]
                    else:
                        result[k] = Parser.merge_results([result[k], i[k]])               
        else:
            # Case: we have a grouped object as a list object or scalar.
            # We can simply merge the two lists since groups should be
            # mutually exclusive.
 
            result = []
            for i in results:
                if type(i) != list:
                    result.append(i)
                else:
                    for v in i:
                        result.append(v) 
    
        return result
            