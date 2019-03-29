#%%
import os
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

#%%
es = Elasticsearch()

#%% ES index for storing acts, ES analyzer for Polish texts:
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
                        "term_vector": "with_positions_offsets_payloads"
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
x = es.termvectors(index="my_index",
    doc_type="legislation",
    id="1994_395.txt")["term_vectors"]
x["text"]["terms"].keys()

#%% 2 Aggregate the result to obtain one global frequency list

#%% 3 Filter the list to keep terms that contain only letters and have at least 2 of them

#%% 4 Plot, log scale, rank vs occurences

#%% 5 Find all words not in dictionary: "polimorfologik"


#%% 6 30 words, with highest ranks that do not belong to the dict

#%% 7 Find 30 words with 3 occurrences that do not belong to the dictionary

#%% 8 Use Levenshtein distance and the frequency list, to determine correction