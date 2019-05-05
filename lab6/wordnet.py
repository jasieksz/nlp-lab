#%%
import requests
from collections import namedtuple
from functools import partial
import networkx as nx
from matplotlib import pyplot as plt
from lab1 import shapers as shp
import nltk
from nltk.corpus import wordnet as wn
import numpy as np

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
dh2 = {word: direct_hyponyms(word) for word in direct_hypo}
print('katastrofa', dh2['katastrofa'], '\n')
print('wykolejenie', dh2['wykolejenie'], '\n')
print('wypadek komunikacyjny', dh2['wypadek komunikacyjny'])

#%% 4.1 Directed graph of semantic relation between groups of lexemes:
# 'szkoda majątkowa' is missing
a = ['strata', 'uszczerbek', 'uszczerbek na zdrowiu',
	 'krzywda', 'niesprawiedliwość', 'nieszczęście', 'szkoda']

b = ['wypadek', 'wypadek komunikacyjny', 'katastrofa budowlana', 
	'wypadek drogowy', 'kolizja', 'zderzenie', 'kolizja drogowa', 'bezkolizyjny']

sen_id = lambda word: get_senses_from_word(word)[0]['id']
syn_id = lambda word: get_synset_from_sense(sen_id(word))['id']

is_node = lambda nodes, rel: rel['synsetTo']['id'] in nodes

def map_relation(relation):
	return 'hiper' if relation == 10 else 'hipo'

def distance_matrix(A):
	edges = []
	dist = []
	for i in range(len(A)):
		dist.append(['']*len(A))

	nodes = list(map(syn_id, A))
	isn = partial(is_node, nodes)

	for i, n in enumerate(nodes):
		relations = [(rel['synsetTo']['id'], rel['relation']['id']) for rel in get_relations_from(n) if isn(rel)]
		for rel in relations:
			dist[i][nodes.index(rel[0])] = map_relation(rel[1])
			edges.append((i, nodes.index(rel[0]))) 
	return dist, edges

distA = distance_matrix(a)
distB = distance_matrix(b)

#%%
lab = lambda lst: {i: lst[i] for i in range(len(lst))}
edge_name = lambda dist, edge: dist[edge[0]][edge[1]] + '/' + dist[edge[1]][edge[0]]

def draw(nodes, edges, dist):
	ed_nm = partial(edge_name, dist)
	G = nx.DiGraph()
	G.add_edges_from(edges)
	G.add_nodes_from(list(range(len(nodes))))
	pos = nx.spring_layout(G)
	edge_lab = {edge: ed_nm(edge) for edge in G.edges}
	node_lab = lab(nodes)
	nx.draw(G, pos, with_labels=True, labels=node_lab, alpha=0.8)
	nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_lab, font_color='red')
	plt.show()

#%% Disconnected nodes removed for clarity
ap = list(filter(lambda w: w != 'szkoda' and w != 'nieszczęście', a))
draw(ap, distA[1], distA[0])

#%% Disconnected nodes removed
draw(b[:4], distB[1], distB[0])

#%% 5. Value of Leacock-Chodorow semantic similarity measure between pairs
x = (('szkoda', 1), ('wypadek', 0))
y = (('kolizja', 1), ('szkoda', 1))
z = (('nieszczęście', 0), ('katastrofa', 1))
arr = [x, y, z]

res = map(lambda t: (wn.synsets(t[0][0])[t[0][1]], wn.synsets(t[1][0])[t[1][1]]), arr)
res = map(lambda t: (t, wn.lch_similarity(t[0], t[1])), res)
list(res)
