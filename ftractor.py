

def ft(words):

    length = len(words)
    feature_vector = {"length":length}

    distance = abs(words[0]["locx"] - words[0]["locy"])
    feature_vector["distance"] = distance



    LOCX = [x for x in words if x["locx"] == 0][0]
    LOCY = [x for x in words if x["locy"] == 0][0]
#counts

    verbcount = len([x for x in words if x["analysis"][0]["partofspeech"] == "V"])
    maarsonacount = len([x for x in words if x["analysis"][0]["partofspeech"] == "D"])
    omadus_algvcount = len([x for x in words if x["analysis"][0]["partofspeech"] == "A"])
    kaasscount = len([x for x in words if x["analysis"][0]["partofspeech"] == "K"])
    namecount = len([x for x in words if x["analysis"][0]["partofspeech"] == "H"])

#postag position

    x1verb = 0
    x2verb = 0
    y1verb = 0
    y2verb = 0

    for word in words:

        if not(x1verb):
            x1verb = 1 if word["locx"] == 1 and word["analysis"][0]["partofspeech"] == "V" else 0

        if not(x2verb):
            x2verb = 1 if word["locx"] == 2 and word["analysis"][0]["partofspeech"] == "V" else 0

        if not(y1verb):
            y1verb = 1 if word["locy"] == 1 and word["analysis"][0]["partofspeech"] == "V" else 0

        if not(y2verb):
            y2verb = 1 if word["locy"] == 2 and word["analysis"][0]["partofspeech"] == "V" else 0



    feature_vector["x1verb"] = x1verb
    feature_vector["x2verb"]= x2verb

    feature_vector["y1verb"]=y1verb
    feature_vector["y2verb"]=y2verb

    return feature_vector
