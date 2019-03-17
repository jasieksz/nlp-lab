#%%
import re
from typing import List, Optional, Match, Any, Tuple, Sequence
from lab1 import patterns

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

#%%
resource_path = 'resources/ustawy/'
filename = '1997_494.txt'
sp = StatuteProcessor(resource_path + filename)

#%%
sp.get_statue_info()

