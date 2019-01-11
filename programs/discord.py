#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:18:18 2018

@author: wolf
"""
from disco.client import Client, ClientConfig
from disco.bot import Bot, BotConfig
from disco.util.logging import setup_logging
import logging
from dogma.program import Program
#from dogma import Program

class DiscoBot(Program):
    def __init__(self, agent):
        Program.__init__(self, agent)
        self.client = None
        self.bot = None

    def load(self, config=None, state=None):
        Program.load(self, config, state)
        config = ClientConfig()
        config.token = self.config.get('token')
        config.max_reconnects = 0
        setup_logging(level=getattr(logging, config.log_level.upper()))
        self.client = Client(config)
        self.client.parent = self

        self.bot = None
        bot_config = BotConfig()
        bot_config.commands_require_mention = False
        bot_config.commands_prefix = '.'
        bot_config.plugins = self.config.get('plugins', [])
        self.bot = Bot(self.client, bot_config)

    def unload(self, state=None):
        #TODO: proper disconnect and shutdown for discord
        state = Program.unload(self, state)
        return state

    def run(self):
        (self.bot or self.client).run_forever()

