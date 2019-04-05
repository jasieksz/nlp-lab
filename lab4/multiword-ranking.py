#%%
import numpy as np
import os
import seaborn as sns
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
                        "term_vector": "with_positions_offsets_payloads"
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
                                analyze(text)['tokens'])))

#%% 1.1 Compute bigram counts in the corpora
resource_path = 'resources/ustawy'
shingles = []
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        shingles.append(get_shingles(legislation))

#%% 1.2 Filter shingles - text only, lowercase, no punctuation

#%% 2. Pointwise Mutal Information score

#%% 3. 30 top from ex.2

#%% 4. Log Likelihood Ration score

#%% 5. 30 top from ex.4

#%% 6.1 PMI or LLR ?

#%% 6.2 How to build multiword dictionary

#%% 6.3 Metric threshold for good/bad multiword
