#%%
import fastText
from lab8 import tagger
from lab8 import classifier

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
