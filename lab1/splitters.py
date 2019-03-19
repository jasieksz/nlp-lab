#%%
import re
from lab1 import shapers
from lab1 import patterns
from typing import List, Tuple, Any

def clean_external(txt: str) -> str:
    txt = txt.replace(u'\xa0', u' ')
    txt = re.sub('Dz\.\s*(U|u)\.', '', txt)
    txt = txt.replace('\n', '')
    txt = re.sub(r'i(?=\d*)', ',', txt)
    txt = re.sub(r'(i|oraz)', ',', txt)
    txt = re.sub(r'\bz','',txt)
    txt = re.sub(r'\.(?!r)', ',', txt)
    txt = txt.replace(' ', '')
    txt = re.sub(r'\[\d+\]', '', txt)
    splitted = [x for x in txt.split(',') if (re.match(r'(Nr)*\d+', x) or x=='poz')]
    txt = ','.join(splitted)
    return '2049r,'+txt if re.match(r'Nr', txt) else txt

def split_year(txt: str) -> List[str]:
    r = [x for x in re.split(r'((?:19|20)\d{2})r*', txt) if len(x) > 1]
    return shapers.pairs(r)

def split_nr(txt: str) -> List[str]:
    r = [x for x in re.split(r'Nr(\d*)', txt) if len(x) and x != ',']
    return shapers.pairs(r)

def split_pos(txt: str) -> List[str]:
    txt = txt.replace('poz', '')
    return [x.replace(',','') for x in re.split(r',', txt) if len(x)  and x != ',']
    
def match_and_trim(txt: str, pattern: str) -> Tuple[bool, str, str]:
    match = re.search(pattern, txt)
    return (True, match.group(0), txt[match.span()[1]:]) if match else (False, '', txt)
    
def index_split_by(txt: str, pattern: str, parent_size: int) -> List[Tuple[int, int]]:
    split = [m.span() for m in re.finditer(pattern, txt)]
    if not split:
        return [(0,len(txt))]
    last_index = split[len(split) - 1][1]
    result = [(split[i][1], split[i+1][0]) for i in range(0, len(split)-1)]
    result.append((last_index, parent_size))
    return result

def split_section(txt: str, parent_size: int) -> List[Tuple[int, int]]:
    return index_split_by(txt, patterns.section(), parent_size) 

def split_paragraph(txt: str, parent_size: int) -> List[Tuple[int, int]]:
    return index_split_by(txt, patterns.paragraph(), parent_size)
    
def split_point(txt: str, parent_size: int) -> List[Tuple[int, int]]:
    return index_split_by(txt, patterns.point(), parent_size)