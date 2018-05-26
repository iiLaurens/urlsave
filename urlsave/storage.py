# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from datetime import datetime
import os
from json import loads, dumps
import sqlite3

class Storage(object):
    def __init__(self, path):
        self.path = path
        self.con = self.connect_db()
    
    def connect_db(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        
        # Create table if it does not exist yet
        create_table_sql = ["""
            CREATE TABLE IF NOT EXISTS `documents` (
            	`id`	    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            	`active`	 INTEGER NOT NULL DEFAULT 1,
              `new`	INTEGER NOT NULL DEFAULT 1,
            	`start_timestamp` 	TEXT NOT NULL,
              `last_timestamp`  TEXT NOT NULL,
            	`json`	TEXT NOT NULL
            );""","""
            CREATE INDEX IF NOT EXISTS `json_ind` ON `documents` (
            	`json`	ASC
            );"""]
            
        for query in create_table_sql:
            c.execute(query)
        conn.commit()
        
        return conn
    
    def update_db(self, doclist):
        c = self.con.cursor()
        doclist = Storage.to_json_list(doclist)
        
        timestamp = Storage.make_timestamp()
        
        # Start by detecting new jobs previously unknown to us
        active = []
        new = []
        for doc in doclist:
            result = c.execute(f"SELECT id FROM documents WHERE json='{doc}' AND active=1").fetchone()
            if result:
                active.append(result[0])
            else:
                new.append(doc)
    
        # For all jobs that are no longer active, mark them as inactive
        c.execute("UPDATE documents SET active = 0, new = 0 WHERE active = 1 AND id NOT IN (%s)" % ", ".join([str(x) for x in active]))
        # For all jobs that are still active, update the last timestamp and remove new
        c.execute("UPDATE documents SET last_timestamp = '{timestamp}', new = 0 WHERE active = 1")
    
        # For all jobs that are new, add them to our database
        for doc in doclist:
            c.execute(f"INSERT INTO documents (start_timestamp, last_timestamp, json) VALUES ('{timestamp}', '{timestamp}', '{doc}')")
            
        self.con.commit()
    
    @staticmethod
    def to_json_list(obj, split_dict = True):
        s = (',',':')
        
        if type(obj) == list:
            obj = [dumps(x, separators=s) for x in obj]
        elif type(obj) == dict and split_dict:
            obj = [dumps({k: obj[k]}, separators=s) for k in obj.keys()]
        else:
            obj = [dumps(obj, separators=s)]
        
        return obj
    
    @staticmethod
    def make_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M")
