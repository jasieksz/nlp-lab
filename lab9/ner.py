#%%
import numpy as np
import requests
import os
from bs4 import BeautifulSoup
from functools import partial, reduce
from collections import Counter
import re
import seaborn as sns
from matplotlib import pyplot as plt
import xml.etree.ElementTree as et 
import pandas as pd

#%%
def getRandomStatutes(n=100, path='resources/ustawy'):
    return np.random.choice(os.listdir(path), n)

def readStatute(path):
    with open(path, 'r') as document:
        return document.read()
       
body = lambda model, text: { 
	"lpmn": "any2txt|wcrft2|liner2({\"model\":\"" + model + "\"})",
    "text": text, 
    "user": "m317@adres.mail",
}

n82 = partial(body, 'n82')
top9 = partial(body, "top9")

url = 'http://ws.clarin-pl.eu/nlprest2/base/process'

#%% Test endpoint
res = requests.post(url, json=n82("Donald Tusk nie wie kim jest Donald Tusk"))

y = BeautifulSoup(res.content)
y

#%%


#%% Filter -> Tag -> Reduce
is_NE = lambda x: x.contents[0] != '0'
add = lambda x,y : x + y
tag = lambda x: re.search(r'chan=\"(\w*)\"', str(x)).groups()[0]

def getTags(text, model):
    res = requests.post(url, json=model(text))
    y = BeautifulSoup(res.content)
    r = Counter(list(map(tag, set(filter(is_NE, y.findAll('ann'))))))
    return r

def tagStatutes(paths, model):
    statutes = (readStatute(path) for path in paths)
    tags = (getTags(statute, model) for statute in statutes)
    return reduce(add, tags)

#%% Run 11:10 -12:19
paths = list(map(lambda x: 'resources/ustawy/'+x, getRandomStatutes(100)))

freq_fine = tagStatutes(paths, n82)
freq_coarse = tagStatutes(paths, top9)

#%% Plot
sns.set_style('whitegrid')
sns.set(rc={'figure.figsize':(15,10)})
g = sns.barplot(y=list(freq_fine.keys()), x=list(freq_fine.values()), palette='viridis')
g.set(xticks=list(range(0,350,15)))
plt.show()
h = sns.barplot(y=list(freq_coarse.keys()), x=list(freq_coarse.values()), palette='viridis')
h.set(xticks=list(range(0,400,15)))
plt.show()


#%%
ccl_paths = lambda base: map(lambda path: base+path, os.listdir(base))
get_tree = lambda file_path: et.parse(file_path)
get_root = lambda tree: tree.getroot()

def get_NE_freq(root):
    combined = {}
    for chunk in root:
        chunk_NE_freq = {}
        for sentence in chunk:
            sentence_NE = {}
            for token in sentence:
                if (token.tag == 'tok'):
                    ann = token.find('ann')
                    if (ann != None and ann.text != '0'):
                        key = (ann.attrib['chan'], ann.text)
                        val = token.find('orth').text
                        arr = sentence_NE.get(key, list()) 
                        arr.append(val)
                        sentence_NE[key] = arr
            for k,v in sentence_NE.items():
                key = (k[0], ' '.join(v))
                val = chunk_NE_freq.get(key, 0)
                chunk_NE_freq[key] = val + 1

        for k,v in chunk_NE_freq.items():
            val = combined.get(k, 0) + v
            combined[k] = val
    return combined

def add_dicts(dictionaries):
    result = {}
    for dictio in dictionaries:
        for k,v in dictio.items():
            val = result.get(k, 0) + v
            result[k] = val
    return sorted(result.items(), key=lambda kv: -kv[1])

#%%
top9_base = 'resources/cclki/out_top9/'
roots_9 = map(get_root, map(get_tree, ccl_paths(top9_base)))
NES9 = list(map(get_NE_freq, roots_9))
add_dicts(NES9)

#%%
n82_base = 'resources/cclki/out2/'
roots_82 = map(get_root, map(get_tree, ccl_paths(n82_base)))
NES82 = list(map(get_NE_freq, roots_82))
add_dicts(NES82)
