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

shingles: List[str] = shapers.flatten(doc_shingles)
tokens: List[str] = shapers.flatten(doc_tokens)

#%% 
text_only = lambda x: not re.search(r'\d+', x)
make_tuple = lambda x: tuple(x.split(' '))

#%% 1.2 Filter shingles - text only, lowercase, no punctuation
shingle_freq = Counter(list(map(make_tuple, filter(text_only, shingles))))
tokens_freq = Counter(list(filter(text_only, tokens)))

#%% 2. Pointwise Mutal Information score
p_t = lambda token: tokens_freq[token] / len(tokens_freq)
p_s = lambda shingle: shingle_freq[shingle] / len(tokens_freq)
pmi = lambda x, y: np.log(p_s((x, y)) / (p_t(x) * p_t(y)))

pmis = [(s, pmi(s[0], s[1])) for s in shingle_freq.keys()]

#%% 3. 30 top from ex.2
sorted(pmis, key=lambda e: e[1], reverse=True)[:10]

#%% 4. Log Likelihood Ration score

#%% 5. 30 top from ex.4

#%% 6.1 PMI or LLR ?

#%% 6.2 How to build multiword dictionary

#%% 6.3 Metric threshold for good/bad multiword
