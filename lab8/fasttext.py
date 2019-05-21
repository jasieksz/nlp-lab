#%%
import fastText
from lab8 import tagger
from lab8 import classifier
from flair.data import TaggedCorpus, Sentence
from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentLSTMEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer
from pathlib import Path


#%%
oneline = lambda text: text.replace('\n', ' ')
transform_join_split = lambda getter, doc: list(map(oneline, map(classifier.join, map(getter, doc))))
fast_format = lambda x,y: '__label__' + str(y) + ' ' + x

def save_to_file(txt, path):
    with open(path, "w") as f:
        f.write(txt)

#%%
tagged = tagger.get_tags()
names = tagged.keys()
tags = tagged.values()
x, xv, xt, y, yv, yt = classifier.split(list(names), list(tags))

#%% Foreach transformer
def create_ft_files():
    for transformer, i in zip([classifier.I, classifier.II, classifier.III, classifier.IV], ['1', '2', '3', '4']):
        path = 'resources/fasttext/train-' + i +'.txt'
        X = transform_join_split(transformer, x)
        ffTrain = [fast_format(text, label) for label, text in zip(y, X)]
        save_to_file('\n'.join(ffTrain), path)

#%% 
results = []
for transformer, i in zip([classifier.I, classifier.II, classifier.III, classifier.IV], ['1', '2', '3', '4']):
    path = 'resources/fasttext/train-' + i +'.txt'
    print(path)
    model = fastText.train_supervised(path, epoch=30)
    Xt = transform_join_split(transformer, xt)
    y_pred = [model.predict(e)[0][0].replace('__label__', '') for e in Xt]
    results.append(y_pred)

[classifier.score([str(e) for e in yt], y_pred) for y_pred in results]

# [(0.9308340361473099, 0.9279661016949152, 0.927269829228265, None),
#  (0.7689592074376651, 0.7669491525423728, 0.7676091120080881, None),
#  (0.8047364755049918, 0.8050847457627118, 0.8034113411910592, None),
#  (0.6340067402300551, 0.6313559322033898, 0.6323998680855215, None)]


#%% FLAIR
w_em = [WordEmbeddings('pl'), FlairEmbeddings('polish-forward'), FlairEmbeddings('polish-backward')]
d_em = DocumentLSTMEmbeddings(w_em, hidden_size=512, reproject_words=True, reproject_words_dimension=256)

#%%
corpus = NLPTaskDataFetcher.load_classification_corpus(Path('resources/fasttext/'), test_file='test-3.txt', dev_file='val-3.txt', train_file='train-3.txt')
classifier = TextClassifier(d_em, label_dictionary=corpus.make_label_dictionary(), multi_label=False)

#%%
trainer = ModelTrainer(classifier, corpus)
trainer.train('resources/fasttext/', max_epochs=5)

#         2019-05-20 13:13:38,072 Testing using best model ...
# 2019-05-20 13:13:38,074 loading file resources/fasttext/best-model.pt
# 2019-05-20 13:13:49,123 MICRO_AVG: acc 0.481 - f1-score 0.6495
# 2019-05-20 13:13:49,128 MACRO_AVG: acc 0.4318 - f1-score 0.5839
# 2019-05-20 13:13:49,130 False      tp: 27 - fp: 12 - fn: 63 - tn: 112 - precision: 0.6923 - recall: 0.3000 - accuracy: 0.2647 - f1-score: 0.4186
# 2019-05-20 13:13:49,136 True       tp: 112 - fp: 63 - fn: 12 - tn: 27 - precision: 0.6400 - recall: 0.9032 - accuracy: 0.5989 - f1-score: 0.7492
