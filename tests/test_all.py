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

@pytest.fixture(scope='session')  # one server to rule'em all
def driver():  
    with Browser() as driver:
        yield driver

    
@pytest.mark.parametrize("job,page,result", [
    ("simple_save",         "pokedex_full", "list_pokemons"),
    ("simple_save_details", "pokedex_full", "list_pokemons_details"),
    ("pokemon_keys_to_abilities", "pokedex_full", "dict_pokemons_abilities"),
    ("pokemon_keys_to_details", "pokedex_full", "dict_pokemons_details"),
    ("pokemon_keys_to_numbers_no_grouping", "pokedex_full", "dict_pokemons_numbers"),
    ("filter_on_ability", "pokedex_full", "dict_pokemons_abilities_normal"),
    ("filter_on_pure_normal", "pokedex_full", "dict_pokemons_pure_normal"),
    ("multipage_pokemons", "pokedex_a-1", "list_pokemons_details"),
    ("multipage_pokemons_ajax", "pokedex_full_loading", "list_pokemons_details"),
    ("multipage_pokemons_scroll", "pokedex_full_scroll_load", "list_pokemons_details"),
])
def test_parser(driver, job, page, result):
    job =  os.path.join(os.getcwd(), "tests", "jobs", job + ".txt")
    result = os.path.join(os.getcwd(), "tests", "results", result + ".txt")
    
    # Load our job
    with open(job) as f:
        job = f.read()
    
    # Load the test result
    with open(result) as f:
        result = json.loads(f.read())
    
    # Pre-set the browsers webpage
    driver.get("https://iilaurens.github.io/urlsave/tests/pages/" + page + ".html")
    
    parser = Parser(job, driver = driver, keep_driver = True, test_mode = True)
    parser.start()
    
    assert parser.storage == result
    
def test_storage(tmpdir):
    # Make sure we have a temporary sqlite database
    db = os.path.join(tmpdir, "test.sqlite")
    if os.path.exists(db):
        os.remove(db)  
    db = Storage(db)
    
    # Load something we can possibly store
    src = os.path.join(os.getcwd(), "tests", "results", "list_pokemons_details.txt")
    with open(src, 'r') as f:
        lst = json.loads(f.read())
    
    db.update_db(lst[:100])
    
    db.update_db(lst[50:150])
    
    assert len(db.query("SELECT * FROM documents WHERE active=0")) == 50
    assert len(db.query("SELECT * FROM documents WHERE new=1")) == 50
    assert len(db.query("SELECT * FROM documents WHERE new=0 AND active=0")) == 50
    
    
def create_parse_test(job, job_file, page, result_file):
    with Browser() as driver:
        # Pre-set the browsers webpage
        driver.get("https://iilaurens.github.io/urlsave/tests/pages/" + page + ".html")
        parser = Parser(job, driver = driver, keep_driver = True, test_mode = True)
        parser.start()
        result = parser.storage
    
    job_file =  os.path.join(os.getcwd(), "tests", "jobs", job_file + ".txt")
    result_file = os.path.join(os.getcwd(), "tests", "results", result_file + ".txt")
    
    with open(job_file, 'w+') as f:
        f.write(job)
        
    with open(result_file, 'w+') as f:
        f.write(json.dumps(result, indent=2, separators=(',', ': ')))
    