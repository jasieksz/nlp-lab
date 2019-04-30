#%%
# from wn import WordNet 
# w = WordNet(wordnet_data_dir='resources/plwordnet_2_3/plwordnet_2_3_pwn_format')
# w.synsets("szkoda")

#%%
import requests
from collections import namedtuple
from functools import partial
import networkx as nx
from matplotlib import pyplot as plt
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
# 'szkoda majątkowa' is missing
a = ['szkoda', 'strata', 'uszczerbek', 'uszczerbek na zdrowiu',
	 'krzywda', 'niesprawiedliwość', 'nieszczęście']

b = ['wypadek', 'wypadek komunikacyjny', 'kolizja', 'zderzenie',
	 'kolizja drogowa', 'bezkolizyjny', 'katastrofa budowlana', 'wypadek drogowy']

sen_id = lambda word: get_senses_from_word(word)[0]['id']
syn_id = lambda word: get_synset_from_sense(sen_id(word))['id']

is_node = lambda nodes, rel: rel['synsetTo']['id'] in nodes

def distance_matrix(A):
	graph = []
	for i in range(len(A)):
		graph.append([0]*len(A))

	nodes = list(map(syn_id, A))
	isn = partial(is_node, nodes)

	for i, n in enumerate(nodes):
		relations = [(rel['synsetTo']['id'], rel['relation']['id']) for rel in get_relations_from(n) if isn(rel)]
		for rel in relations:
			graph[i][nodes.index(rel[0])] = rel[1]
	return graph

def draw(distances):
	G=nx.from_numpy_matrix(np.array(distances))
	nx.draw(G)
	plt.show()

dist = distance_matrix(a)
draw(dist)

dist = distance_matrix(b)
draw(dist)

#%% 5. Value of Leacock-Chodorow semantic similarity measure between pairs
from pywnxml import WNQuery

x = ('szkoda', 'wypadek')
y = ('kolizja', 'szkoda majątkowa')
z = ('nieszczęście', 'katastrofa budowlana')

wn = WNQuery.WNQuery('resources/plwordnet_3_0/plwordnet-3.0.xml')

#%%
[wn.similarityLeacockChodorow(e[0], e[1]) for e in [x, y, z]]