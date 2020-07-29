# -*- coding: utf-8 -*-

from disco.bot import Plugin
import re
text_filter = re.compile(r"[^A-Za-z0-9,\./ \~\!\@\#\$\%\^\&\*\(\)\_\-\+\=\|\[\]\{\}]")


class IRCBridge(Plugin):
    def load(self, ctx):
        super(IRCBridge, self).load(ctx)
        self.channel_map = {}
        self.update_channels()
    
    def update_channels(self):
        self.channel_map = {}

        irc = self.bot.client.agent.programs.get('irc')
        if not irc:
            return
        
        bridge = irc.config.get('plugins',{}).get('discord_bridge', {}).get('connect',{})
        for network in bridge:
            for channel, id in bridge[network].items():
                self.channel_map[id] = (network, channel)
        


    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.author.id == self.bot.parent.me.id: # ignore ourself.
            return
        
        if not event.channel_id or not event.channel_id in self.channel_map:
            return
        mapping = self.channel_map[event.channel_id]
                
        irc = self.bot.client.agent.programs.get('irc')
        if not irc or not mapping[0] in irc.networks:
            return
        net = irc.networks[mapping[0]]
        text = event.content.splitlines()
        name = text_filter.sub('', event.author.username)
        if not name:
            name = event.author.id
        text = ["%s (discord): %s" % (name, text_filter.sub('',  t)) for t in text]
        net.privmsg(mapping[1], text)
        
