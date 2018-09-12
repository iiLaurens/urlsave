# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:14:37 2018

@author: Luphcp1
"""

from urlsave.dev.bottle import get, post, request, run # or route
from urlsave import Parser, Browser
import json

from time import sleep

@get('/') # or @route('/login')
def get_urlsave(txt = ""):
    yield f'''
    <form action="/" method="post">
        <textarea name="cmd" rows="10" cols="80" style="white-space: pre;">{txt}</textarea>
    
    
        <fieldset>
            <legend>Choose some monster features</legend>
        
            <div>
                <input type="checkbox" id="headless" name="headless"
                       value="headless"/>
                <label for="headless">Headless Chrome</label>
                
                <br />
                
                <input type="checkbox" id="keep_driver" name="keep_driver"
                       value="keep_driver" checked />
                <label for="keep_driver">Keep driver alive (if not headless)</label>
            </div>    
        </fieldset>
    
        <input type="submit">
    </form>
    '''

@post('/') # or @route('/login', method='POST')
def do_urlsave():
    cmd = request.forms.get('cmd')
    
    headless = request.forms.get('headless')
    headless = True if headless else False
    
    keep_driver = request.forms.get('keep_driver')
    keep_driver = True if keep_driver else False

    
    yield from get_urlsave(cmd)
    
    yield f"Running...<br />"
    
    try:
        driver = Browser(headless=headless)
        
        p = Parser(cmd, driver)
        p.start()
        
        if headless or not keep_driver:
            driver.__exit__()
        
        output = json.dumps(p.storage, indent=2)
        
        yield f"""
        <fieldset>
            <legend>Result</legend>
            <pre>{output}</pre>
        </fieldset>
            """
    except:
        yield "Something failed"
    
run(host='localhost', port=8080)
