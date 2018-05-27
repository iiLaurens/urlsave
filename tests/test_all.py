# -*- coding: utf-8 -*-
"""
Created on Fri May 25 19:14:35 2018

@author: Laurens
"""

import pytest
import json
import os
from urlsave import Parser, Browser
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope='session')  # one server to rule'em all
def driver():  
    with Browser() as driver:
        yield driver

    
@pytest.mark.parametrize("job,page,result", [
    ("simple_save",         "pokedex_full", "list_pokemons"),
    ("simple_save_details", "pokedex_full", "list_pokemons_details"),
    ("unique_abilities", "pokedex_full", "list_abilities"),
    ("pokemon_keys_to_abilities", "pokedex_full", "dict_pokemons_abilities"),
    ("pokemon_keys_to_details", "pokedex_full", "dict_pokemons_details"),
    ("pokemon_keys_to_numbers_no_grouping", "pokedex_full", "dict_pokemons_numbers"),
    ("filter_on_ability", "pokedex_full", "dict_pokemons_abilities_normal"),
    ("filter_on_pure_normal", "pokedex_full", "dict_pokemons_pure_normal"),
    ("multipage_pokemons", "pokedex_a-1", "list_pokemons_details"),
    ("multipage_pokemons_ajax", "pokedex_full_loading", "list_pokemons_details"),
    ("multipage_pokemons_scroll", "pokedex_full_scroll_load", "list_pokemons_details"),
])
def test_eval(driver, job, page, result):
    page = os.path.join(os.getcwd(), "tests", "pages", page + ".html")
    job =  os.path.join(os.getcwd(), "tests", "pages", job + ".txt")
    result = os.path.join(os.getcwd(), "tests", "pages", result + ".txt")
    
    # Load our job
    with open(job) as f:
        job = f.read()
    
    # Load the test result
    with open(result) as f:
        result = json.loads(f.read())
    
    # Pre-set the browsers webpage
    driver.get(page)
    
    parser = Parser(job, driver = driver, keep_driver = True, test_mode = True)
    outcome = parser.parse()
    
    assert outcome == result
    
def create_test(job, job_file, page, result_file):
    page = os.path.join(os.getcwd(), "tests", "pages", page + ".html")
    browser_args = get_driver_options()
    with Browser(**browser_args) as driver:
        # Pre-set the browsers webpage
        driver.get(page)
        parser = Parser(job, driver = driver, keep_driver = True, test_mode = True)
        result = parser.parse()
    
    job_file =  os.path.join(os.getcwd(), "tests", "pages", job_file + ".txt")
    result_file = os.path.join(os.getcwd(), "tests", "pages", result_file + ".txt")
    
    with open(job_file, 'w+') as f:
        f.write(job)
        
    with open(result_file, 'w+') as f:
        f.write(json.dumps(result, indent=2, separators=(',', ': ')))
    