#%%
import re
from typing import List, Tuple, Optional, Match, Any
from collections import Counter
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
    
    def get_statue_title(self) -> str:
        dt = re.search(pts.date_title(), self.statue)
        if dt:
            return ' '.join([e for e in re.sub(r'\n*', '', dt.group(0)).split(' ') if e != ''])
        return ''
            
    def get_external_references(self) -> List[Tuple[str, str, str]]:
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

    def get_internal_references(self):
        references = []
        sections = splt.split_section(self.statue, len(self.statue))
        for section_id, section_span in enumerate(sections,1):
            section_text = self.statue[section_span[0]:section_span[1]]
            paragraphs = splt.split_paragraph(section_text, len(section_text))
            for paragraph_id, paragraph_span in enumerate(paragraphs, 1):
                paragraph_text = section_text[paragraph_span[0]:paragraph_span[1]]
                for p,f in zip(pts.internal_pattern_order(), shp.internal_lambda_order()):
                    matches = re.findall(p, paragraph_text)
                    if matches:
                        references.append(list(map(f, matches)))
                        paragraph_text = re.sub(p, '', paragraph_text)

        return Counter(shp.flatten(references))

    def get_ustawa_count(self) -> int:
        base = r'u\s*s\s*t\s*a\s*w'
        wb = r'\b'
        suffix = [r'a', r'y', r'ie', r'ę', r'ą', r'o', r'om', r'ami', r'ach']
        forms = [wb+base+suf+wb for suf in suffix]
        count: int = 0
        for line in self.statue_lines:
            count += sum(len(re.findall(f, line.lower())) for f in forms)
        return count

    def test_any_pattern(self, pattern: str) -> Optional[Match[Any]]:
        x = re.search(pattern, self.statue)
        return x
