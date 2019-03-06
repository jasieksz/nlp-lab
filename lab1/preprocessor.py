#%%
import re

#%%
class StatuteProcessor():
    patterns: dict = {
        'section': (lambda number : r'\s*Art. ' + re.escape(number) + r'.\n')
    }
    
    def __init__(self, statue_path):
        self.statue_path: str = statue_path
        self.statue_lines: List[str] = self.read_statue()
    
    def read_statue(self):
        with open(self.statue_path, 'r') as document:
            return document.readlines()

    # TODO : Refactor, make more pythonic!
    def get_article(self, number: int):
        article = []
        inside_article: int = False
        for line in self.statue_lines:
            if not inside_article and re.match(self.patterns['section'](str(number)), line):
                inside_article = True
            if inside_article and re.match(self.patterns['section'](str(number+1)), line):
                inside_article = False
            if inside_article:
                article.append(line)
        return article


#%%
resource_path = 'nlp-lab/resources/ustawy/'
filename = '1997_511.txt'
sp = StatuteProcessor(resource_path + filename)

#%%
sp.get_article(3)


