#%%
# from wn import WordNet 
# w = WordNet(wordnet_data_dir='resources/plwordnet_2_3/plwordnet_2_3_pwn_format')
# w.synsets("szkoda")

#%%
import requests

#%%
def get_senses_from_word(word):
    return query_wordnet('senses/search?lemma=' + str(word) + '&&&&&&&&&')['content']

def get_synset_from_sense(sense_id):
    return query_wordnet('senses/' + str(sense_id) + '/synset')

def get_senses_from_synset(synset_id):
    return query_wordnet('synsets/' + str(synset_id) + '/senses')

def get_relations_to(synset_id):
    return query_wordnet('synsets/' + str(synset_id) + '/relations/to')

def get_relations_from(synset_id):
    return query_wordnet('synsets/' + str(synset_id) + '/relations/from')

def query_wordnet(url):
    resp = requests.get('http://api.slowosiec.clarin-pl.eu/plwordnet-api/' + url)
    return resp.json()