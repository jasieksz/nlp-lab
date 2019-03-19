#%%
import os
from collections import Counter
from lab1 import processor

def ex1(): # ('1998', '106', '668'): 731
    resource_path = 'resources/ustawy'
    result = []
    for filename in os.listdir(resource_path):
        sp = processor.StatuteProcessor(resource_path + '/' + filename)
        result.append(sp.get_external_references())
    return Counter(processor.shp.flatten(result))

def ex2():
    resource_path = 'resources/ustawy'
    result = []
    for filename in os.listdir(resource_path):
        sp = processor.StatuteProcessor(resource_path + '/' + filename)
        title = sp.get_statue_title()
        references = sp.get_internal_references()
        result.append((title, references))
    return result

def ex3(): # 24183
    resource_path = 'resources/ustawy'
    count = 0
    for filename in os.listdir(resource_path):
        sp = processor.StatuteProcessor(resource_path + '/' + filename)
        count += sp.get_ustawa_count()
    return count

#%%
print(ex1())
print(ex3())

#%% ex2 example run
resource_path = 'resources/ustawy/'
sp = processor.StatuteProcessor(resource_path + '1996_603.txt')
sp.get_internal_references()
