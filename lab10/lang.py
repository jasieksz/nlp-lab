#%%
import numpy as np
from fastai.text import * 
import pandas as pd
import os
from pathlib import Path

#%%[markdown]
# https://docs.fast.ai/text.html

#%% IMBD reviews, with sentiment label
path = untar_data(URLs.IMDB_SAMPLE)
# path = Path('/home/jasiek/.fastai/data/imdb_sample')

#%%
df = pd.read_csv(path/'texts.csv')
df.head()

#%%
data_lm = TextLMDataBunch.from_csv(path, 'texts.csv')
data_clas = TextClasDataBunch.from_csv(path, 'texts.csv', vocab=data_lm.train_ds.vocab, bs=32)

#%%
data_lm.save('data_lm_export.pkl')
data_clas.save('data_clas_export.pkl')

#%%
learn = language_model_learner(data_lm, AWD_LSTM, drop_mult=0.5)
learn.fit_one_cycle(1, 1e-2)

#%%
learn.save_encoder('enc1')

#%%
learn.unfreeze()
learn.fit_one_cycle(1, 1e-3)
learn.save_encoder('enc2')


#%% Reload
data_lm = load_data(path, 'data_lm_export.pkl')
data_clas = load_data(path, 'data_clas_export.pkl', bs=16)
learn = language_model_learner(data_clas, AWD_LSTM, drop_mult=0.5)
learn.load_encoder('enc2')

#%%
learn.predict("London is the biggest", n_words=4)

#%%
learn.predict("Policeman is looking for", n_words=8)

#%%
learn.predict("Filmmakers also have a habit of trying to", n_words=5)

#%%
learn.predict("Perfect mix of comedy and", n_words=1)
