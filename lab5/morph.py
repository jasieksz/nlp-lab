#%%
import numpy as np
import os
import re
import seaborn as sns
from collections import Counter
from functools import reduce, partial
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from lab1 import shapers
from typing import List, Tuple
import requests

#%% ES index for storing acts, ES analyzer for Polish texts:
es = Elasticsearch()
es.indices.create(
    index="my_index",
    body={
        "settings": {
            "analysis": {
                "analyzer": {
                  "my_analyzer": {
                      "type": "custom",
                      "tokenizer": "standard",
                      "filter": ["lowercase", "shingle"],
                    }
                }
            }
        },
        "mappings": {
            "legislation": {
                "properties": {
                    "text": {
                        "type": "text",
                        "analyzer": "my_analyzer",
                    }
                }                
            }
        }
    }
)

#%% Extract shingles (pairs) from the text
body = lambda text: {"tokenizer": "standard",
        "filter": ["lowercase", "shingle"],
        "text": text
}
analyze = lambda text: es.indices.analyze("my_index", body(text))

get_shingles = lambda text: list(map(lambda x: x['token'],
                                filter(lambda x: x['type'] == 'shingle',
                                text)))

get_tokens = lambda text: list(map(lambda x: x['token'],
                                filter(lambda x: x['type'] == '<ALPHANUM>',
                                text)))

text_only = lambda x: not re.search(r'\d+', x)
make_tuple = lambda x: tuple(x.split(' '))

#%% Bigram counts in the corpora
resource_path = 'resources/ustawy'
doc_shingles: List[List[str]] = []
doc_tokens: List[List[str]] = []
for filename in os.listdir(resource_path):
    with open(resource_path + '/' + filename, 'r') as document:
        legislation = document.read()
        doc = analyze(legislation)['tokens']
        doc_shingles.append(get_shingles(doc))
        doc_tokens.append(get_tokens(doc))

#%%
shingles = map(make_tuple, filter(text_only, shapers.flatten(doc_shingles)))
tokens = filter(text_only, shapers.flatten(doc_tokens))

#%% Morphosyntactic tagging - krnnt
split = lambda x: x[1].split('\t')[1:3]
twos = lambda x: len(x) == 2
tuple_split = lambda x: (x[0], x[1].split(':')[0])
composed = lambda a, b: a[1] == "subst" and b[1] == "subst"

def krnnt(text):
    response = requests.post('http://localhost:9200', text.encode("utf-8")) \
            .content.decode("utf-8") \
            .split("\n")
    return list(map(tuple_split, filter(twos, map(split, shapers.pairs(response)))))[0]

#%%
tokens_freq = Counter(list(tokens))
shingle_freq = Counter(list(shingles))
# token_tag = {token: krnnt(token) for token in list(tokens_freq.keys())[:100]}

#%
# shingle_tag = {}
# for k,v in shingle_freq.items():
#     t = (token_tag[k[0]], token_tag[k[1]])
#     if composed(t[0], t[1]):
#         shingle_tag[k] = v

#%%

#%% LLR score
h = lambda k: (k/k.sum() * np.log(k/k.sum() + (k==0))).sum()
llr = lambda k: 2*k.sum() * (h(k) - h(k.sum(axis=0)) - h(k.sum(axis=1)))
sum_shingles = sum(list(shingle_freq.values()))

def prob(a, b):
    a_and_b = shingle_freq.get((a, b), 0)
    a_not_b = tokens_freq[a] - a_and_b
    b_not_a = tokens_freq[b] - a_and_b
    none = sum_shingles - a_not_b - b_not_a - a_and_b
    return np.array([[a_and_b, a_not_b], [b_not_a, none]])

llrs = []
for e in ((s, prob(s[0], s[1])) for s in shingle_freq.keys()):
    score = 0
    try:
        score = llr(e[1])
    except:
        score = 0
    finally:        
        llrs.append((e[0], score))
llrs = sorted(llrs, key=lambda e: e[1], reverse=True)

#%%
split = lambda x: x[1].split('\t')[1:3]
twos = lambda x: len(x) == 2
tuple_split = lambda x: (x[0], x[1].split(':')[0])
composed = lambda a, b: a[1] == "subst" and b[1] == "subst"

def krnnt(text):
    response = requests.post('http://localhost:9200', text.encode("utf-8")) \
            .content.decode("utf-8") \
            .split("\n")
    return list(map(tuple_split, filter(twos, map(split, shapers.pairs(response)))))[0]

simple_composed = lambda a, b: a == "subst" and b == "adj"

tags = {}
for k, v in llrs[:1000]:
    w1, w2 = k
    if w1 not in tags:
        tags[w1] = krnnt(w1)[0][1]
    if w2 not in tags:
        tags[w2] = krnnt(w2)[0][1]

res = []
for k, v in llrs[:1000]:
    if simple_composed(tags[k[0]], tags[k[1]]):
        res.append((k, v))

# [(('minister', 'właściwy'), 52540.094674199914),
#  (('rzeczypospolitej', 'polskiej'), 48503.0586858395),
#  (('samorządu', 'terytorialnego'), 24585.651150796628),
#  (('unii', 'europejskiej'), 19333.34152186877),
#  (('ministra', 'właściwego'), 18495.828483214482),
#  (('spraw', 'wewnętrznych'), 17541.613002768823),
#  (('ministrem', 'właściwym'), 16562.68916409943),
#  (('obrony', 'narodowej'), 16014.205277177041),
#  (('finansów', 'publicznych'), 15122.035444822655),
#  (('opieki', 'zdrowotnej'), 14984.55841457874),
#  (('działalności', 'gospodarczej'), 14725.393514715146),
#  (('straży', 'granicznej'), 13952.122070427504),
#  (('administracji', 'rządowej'), 13435.393024880126),
#  (('produktu', 'leczniczego'), 12980.074182948434),
#  (('ubezpieczeń', 'społecznych'), 12911.240610180052),
#  (('papierów', 'wartościowych'), 12680.178581487156),
#  (('tekstu', 'jednolitego'), 9128.717330235475),
#  (('życie', 'niniejszej'), 8767.555544984505),
#  (('produktów', 'leczniczych'), 8535.86909333373),
#  (('służby', 'cywilnej'), 7999.866348819152),
#  (('straży', 'pożarnej'), 7677.669429529303),
#  (('jednostek', 'organizacyjnych'), 7552.486023228135),
#  (('sił', 'zbrojnych'), 7474.766199147115),
#  (('dzienniku', 'urzędowym'), 7309.354373109792),
#  (('wyrobów', 'akcyzowych'), 7249.038566370878),
#  (('administracji', 'publicznej'), 6749.48652040007),
#  (('służby', 'wojskowej'), 6563.573882861266),
#  (('osobowości', 'prawnej'), 6461.516560285395),
#  (('ministrowi', 'właściwemu'), 6437.6756568103365),
#  (('państwa', 'członkowskiego'), 6301.717170363108),
#  (('energii', 'elektrycznej'), 6253.727208427944),
#  (('pomocy', 'społecznej'), 6103.611447574544),
#  (('postępowania', 'karnego'), 6082.8448244408055),
#  (('osób', 'fizycznych'), 5844.750760129249),
#  (('zdanie', 'drugie'), 5695.5451098645735),
#  (('jednostki', 'organizacyjne'), 5663.441968042447),
#  (('środków', 'trwałych'), 5211.860810648399),
#  (('działalność', 'gospodarczą'), 5056.578836129442),
#  (('osób', 'prawnych'), 5011.530123038065),
#  (('organ', 'egzekucyjny'), 4831.071945518962),
#  (('jednostki', 'organizacyjnej'), 4819.960227364898),
#  (('podatku', 'dochodowym'), 4814.523728121385),
#  (('obszar', 'celny'), 4725.354688212613),
#  (('podatku', 'dochodowego'), 4706.270706968501),
#  (('komisji', 'wyborczej'), 4653.176969472725),
#  (('rozporządzenia', 'szczegółowe'), 4533.003477497759),
#  (('komisja', 'wyborcza'), 4526.6074825933065),
#  (('podstawie', 'odrębnych'), 4476.855832974852),
#  (('monitor', 'polski'), 4423.48989202928),
#  (('kapitału', 'zakładowego'), 4406.420997237338),
#  (('sądu', 'okręgowego'), 4270.55154475751),
#  (('papierami', 'wartościowymi'), 4175.553153773603),
#  (('państw', 'członkowskich'), 4134.77574720542),
#  (('stanowisko', 'służbowe'), 4127.418284610179),
#  (('lokalu', 'mieszkalnego'), 4065.565798739738),
#  (('rady', 'nadzorczej'), 4062.730816161752),
#  (('ubezpieczenia', 'zdrowotnego'), 4038.2109674917974),
#  (('papiery', 'wartościowe'), 3920.0428622577006),
#  (('trybie', 'określonym'), 3904.749572427557),
#  (('gospodarki', 'wodnej'), 3880.6204309312557),
#  (('informacji', 'niejawnych'), 3877.584108626473),
#  (('opieki', 'społecznej'), 3866.7616884441773),
#  (('organ', 'celny'), 3779.713914488449),
#  (('odpisów', 'amortyzacyjnych'), 3764.4264361695195),
#  (('gospodarki', 'żywnościowej'), 3736.642681428031),
#  (('rzeczpospolita', 'polska'), 3611.5414573765615),
#  (('sprawozdania', 'finansowego'), 3568.4475552480285),
#  (('pochodzenia', 'zwierzęcego'), 3545.0461073571037),
#  (('żandarmerii', 'wojskowej'), 3489.097755042418),
#  (('żołnierza', 'zawodowego'), 3488.7987461871558),
#  (('postępowaniu', 'egzekucyjnym'), 3475.5120859700464),
#  (('kodeksu', 'karnego'), 3475.459383215801),
#  (('materiału', 'siewnego'), 3434.4190007174984),
#  (('gospodarki', 'morskiej'), 3406.9027339396293),
#  (('okręgu', 'wyborczym'), 3393.691841489328),
#  (('wartości', 'niematerialnych'), 3390.1171871692104),
#  (('polityki', 'socjalnej'), 3381.5008972368846),
#  (('żołnierzy', 'zawodowych'), 3379.7569550672956),
#  (('rynków', 'rolnych'), 3305.8602616745375),
#  (('komendant', 'główny'), 3292.5812110874076),
#  (('parlamentu', 'europejskiego'), 3270.376482830321),
#  (('sądu', 'najwyższego'), 3263.811086348143),
#  (('należności', 'pieniężnych'), 3257.761753994262),
#  (('masie', 'jednostkowej'), 3226.9265527282237),
#  (('kultury', 'fizycznej'), 3221.7647201996397),
#  (('urzędu', 'statystycznego'), 3156.3067891100122),
#  (('ordynacja', 'podatkowa'), 3119.0596363665245),
#  (('osoby', 'prawne'), 3111.916777568142),
#  (('zabezpieczenia', 'społecznego'), 3050.350226168169),
#  (('decyzji', 'administracyjnej'), 3005.9150767742494),
#  (('ubezpieczenie', 'społeczne'), 2995.9655211970303),
#  (('ubezpieczenie', 'zdrowotne'), 2975.058108211649),
#  (('postępowania', 'administracyjnego'), 2951.707966261244),
#  (('roku', 'podatkowym'), 2951.3728322066913),
#  (('roku', 'kalendarzowym'), 2940.893437364088),
#  (('rybołówstwa', 'morskiego'), 2917.966174690502),
#  (('paliw', 'gazowych'), 2891.76513632878),
#  (('podmiot', 'odpowiedzialny'), 2887.049206392873),
#  (('zasobów', 'naturalnych'), 2858.854313636511),
#  (('tego', 'samego'), 2853.9543666469053),
#  (('tym', 'samym'), 2820.3803664673223),
#  (('przestępstwo', 'skarbowe'), 2808.0750231710476),
#  (('państwie', 'członkowskim'), 2802.1761112918143),
#  (('sądu', 'apelacyjnego'), 2786.5912536234728),
#  (('finansach', 'publicznych'), 2779.9695415587066),
#  (('służbę', 'wojskową'), 2773.78651725867),
#  (('świadczeń', 'zdrowotnych'), 2725.6380750245603),
#  (('ubezpieczenia', 'społecznego'), 2703.6718138154692),
#  (('przepisów', 'wykonawczych'), 2703.449919491868),
#  (('danych', 'osobowych'), 2698.3694807420334),
#  (('rzeczników', 'patentowych'), 2687.7884717749953),
#  (('przepisy', 'ogólne'), 2672.671676485849),
#  (('kontroli', 'skarbowej'), 2646.5352881920157),
#  (('osoby', 'fizyczne'), 2635.2807028584416),
#  (('zaopatrzeniu', 'emerytalnym'), 2626.886009270606),
#  (('parku', 'narodowego'), 2593.3408000072304),
#  (('roku', 'kalendarzowego'), 2576.3066035989696),
#  (('osobowość', 'prawną'), 2553.331724955611),
#  (('umów', 'międzynarodowych'), 2528.784729420532),
#  (('dozoru', 'technicznego'), 2509.0096009480326),
#  (('wyrobów', 'medycznych'), 2507.643639313312),
#  (('przedsiębiorstw', 'państwowych'), 2481.553797045663),
#  (('urzędu', 'skarbowego'), 2476.589894088154),
#  (('lokali', 'mieszkalnych'), 2475.854723061323),
#  (('komendanta', 'głównego'), 2419.833600738433),
#  (('jednostka', 'organizacyjna'), 2393.719818098988),
#  (('obszarze', 'gospodarczym'), 2390.599822673806),
#  (('sprawozdanie', 'finansowe'), 2387.2760431279976),
#  (('rok', 'podatkowy'), 2385.6596332600143),
#  (('usługi', 'certyfikacyjne'), 2346.2098408735815),
#  (('nadzoru', 'wewnętrznego'), 2336.6340994088996),
#  (('zdaniu', 'wstępnym'), 2321.8126775510937),
#  (('postępowanie', 'dyscyplinarne'), 2321.7879997326736),
#  (('jednostkach', 'organizacyjnych'), 2320.8335292362235),
#  (('sądu', 'administracyjnego'), 2319.1002003350886),
#  (('kary', 'dyscyplinarnej'), 2317.599081185192),
#  (('produkt', 'leczniczy'), 2306.846193582897),
#  (('przepisy', 'wykonawcze'), 2301.3281797022482),
#  (('przymusu', 'bezpośredniego'), 2285.2849479074794),
#  (('dziedzictwa', 'narodowego'), 2281.8931419910873),
#  (('banku', 'polskiego'), 2270.6031353092594),
#  (('bank', 'polski'), 2261.2105560672617),
#  (('organ', 'podatkowy'), 2256.2520424158065),
#  (('ubezpieczeniu', 'społecznym'), 2252.0851829448898),
#  (('spraw', 'zagranicznych'), 2246.231751599539),
#  (('podatek', 'dochodowy'), 2241.8165966242395),
#  (('postępowania', 'dyscyplinarnego'), 2233.206989952798),
#  (('gospodarstwa', 'krajowego'), 2233.0531738774926),
#  (('partii', 'politycznej'), 2226.733725410508),
#  (('rok', 'obrotowy'), 2226.2601907978164),
#  (('stawek', 'dziennych'), 2225.9659768483025),
#  (('chorób', 'zakaźnych'), 2224.342039352804),
#  (('inspektor', 'sanitarny'), 2221.595883646435),
#  (('postępowania', 'cywilnego'), 2213.3932758377805),
#  (('przetworów', 'mlecznych'), 2199.4292820779046),
#  (('jednostkę', 'organizacyjną'), 2196.64647887318),
#  (('szkolnictwa', 'wyższego'), 2192.3275391237626),
#  (('urzędu', 'celnego'), 2167.7293917837014),
#  (('oddziału', 'terenowego'), 2167.593599233241),
#  (('dane', 'osobowe'), 2141.2476697253796),
#  (('obiektu', 'budowlanego'), 2122.150211577524),
#  (('urząd', 'skarbowy'), 2115.5193320462104),
#  (('osoba', 'fizyczna'), 2113.7106529688936),
#  (('sąd', 'rejestrowy'), 2111.9354852301444),
#  (('rzecznika', 'dyscyplinarnego'), 2108.5341132154495),
#  (('badań', 'naukowych'), 2104.8125339949524),
#  (('zamówień', 'publicznych'), 2089.199484429417),
#  (('karę', 'pieniężną'), 2086.0157275806127),
#  (('nadzoru', 'budowlanego'), 2080.5487880997434),
#  (('instytucji', 'finansowych'), 2075.0224670629063),
#  (('żeglugi', 'śródlądowej'), 2070.0203172804613),
#  (('materiał', 'siewny'), 2069.8993109784988),
#  (('przepisy', 'przejściowe'), 2063.108235527565),
#  (('gospodarstwa', 'rolnego'), 2057.474156993274),
#  (('środki', 'finansowe'), 2051.088993239796),
#  (('nadzoru', 'bankowego'), 2043.7468288909542),
#  (('środków', 'finansowych'), 2041.1565089167618),
#  (('osoby', 'prawnej'), 2029.6426240702367),
#  (('roku', 'obrotowego'), 2026.2632696694602),
#  (('sąd', 'najwyższy'), 2021.543954118114),
#  (('renty', 'rodzinnej'), 2020.945434098463),
#  (('broni', 'palnej'), 2019.8132715976294),
#  (('roku', 'podatkowego'), 2006.8609932507316),
#  (('stanowiska', 'służbowego'), 1976.2423494303785),
#  (('ruchu', 'drogowym'), 1975.2978889718963),
#  (('komisji', 'egzaminacyjnej'), 1972.7926372478255),
#  (('wyroby', 'akcyzowe'), 1967.564495022206),
#  (('statku', 'rybackiego'), 1955.432751939934),
#  (('formie', 'pisemnej'), 1946.4246108974805),
#  (('zdaniu', 'pierwszym'), 1939.1477999609856),
#  (('diagnostów', 'laboratoryjnych'), 1936.8442271629415),
#  (('inspekcji', 'sanitarnej'), 1928.828413596699),
#  (('produktami', 'leczniczymi'), 1925.6119162456696),
#  (('rynku', 'rolnego'), 1924.621135417536),
#  (('materiałów', 'włókienniczych'), 1918.8400198334384),
#  (('komisji', 'rewizyjnej'), 1903.141061758929),
#  (('korzyści', 'majątkowej'), 1901.6182296497684),
#  (('należności', 'celnych'), 1893.1968891323643),
#  (('sądów', 'wojskowych'), 1892.3641474889944),
#  (('ruchu', 'drogowego'), 1880.2191910343806),
#  (('zarządzania', 'kryzysowego'), 1876.0807217884267),
#  (('obowiązków', 'służbowych'), 1866.1019782755754),
#  (('subwencji', 'ogólnej'), 1860.7140667065444),
#  (('środków', 'spożywczych'), 1859.821345629995),
#  (('osoba', 'która'), 1857.8530717052768),
#  (('inspektor', 'farmaceutyczny'), 1844.1858712723804),
#  (('inspekcji', 'weterynaryjnej'), 1840.6949389945269),
#  (('radców', 'prawnych'), 1836.3702273807976),
#  (('służbie', 'cywilnej'), 1834.3865844230763),
#  (('pracę', 'zarobkową'), 1832.0024222122302),
#  (('pozwolenia', 'wodnoprawnego'), 1831.6957788219856),
#  (('rozwoju', 'regionalnego'), 1831.3940340717613),
#  (('żołnierz', 'zawodowy'), 1829.7642835727474),
#  (('zakresie', 'określonym'), 1819.6815328302916),
#  (('grupy', 'kapitałowej'), 1814.9201319829667),
#  (('jakości', 'handlowej'), 1813.8692977265305),
#  (('rzecznik', 'dyscyplinarny'), 1812.301894352234),
#  (('praw', 'majątkowych'), 1803.1167261169523),
#  (('państwach', 'członkowskich'), 1798.0445129834643),
#  (('rejestru', 'sądowego'), 1797.2811069871043),
#  (('ubezpieczenia', 'emerytalne'), 1795.3899730137184),
#  (('organizmów', 'morskich'), 1794.4722982233036),
#  (('raz', 'pierwszy'), 1776.5605359481244),
#  (('osobę', 'fizyczną'), 1752.7828547028105),
#  (('uposażenia', 'zasadniczego'), 1752.59775959053),
#  (('urząd', 'patentowy'), 1747.016574736988),
#  (('funduszy', 'inwestycyjnych'), 1743.1522429555962),
#  (('ksiąg', 'rachunkowych'), 1736.738441287622),
#  (('stanowisku', 'służbowym'), 1736.4148774173261),
#  (('przepisy', 'dotychczasowe'), 1735.4256274393235),
#  (('wykroczenie', 'skarbowe'), 1726.170420945968),
#  (('usług', 'konsumpcyjnych'), 1724.5883239683626),
#  (('zakresie', 'niezbędnym'), 1722.3206900147536),
#  (('sprawozdań', 'finansowych'), 1720.2668106952115),
#  (('zdanie', 'pierwsze'), 1707.2656272683043),
#  (('napojów', 'alkoholowych'), 1706.0688969194978),
#  (('niektórych', 'innych'), 1703.8035179707877),
#  (('powierzchni', 'użytkowej'), 1696.3208304253828),
#  (('narodowi', 'polskiemu'), 1690.833848438677),
#  (('wód', 'powierzchniowych'), 1682.9060467204567),
#  (('gospodarki', 'przestrzennej'), 1676.328153412149),
#  (('rachunek', 'bankowy'), 1672.2091882298137),
#  (('sprzedaży', 'detalicznej'), 1666.8273533540723),
#  (('gazu', 'ziemnego'), 1665.402219994319),
#  (('kodeks', 'karny'), 1650.573915467899),
#  (('tytułu', 'wykonawczego'), 1644.2606353701922),
#  (('inspekcji', 'handlowej'), 1639.757829606285),
#  (('okręg', 'wyborczy'), 1623.6614296509556),
#  (('sierści', 'zwierzęcej'), 1623.5499926352147),
#  (('radcy', 'prawnego'), 1616.2493931401705)]