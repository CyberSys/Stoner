#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:36:09 2018

@author: wolf
"""

import dogma.program
PROGRAM_COMMANDS = ('list', 'load', 'unload','reload')
import re

class Plugin(dogma.program.Plugin):
    access = {
        'ev' : 1000,
        'join' : 80,
        'part' : 80,
        'shutdown' : 1000,
        'program' : 1000,
        'plugin' : 1000,
    }
    def __init__(self, client):
        super().__init__(client)
        #Plugin.__init__(self, client)


    def load(self, config=None, state=None):
        super().load(config, state)
        self.config = config


    def _event_INVITE(self, event):
        if event.network.getaccess(event.source) >= self.access['join']:
            event.network.join(event.text)


    def _command_join(self, event, args):
        event.network.join(args)


    def _command_part(self, event, args):
        event.network.part(args)


    def _command_shutdown(self, event, args):
        self.agent().shutdown()


    def _command_program(self, event, args):
        try:
            cmd, unique_id = args.split(None, 1)
        
        except ValueError:
            cmd, unique_id = args, None

        try:
            if cmd == 'list':
                event.reply(str(self.agent().programs.keys()))
    
            if cmd == 'load':
                config = self.agent().config_load(unique_id)
                if not config:
                    raise dogma.program.ProgramLoadError("No config file for %s" % unique_id)
                program = self.agent().program_import(
                    module=config["_module"],
                    unique_id=unique_id,
                    classname=config["_class"], 
                    config=config,
                    plugins=config.get('plugins')
                )

                program.init()
                event.reply("ok")

            elif cmd == "unload":
                self.agent().program_unload(unique_id)
                event.reply("ok")
            
            elif cmd == "reload":
                self.agent().program_reload(unique_id)
                event.reply("ok")

        except dogma.program.ProgramLoadError as msg:
            event.reply(f"**ProgramLoadError** `{msg}`")


    def _command_plugin(self, event, args):
        
        match = re.match(r' *(\S+) +(\S+)(?: (\S+))? *', args)
        if not match:
            event.reply(f"**BadInputError** Command syntax is 'plugin <cmd> <program> [<plugin>]`")
            return
        
        cmd, program, plugin = match.groups()

        if not cmd in PROGRAM_COMMANDS:
            event.reply(f"**BadInputError** {cmd} not in {PROGRAM_COMMANDS}`")
            return

        pro = self.uncle(program)
        if not pro:
            event.reply(f"**BadInputError** `can't {cmd} plugin for non-loaded program {program}`")
            return

        try:        
            if cmd == 'list':
                event.reply(str(self.parent.plugins.keys()))

            elif cmd == 'load':
                pro.plugin_import(plugin, pro.config.get('plugins', {}).get(plugin))
                event.reply("ok")

            elif cmd == "unload":
                pro.plugin_unload(plugin)
                event.reply("ok")

            elif cmd == "reload":
                pro.plugin_reload(plugin)
                event.reply("ok")

        except dogma.program.ProgramLoadError as msg:
            event.reply(f"**ProgramLoadError** `{msg}`")

