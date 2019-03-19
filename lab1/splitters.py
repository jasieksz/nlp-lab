#%%
import re
from lab1 import shapers
from typing import List

def clean_external(txt: str) -> str:
    txt = re.sub('Dz\.(U|u)\.', '', txt)
    txt = txt.replace('\n', '')
    txt = re.sub(r'i(?=\d*)', ',', txt)
    txt = re.sub(r'(i|oraz)', ',', txt)
    txt = re.sub(r'\bz','',txt)
    txt = re.sub(r'\.(?!r)', ',', txt)
    txt = txt.replace(' ', '')
    return txt

def split_year(txt: str) -> List[str]:
    r = [x for x in re.split(r'((?:19|20)\d{2})r*', txt) if len(x) > 1]
    return shapers.pairs(r)

def split_nr(txt: str) -> List[str]:
    r = [x for x in re.split(r'Nr(\d*)', txt) if len(x) and x != ',']
    return shapers.pairs(r)

def split_pos(txt: str) -> List[str]:
    txt = txt.replace('poz', '')
    return [x.replace(',','') for x in re.split(r',', txt) if len(x)  and x != ',']