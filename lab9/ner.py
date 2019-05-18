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

#%%
def getRandomStatutes(n=100, path='resources/ustawy'):
    return np.random.choice(os.listdir(path), n)

def readStatute(path):
    with open(path, 'r') as document:
        return document.read()
       
body = lambda model, text: { 
	"lpmn": "any2txt|wcrft2|liner2({\"model\":\"" + model + "\"})",
    "text": text, 
    "user": "moj2@adres.mail",
}

n82 = partial(body, 'n82')
top9 = partial(body, "top9")

url = 'http://ws.clarin-pl.eu/nlprest2/base/process'

#%% Test endpoint
res = requests.post(url, json=n82("Donald Tusk nie wie kim jest niedźwiedź Wojtek mieszkający w Londynie,\
            natomiast bardzo dobrze zna żyrafę Jadwigę,\
            którą można spotkać na Rynku Krakowskim lub na moście Łazienkowskim."))

y = BeautifulSoup(res.content)
y

#%% Filter -> Tag -> Reduce
is_NE = lambda x: x.contents[0] != '0'
add = lambda x,y : x + y
tag = lambda x: re.search(r'chan=\"(\w*)\"', str(x)).groups()[0]

def getTags(text, model):
    res = requests.post(url, json=model(text))
    y = BeautifulSoup(res.content)
    print(y)
    r = Counter(list(map(tag, set(filter(is_NE, y.findAll('ann'))))))
    print(r)
    return r

def tagStatutes(paths, model):
    statutes = (readStatute(path) for path in paths)
    tags = (getTags(statute, model) for statute in statutes)
    return reduce(add, tags)

#%% Run
paths = list(map(lambda x: 'resources/ustawy/'+x, getRandomStatutes(1)))

freq_fine = tagStatutes(paths, n82)
freq_coarse = tagStatutes(paths, top9)

#%% Plot
sns.set_style('whitegrid')
sns.barplot(y=list(freq_fine.keys()), x=list(freq_fine.values()), palette='viridis')
plt.show()
sns.barplot(y=list(freq_coarse.keys()), x=list(freq_coarse.values()), palette='viridis')
            