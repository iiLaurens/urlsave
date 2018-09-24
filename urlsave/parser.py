# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

import yaml
from lxml import html
from time import sleep
import re
from urllib.parse import urljoin, urlparse
import os
from locale import atof

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Parser(object):
    def __init__(self, job, driver=None, test_mode = False):
        # If we have raw string, then transform it into a dictionary
        if type(job) == str:
            job = read_secrets(job)
            job = yaml.load(job)
            
        # Store variables
        self.job = job
        self.driver = driver
        self.storage = None
        
        if not self.job.get('Url'):
            raise Exception("No URL given in job config")
        
    def start(self):
        job = self.job.copy()        
        self.parse(job)
    
    
    def test(self, job):
        name, value = list(job.items())[0]
        name = name.lower()
        results = getattr(self, name)(value)
        self.test_recursive(results)
    
    
    def test_recursive(self, results, path = "$"):
        # Traverse our result object recursively and find any empty list/dict
        if results == None:
            if path == "$":
                parent = "root"
            elif path[-1] == "]":
                parent = "list"
            else:
                parent = "dict"
            raise XPathException(f"Testing of XPath resulted in empty {parent}: {path}")
        elif type(results) == list:
            for i in range(len(results)):
                self.test_recursive(results[i], path + f"[{i}]")
        elif type(results) == dict:
            for i in results:
                self.test_recursive(results[i], path + f".{i}")   
        
    
    def navigate(self, value):
        navi = listify(value)
        # This function expects a list of dicts, with each dict describing
        # an action with possible parameters.
        
        # Get first task of our first navigation action
        for task in navi:   
            try:
                name, value = list(task.items())[0]
                name = name.lower().replace(" ", "_")
            except:
                raise YAMLException("Navigation action must be a dict.")
            
            if name.lower() == "wait for":
                self.wait_for_element(value)
                
            if name.lower() == "pause":
                sleep(value)
            
            if name.lower() == "click":
                try:
                    self.wait_for_element(value)
                except:
                    raise XPathException(f"XPath did not lead to an element to click: {value}")
                self.driver.find_element_by_xpath(value).click()
                    
            if name.lower() == "fill":
                path = value["Path"]
                value = value["Value"]
                try:
                    self.wait_for_element(path)
                except:
                    raise XPathException(f"XPath did not lead to textbox: {path}")
                self.driver.find_element_by_xpath(path).send_keys(str(value))
                
            if name.lower() == "url":
                self.url(value)
            
            self.update()


    def wait_for_element(self, path):
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, path)))
    
    
    def multipage(self, job):
        max_pages = job.get("Max pages", 10)
        pause_time = job.get("Pause", 0.5)
        next_path = job.get("Next")
        scroll_load = job.get("Scrolling", False)
        cumulative = job.get("Cumulative", False)
        group = ("Group" in job)
        
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
                self.update()
                result = self.group(job["Group"]) if group else self.save(job["Save"])
                results.append(result)
            
            if page + 1 == max_pages:
                break

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
        
        if not cumulative:
            result = merge_results(results)
        else:
            self.update()
            result = self.group(job["Group"]) if group else self.save(job["Save"])
        
        return result
    
                            
    def xpath(self, path):
        # Test validity of XPath
        NSregexp = "http://exslt.org/regular-expressions"
        return self.active_element.xpath(path, namespaces={"re": NSregexp})
    
        
    def save_xpath(self, job):
        # Strip trailing or leading whitespace from
        job = job.strip()
        
        # Seperate options/arguments from XPath string
        options = ["--"+x for x in job.split(" --")[1:]]
        job = job.split(" --")[0]
        
        if '--text' in options:
            return job
        
        # Get results
        result = self.xpath(job)
        
        # Note that if the xpath delivers an element, the expression below
        # will extract all text contents and strip leading or trailing
        # whitespace. If not an element but already text, for example
        # because the xpath selects some attribute value such as class, 
        # then only stripping is required.      
        if type(result) == list:
            result = [e.text_content().strip() if type(e) == html.HtmlElement
                      else e.strip() for e in result]
        else:
            # This might happen when an text or string is returned, for example
            # after a re:replace function
            result = [str(result).strip()]
        
        if len(result) == 0:
            return None
        
        if '--url' in options:
            result = make_absolute_url(self.driver.current_url, result)
            
        if '--number' in options:
            result = [atof(x) for x in result]

        if '--unique' in options:
            try:
                result = list(dict.fromkeys(result))
            except:
                raise Exception("Could not remove duplicates! Ensure that the output is a list of strings.")
        
        # If the single option is given, then collapse the list
        if not '--keep-list' in options:
            result = result if len(result) != 1 else result[0]
        
        return result
        
    
    def save(self, save):
        if type(save) == str:
            return self.save_xpath(save)
        
        if type(save) == list:
            return [self.save(x) for x in save]
        
        if type(save) == dict:
            save = save.copy()
            dic = {k: self.save(v) for k, v in save.items()}
            
            for k in dic.copy():
                keyPath = re.match("Keys\((.*)\)", k)
                if keyPath:
                    values = dic.pop(k)
                    keys = self.save_xpath(keyPath[1])
                    dic = zip_keys(dic, keys, values)
            
            return dic
        
    def group(self, job):
        job = job.copy()
        by = job.pop("By", None)
        save = job.pop("Save", None)
        
        if not by or not save:
            raise Exception("Group statements needs 'By' and 'Save' clause")
        
        lst = []
        keys = []
        elements = self.xpath(by)
        if len(elements) == 0:
            return None
        
        for e in elements:
            self.active_element = e
            lst.append(self.save(save))
            if "Keys" in job:
                keys.append(self.save_xpath(job["Keys"]))
                
        if len(keys) > 0:
            if len(keys) != len(lst):
                raise Exception("Cannot create dictionary in group because not enough keys found")
            dic = {}
            return zip_keys(dic,keys, lst)
        
        return lst
    
    def url(self, value):
        self.driver.get(value)
        self.update()
        
        
    def update(self):
        self.html = self.driver.page_source
        self.page = html.document_fromstring(self.html)
        self.active_element = self.page
        
    def parse(self, job):
        job = listify(job)
        
        # Get first task of our scheduled job
        for task in job:
            try:
                name, value = list(task.items())[0]
                name = name.lower()
            except:
                raise Exception("Top level task must be a dict.")
            
            
            if name in ["save", "group", "multipage"]:
                self.storage = getattr(self, name)(value)
                continue
            
            try:
                getattr(self, name)(value)
            except AttributeError:
                raise AttributeError(f"A task with name '{name}' does not exist.")
    
    
    
        
def listify(obj):
    lst = []
    if type(obj) == dict:
        for k, v in obj.items():
            lst.append({k: v})
    elif type(obj) == list:
        lst = obj
    elif type(obj) == str:
        lst = [obj]
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
                    result[k] = merge_results([result[k], i[k]])               
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

def zip_keys(dic, keys, values):
    """
    Merge keys and lists and add to original dictionary. Keys are defined
    by an XPath string.
    """
    if keys == None or values == None:
        raise Exception("Keys and/or values appear to be missing when zipping!")
    if type(values) != list:
        raise Exception(f"Value(s) belonging to {keys} must be a list")
    if len(keys) != len(values):
        raise Exception(f"Cannot zip keys and values of {keys} if not same length")
    
    for i in range(len(keys)):
        dic[keys[i]] = values[i]
        
    return dic

def make_absolute_url(current, hrefs):
    new = hrefs.copy()
    for idx, href in enumerate(hrefs):
        if not bool(urlparse(href).netloc):
            new[idx] = urljoin(current, href)
    return new

def read_secrets(s):
    values = []
    for match in re.finditer("\{\{(.*):(.*)\}\}", s):
        try:
            with open(os.path.normpath(match[1])) as f:
                value = yaml.load(f.read())[match[2]]
            values.append(value)
        except:
            raise YAMLException(f"Could not extract secret with key '{match[2]}' from file: {match[1]}")
                
    for v in values:
        s = re.sub("\{\{.*:.*\}\}", str(v), s, count=1)
        
    return s

class YAMLException(Exception):
    pass

class XPathException(Exception):
    pass