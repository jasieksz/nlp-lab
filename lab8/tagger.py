#%%
import os
import numpy as np
import re
from lab1 import patterns
from typing import List, Tuple

#%%
def get_statute_file(path: str = 'resources/ustawy'):
    for filename in os.listdir(path):
        yield path + '/' + filename

def read_statute(path: str) -> List[str]:
    with open(path, 'r') as document:
        return document.readlines()

clean = lambda x: re.sub(r'\xa0', ' ', x)

def remove_prefix(statute: List[str], pattern=None) -> Tuple[int, List[str]]:
    first_section = 0
    if not pattern:
        pattern = patterns.section()
    while (not re.search(pattern, clean(statute[first_section]))):
        first_section += 1
    return first_section, statute[first_section:]
    
# statute_fragment = statute[:first_section]
def is_update(statute_fragment: List[str]) -> bool:
    fragment = ''.join(statute_fragment)
    if (re.search(patterns.changed_statute(), fragment)):
        return True
    return False

def tag_statutes(filenames: List[str]):
    for filename in filenames:
        statute = read_statute(filename)
        section_one, _ = remove_prefix(statute, r'\bArt\.')
        yield filename, section_one, is_update(statute[:section_one])

def get_tags():
    filenames = get_statute_file()
    files = list(filenames)
    return {(filename, section_one): update_tag for filename, section_one, update_tag in tag_statutes(files)}