#%%
# from wn import WordNet 
# w = WordNet(wordnet_data_dir='resources/plwordnet_2_3/plwordnet_2_3_pwn_format')
# w.synsets("szkoda")

#%%
import requests
from collections import namedtuple
from lab1 import shapers as shp

#%% Helpers
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

#%% 1. Meanings of the 'szkoda' and display all their synonyms
SenseDesc = namedtuple('sen', ['id', 'desc'])

meanings = get_senses_from_word('szkoda')
id_desc = [SenseDesc(r['id'], r['domain']['description']) for r in meanings]
print(id_desc)

syn_ids = shp.flatten([get_senses_from_synset(syn) for syn in (get_synset_from_sense(sen.id)['id'] for sen in id_desc)])
synonims = [syn['lemma']['word'] for syn in syn_ids]
synonims

#%% 2.1 Closure of hypernymy relation for the first meaning of the 'wypadek drogowy'
sen_id = get_senses_from_word('wypadek drogowy')[0]['id']
syn_id = get_synset_from_sense(sen_id)['id']
ids = [syn_id]

hypernymy = lambda synset: synset['relation']['id'] == 10

for id in ids:
	relation_ids = [rel['synsetTo']['id'] for rel in get_relations_from(id) if hypernymy(rel)]
	for i in relation_ids:
		if i not in ids:
			ids.append(i)     

closure = [syn['lemma']['word'] for syn in shp.flatten([get_senses_from_synset(i) for i in ids])]
closure

#%% 2.2 Diagram of the relations as a directed graph
# This graph is just a simple path.

#%% 3.1 Direct hyponyms of 'wypadek'
sen_id = lambda word: get_senses_from_word(word)[0]['id']
syn_id = lambda word: get_synset_from_sense(sen_id(word))['id']
hyponyms = lambda word: [rel['synsetTo']['id'] for rel in get_relations_from(syn_id(word)) if rel['relation']['id'] == 11]
direct_hyponyms = lambda word: [sen['lemma']['word'] for sen in shp.flatten([get_senses_from_synset(hyp) for hyp in hyponyms(word)])]

direct_hypo = direct_hyponyms('wypadek')
direct_hypo

#%% 3.2 Second-order hyponyms of 'wypadek'
{word: direct_hyponyms(word) for word in direct_hypo}

#%% 4.1 Directed graph of semantic relation between groups of lexemes:
a = ['szkoda', 'strata', 'uszczerbek','szkoda majątkowa',
	 'uszczerbek na zdrowiu', 'krzywda', 'niesprawiedliwość', 'nieszczęście']

b = ['wypadek', 'wypadek komunikacyjny', 'kolizja', 'zderzenie',
	 'kolizja drogowa', 'bezkolizyjny', 'katastrofa budowlana', 'wypadek drogowy']

#%% 5. Value of Leacock-Chodorow semantic similarity measure between pairs
x = ('szkoda', 'wypadek')
y = ('kolizja', 'szkoda majątkowa')
z = ('nieszczęście', 'katastrofa budowlana')
