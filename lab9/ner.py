#%%
import numpy as np
import requests
import os
from bs4 import BeautifulSoup
from functools import partial, reduce
from collections import Counter

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

url = 'http://ws.clarin-pl.eu/nlprest2/base/process'

#%% Test endpoint
res = requests.post(url, json=n82("Donald Tusk nie wie kim jest niedźwiedź Wojtek mieszkający w Londynie,\
            natomiast bardzo dobrze zna żyrafę Jadwigę,\
            którą można spotkać na Rynku Krakowskim lub na moście Łazienkowskim."))

y = BeautifulSoup(res.content)

#%% Filter -> Tag -> Reduce
is_NE = lambda x: x.contents[0] != '0'
add = lambda x,y : x + y

def getTags(text):
    res = requests.post(url, json=n82(text))
    y = BeautifulSoup(res.content)
    return Counter(list(filter(is_NE, y.findAll('ann'))))

def tagStatutes(paths):
    statutes = (readStatute(path) for path in paths)
    tags = (getTags(statute) for statute in statutes)
    return reduce(add, tags)

#%% Run
paths = list(map(lambda x: 'resources/ustawy/'+x, getRandomStatutes(2)))
res = tagStatutes(paths)
res

