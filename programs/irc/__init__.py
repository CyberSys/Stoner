#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: wolf
"""
import sys
import builtins as exceptions # python 3 hack
#import exceptions
import irclite
from dogma.program import PlugableProgram

class Program(PlugableProgram, irclite.Client):
    def __init__(self, parent):
        PlugableProgram.__init__(self, parent)
        irclite.Client.__init__(self)

    def load(self, config=None, state=None):
        PlugableProgram.load(self, config, state)
        irclite.Client.load(self, config)


    def unload(self, state=None):
        irclite.Client.shutdown(self)
        state = PlugableProgram.unload(self, state)
        return state


    def init(self):
        irclite.Client.init(self)
        PlugableProgram.init(self)


    def run(self):
        irclite.Client.run(self)


    def handle_command(self, command, args, event):
        for plugin in self.plugins.values():
            callback = getattr(plugin, '_command_%s' % command, None)
            if not callback:
                continue
            if event.network.getaccess(event.source) < getattr(plugin, 'access', {}).get(command, 0):
                continue
            ### general catch all, bad stuff
            try:
                callback(event, args)
            except:
                et, ev, etr = sys.exc_info()
                if et == exceptions.SystemExit:
                    exit()
                event.reply(f'{et} {ev}')


    def handle_event(self, event):
        for plugin in self.plugins.values():
            callback = getattr(plugin, '_event_%s' % event.type, None)
            if not callback:
                continue
            ### general catch all, bad stuff
            try:
                callback(event)
            except:
                et, ev, etr = sys.exc_info()
                if et == exceptions.SystemExit:
                    exit()
