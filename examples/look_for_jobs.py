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
from json import dumps

######
### Prepare SQL connection
######

def connect_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    
    # Create table if it does not exist yet
    create_table_sql = ["""
        CREATE TABLE IF NOT EXISTS `jobs` (
        	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        	`job`	TEXT NOT NULL,
        	`company`	TEXT,
        	`active`	INTEGER NOT NULL DEFAULT 1,
           `new`	INTEGER NOT NULL DEFAULT 1,
        	`timestamp`	TEXT NOT NULL,
        	`json`	TEXT
        );""","""
        CREATE INDEX IF NOT EXISTS `job_ind` ON `jobs` (
        	`job`	ASC
        );"""]
        
    for query in create_table_sql:
        c.execute(query)
    conn.commit()
    
    return conn

######
### Prepare a browser
######
def create_browser_session():  
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-infobars")
    
    chrome_driver = 'c:\Windows\chromedriver.exe'
    
    driver = webdriver.Chrome(chrome_options=chrome_options, 
                              executable_path=chrome_driver)
    
    return driver

######
### Parse job sites
######
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def get_joblist(driver):
    joblist = []
    path = "./examples/jobsites"
    
    # Loop over every website config found in the directory
    for file in os.listdir(path):
        if file.endswith(".yml"):
            with open(os.path.join(path, file)) as f: task = f.read()
            
            jobs = None
            jobsite = Parser(task, driver=driver, keep_driver=True)
            
            # Try to obtain job listings of the website
            try:
                jobs = jobsite.parse()
            except:
                pass
            
            if jobs == None or len(jobs) == 0:
               # Report to log if no job was found (possible sign of website change)
                with open(os.path.join(path, "errors.log"), 'a+') as f:
                    if jobs == None:
                        f.write(timestamp() + f": Error in parsing {file}\n")
                    else:
                        f.write(timestamp() + f": No results for {file}, possibly incorrect XPath (?)\n")
            else:
                # Add job to our list
                joblist.extend(jobs)
     
    return joblist
            
######
### Add jobs to database
######
def update_db(conn, joblist):
    c = conn.cursor()
    
    # Start by detecting new jobs previously unknown to us
    active = []
    new = []
    for job in joblist:
        result = c.execute(f"SELECT id FROM jobs WHERE '{job['Title']}'=job AND '{job['Company']}'=company AND active=1").fetchone()
        if result:
            active.append(result[0])
        else:
            new.append(job)

    # For all jobs that are no longer active, mark them as inactive
    c.execute("UPDATE jobs SET active = 0, new = 0 WHERE active = 1 AND id NOT IN (%s)" % ", ".join([str(x) for x in active]))

    # For all jobs that are new, add them to our database
    for job in new:
        c.execute(f"INSERT INTO jobs (job, company, timestamp, json) VALUES ('{job['Title']}', '{job['Company']}', '{timestamp()}', '{dumps(job)}')")
        
    conn.commit()
    
def main():
    driver = create_browser_session()
    joblist = get_joblist(driver)
    driver.quit()
    
    conn = connect_db("D:/Temp/db.sqlite")
    update_db(conn, joblist)
    conn.close()

if __name__ == "__main__":
    main()