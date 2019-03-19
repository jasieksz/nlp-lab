#%%
import re
from typing import List, Tuple, Optional, Match, Any
from lab1 import patterns as pts
from lab1 import shapers as shp
from lab1 import splitters as splt

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
            if re.search(pts.section(), line):
                count += 1
        return count

    def test_any_pattern(self, pattern: str) -> Optional[Match[Any]]:
        x = re.search(pattern, self.statue)
        return x
    
    def get_statue_info(self):
        j: Tuple = re.search(pts.journal(), self.statue).groups()
        dt: Tuple = re.search(pts.date_title(), self.statue).groups()
        if (len(j) == 2 and len(dt) >= 4):
            return (dt[3], (dt[2], dt[1], dt[0]), j)
        return None
            
    def get_external_references(self):
        trim = re.search(pts.journal(), self.statue).span()[1]
        statue_trimed = self.statue[trim:]
        references = []
        while (True):
            match = re.search(pts.external_reference(), statue_trimed)
            if not match:
                break
            idx = match.span()
            statue_trimed = statue_trimed[idx[1]:]
            txt = match.group(0)

            txt = clean_external(txt)
            by_year: List[Tuple[str,str]] = splt.split_year(txt)
            
            for year in by_year:
                by_nr: List[str] = splt.split_nr(year[1])
                for nr in by_nr:
                    pos: List[str] = splt.split_pos(nr[1])
                    y = year[0]
                    n = nr[0]
                    if not re.match(r'\d{4}', y):
                        y = '0000'
                    if not re.match(r'\d+', n):
                        n = '000'
                    references.append((y, n, pos))
        return shp.flatten(list(map(shp.flatten_references, references)))

#%%
resource_path = 'resources/ustawy/'
# filename = '1997_494.txt'
filename = '1999_804.txt'
# filename = '2000_700.txt'
sp = StatuteProcessor(resource_path + filename)

#%%
sp.get_external_references()
