# -*- coding: utf-8 -*-

from itertools import combinations,permutations
import estnltk.wordnet.wn as wn
from estnltk import Text
from collections import defaultdict
from pprint import pprint
import os.path
from multiprocessing import Pool
import multiprocessing
import sys
import time
import itertools
import json
import pickle
from time import time
sent_count = 0
hp_count = 0
#syn_hyper = {}

def hyper_level3(pospairs):
    syn_hyper = {}
    for key in pospairs:
        for lemma in pospairs[key]:
            for syn1, syn2 in lemma:
                #if not(syn1 in syn_hyper.keys()):
                h1 = []
                try:
                    hyp01 = syn1.hypernyms()
                    h1.append(hyp01[0])
                    hyp11 = hyp01[0].hypernyms()
                    h1.append(hyp11[0])
                    hyp21 = hyp11[0].hypernyms()
                    h1.append(hyp21[0])
                    #hyp31 = hyp21[0].hypernyms()
                    #h1.append(hyp31[0])
                except IndexError:
                    pass
                syn_hyper[syn1] = h1
                #if not(syn2 in syn_hyper.keys()):
                try:
                    h2 = []
                    hyp02 =  syn2.hypernyms()[0]
                    h2.append(hyp02)
                    hyp12 =  hyp02.hypernyms()[0]
                    h2.append(hyp12)
                    hyp22 = hyp12.hypernyms()[0]
                    h2.append(hyp22)
                    #hyp32 = hyp22.hypernyms()[0]
                    #h2.append(hyp32)
                except IndexError:
                    pass
                syn_hyper[syn2] = h2

    return syn_hyper


def hyper(text):
    global sent_count, hp_count
    WN_POS = {u'A',u'S',u'V',u'D'}

    words = text.words
    pos = text.postags
    lemmas_ = text.lemmas
    lemmas =[]
    for lemma in lemmas_:
        if "|" in lemma:
            lemma = lemma[:lemma.index("|")]
        lemmas.append(lemma)
    lemma_pos = zip(lemmas, pos)

    pos2lemmas = defaultdict(set)


    for lemma, pos in lemma_pos:
        if pos in WN_POS:
            pos2lemmas[pos].add(lemma)

    pos2pairs = dict()

    for pos in pos2lemmas:
        if len(pos2lemmas[pos]) > 1:
            combs = combinations(pos2lemmas[pos],2)
            pos2pairs[pos] = [comb for comb in combs]

    pos2pairs2 = {}

    for pos in pos2pairs:
        pairs_for_pos = []
        for lemma1, lemma2 in pos2pairs[pos]:
            pairs_for_synsets = set()
            synsets1 = wn.synsets(lemma1)
            synsets2 = wn.synsets(lemma2)
            pairs_for_pos.append([x for x in itertools.product(synsets1, synsets2)])
            #pairs_for_pos.append(pairs_for_synsets)

        pos2pairs2[pos] = pairs_for_pos

    #võtab sõnaraamatu tagastab 3 taset ülespoole mõlemal

    syn_hyper = hyper_level3(pos2pairs2)
    sent_count += 1
    objects = []
    for key in pos2pairs:
        for idx in range(len(pos2pairs2[key])):
            value = pos2pairs2[key][idx]
            try:
                for syn1, syn2 in value:
                    if syn1 in syn_hyper[syn2]:
                        obj = {}
                        hp_count +=1
                        print("HP" , syn_hyper[syn2].index(syn1)+1)
                        print(syn_hyper[syn2])
                        lemma1, lemma2 = pos2pairs[key][idx]
                        print("WORDS" , words[lemmas.index(lemma1)], words[lemmas.index(lemma2)],)
                        print("LEMMAS" , lemma1, lemma2)
                        print(text)
                        obj["type"] = "HP" + str(syn_hyper[syn2].index(syn1)+1)
                        obj["lemmas"] = lemma1, lemma2
                        obj["start"] = words[lemmas.index(lemma1)]["start"], words[lemmas.index(lemma2)]["start"]
                        obj["end"] = words[lemmas.index(lemma1)]["end"], words[lemmas.index(lemma2)]["end"]
                        return obj
                    elif syn2 in syn_hyper[syn1]:
                        obj = {}
                        hp_count +=1
                        print("HP" , syn_hyper[syn1].index(syn2)+1)
                        print(syn_hyper[syn1])
                        lemma1, lemma2 = pos2pairs[key][idx]
                        print("WORDS" , words[lemmas.index(lemma1)], words[lemmas.index(lemma2)],)
                        print("LEMMAS" , lemma2, lemma1)
                        print(text)
                        obj["type"] = "HP" + str(syn_hyper[syn1].index(syn2)+1)
                        obj["lemmas"] = lemma2, lemma1
                        obj["start"] = words[lemmas.index(lemma1)]["start"], words[lemmas.index(lemma2)]["start"]
                        obj["end"] = words[lemmas.index(lemma1)]["end"], words[lemmas.index(lemma2)]["end"]
                        return obj

            except IndexError:
                continue


    print(sent_count)
    #print("len(s_h)", len(syn_hyper))
    print("HP protsent", (hp_count/sent_count)*100)

    return None
def writer(s):
    with open(r"new5/"+s["data"]["title"]+".txt", 'w', encoding='utf8') as f:
        json.dump(s, f)


def worker(filename):
    with open(filename, 'r', encoding='utf8') as f:
        s = json.load(f)
    text = Text(s).split_by_sentences()
    for sent in text:
        if len(sent.text) > 500:
            continue
        new_sent = hyper(sent)
        if not (new_sent == None):
            sent['HP'] = new_sent
    s['sentences'] = text
    writer(s)


if __name__ == '__main__':
    start = time()
    with multiprocessing.Pool(8) as pool: # pool of 48 processes
        walk = os.walk("/home/andresmt/Text1/wiki/wikidump/wikitext5")
        fn_gen = itertools.chain.from_iterable((os.path.join(root, file)
                                                    for file in files)
                                                   for root, dirs, files in walk)

        pool.map(worker,  [sent for sent in fn_gen]) # this does the parallel processing
    #for f in fn_gen:
    #    worker(f)

    #pickle.dump(syn_hyper, open("syn_hyper.p", "wb"))

    #print("Duration", time()- start )