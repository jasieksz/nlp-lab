#%%
import numpy as np
import os
import re
import seaborn as sns
from collections import Counter
from functools import reduce, partial
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from lab1 import shapers
from typing import List, Tuple

#%% ES index for storing acts, ES analyzer for Polish texts:
es = Elasticsearch()
es.indices.create(
    index="my_index",
    body={
        "settings": {
            "analysis": {
                "analyzer": {
                  "my_analyzer": {
                      "type": "custom",
                      "tokenizer": "standard",
                      "filter": ["lowercase", "shingle"],
                    }
                }
            }
        },
        "mappings": {
            "legislation": {
                "properties": {
                    "text": {
                        "type": "text",
                        "analyzer": "my_analyzer",
                    }
                }                
            }
        }
    }
)

#%% Extract shingles (pairs) from the text
body = lambda text: {"tokenizer": "standard",
        "filter": ["lowercase", "shingle"],
        "text": text
}
analyze = lambda text: es.indices.analyze("my_index", body(text))

get_shingles = lambda text: list(map(lambda x: x['token'],
                                filter(lambda x: x['type'] == 'shingle',
                                text)))

get_tokens = lambda text: list(map(lambda x: x['token'],
                                filter(lambda x: x['type'] == '<ALPHANUM>',
                                text)))

text_only = lambda x: not re.search(r'\d+', x)
make_tuple = lambda x: tuple(x.split(' '))

#%% Bigram counts in the corpora
resource_path = 'resources/ustawy'
doc_shingles: List[List[str]] = []
doc_tokens: List[List[str]] = []
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        doc = analyze(legislation)['tokens']
        doc_shingles.append(get_shingles(doc))
        doc_tokens.append(get_tokens(doc))

shingles = map(make_tuple, filter(text_only, shapers.flatten(doc_shingles)))
tokens = filter(text_only, shapers.flatten(doc_tokens))

#%% Morphosyntactic tagging - krnnt
split = lambda x: x[1].split('\t')[1:3]
twos = lambda x: len(x) == 2
tuple_split = lambda x: (x[0], x[1].split(':')[0])
composed = lambda a, b: a == "subst" and b == "adj"

def krnnt(text):
    response = req.post('http://localhost:9200', text.encode("utf-8")) \
            .content.decode("utf-8") \
            .split("\n")
    return list(map(tuple_split, filter(twos, map(split, shapers.pairs(response)))))

shingles = (e for e in ((krnnt(sh[0]), krnnt(sh[1])) for sh in shingles) if composed(e[0], e[1]))
shingle_freq = Counter(list(shingles))

#%% LLR score
h = lambda k: (k/k.sum() * np.log(k/k.sum() + (k==0))).sum()
llr = lambda k: 2*k.sum() * (h(k) - h(k.sum(axis=0)) - h(k.sum(axis=1)))
sum_shingles = sum(list(shingle_freq.values()))

def prob(a, b):
    a_and_b = shingle_freq.get((a, b), 0)
    a_not_b = tokens_freq[a] - a_and_b
    b_not_a = tokens_freq[b] - a_and_b
    none = sum_shingles - a_not_b - b_not_a - a_and_b
    return np.array([[a_and_b, a_not_b], [b_not_a, none]])

llrs = []
for e in ((s, prob(s[0], s[1])) for s in shingle_freq.keys()):
    score = 0
    try:
        score = llr(e[1])
    except:
        score = 0
    finally:        
        llrs.append((e[0], score))
llrs = sorted(llrs, key=lambda e: e[1], reverse=True)

#%%
llrs[:30]