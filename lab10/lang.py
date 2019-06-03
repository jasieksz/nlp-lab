#%% Clean virtualenv to resolve conflicts
import numpy as np
import fastai
from fastai.text import *
from sentencepiece import SentencePieceProcessor

#%%
fastai_model = 'resources/work/up_low50k/models/fwd_v50k_finetune_lm_enc.h5'
sp_model = 'resources/work/up_low50k/tmp/sp-50k.model'

#%%
processor = SentencePieceProcessor()
processor.Load(sp_model)
processor.SetEncodeExtraOptions('bos:eos')
processor.SetDecodeExtraOptions('bos:eos')

#%%
bptt = 5
max_seq = 1000000
n_tok = len(processor)
emb_sz = 400
n_hid = 1150
n_layers = 4
pad_token = 1
bidir = False
qrnn = False

rnn = MultiBatchRNN(bptt, max_seq, n_tok, emb_sz, n_hid, n_layers, pad_token, bidir, qrnn)
model = SequentialRNN(rnn, LinearDecoder(n_tok, emb_sz, 0, tie_encoder=rnn.encoder))

load_model(model[0], fastai_model)
model.reset()
model.eval()

#%%
class TextDataset(Dataset):
    def __init__(self, x):
        self.x = x

    def __getitem__(self, idx):
        sentence = self.x[idx]
        return sentence[:-1], sentence[1:]

def next_word(sentence, mode, deterministic=True): 
    ids = [np.array(processor.encode_as_ids(sentence))]

    dataset = TextDataset(ids)
    sampler = SortSampler(ids, key=lambda x: len(ids[x]))
    dl = DataLoader(dataset, batch_size=100, transpose=True, pad_idx=1, sampler=sampler, pre_pad=False)

    tensors = None
    with no_grad_context():
        for (x, y) in dl:
            tensors, _, _ = model(x)       
    last_tensor = tensors[-1]

    # best = int(torch.argmax(last_tensor))
    best = int(
        torch.argmax(arg) if deterministic else torch.
        multinomial(last_tensor.exp(), 1))
    word = processor.decode_ids([best])
   
    while best in ids[0] or not word.isalpha():
        last_tensor[best] = -1
        best = int(torch.argmax(last_tensor))
        word = processor.decode_ids([best])
    return word

def predict(model, sentence, word_count, deterministic=True):
    result = ""
    for _ in range(word_count):
        word = next_word(sentence + " " + result, model, deterministic)
        result += (" " + word)
    return result

#%%
sentences = [
    'Warszawa to największe',
    'Te zabawki należą do',
    'Policjant przygląda się',
    'Na środku skrzyżowania widać',
    'Właściciel samochodu widział złodzieja z',
    'Prezydent z premierem rozmawiali wczoraj o',
    'Witaj drogi',
    'Gdybym wiedział wtedy dokładnie to co wiem teraz, to bym się nie',
    'Gdybym wiedziała wtedy dokładnie to co wiem teraz, to bym się nie',
    'Polscy naukowcy odkryli w Tatrach nowy gatunek istoty żywej.\
    Zwięrzę to przypomina małpę, lecz porusza się na dwóch nogach i potrafi\
    posługiwać się narzędziami. Przy dłuższej obserwacji okazało się, że potrafi\
    również posługiwać się językiem polskim, a konkretnie gwarą podhalańską.\
    Zwierzę to zostało nazwane']

#%%
for sentence in sentences:
    print(sentence + " -->\n")
    print(predict(model, sentence, 5))
    print(predict(model, sentence, 10))
    print(predict(model, sentence, 25))
    print("")
