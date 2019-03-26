#%%
import os
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

#%%
es = Elasticsearch()

#%% 3,4 ES index for storing acts, ES analyzer for Polish texts:
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
                        "analyzer": "my_analyzer"
                    }
                }
            }
        }
    }
)

#%% 5 Load the data to the ES index
resource_path = 'resources/ustawy'
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        es.create("my_index", "legislation", filename, {"text": legislation})

#%% 6 number of legislative acts containing the word ustawa 
es.search(
    index="my_index",
    doc_type="legislation",
    body={
        "query": {
            "match": {
                "text": {
                    "query": "ustawa"
                }
            }
        }
    }
)["hits"]["total"]

#%% 7 containing the words kodeks postępowania cywilnego 
es.search(
    index="my_index",
    doc_type="legislation",
    body={
        "query": {
            "match_phrase": {
                "text": {
                    "query": "kodeks postępowania cywilnego"
                }
            }
        }
    }
)["hits"]["total"]

#%% 8 containing the words wchodzi w życie 1175
es.search(
    index="my_index",
    doc_type="legislation",
    body={
        "query": {
            "match_phrase": {
                "text": {
                    "query": "wchodzi w życie",
                    "slop": 2
                }                             
            }
        },
    }
)["hits"]["total"]

#%% 9 documents that are the most relevant for the phrase konstytucja
x = es.search(
    index="my_index",
    doc_type="legislation",
    size=45,
    body={
        "query": {
            "match": {
                "text": {
                    "query": "konstytucja",
                }                             
            }
        },
        "highlight" : {
            "fields" : {
                "text" : {}
            },
            "boundary_scanner": "sentence",
            "number_of_fragments": 3,
            "order": "score"
        }
    }
)["hits"]
top = [[ e['_score'], e['_id'], e['highlight']['text']] for e in sorted(x['hits'], key=lambda e: -e['_score'])][:10]
top = np.array(top)
top[:,:2]

#%% 10 excerpts containing the word konstytucja from ex9
top[:,1:]
