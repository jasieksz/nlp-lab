# Language modelling

The exercise shows how a language model may be used to solve word-prediction tasks and used to generate text.


## Tasks

1. Read the documentation of [FastAI](https://github.com/fastai/fastai)
1. Read the documentation of [Polish adaptations](https://github.com/n-waves/poleval2018) for FastAI.
1. Download the [Polish model](https://go.n-waves.com/poleval2018-modelv1) for sentencepiece and FastAI. 
1. Produce the model predictions for the following sentences:
   1. (M) Warszawa to największe ? 
   1. (D) Te zabawki należą do ?
   1. (C) Policjant przygląda się ?
   1. (B) Na środku skrzyżowania widać ?
   1. (N) Właściciel samochodu widział złodzieja z ?
   1. (Ms) Prezytend z premierem rozmawiali wczoraj o ?
   1. (W) Witaj drogi ?
1. Check the model predictions for the following sentences:
   1. Gdybym wiedział wtedy dokładnie to co wiem teraz, to bym się nie ?
   1. Gdybym wiedziała wtedy dokładnie to co wiem teraz, to bym się nie ?
1. Check the model prediction for a longer span of text (at leas 30 tokens) for the following text piece:


Polscy naukowcy odkryli w Tatrach nowy gatunek istoty żywej. Zwięrzę to przypomina małpę, lecz porusza się na dwóch
nogach i potrafi posługiwać się narzędziami. Przy dłuższej obserwacji okazało się, że potrafi również posługiwać się
językiem polskim, a konkretnie gwarą podhalańską. Zwierzę to zostało nazwane ?


## Hints

