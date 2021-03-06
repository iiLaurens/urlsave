# -*- coding: utf-8 -*-
"""
Created on Fri May 25 19:14:35 2018

@author: Laurens
"""

import pytest
import json
import os
from tempfile import TemporaryFile
from urlsave import Parser, Browser, Storage
from urlsave.parser import XPathException

@pytest.fixture(scope='session')  # one server to rule'em all 
def driver():  
    """
    This function provides a single session shared over all tests (to save on time)
    """
    with Browser() as driver:
        yield driver

    
@pytest.mark.parametrize("input, output", [
    ("001_save_single_xpath",        "001_output"),
    ("002_save_single_xpath_scalar", "002_output"),
    ("003_save_list_xpath", "003_output"),
    ("004_save_dict_xpath", "004_output"),
    ("005_save_nested", "005_output"),
    ("006_save_argument_text", "006_output"),
    ("007_save_argument_keep-list", "007_output"),
    ("008_save_argument_unique", "008_output"),
    ("009_save_argument_number", "009_output"),
    ("010_save_argument_url", "010_output"),
    ("011_save_dict_pair", "011_output"),
    ("012_group_list", "012_output"),
    ("013_group_dict", "013_output"),
    ("014_multipage_save", "014_output"),
    ("015_multipage_max_pages", "015_output"),
    ("016_multipage_load_button", "016_output"),
    ("017_multipage_load_button_max_pages", "017_output"),
    ("018_multipage_load_scroll", "018_output"),
    ("019_multipage_load_scroll_max_pages", "019_output"),
])
def test_parser(driver, input, output):
    driver.get("about:blank") # blank out page

    input =  os.path.join(os.getcwd(), "tests", "jobs", input + ".yml")
    output = os.path.join(os.getcwd(), "tests", "results", output + ".json")
    
    # Load our job
    with open(input) as f:
        input = f.read()
    
    # Load the test result
    with open(output, encoding="utf-8") as f:
        output = json.loads(f.read())
    
    parser = Parser(input, driver = driver)
    parser.start()
    
    assert parser.storage == output
    
# def test_storage(tmpdir):
#     # Make sure we have a temporary sqlite database
#     db = os.path.join(tmpdir, "test.sqlite")
#     if os.path.exists(db):
#         os.remove(db)  
#     db = Storage(db)
    
#     # Load something we can possibly store
#     src = os.path.join(os.getcwd(), "tests", "results", "list_pokemons_details.txt")
#     with open(src, 'r') as f:
#         lst = json.loads(f.read())
    
#     db.update_db(lst[:100])
    
#     db.update_db(lst[50:150])
    
#     assert len(db.query("SELECT * FROM documents WHERE active=0")) == 50
#     assert len(db.query("SELECT * FROM documents WHERE new=1")) == 50
#     assert len(db.query("SELECT * FROM documents WHERE new=0 AND active=0")) == 50


# @pytest.mark.parametrize("job", ["test_function_1", "test_function_2", "test_function_3"])
# def test_tester(driver, job):
#     driver.get("https://iilaurens.github.io/urlsave/tests/pages/pokemon_full.html")
    
#     job =  os.path.join(os.getcwd(), "tests", "jobs", job + ".txt")
#     with open(job) as f:
#         job = f.read()
    
#     parser = Parser(job, driver = driver, test_mode = True)

#     with pytest.raises(XPathException) as e_info:
#         parser.start()
