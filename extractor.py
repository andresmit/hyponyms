# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import json
__author__ = 'Andres'
from estnltk import Text
from pprint import pprint
import pickle
import os
import itertools
import multiprocessing
from collections import defaultdict
import operator
import numpy as np
from ftractor import ft

objects = []

two_nouns_clause=0
artcount = 0
sentcount = 0
hpsent = 0
hpclause = 0
nouncount = 0

categories = defaultdict(int)

def str2clauses(t):
    result = []
    t = " ".join(x for x in Text(t).lemmas)
    text = Text(t)
    text.tag_clauses()
    for elem in text['clauses']:
        r = []
        start =elem["start"]
        end = elem["end"]
        r = [x['text'] for x in (Text(t[start[0]:end[0]]).words)]
        result.append(r)
    return result

def ftraktor(filename):
    #for every HP+ sentence in the file one HP-

    global sentcount, hpsent, hpclause, categories, artcount, nouncount, objects, two_nouns_clause

    artcount += 1
    with open(filename, 'r', encoding='utf8') as f:
        s = json.load(f)

    for sent in s["sentences"]:
        sentcount += 1
        if "HP" in sent.keys():
            if "\n" in sent["text"]:
                continue

            try:
                for cat in s["data"]["categories"]:
                    categories[cat] += 1
            except KeyError:
                pass

            text = sent["text"]
            t = Text(text).tag_clauses()

            hpstart = min(sent["HP"]["start"])
            hpend = max(sent["HP"]["end"])

            words = t["words"]

            for i in range(len(words)):
                if hpstart == words[i]["start"]:
                    locx = i
                if hpend == words[i]["end"]:
                    locy = i

            for i in range(len(words)):
                words[i]["locx"] = i - locx
                words[i]["locy"] = i - locy

            #Feature 1 locy - locx
            #Feature 2 locx +1 pos == Verb binaarne
            #Feature 3 locx +2 pos == S binaarne



            for idx, elem in enumerate(t['clauses']):
                start =elem["start"][0]
                end = elem["end"][0]

                if start <= hpstart and hpend <= end:

                    #kas hüponüümia on nimisõnade vahel



                    #kas osalauses on kaks nimisõna

                    clause = Text(t.text[start:end])

                    nouns = [x for x in clause.analysis if x[0]['partofspeech'] == "S"]

                    if len(nouns) == 2:
#                        continue
#                    else:
                        two_nouns_clause += 1


                        features = ft([x for x in words if x["clause_index"] == idx])


                    if "S" in Text(sent["HP"]["lemmas"][0]).postags:
                        #print(s["data"]["title"])
                        nouncount += 1
                        #print(sent["HP"])
                        #print("OSALAUSES, nimisõnad:", text[start:end])

                    hpclause += 1

                else:
                    hpsent += 1
                    #print(sent["text"])

    return sentcount, hpsent

if __name__ == '__main__':

    #with multiprocessing.Pool(4) as pool: # pool of 48 processes
    walk = os.walk("wikitext")
    fn_gen = itertools.chain.from_iterable((os.path.join(root, file)
                                                    for file in files)
                                                   for root, dirs, files in walk)
        #results_of_work = pool.map(worker,  [sent for sent in fn_gen]) # this does the parallel processing

    for filename in fn_gen:
        ftraktor(filename)

    print("ARTIKLEID KOKKU", artcount )
    print("LAUSEID KOKKU", sentcount)
    print("HP LAUSEID", hpsent)
    print("HP CLAUSES", hpclause)
    print("NOUN CLAUSES", nouncount)
    print("2 NOUN CLAUSES", two_nouns_clause)
    print("ENIM HP+ LAUSEID SISALDAVAD KATEGOORIAD")

    n = 0

    for key, value in sorted(categories.items(), key=operator.itemgetter(1), reverse=True):
        print("%s: %i" % (key, value))
        n +=1
        if n == 20: break
