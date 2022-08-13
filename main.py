from typing import Union, List, Dict
from fastapi import FastAPI
from fastapi.param_functions import Depends
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
from collections import OrderedDict
from detoxify import Detoxify
import re

app = FastAPI()


pipe_is_hate_prod = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/dehatebert-mono-english"), \
                    tokenizer=AutoTokenizer.from_pretrained("Hate-speech-CNERG/dehatebert-mono-english"), \
                    return_all_scores=True)

pipe_is_hate_bert = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain-rationale-two"), \
                    tokenizer=AutoTokenizer.from_pretrained("Hate-speech-CNERG/bert-base-uncased-hatexplain-rationale-two"), \
                    return_all_scores=True)

pipe_is_hate_dberta = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("stevenlx96/distilbert-base-uncased-finetuned-hated"), \
                    tokenizer=AutoTokenizer.from_pretrained("stevenlx96/distilbert-base-uncased-finetuned-hated"), \
                    return_all_scores=True)

pipe_is_hate_hbert = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("GroNLP/hateBERT"), \
                    tokenizer=AutoTokenizer.from_pretrained("GroNLP/hateBERT"), \
                    return_all_scores=True)

pipe_sentiment = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment"), \
                    tokenizer=AutoTokenizer.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment"), \
                    return_all_scores=True)

pipe_intent = TextClassificationPipeline(
                    model=AutoModelForSequenceClassification.from_pretrained("pysentimiento/bertweet-hate-speech"), \
                    tokenizer=AutoTokenizer.from_pretrained("pysentimiento/bertweet-hate-speech"), \
                    return_all_scores=True)
"""
Initialize any other model pipelines here
"""

lgbtq_terms = open("lgbtqterms.txt", "r")
bad_words = open("badwordlist.txt", "r")
lgbtq_list = lgbtq_terms.read().split("\n")
bad_words_list = bad_words.read().split("\n")
regex = re.compile('[^a-zA-Z]')

# HATE FIRST, NON_HATE SECOND

# Query BERT base model
# Labels: NORMAL = NON_HATE, ABUSIVE = HATE
@app.get("/ishatebbert")
def is_hate_bert(text: str):
    text = text.lower()
    output = pipe_is_hate_bert(text)[0]
    returndict = {}
    for prediction in output:
        if prediction.get('label') == 'NORMAL':
            returndict['NON_HATE'] = prediction.get('score')
        else: 
            returndict['HATE'] = prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Query the ensemble model of distillBERT and roBERTa
# Labels: LABEL_2 = NON_HATE, LABEL_0 + LABEL_1 = HATE
@app.get("/ishatedistillberta")
def is_hate_dberta(text: str):
    text = text.lower()
    output = pipe_is_hate_dberta(text)[0]
    returndict = {}
    for prediction in output:
        if prediction.get('label') == 'LABEL_2':
            returndict['NON_HATE'] = prediction.get('score')
        else: 
            returndict['HATE'] = returndict.get('HATE', 0) + prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Query the hateBERT model
# Labels: LABEL_0, LABEL_1
@app.get("/ishatehbert")
def is_hate_hbert(text: str):
    text = text.lower()
    output = pipe_is_hate_hbert(text)[0]
    returndict = {}
    for prediction in output:
        if prediction.get('label') == 'LABEL_1':
            returndict['NON_HATE'] = prediction.get('score')
        else: 
            returndict['HATE'] = returndict.get('HATE', 0) + prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Used when false negative results are more important than true positives
# Blending models and fitting to both
# This model can be edited to meet any standard (in confusion matrix)
@app.get('/ishateall')
def is_hate_all(text: str):
    text = text.lower()
    output = pipe_is_hate_prod(text)[0] 
    output2 = pipe_is_hate_dberta(text)[0]
    # output3 = pipe_is_hate_hbert(text)[0] 
    returndict = {}
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    for prediction in output2:
        if prediction.get('label') == 'LABEL_2':
            returndict['NON_HATE'] = prediction.get('score')
        else: 
            returndict['HATE'] = returndict.get('HATE', 0) + prediction.get('score')
    """
    Add your own model here if required
    """
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Applies ensembling and blending to models to determine the best accuracy/f1
# Labels: HATE, NON_HATE
@app.get("/ishate")
def is_hate(text: str):
    text = text.lower()
    output = pipe_is_hate_prod(text)[0]
    returndict = {}
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Checks if speech is homophobia or not
# Boolean endpoint function: Only returns True or False
@app.get("/ishomophobia")
def is_hate_prod(text: str):
    text = text.lower()
    islgbtq = False
    output = pipe_is_hate_prod(text)[0]
    returndict = {}
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    for word in text.split(' '):
        for lgbtq_word in lgbtq_list:
            if lgbtq_word in regex.sub('', word):
                islgbtq = True
                break
    if (returndict.get('HATE') > returndict.get('NON_HATE') and islgbtq):
        return {'ishomophobia' : True}
    return {'ishomophobia' : False}

# Checks if the text has swear words
# If it does, the API removes it, and returns the censored text
@app.get("/isswearing")
def is_swearing(text: str):
    text = text.lower()
    isswearing = False
    for word in text.split(' '):
        for bad_word in bad_words_list:
            if bad_word in regex.sub('', word):
                isswearing = True
                text = text.replace(word, '*' * len(word))
    return {'isswearing' : isswearing, 'text': text}

# Get sentiment of text
# Labels: Negative, Neutral, Positive
@app.get("/sentiment")
def sentiment(text: str):
    text = text.lower()
    output = pipe_sentiment(text)[0]
    returndict = {}
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Get intent of text
# Labels: aggressive, hateful, targeted
@app.get('/intent')
def intent(text: str):
    text = text.lower()
    output = pipe_intent(text)[0]
    returndict = {}
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    returndict = dict(OrderedDict(sorted(returndict.items())))
    return returndict

# Get toxicity of text
# Slower due to model being more robust
@app.get("/toxicity")
def toxicity(text: str):
    text = text.lower()
    results = Detoxify('unbiased').predict(text)
    returndict = {}
    for key, value in results.items():
        returndict[key] = value.item()
    return returndict

# Return all possible labels (may take longer to run)
@app.get("/returnlabels")
def returnall(text: str):
    text = text.lower()
    # Add production hate speech labels
    returndict = {}
    output = pipe_is_hate_prod(text)[0]
    for prediction in output:
        returndict[prediction.get('label')] = prediction.get('score')
    # Add sentiment labels
    output2 = pipe_sentiment(text)[0]
    for prediction in output2:
        returndict[prediction.get('label')] = prediction.get('score')
    # Add intent labels
    output3 = pipe_intent(text)[0]
    for prediction in output3:
        if prediction.get('label') == 'hateful':
            returndict[prediction.get('label')] = prediction.get('score')
    # Add toxicity labels
    results = Detoxify('unbiased').predict(text)
    for key, value in results.items():
        returndict[key] = value.item()
    isswearing = False
    # Add swearing labels
    for word in text.split(' '):
        for bad_word in bad_words_list:
            if bad_word in regex.sub('', word).lower():
                isswearing = True
                text = text.replace(word, '*' * len(word))
    returndict['isswearing'] = isswearing
    islgbtq = False
    for word in text.split(' '):
        for lgbtq_word in lgbtq_list:
            if regex.sub('', word).lower() in lgbtq_list:
                islgbtq = True
                break
    if (returndict.get('HATE') > returndict.get('NON_HATE') and islgbtq):
        returndict['ishomophobia'] = True
    else:
        returndict['ishomophobia'] = False
    # Return the combination of all labels
    return returndict   