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
        j = re.search(pts.journal(), self.statue)
        dt = re.search(pts.date_title(), self.statue)
        if (j and dt):
            j = j.groups()
            dt = dt.groups()
            if (len(j) == 2 and len(dt) >= 4):
                return (dt[3], (dt[2], dt[1], dt[0]), j)
        return None
            
    def get_external_references(self):
        is_match, text_match, trimmed = splt.match_and_trim(self.statue, pts.journal())
        references = []
        is_match = True # Force while entry
        while (is_match):
            is_match, text_match, trimmed = splt.match_and_trim(trimmed, pts.external_reference())
            if not is_match: 
                is_match, text_match, trimmed = splt.match_and_trim(trimmed, pts.external_reference_ketless())
                if not is_match:
                    break

            text = splt.clean_external(text_match)
            by_year: List[Tuple[str,str]] = splt.split_year(text)
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

    def get_ustawa_count(self) -> int:
        base = r'u\s*s\s*t\s*a\s*w'
        wb = r'\b'
        suffix = [r'a', r'y', r'ie', r'ę', r'ą', r'o', r'om', r'ami', r'ach']
        forms = [wb+base+suf+wb for suf in suffix]
        count: int = 0
        for line in self.statue_lines:
            count += sum(len(re.findall(f, line.lower())) for f in forms)

        return count
        