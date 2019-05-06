#%%
import numpy as np 
import seaborn as sns
from sklearn import manifold
from gensim.models import KeyedVectors
from functools import partial
import pprint

#%% Load Word2Vec
path = 'resources/skipgram_v100/skipgram/skip_gram_v100m8.w2v.txt'
wv = KeyedVectors.load_word2vec_format(path, binary=False)

#%% 3. Most similar expressions:
expr = [['sąd::noun', 'wysoki::adj'], ['trybunał::noun', 'konstytucyjny::adj'], ['kodeks::noun', 'cywilny::adj'], 'kpk::noun',
        ['sąd::noun', 'rejonowy::adj'], 'szkoda::noun', 'wypadek::noun', 'kolizja::noun', ['szkoda::noun', 'majątkowy::adj'],
        'nieszczęście::noun', 'rozwód::noun']

model_similar = lambda model, words: model.most_similar(words)
similiar = partial(model_similar, wv)

sml_expr = map(similiar, expr)
for k, v in zip(expr, sml_expr):
    print('\n', k)
    pprint.pprint(v[:3])

#%% 4. Solve equations
params = [[['sąd::noun', 'wysoki::adj', 'konstytucja::noun'], ['kpk::noun']],
          [['pasażer::noun', 'kobieta::noun'], ['mężczyzna::noun']],
          [['samochód::noun', 'rzeka::noun'], ['droga::noun']]]

model_equation = lambda model, pos, neg: model.most_similar(pos, neg)
calculator = partial(model_equation, wv)
result = (calculator(p[0], p[1]) for p in params)

for k, v in zip(params, result):
    print('\n', k)
    pprint.pprint(v[:3])

#%% 5. Project random 1000 words and highlight selected parametrs if present
def csum(arr):
    if len(arr) != 100:
        return sum(arr)    
    return arr

arguments = ['szkoda::noun', 'strata::noun', 'uszczerbek::noun', ['szkoda::noun', 'majątkowy::adj'], 'krzywde::noun',
             ['uszczerbek::noun', 'na::prep', 'zdrowie::noun'], 'nieszczęście::noun', 'niesprawiedliwość::noun']

tsne = manifold.TSNE(2, init='pca', random_state=0, n_iter=2000, perplexity=40, learning_rate=100)

words = np.random.choice(list(wv.vocab.keys()), 1000)
words = np.concatenate((words, arguments))
vectors = map(lambda word: csum(wv[word]), words)

viz = tsne.fit_transform(list(vectors))

#%%
sns.set_style('dark')
hue = [0 for i in range(1000)] + [1 for i in range(8)]  
sns.scatterplot(viz[:,0], viz[:,1], hue=hue, palette=['red', 'blue'])
