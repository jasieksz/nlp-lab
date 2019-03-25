#%%
import os
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
                      "filter": ["lowercase", "my_synonyms", "morfologik_stem"]
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


#%% 3 Test
analyzer_params = lambda txt: {
    "tokenizer": "standard",
    "filter": ["lowercase", "my_synonyms", "morfologik_stem"],
    "text": txt}

es.indices.analyze("my_index2", analyzer_params("JESTEM KC"))

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


#%% 8 containing the words wchodzi w życie

#%% 9 documents that are the most relevant for the phrase konstytucja

#%% 10 excerpts containing the word konstytucja from ex9

