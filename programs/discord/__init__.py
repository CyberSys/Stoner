#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 15:18:18 2018

@author: wolf
"""

import logging
from disco.client import Client, ClientConfig
from disco.bot import Bot, BotConfig
import dogma.program

logger = logging.getLogger(__name__)


class Program(dogma.program.Program):

    def __init__(self, agent):
        super().__init__(agent)
        self.client = None
        self.bot = None
        self.me = None


    def load(self, config=None, state=None):
        super().load(config=config, state=state)

        conf = ClientConfig()
        conf.token = self.config.get('token')
        conf.max_reconnects = 0
        self.client = Client(conf)
        self.client.parent = self
        self.client.agent = self.agent

        self.bot = None
        bot_config = BotConfig()
        bot_config.commands_require_mention = False
        bot_config.commands_prefix = self.config.get('command_prefix', '.')

        bot_config.levels = self.config.get('access', {})

        bot_config.commands_level_getter = self.level_getter
        self.bot = Bot(self.client, bot_config)

        for unique_id, pconf in self.config.get('plugins').items():
            if pconf is None:
                pconf = {}

            pconf.setdefault("_autoload", True)
            pconf.setdefault("_module", unique_id)
            if not pconf["_autoload"]:
                continue

            self.bot.add_plugin_module(pconf["_module"], pconf) #TODO: replace

        for _, plugin in self.bot.plugins.items():
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
        if "owner" in self.config:
            return

        user = self.client.api.users_get(self.config["owner"])
        if user:
            user.open_dm().send_message("%s : %s" % (title, content))


    def is_me(self, actor):
        return (actor.id == self.me.id)


    def is_owner(self, actor):
        return ('owner' in self.config and actor.id == self.config['owner'])


    @staticmethod
    def level_getter(client, actor):
        # replacement for disco.py's access level check. limited since its only passing 'actor'
        # only need this for the bot's .commands anyways. Ideally should eventually replace disco's
        # .command system entirely
        level = client.config.levels.get(str(actor.id), 0)
        return level

    @staticmethod
    def check_access(plugin, event, level=0, dm_level=0, allow_dm=True, allow_bots=False, require_whitelists=False):
        # this should use a role based system instead (note: custom defined roles, not discord server roles)
        if plugin.parent.is_me(event.author): # ignore ourself
            return False

        if (not allow_bots and event.author.bot) or not event.content:
            return False

        # seems weird to get access this way, since its calling the static method level_getter above.
        access = plugin.bot.get_level(event.author)

        logger.debug("Checking access level %s >= %s for %s", access, level, str(plugin))        
        
        if event.guild:
            logger.debug("Channel: %s", event.channel.id)        
            if access < level:
                return False

            config = plugin.config if plugin.config else {}
            server_whitelist = config.get('server_whitelist', [])
            channel_whitelist = config.get('channel_whitelist', [])
            channel_blacklist = config.get('channel_blacklist', [])

            # check channel blacklists
            if event.channel.id in channel_blacklist:
                return False

            if require_whitelists and (event.guild.id not in server_whitelist
                                       and event.channel.id not in channel_whitelist):
                return False
            logger.debug("allowing channel access")            
            return True

        if plugin.parent.is_owner(event.author):
            logger.debug("allowing owner DM access")
            return True

        logger.debug("DM access result: %s", (allow_dm is True and access < level))

        return (allow_dm is True and access < level)

