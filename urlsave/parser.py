# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

import yaml
from lxml import html
from time import sleep
import re

class Parser(object):
    def __init__(self, job, driver=None, keep_driver = False,
                 test_mode = False):
        # If we have raw string, then transform it into a dictionary
        if type(job) == str:
            job = yaml.load(job)
            
        # Store variables
        self.job = job
        self.driver = driver
        self.keep_driver = keep_driver
        self.storage = None
        
        if not driver and not html:
            raise Exception("No HTML provided and no webdriver found")
        elif driver and not self.job.get('Url') and not test_mode:
            raise Exception("No URL given in job config")
        
    def start(self):
        job = self.job.copy()
        self.parse(job)
    
        
    def parse(self, job):
        job = listify(job)
        
        # Get first task of our scheduled job
        for task in job:
            try:
                name, value = list(task.items())[0]
                name = name.lower()
            except:
                raise Exception("Top level task must be a dict.")
            
            try:
                getattr(self, name)(value)
            except AttributeError:
                raise SyntaxError(f"A task with name '{name}' does not exist.")
    
    def url(self, value):
        self.driver.get(value)
        self.update()
        
    def update(self):
        self.html = self.driver.page_source
        self.page = html.fromstring(self.html)
        self.active_element = self.page
    
    
    def navigate(self, value):
        navi = listify(value)
        # This function expects a list of dicts, with each dict describing
        # an action with possible parameters.
        
        # Get first task of our first navigation action
        for task in navi:   
            try:
                name, value = list(task.items())[0]
                name = name.lower()
            except:
                raise Exception("Navigation action must be a dict.")
            
            if name.lower() == "click":
                try:
                    self.driver.find_element_by_xpath(value).click()
                except:
                    raise Exception("XPath did not lead to an element to click")
                        
        
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
        
        
    def save(self, save):

        if type(save) == str:
            return self.save_xpath(save)
        
        if type(save) == list:
            return [self.save(x) for x in save]
        
        if type(save) == dict:
            dic = {k: self.save(v) for k, v in save.items()}
            
            for k in dic:
                isKeysMatch = re.match("keys\((.*)\)", k)
                if isKeysMatch:
                    values = dic.pop(k)
                    if type(values) != list:
                        raise Exception(f"Value(s) belonging to {k} must be a list")
                    keys = self.save_xpath(isKeysMatch[1])
                    if len(keys) != len(values):
                        raise Exception(f"Cannot zip keys and values of {k} if not same length")
                    
                    for i in range(len(keys)):
                        dic[keys[i]] = values[i]
            
            return dic
                
                
        
        
def listify(obj):
    lst = []
    if type(obj) == dict:
        for k, v in obj.items():
            lst.append({k: v})
    if type(obj) == list:
        lst = obj
    elif type(obj) != list:
        raise Exception("Parser did not receive a list or dictionary!")
        
    return lst


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
            