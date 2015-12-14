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

objects = []

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

def worker(filename):
    global sentcount, hpsent, hpclause, categories, artcount, nouncount
    artcount += 1
    global objects
    with open(filename, 'r', encoding='utf8') as f:
        s = json.load(f)

    for sent in s["sentences"]:
        sentcount += 1
        if "HP" in sent.keys():
            pass
            if "\n" in sent["text"]:
                continue

            try:
                for cat in s["data"]["categories"]:
                    categories[cat] += 1
            except KeyError:
                pass

            #print(s["data"]["title"])
            #print(sent["HP"])
            hpstart = min(sent["HP"]["start"])
            hpend = max(sent["HP"]["end"])

            words = sent["words"]

            for i in range(len(words)):
                if hpstart == words[i]["start"]:
                    locx = i
                if hpend == words[i]["end"]:
                    locy = i

            for i in range(len(words)):
                words[i]["locx"] = i - locx
                words[i]["locy"] = i - locy

            text =sent["text"]
            t = Text(text).tag_clauses()

            for elem in t['clauses']:
                start =elem["start"][0]
                end = elem["end"][0]

            if start <= hpstart and hpend <= end:
                if "S" in Text(sent["HP"]["lemmas"][0]).postags:
                    print(s["data"]["title"])
                    nouncount += 1
                    print(sent["HP"])
                    print(text[start:end])
                    print("locx:",locx,"locy:", locy)

                hpclause += 1

            else:
                hpsent += 1
                #print(sent["text"])

    return sentcount, hpsent

if __name__ == '__main__':

    #with multiprocessing.Pool(4) as pool: # pool of 48 processes
    walk = os.walk("new")
    fn_gen = itertools.chain.from_iterable((os.path.join(root, file)
                                                    for file in files)
                                                   for root, dirs, files in walk)
        #results_of_work = pool.map(worker,  [sent for sent in fn_gen]) # this does the parallel processing

    for filename in fn_gen:
        worker(filename)

    print("ARTIKLEID KOKKU", artcount )
    print("LAUSEID KOKKU", sentcount)
    print("HP LAUSEID", hpsent)
    print("HP CLAUSES", hpclause)
    print("NOUN CLAUSES", nouncount)
    print("ENIM HP+ LAUSEID SISALDAVAD KATEGOORIAD")

    n = 0

    for key, value in sorted(categories.items(), key=operator.itemgetter(1), reverse=True):
        print("%s: %i" % (key, value))
        n +=1
        if n == 20: break
