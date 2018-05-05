# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 21:47:09 2018

@author: Laurens
"""

from urlsave.parser import Parser
from textwrap import dedent

def test_pokedex():
    with open("./tests/pokedex.html","r") as f:
        read_data = f.read()
        
    ##################
    # First test job #
    ##################
    job = 'Save: //div[@class="pokemon-info"]/h5'
    result = ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Charmander', 'Charmeleon',
              'Charizard', 'Squirtle', 'Wartortle', 'Blastoise', 'Caterpie',
              'Metapod', 'Butterfree']
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    
    ###################
    # Second test job #
    ###################
    job = dedent("""
        Save:
            Group by: //div[@class="pokemon-info"]
            name: /h5
            id: /p[@class="id"]
            abilities: /div[@class="abilities"]/span
            
     """).strip()
    result = [{'name': 'Bulbasaur', 'id': '#001', 'abilities': ['Grass', 'Poison']},
              {'name': 'Ivysaur', 'id': '#002', 'abilities': ['Grass', 'Poison']},
              {'name': 'Venusaur', 'id': '#003', 'abilities': ['Grass', 'Poison']},
              {'name': 'Charmander', 'id': '#004', 'abilities': 'Fire'},
              {'name': 'Charmeleon', 'id': '#005', 'abilities': 'Fire'},
              {'name': 'Charizard', 'id': '#006', 'abilities': ['Fire', 'Flying']},
              {'name': 'Squirtle', 'id': '#007', 'abilities': 'Water'},
              {'name': 'Wartortle', 'id': '#008', 'abilities': 'Water'},
              {'name': 'Blastoise', 'id': '#009', 'abilities': 'Water'},
              {'name': 'Caterpie', 'id': '#010', 'abilities': 'Bug'},
              {'name': 'Metapod', 'id': '#011', 'abilities': 'Bug'},
              {'name': 'Butterfree', 'id': '#012', 'abilities': ['Bug', 'Flying']}]
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    
    ##################
    # Third test job #
    ##################
    job = dedent("""
        Save:
            name: //div[@class="pokemon-info"]/h5
            id: //div[@class="pokemon-info"]/p[@class="id"]
            abilities: //div[@class="abilities"]/span -u
            
     """).strip()
    result = [{'name': ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Charmander',
                        'Charmeleon', 'Charizard', 'Squirtle', 'Wartortle',
                        'Blastoise', 'Caterpie', 'Metapod', 'Butterfree'],
               'id': ['#001', '#002', '#003', '#004', '#005', '#006', '#007',
                      '#008', '#009', '#010', '#011', '#012'],
               'abilities': ['Grass', 'Poison', 'Fire', 'Flying', 'Water', 'Bug']}]
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    ###################
    # Fourth test job #
    ###################
    job = dedent("""
        Save:
            Group by: //div[@class="pokemon-info"]
            Keys: /h5
            Save: //div[@class="abilities"]/span
            
     """).strip()
    result = {'Bulbasaur': ['Grass', 'Poison'], 'Ivysaur': ['Grass', 'Poison'],
              'Venusaur': ['Grass', 'Poison'], 'Charmander': 'Fire',
              'Charmeleon': 'Fire', 'Charizard': ['Fire', 'Flying'],
              'Squirtle': 'Water', 'Wartortle': 'Water',
              'Blastoise': 'Water', 'Caterpie': 'Bug', 'Metapod': 'Bug',
              'Butterfree': ['Bug', 'Flying']}
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    ###################
    # Fifth test job #
    ###################
    job = dedent("""
        Save:
            Group by: //div[@class="pokemon-info"]
            Keys: /h5
            id: /p[@class="id"]
            abilities: //div[@class="abilities"]/span
            
     """).strip()
    result = {'Bulbasaur': {'id': '#001', 'abilities': ['Grass', 'Poison']},
              'Ivysaur': {'id': '#002', 'abilities': ['Grass', 'Poison']},
              'Venusaur': {'id': '#003', 'abilities': ['Grass', 'Poison']},
              'Charmander': {'id': '#004', 'abilities': 'Fire'},
              'Charmeleon': {'id': '#005', 'abilities': 'Fire'},
              'Charizard': {'id': '#006', 'abilities': ['Fire', 'Flying']},
              'Squirtle': {'id': '#007', 'abilities': 'Water'},
              'Wartortle': {'id': '#008', 'abilities': 'Water'},
              'Blastoise': {'id': '#009', 'abilities': 'Water'},
              'Caterpie': {'id': '#010', 'abilities': 'Bug'},
              'Metapod': {'id': '#011', 'abilities': 'Bug'},
              'Butterfree': {'id': '#012', 'abilities': ['Bug', 'Flying']}}
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    ##################
    # Sixth test job #
    ##################
    job = dedent("""
        Save:
            Group by: //div[@class="pokemon-info"]
            Keys: /h5
            Save: /p[@class="id"]
     """).strip()
    result = {'Bulbasaur': '#001', 'Ivysaur': '#002', 'Venusaur': '#003',
              'Charmander': '#004', 'Charmeleon': '#005', 'Charizard': '#006',
              'Squirtle': '#007', 'Wartortle': '#008', 'Blastoise': '#009',
              'Caterpie': '#010', 'Metapod': '#011', 'Butterfree': '#012'}
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    ####################
    # Seventh test job #
    ####################
    job = dedent("""
        Save:
            Keys: //div[@class="pokemon-info"]/h5
            Save: //div[@class="pokemon-info"]/p[@class="id"]
     """).strip()
    result = {'Bulbasaur': '#001', 'Ivysaur': '#002', 'Venusaur': '#003',
              'Charmander': '#004', 'Charmeleon': '#005', 'Charizard': '#006',
              'Squirtle': '#007', 'Wartortle': '#008', 'Blastoise': '#009',
              'Caterpie': '#010', 'Metapod': '#011', 'Butterfree': '#012'}
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    
    ###################
    # Eight test job  #
    ###################
    job = dedent("""
        Save:
            Group by: //div[@class="pokemon-info"]
            Keys: /h5
            id: /p[@class="id"]
            abilities: //div[@class="abilities"]/span -f Flying
            
     """).strip()
    result = {'Bulbasaur': {'id': '#001', 'abilities': ['Grass', 'Poison']},
              'Ivysaur': {'id': '#002', 'abilities': ['Grass', 'Poison']},
              'Venusaur': {'id': '#003', 'abilities': ['Grass', 'Poison']},
              'Charmander': {'id': '#004', 'abilities': 'Fire'},
              'Charmeleon': {'id': '#005', 'abilities': 'Fire'},
              'Charizard': {'id': '#006', 'abilities': ['Fire', 'Flying']},
              'Squirtle': {'id': '#007', 'abilities': 'Water'},
              'Wartortle': {'id': '#008', 'abilities': 'Water'},
              'Blastoise': {'id': '#009', 'abilities': 'Water'},
              'Caterpie': {'id': '#010', 'abilities': 'Bug'},
              'Metapod': {'id': '#011', 'abilities': 'Bug'},
              'Butterfree': {'id': '#012', 'abilities': ['Bug', 'Flying']}}
    test_obj = Parser(job, html=read_data)
    test_obj.start()
    assert test_obj.storage == result
    