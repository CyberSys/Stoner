#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 19:39:45 2020

@author: wolf
"""
import random
import importlib
import logging
import gevent
import chatterbot
import chatterbot.response_selection
from chatterbot.tagging import PosLemmaTagger
from chatterbot.conversation import Statement
from dogma.program import PlugableProgram
import programs.chatter.logic as logic
#from chatterbot.trainers import ListTrainer
#from chatterbot.response_selection import get_most_frequent_response, get_random_response, get_first_response
logger = logging.getLogger(__name__)


class Program(PlugableProgram):
    def __init__(self, parent):
        super().__init__(parent)
        self.responders = []
        self.bot = None

    def load(self, config=None, state=None):
        super().load(config=config, state=state)
        importlib.reload(logic)
        # set our bot default
        config.setdefault('min_response_confidence', 0.9)
        config.setdefault('min_response_confidence_mentioned', 0.3)
        config.setdefault('max_responders', 5)
        config.setdefault('persona', 'Stoner')
        config.setdefault('read_only', True)
        config.setdefault('storage_adapter', 'chatterbot.storage.SQLStorageAdapter')
        config.setdefault('database_uri', 'sqlite:///chatter.sqlite3')
        config.setdefault('preprocessors', [])
        config.setdefault('logic_adapters', [
            {
                "import_path" : "programs.chatter.logic.QueryLogicAdapter"
            },
            {
                "import_path" : "chatterbot.logic.BestMatch",
                "statement_comparison_function" : "chatterbot.comparisons.SpacySimilarity",
                "response_selection_method" : "get_random_response"
            }
            ])

        for adapter in config['logic_adapters']:
            response_selection_method = adapter.get('response_selection_method')
            if type(response_selection_method) != str:
                continue

            if hasattr(chatterbot.response_selection, response_selection_method):
                # this needs some work. it limits the methods to the chatterbot.response_selection module
                adapter['response_selection_method'] = getattr(chatterbot.response_selection, response_selection_method)
            else:
                logger.error('Invalid response_selection_method %s, using default', response_selection_method)
                del config['response_selection_method']

        self.bot = chatterbot.ChatBot(
            config['persona'],
            read_only=config['read_only'],
            storage_adapter=config['storage_adapter'],
            database_uri=config['database_uri'],
            preprocessors=config['preprocessors'],
            logic_adapters=config['logic_adapters']
            )


    def run(self):
        while True:
            # Nothing to be done (for now)
            gevent.sleep(0.01)


    def spawn_response(self, **kwargs):
        if len(self.responders) >= self.config['max_responders']:
            return
        self.responders.append(gevent.spawn(self._responder, **kwargs))


    def _responder(self, callback, **kwargs):
        reply = self.get_response(**kwargs)
        try:
            self.responders.remove(gevent.getcurrent())
        except ValueError:
            pass

        callback(reply, **kwargs)


    def get_response(self, text, min_confidence=0.9, default=None, **kwargs):

        response = self.bot.get_response(text)
        if response.confidence >= min_confidence:
            return response

        if not default:
            return None

        try:
            response = Statement(random.choice(default))
            response.confidence = 0

        except TypeError:
            pass

        return response


    def train_question(self, questions, answers):
        if isinstance(answers, str):
            answers = [answers]

        if isinstance(questions, str):
            questions = [questions]

        logger.info('Adding questions: %s', questions)
        logger.info('Adding answers: %s', answers)

        tagger = PosLemmaTagger(language=self.bot.storage.tagger.language)
        for q in questions:
            question = Statement(
                text=q,
                in_response_to=None,
                conversation='training',
                )

            for preprocessor in self.bot.preprocessors:
                question = preprocessor(question)

            question.search_text = tagger.get_text_index_string(question.text)
            # bypass learn_response when adding are questions. stupid function
            # automatically tries to tag the in_response_to field with the previous
            # question from the conversation
            self.bot.storage.create(**question.serialize())
            for reply in answers:
                statement = Statement(
                    text=reply,
                    in_response_to=question.text,
                    conversation='training',
                )

                for preprocessor in self.bot.preprocessors:
                    statement = preprocessor(statement)

                statement.search_text = tagger.get_text_index_string(statement.text)
                statement.search_in_response_to = question.search_text
                statement.persona = "bot:Eugene"
                self.bot.learn_response(statement, question)


    def train(self, *args):
        from chatterbot.trainers import ChatterBotCorpusTrainer
        trainer = ChatterBotCorpusTrainer(self.bot)

        trainer.train(*args)


    def propogate(self, command, data):
        if command == 'rehash':
            pass
