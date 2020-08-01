#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:18:18 2018

@author: wolf
"""

from disco.client import Client, ClientConfig
from disco.bot import Bot, BotConfig
import dogma.program



def get_level(self, actor):
    level = self.config.levels.get(str(actor.id), 0) # ugh. stupid json limitations.

    #if isinstance(actor, GuildMember):
    #    for rid in actor.roles:
    #        if rid in self.config.levels and self.config.levels[rid] > level:
    #            level = self.config.levels[rid]
    return level


class Program(dogma.program.Program):
    
    def __init__(self, agent):
        super().__init__(agent)
        self.client = None
        self.bot = None


    def load(self, config=None, state=None):
        super().load(config=config, state=state)

        config = ClientConfig()
        config.token = self.config.get('token')
        config.max_reconnects = 0
        self.client = Client(config)
        self.client.parent = self
        self.client.agent = self.agent

        self.bot = None
        bot_config = BotConfig()
        bot_config.commands_require_mention = False
        bot_config.commands_prefix = '.'
        
        bot_config.levels = self.config.get('access', {})
        
        bot_config.commands_level_getter  = get_level
        self.bot = Bot(self.client, bot_config)
        for plugin_mod, config in self.config.get('plugins').items():
            self.bot.add_plugin_module(plugin_mod, config)
        
        for name, plugin in self.bot.plugins.items():
            plugin.parent = self

        self.bot.agent = self.agent
        self.bot.parent = self

        self.me = self.client.api.users_me_get()


    def unload(self, state=None):
        state = super().unload(state)
        return state


    def run(self):
        (self.bot or self.client).run_forever()


    def notify(self, title, content):
        if not self.config.get("owner"):
            return

        user = self.client.api.users_get(self.config["owner"])
        if user:
            user.open_dm().send_message("%s : %s" % (title, content))

