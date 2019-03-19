#%%
import itertools
from typing import List, Tuple

def flatten(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

def flatten_references(ref: Tuple[str, str, List[str]]):
    year = ref[0]
    nr = ref[1]
    return [(year, nr, pos) for pos in ref[2]]

def pairs(list):
    size = len(list)
    return [(list[i], list[(i+1) % size]) for i in range(0,len(list),2)]
    
