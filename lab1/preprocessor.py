#%%
import re
from typing import List, Optional, Match, Any, Tuple, Sequence
from lab1 import patterns
import itertools

#%%
def clean_external(txt: str) -> str:
    txt = re.sub('Dz\.(U|u)\.', '', txt)
    txt = txt.replace('\n', '')
    txt = re.sub(r'(i|oraz)', ',', txt)
    txt = re.sub(r'\bz','',txt)
    txt = re.sub(r'\.(?!r)', ',', txt)
    txt = txt.replace(' ', '')
    return txt

def split_year_external(txt: str) -> List[str]:
    return [x for x in re.split(r'\d{4}r', txt) if len(x)]

def split_record_external(txt: str) -> List[int]:
    splt = re.split(r'Nr(\d*)\,poz\,(\d*)', txt)
    return [int(num) for num in splt if re.match(r'\d', num)]

#%%
def flatten(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def pairs(list):
    return [(list[i], list[i+1]) for i in range(0,len(list),2)]

#%%
class StatuteProcessor():
    def __init__(self, statue_path: str):
        self.statue_path: str = statue_path
        self.statue_lines: List[str] = self.read_statue_lines()
        self.statue: str = self.read_statue()
    
    def read_statue_lines(self) -> List[str]:
        with open(self.statue_path, 'r') as document:
            return document.readlines()

    def read_statue(self) -> str:
        with open(self.statue_path, 'r') as document:
            return document.read()

    def get_article_count(self) -> int:
        count: int = 0
        for line in self.statue_lines:
            if re.search(patterns.section(), line):
                count += 1
        return count

    def test_any_pattern(self, pattern: str) -> Optional[Match[Any]]:
        x = re.search(pattern, self.statue)
        return x
    
    def get_statue_info(self):
        j: Tuple = re.search(patterns.journal(), self.statue).groups()
        dt: Tuple = re.search(patterns.date_title(), self.statue).groups()
        if (len(j) == 2 and len(dt) >= 4):
            return (dt[3], (dt[2], dt[1], dt[0]), j)
        return None
            
    def get_external_references(self):
        statue_trimed = self.statue[len(self.statue_lines[4]):]
        references = []
        while (True):
            match = re.search(patterns.external_reference(), statue_trimed)
            if not match:
                break
            idx = match.span()
            statue_trimed = statue_trimed[idx[1]:]
            txt = match.group(0)
            txt = clean_external(txt)
            by_year = split_year_external(txt)
            for year in by_year:
                by_record = split_record_external(year)
                references.append(by_record)
        return pairs((flatten([r for r in references if len(r) > 0 and len(r) % 2 == 0])))

#%%
resource_path = 'resources/ustawy/'
# filename = '1997_494.txt'
filename = '1999_804.txt'
sp = StatuteProcessor(resource_path + filename)

#%%
sp.get_external_references()
