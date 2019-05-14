#%%
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_fscore_support
from typing import List, Tuple, Any
from types import LambdaType
from functools import partial
from lab8 import tagger

#%%
def split(data: List[str], tags: List[bool]) -> Tuple[List[Tuple[str,int]], List[Tuple[str,int]], List[Tuple[str,int]],\
                                                      List[bool], List[bool], List[bool]]:
    x, xtest, y, ytest = train_test_split(data, tags, test_size=0.2, random_state=42)
    x, xval, y, yval = train_test_split(x, y, test_size=0.25, random_state=42)
    return x, xval, xtest, y, yval, ytest

def get_document(name: str, section_one: int, select_fun) -> List[str]:
    statute = tagger.read_statute(name)
    return select_fun(statute[section_one:])

selector = lambda s, document: np.random.choice(document, size=s)
full = lambda document: document
ten_percent = lambda document: selector(len(document) // 10, document)
ten_lines = partial(selector, 10)
one_line = partial(selector, 1)

I = lambda nt: get_document(nt[0], nt[1], full)
II = lambda nt: get_document(nt[0], nt[1], ten_percent)
III = lambda nt: get_document(nt[0], nt[1], ten_lines)
IV = lambda nt: get_document(nt[0], nt[1], one_line)

join = lambda lines: ''.join(lines)
transform_join = lambda getter, doc: list(map(join, map(getter, doc)))




#%%
def SVM(transformer, x, xv, xt, y, yv, yt):
    feature_extraction = TfidfVectorizer()
    X = feature_extraction.fit_transform(transform_join(transformer, x+xv))
    # Xv = feature_extraction.transform(transform_join(transformer, xv))
    Xt = feature_extraction.transform(transform_join(transformer, xt))

    svc = SVC(kernel='linear')
    C_s = np.logspace(-10, 0, 10)

    clf = GridSearchCV(estimator=svc, param_grid=dict(C=C_s), n_jobs=-1)
    clf.fit(X, y+yv)

    Y_pred = clf.best_estimator_.predict(Xt)
    return yt, Y_pred

def score(test, prediction):
    return precision_recall_fscore_support(test, prediction, average='weighted')

#%% Ex: 1, 2, 3, 4
def run():
    tagged = tagger.get_tags()
    names = tagged.keys()
    tags = tagged.values()
    x, xv, xt, y, yv, yt = split(list(names), list(tags))

    SVM_results = [SVM(t_func, x, xv, xt, y, yv, yt) for t_func in [I, II, III, IV]]
    scores = [score(res[0], res[1]) for res in SVM_results]
    return scores

# [(0.9308340361473099, 0.9279661016949152, 0.927269829228265, None),
#  (0.7460115295914258, 0.7330508474576272, 0.7187353301344404, None),
#  (0.7552966101694916, 0.7542372881355932, 0.7490003353713592, None),
#  (0.6020594131583744, 0.6101694915254238, 0.5754640839386601, None)]