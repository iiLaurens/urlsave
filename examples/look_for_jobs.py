# -*- coding: utf-8 -*-
"""
Created on Fri May 11 18:45:57 2018

@author: Laurens
"""

import sqlite3
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import os
from urlsave.parser import Parser
from datetime import datetime

######
### Prepare SQL connection
######

conn = sqlite3.connect("D:/Temp/db.sqlite")
c = conn.cursor()

create_table_sql = ["""
    CREATE TABLE IF NOT EXISTS `jobs` (
    	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    	`job`	TEXT NOT NULL,
    	`company`	TEXT,
    	`active`	INTEGER NOT NULL DEFAULT 1,
    	`timestamp`	TEXT NOT NULL,
    	`json`	TEXT
    );""","""
    CREATE INDEX IF NOT EXISTS `job_ind` ON `jobs` (
    	`job`	ASC
    );"""]
    
for query in create_table_sql:
    c.execute(query)
    
    
######
### Prepare a browser
######
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-infobars")

chrome_driver = 'c:\Windows\chromedriver.exe'

driver = webdriver.Chrome(chrome_options=chrome_options, 
                          executable_path=chrome_driver)

######
### Parse job sites
######
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H-%M")

jobs = []
path = "./examples/jobsites"
for file in os.listdir(path):
    if file.endswith(".yml"):
        with open(os.path.join(path, file)) as f: task = f.read()
        try:
            jobsite = Parser(task, driver=driver, keep_driver=True)
            jobs = jobsite.parse()
        except:
            jobs = None
        
        if jobs == None or len(jobs) == 0:
            with open(os.path.join(path, "errors.log"), 'a+') as f:
                if jobs == None:
                    f.write(timestamp() + f": Error in parsing {file}")
                else:
                    f.write(timestamp() + f": No results for {file}, possibly incorrect XPath (?)")
        
        else:
            jobs.extend(jobs)
    
conn.commit()
conn.close()