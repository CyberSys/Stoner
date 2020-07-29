# -*- coding: utf-8 -*-

import dogma.program
import re
text_filter = re.compile(r"[^A-Za-z0-9,\./ \~\!\@\#\$\%\^\&\*\(\)\_\-\+\=\|\[\]\{\}]")

class Plugin(dogma.program.Plugin):
    def init(self):
        disco = self.uncle('discord')
        if not disco:
            return
        bridge = disco.bot.plugins.get('IRCBridge')
        if not bridge:
            return
        bridge.update_channels()



    def _event_PRIVMSG(self, event):
        if not event.chan:
            return 

        if event.nick == event.network.nick:
            return

        if event.text.startswith(event.network.config["command_prefix"]):
            return

        id = self.config['connect'].get(event.network.name, {}).get(event.chan)
        disco = self.uncle('discord')
        if not id or not disco:
            return

        text = text_filter.sub("", event.text)
        disco.client.api.channels_messages_create(id, "**%s** *(irc)*: `%s`" % (event.nick, text))


