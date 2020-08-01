#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 07:21:17 2020

@author: wolf
"""
import random
import re
import logging
from collections import namedtuple
import spacy
from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
from nltk.corpus import wordnet

RE_QUERIES = {
    'examples' : re.compile(r'^ *(?:what +are|name|give +me|explain)(?: +some| +a few)?(?: +different)? +(?:meanings|examples) +(?:of|for)(?: +a)? +(\w+) *\?? *$'),
    'what is' : re.compile(r"^ *what(?:'?s| +are| +is)(?: +a| +the)? +(\w+)(?: +(?:in +the +context +of|refering +to|talking +about|as +a) +(\w+))? *\?? *$"),
    'is a' : re.compile(r"^ *(?:are|is)(?: +a)? +(\w+)(?: +a| +the +same +as| +similar to| +a +type +of)? +(\w+)\?? *$")
}
Query = namedtuple("Query", ('type', 'match'))
logger = logging.getLogger(__name__)

class Relation:
    def __init__(self, this, other):
        self.this = this
        self.other = other
        self.depth = this.min_depth() - other.min_depth()
        self.common = this.lowest_common_hypernyms(other)
        self.path = this.path_similarity(other)
        if not self.path:
            self.path = 0
        self.score = 0 # over all probability score

        sim_score = 0
        if other in self.common:
            sim_score = 1

        self.score = (self.path + sim_score) / 2


def vague_relation(sub, ref):
    """given 2 vague words as input finds the best relation between them: dog and cat will return the
    nouns for the dog and cat animals, while dog and follow return the verbs to give chase."""
    sets = wordnet.synsets
    relist = [Relation(s, r) for r in sets(ref) for s in sets(sub)]
    if not relist:
        return None
    return max(relist, key=lambda x: x.score)


def random_lemma(syn, count=1):
    """returns N random entries from a synset"""
    if isinstance(syn, str):
        syn = wordnet.synset(syn)
    
    names = syn.lemma_names()
    if len(names) < count:
        count = len(names)
    if not count:
        return None

    return random.sample(names, count)


def solve_isa(subject, context):
    # this assumes a object|context relationship (is gold metal, is a dog a animal, etc)
    # this does not work for attributes (is a ball round)
    relate = vague_relation(subject, context)
    if not relate:
        return None

    if relate.other in relate.common:
        return "Yes - (%s similarity)" % round(relate.score, 3)

    if relate.this in relate.common:
        return 'No, but %s is %s' % (context, subject)

    return 'No.'


def join_description(syn):
    lemma = ', '.join(random_lemma(syn, count=random.randint(1, 5)))
    return "%s (%s): %s" % (syn.lexname().replace('.', ', '), lemma, syn.definition())

    
def solve_examples(subject):
    sets = wordnet.synsets(subject)
    if not sets:
        return None
    return '\n'.join([join_description(syn) for syn in sets])



    
def solve_what_is(subject, context):
    if context:
        relate = vague_relation(subject, context)
        if not relate:
            return None

        syn = relate.this

    else:
        sets = wordnet.synsets(subject)
        if not sets:
            return None

        if len(sets) > 1:
            return 'Please specify a context. Multiple meanings exist.'

        syn = sets[0]

    return join_description(syn)


class QueryLogicAdapter(LogicAdapter):

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.nlp = spacy.load("en_core_web_sm")
        self.query_type = None
        self.query_match = None
        self.cache = {}

    def can_process(self, statement):
        query = Query(None, None)
        for qtype, regex in RE_QUERIES.items():
            match = regex.match(statement.text)
            if match:
                query = Query(qtype, match)
                break

        self.cache[statement.text] = query
        return query.type is not None


    def process(self, statement, additional_response_selection_parameters):

        result = Statement("I have no idea.")
        result.confidence = 0.9
        if statement.text not in self.cache: # this should never happen?
            return result

        query = self.cache[statement.text]
        self.cache = {}

        text, confidence = None, 0
        if query.type == 'is a':
            text, confidence = solve_isa(*query.match.groups()), 1.0

        elif query.type == 'what is':
            text, confidence = solve_what_is(*query.match.groups()), 1.0

        elif query.type == 'examples':
            text, confidence = solve_examples(*query.match.groups()), 1.0
            

        if text:
            result = Statement(text)
            result.confidence = confidence
            
        return result
