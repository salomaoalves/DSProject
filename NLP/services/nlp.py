# Imports
import pandas as pd
import numpy as np
import nltk
import spacy # vai fazer a lemmatização
import re
import string
import unidecode
import math

nltk.download('stopwords')
from nltk.corpus import stopwords

# load dic in spacy session

# for jupyter
#!python -m spacy download pt_core_news_sm
# for vscode
nlp = spacy.load("pt_core_news_sm")

# How to load pos_tag in pt-br -- you should have the file POS_tagger_brill.pkl downloaded 
# https://github.com/inoueMashuu/POS-tagger-portuguese-nltk/tree/master/trained_POS_taggers
import joblib
pos_tag_pt = joblib.load('POS_tagger_brill.pkl')

# list of stopwords
stopwords = set(stopwords.words('portuguese'))

def run(commen):
    '''Delete special characters/accents and tokenize comments in words'''

    new_comen = []
    for text in commen:
        text = unidecode.unidecode(text)
        regex = re.compile('[' + re.escape(string.punctuation) + '\\r\\t\\n]')
        nopunct = regex.sub(" ", str(text))
        doc = nlp(nopunct, disable = ['parser', 'ner'])
        tokinizado = [token.text.lower() for token in doc]
        new_comen.append(tokinizado)
        new_comen.append(' ')
    new_comen = [item for items in new_comen for item in items]

    # get ngram's
    df_unagram = unagram(new_comen)
    df_bigram = bigram(new_comen)
    df_trigram = trigram(new_comen)
    df_frequency = all_ngram(df_unagram,df_bigram,df_trigram,15)

    #get TF-IDF
    dic_tf_idf = tf_idf(new_comen, commen, 'anos')

    # delete spaces and stopwords
    new_comen = [w for w in new_comen if not w.isspace() and w not in stopwords]

    return df_unagram, df_bigram, df_trigram, df_frequency, dic_tf_idf, new_comen


def filter_type_token_bigram(ngram):
    '''Filter ADJ/NN and delete stopwords/spaces in bigrams'''

    # delete spaces and stopwords
    for word in ngram:
        if word in stopwords or word.isspace():
            return False
        
    # types of tokens accepted
    acceptable_types = ('N', 'NPROP') #adjective, noun
    second_type = ('N', 'NPROP', 'ADJ') #noun
    
    # tags
    tags = pos_tag_pt.tag([str(ngram[0]),str(ngram[1])])

    # filtering
    if tags[0][1] in acceptable_types and tags[1][1] in second_type:
        return True
    else:
        return False


def filter_type_token_trigram(ngram):
    '''Filter ADJ/NN and delete stopwords/spaces in trigrams'''

    # delete spaces and stopwords
    for word in ngram:
        if word in stopwords or word.isspace():
            return False
        
    # types of tokens accepted
    first_type = ('ADJ', 'N', 'NPROP') #adjective, noun
    second_type = ('ADJ', 'N', 'NPROP') #adjective, noun
    
    # tags
    tags = pos_tag_pt.tag([str(ngram[0]),str(ngram[1]),str(ngram[2])])
    
    # filtering
    if tags[0][1] in first_type and tags[2][1] in second_type:
        return True
    else:
        return False


def unagram(new_comen):
    # delete spaces and stopwords
    new_comen = [w for w in new_comen if not w.isspace() and w not in stopwords]

    # create the unagram
    df = pd.DataFrame(new_comen, dtype=str)
    return pd.DataFrame({'anagram': df[0].value_counts().index,
                         'anagram_frequency': df[0].value_counts().values})


def bigram(new_comen):
    # reate the bigramas
    buscaBigramas = nltk.collocations.BigramCollocationFinder.from_words(new_comen)

    # frenquency table
    bigram_freq = buscaBigramas.ngram_fd.items()
    FreqTabBigramas = pd.DataFrame(list(bigram_freq), 
                                   columns=['bigram', 'bigram_frequency']
                                  ).sort_values(by='bigram_frequency', ascending=False)
    
    # filter
    bigram_filter = FreqTabBigramas[FreqTabBigramas.bigram.map(lambda x: filter_type_token_bigram(x))]
    
    return bigram_filter


def trigram(new_comen):
    # create the trigrams
    buscaTrigramas = nltk.collocations.TrigramCollocationFinder.from_words(new_comen)

    # frenquency table
    trigram_freq = buscaTrigramas.ngram_fd.items()
    FreqTabTrigramas = pd.DataFrame(list(trigram_freq), 
                                    columns=['trigram','trigram_frequency']
                                   ).sort_values(by='trigram_frequency',ascending=False)
    # filter
    trigram_filter = FreqTabTrigramas[FreqTabTrigramas.trigram.map(lambda x: filter_type_token_trigram(x))]

    return trigram_filter


def all_ngram(anagram_df, bigram_df, trigram_df, n):
    """Returns the top n frequency of all gram's."""

    anagram_df = anagram_df.reset_index(drop=True).head(n)
    bigram_df = bigram_df.reset_index(drop=True).head(n)
    trigram_df = trigram_df.reset_index(drop=True).head(n)

    anagram_df["anagram_frequency"] = anagram_df["anagram_frequency"].astype(int)
    bigram_df["bigram_frequency"] = bigram_df["bigram_frequency"].astype(int)
    trigram_df["trigram_frequency"] = trigram_df["trigram_frequency"].astype(int)

    frequency_df = anagram_df.join(bigram_df)
    frequency_df = frequency_df.join(trigram_df)

    frequency_df.fillna(".", inplace=True)
    return frequency_df

def tf_idf(comments_token, comments_phrases, t):
    '''Get the TF, DF, IDF and TF-IDF'''

    # delete spaces and stopwords
    comments_token = [w for w in comments_token if not w.isspace() and w not in stopwords]

    # documents size
    d = len(comments_token)
    n = len(comments_phrases)

    # creted frequency table
    df = pd.DataFrame(comments_token, dtype=str)
    freq_table = pd.DataFrame({'anagram_frequency': df[0].value_counts().values},
                              index = df[0].value_counts().index)

    #cada comentario é um documento (tf)
    #todos os comentarios são 1 documento (df/idf)
    # add essas observações na web #

    # metrics
    tf = int(freq_table.loc[t])/d 
    df = 0 
    for p in comments_phrases:
        if t in p:
            df += 1
    idf = math.log(n/df) 
    tf_idf = tf*idf
    return {'tf':np.round(tf,4), 'df':np.round(df,4), 
            'idf':np.round(idf,4), 'tf_idf':np.round(tf_idf,4)}


co = ['Oi\nBoa tarde e um ótimo domingo.\nQueria saber como faço para baixar o aplicativo. Tenho uma área é estou pensando em plantar. Minha área é de 220 equitares é já vem sendo cultivada por mais de 10 anos através de arrendamento. Mais estou criando coragem para eu mesmo plantar. Mais não tenho esperiencia no ramo. Queria ver se posso ter um acompanhamento tequinico para me assessorar nessa impreitada. Estava assistindo o Manual do Operador com o Allan é ele fez a propaganda deste canal de informações entre produtores. Desde já muito obrigado.', '']
gram = run(co)
print(gram[0])
print('-----------------------------------------------------------')
print(gram[1])
print('-----------------------------------------------------------')
print(gram[2])
print('-----------------------------------------------------------')
print(gram[3])
print('-----------------------------------------------------------')
print(gram[4])
print('-----------------------------------------------------------')
print(gram[5])