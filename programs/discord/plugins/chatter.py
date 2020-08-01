#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 15:29:24 2020

@author: wolf
"""
import re
from disco.bot import Plugin
text_filter = re.compile(r"[^A-Za-z0-9,\./ \~\!\@\#\$\%\^\&\*\(\)\_\-\+\=\|\[\]\{\}\:]")


class ChatterPlugin(Plugin):
    def agent(self):
        return self.parent.agent

    def uncle(self, unique_id):
        return self.bot.client.agent.programs.get(unique_id)


    def train_chatter(self, event):
        chatter = self.uncle('chatter')
        if not chatter:
            return None

        for block in re.findall('```(.+?)```', event.content, re.S):
            lines = block.splitlines()
            questions, answers = [], []
            for line in lines:
                if line.startswith('Q:'):
                    questions.append(line[2:].strip())

                elif line.startswith('A:'):
                    answers.append(line[2:].strip())

            chatter.train_question(questions, answers)

        event.reply("Ok.")


    def get_chatter(self, event):
        chatter = self.uncle('chatter')
        if not chatter:
            return None

        text = re.sub('(@!?([0-9]+))', '', event.content)
        text = re.sub('(?:https?|ftps?)\:\/\/[^\s]*', '', text)
        text = [text_filter.sub('',  t) for t in text.splitlines()]
        min_confidence = chatter.config['min_response_confidence']
        default = []
        if event.is_mentioned(self.bot.parent.me.id) or event.guild is None:
            min_confidence = chatter.config['min_response_confidence_mentioned']
            default = ("Sorry you lost me.", "no comment.")

        for line in text:
            chatter.spawn_response(
                text=line, 
                min_confidence=min_confidence, 
                default=default,
                callback=self.chatter_reply,
                event=event
                )
        
        return True


    def chatter_reply(self, reply, event, **kwargs):
        if not reply:
            return

        event.reply(reply.text)


    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.author.id == self.bot.parent.me.id: # ignore ourself.
            return

        if event.author.bot: # we could just use this to ingore ourself...
            return

        access = self.bot.get_level(event.author)
        if event.content[0] == self.bot.config.commands_prefix:
            if access == 1000 and event.content[1:6] == 'learn':
                self.train_chatter(event)

            return

        if event.guild is None and not access:
            return

        if "```" in event.content: 
            return
        
        server_whitelist = self.config['server_whitelist']
        channel_whitelist = self.config['channel_whitelist']
        channel_blacklist = self.config['channel_blacklist']

        if event.channel and event.channel.id in channel_blacklist:
            return

        if event.guild and (event.guild.id not in server_whitelist and event.channel.id not in channel_whitelist):
            return

        self.get_chatter(event)


