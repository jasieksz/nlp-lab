#%%
import itertools
from collections import namedtuple
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
    

Isprpt = namedtuple('Isprpt', ['s', 'pr', 'pt'])
Ispt = namedtuple('Ispt', ['s', 'pt'])
Ispr = namedtuple('Ispr', ['s', 'pr'])
Ipr = namedtuple('Ipr', ['pr'])

isprpt_f = lambda arg: Isprpt(arg[0], arg[1], arg[2])
ispt_f = lambda arg: Ispt(arg[0], arg[1])
ispr_f = lambda arg: Ispr(arg[0], arg[1])
ipr_f = lambda arg: Ipr(arg[0]) 

def internal_lambda_order():
    return [isprpt_f, ispt_f, ispr_f, ipr_f]