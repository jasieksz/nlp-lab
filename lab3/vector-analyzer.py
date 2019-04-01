#%%
import os
import numpy as np
import re
import seaborn as sns
import pandas as pd
import Levenshtein
from collections import Counter
from functools import reduce, partial
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

#%% ES index for storing acts, ES analyzer for Polish texts:
es = Elasticsearch()
es.indices.create(
    index="my_index",
    body={
        "settings": {
            "analysis": {
                "filter": {
                  "my_synonyms": {
                      "type": "synonym",
                      "synonyms": [ 
                          "kpk => kodeks postępowania karnego",
                          "kpc => kodeks postępowania cywilnego",
                          "kk => kodeks karny",
                          "kc => kodeks cywilny"]
                    }    
                },
                "analyzer": {
                  "my_analyzer": {
                      "type": "custom",
                      "tokenizer": "standard",
                      "filter": ["my_synonyms", "morfologik_stem", "lowercase"]
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
                        "term_vector": "with_positions_offsets_payloads",
                    }
                }                
            }
        }
    }
)

#%% Load the data to the ES index
resource_path = 'resources/ustawy'
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        es.create("my_index", "legislation", filename, {"text": legislation})

#%% 1 Find terms (tokens) that are present in the document, and their count
body = {"term_statistics" : "true"} # , "filter" : {"min_word_length" : 2}
def get_term_freq(id: str):
    x = es.termvectors(index="my_index", doc_type="legislation", id=id, body=body)["term_vectors"]
    return Counter(dict([(k, v["term_freq"]) for k,v in x["text"]["terms"].items() if not re.match(r'\d+', k)]))

#%% 2 Aggregate the result to obtain one global frequency list
term_freq = reduce(lambda x,y : x + y, [get_term_freq(f_id) for f_id in os.listdir(resource_path)])

#%% 3 Filter the list to keep terms that contain only letters and have at least 2 of them
term_freq = Counter(dict(filter(lambda x: len(x[0]) > 1, term_freq.most_common())))
# len(t_f) = 22880

#%% 4 Plot, log scale, rank vs occurences
rank, freq = zip(*enumerate(term_freq.most_common()))
rank = list(map(lambda x: x+1, rank))
freq = list(map(lambda x: int(x), np.array(freq)[:,1]))

sns.set_style("whitegrid")
g = sns.lineplot(x=rank, y=freq, color='coral', lw=2.75)
g.set(yscale="log")
g.set(xscale="log")

#%% 5 Find all words not in dictionary: "polimorfologik"
df = pd.read_csv('resources/polimorfologik-2.1/polimorfologik-2.1.csv', delimiter=';')
forms = set(map(lambda x: re.sub(r'-', '', x).lower(), df['form'].unique()))
missing = [x for x in term_freq.most_common() if not x[0] in forms]

#%% 6 30 words, with highest ranks that do not belong to the dict
missing[:30]

#%% 7 Find 30 words with 3 occurrences that do not belong to the dictionary
# missing_triples = list(map(lambda x: (re.sub(r'\xad', '', x[0]), x[1]), filter(lambda x: x[1] == 3, missing)))
missing_triples = list(filter(lambda x: x[1] == 3, missing))
missing_triples[:30]

#%% 8 Use Levenshtein distance and the frequency list, to determine correction
def correction(word):
    order = lambda x: np.divide(np.log(x[1]), Levenshtein.distance(word[0], x[0]))
    max_dist = lambda correction: Levenshtein.distance(correction[0], word[0]) <= 4 and correction[0] in forms
    possible = sorted(term_freq.items(), key=order, reverse=True)[:3]
    return list(filter(max_dist, possible))
    
def corrections(words):
    for word in words:
        yield (word, [x for x in correction(word)])

cor = dict(corrections(missing_triples))
cor
