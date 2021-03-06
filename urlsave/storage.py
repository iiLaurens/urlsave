# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from datetime import datetime
from json import dumps
import sqlite3

class Storage(object):
    def __init__(self, path):
        self.path = path
        
        self.con = sqlite3.connect(self.path)
        
        self.initiate_db()
    
    def initiate_db(self):
        con = self.con
        
        c = con.cursor()
        
        # Create table if it does not exist yet
        create_table_sql = ["""
            CREATE TABLE IF NOT EXISTS `documents` (
            	`id`	    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            	`active`	 INTEGER NOT NULL DEFAULT 1,
              `new`	INTEGER NOT NULL DEFAULT 1,
              `subset` TEXT,
            	`start_timestamp` 	TEXT NOT NULL,
              `last_timestamp`  TEXT NOT NULL,
            	`json`	TEXT NOT NULL
            );""","""
            CREATE INDEX IF NOT EXISTS `json_ind` ON `documents` (
            	`json`	ASC
            );"""]
            
        for query in create_table_sql:
            c.execute(query)
        con.commit()
        

    def update_db(self, doclist, subset = None):
        con = self.con
    
        c = con.cursor()
        doclist = Storage.to_json_list(doclist)
        
        timestamp = Storage.make_timestamp()
        
        subset_qry = f"AND subset='{subset}'" if subset else ""
        
        # Start by detecting new jobs previously unknown to us
        active = []
        new = []
        for doc in doclist:
            result = c.execute(f"SELECT id FROM documents WHERE json='{doc}' AND active=1 {subset_qry}").fetchone()
            if result:
                active.append(result[0])
            else:
                new.append(doc)
    
        # For all jobs that are no longer active, mark them as inactive
        ids_str = ", ".join([str(x) for x in active])
        c.execute(f"UPDATE documents SET active = 0, new = 0 WHERE active = 1 AND id NOT IN ({ids_str}) {subset_qry}" )
        # For all jobs that are still active, update the last timestamp and remove new
        c.execute(f"UPDATE documents SET last_timestamp = '{timestamp}', new = 0 WHERE active = 1 {subset_qry}")
    
        # For all jobs that are new, add them to our database
        for doc in new:
            if subset:
                c.execute(f"INSERT INTO documents (start_timestamp, last_timestamp, subset, json) VALUES ('{timestamp}', '{timestamp}', '{subset}', '{doc}')")
            else:
                c.execute(f"INSERT INTO documents (start_timestamp, last_timestamp, json) VALUES ('{timestamp}', '{timestamp}', '{doc}')")
            
        con.commit()
            
        
    def get_new(self, subset = None):
        con = self.con
        c = con.cursor()
        
        subset_qry = f"AND subset='{subset}'" if subset else ""
        results = c.execute(f"SELECT json FROM documents WHERE new = 1 {subset_qry}").fetchall()
        return [x[0] for x in results]
    
    
    def get_active(self, subset = None):
        con = self.con
        c = con.cursor()
        
        subset_qry = f"AND subset='{subset}'" if subset else ""
        results = c.execute(f"SELECT json FROM documents WHERE active = 1 {subset_qry}").fetchall()
        return [x[0] for x in results]
        
    def query(self, qry):
        con = self.con
        
        c = con.cursor()
        return c.execute(qry).fetchall()
        
    
    def __enter__(self):
        return self
    
    
    def __exit__(self, *args, **kwargs):
        self.__del__()
        
        
    def __del__(self):
        self.con.close()
    
    @staticmethod
    def to_json_list(obj, split_dict = True):
        s = (',',':')
        
        if type(obj) == list:
            obj = [dumps(x, separators=s, ensure_ascii=False) for x in obj]
        elif type(obj) == dict and split_dict:
            obj = [dumps({k: obj[k]}, separators=s, ensure_ascii=False) for k in obj.keys()]
        else:
            obj = [dumps(obj, separators=s, ensure_ascii=False)]
        
        return obj
    
    @staticmethod
    def make_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M")
