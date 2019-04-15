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
                      "filter": ["morfologik_stem", "lowercase", "shingle"],
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

#%% 1.1 Compute bigram counts in the corpora
resource_path = 'resources/ustawy'
doc_shingles: List[List[str]] = []
doc_tokens: List[List[str]] = []
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        doc = analyze(legislation)['tokens']
        doc_shingles.append(get_shingles(doc))
        doc_tokens.append(get_tokens(doc))

shingles = shapers.flatten(doc_shingles)
tokens = shapers.flatten(doc_tokens)

#%% 
text_only = lambda x: not re.search(r'\d+', x)
make_tuple = lambda x: tuple(x.split(' '))

#%% 1.2 Filter shingles - text only, lowercase, no punctuation
shingle_freq = Counter(list(map(make_tuple, filter(text_only, shingles))))
tokens_freq = Counter(list(filter(text_only, tokens)))

#%% 2. Pointwise Mutal Information score
p_t = lambda token: tokens_freq[token] / len(tokens_freq)
p_s = lambda shingle: shingle_freq[shingle] / len(shingle_freq)
pmi = lambda x, y: np.log(p_s((x, y)) / (p_t(x) * p_t(y)))

#%% 3. 30 top from ex.2
pmis = [(s, pmi(s[0], s[1])) for s in shingle_freq.keys()]
pmis = sorted(pmis, key=lambda e: e[1], reverse=True)
pmis[:30]

#%% filtered 30 top from ex.2
pmis2 = [(s, pmi(s[0], s[1])) for s in shingle_freq.keys() if shingle_freq[s] > 10]
pmis2 = sorted(pmis2, key=lambda e: e[1], reverse=True)
pmis2[:30]

#%% 4. Log Likelihood Ration score
h = lambda k: (k/k.sum() * np.log(k/k.sum() + (k==0))).sum()
llr = lambda k: 2*k.sum() * (h(k) - h(k.sum(axis=0)) - h(k.sum(axis=1)))
sum_shingles = sum(list(shingle_freq.values()))

def prob(a, b):
    a_and_b = shingle_freq.get((a, b), 0)
    a_not_b = tokens_freq[a] - a_and_b
    b_not_a = tokens_freq[b] - a_and_b
    none = sum_shingles - a_not_b - b_not_a - a_and_b

    return np.array([[a_and_b, a_not_b], [b_not_a, none]])

arr = shingle_freq.items()
gen_probs = ((s, prob(s[0], s[1])) for s in shingle_freq.keys())

#%%
llrs = []
for e in gen_probs:
    score = 0
    try:
        score = llr(e[1])
    except:
        score = 0
    finally:        
        llrs.append((e[0], score))
llrs = sorted(llrs, key=lambda e: e[1], reverse=True)


