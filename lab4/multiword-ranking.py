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

#%% 4. LLR
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

#%% 5. 30 top from ex.4
llrs[:30]

#%% 5. Filtered top 30 from ex.4
list(filter(lambda t: len(t[0][0]) > 1 and len(t[0][1]) > 1, llrs))[:30]

#%% 6.1 PMI or LLR ?
# LLR
# http://www.lrec-conf.org/proceedings/lrec2002/pdf/128.pdf

#%% 6.2 How to build multiword dictionary
# Large dataset

#%% 6.3 Metric threshold for good/bad multiword
threshold = np.nanquantile(list((v for (k, v) in llrs)), 0.95)
print(threshold)
[p for (p, q) in ((k,v) for (k, v) in llrs if v > threshold)]

#%%
sns.set_style('whitegrid')
sns.distplot([e for e in (np.log10(v) for (k, v) in llrs)], bins=75, kde=False)

#%% LAB5
import requests

split = lambda x: x[1].split('\t')[1:3]
twos = lambda x: len(x) == 2
tuple_split = lambda x: (x[0], x[1].split(':')[0])
composed = lambda a, b: a[1] == "subst" and b[1] == "subst"
simple_composed = lambda a, b: a == "subst" and b == "adj"

def krnnt(text):
    response = requests.post('http://localhost:9200', text.encode("utf-8")) \
            .content.decode("utf-8") \
            .split("\n")
    return list(map(tuple_split, filter(twos, map(split, shapers.pairs(response)))))[0]


#%%
tags = {}
for k, v in llrs[:100]:
    w1, w2 = k
    if w1 not in tags:
        tags[w1] = krnnt(w1)[1]
    if w2 not in tags:
        tags[w2] = krnnt(w2)[1]

res = []
for k, v in llrs[:100]:
    if simple_composed(tags[k[0]], tags[k[1]]):
        res.append((k, v))

res