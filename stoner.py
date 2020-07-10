#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StereoTypical Ordinary Normal Everyday Robot

A example of using the dogma framework, as used in the ORGM discord/irc bot.
This example uses several 'dogma programs' (located in the programs directory):

discord - a discord bot component, using disco-py
irc - a minimal irc client, using irclite
pz - a component that uses pyZomboid to load and execute Project Zomboid's lua files
wsgi - a minimal wsgi web server, capable of serving dynamic or static files


Created on Sat Nov  3 10:29:59 2018

@author: wolf
"""

from gevent import monkey
monkey.patch_all()
import os
import json

import dogma
#dog = dogma.Agent()
#dog.config_dir = "conf"
#dog.program_directory = "programs"

class Stoner(dogma.Agent):
    config_dir = "config"
    config_ext = ".json"
    program_directory = "programs"
    
    def config_load(self, program_name):
        fi = open('%s/%s%s' % (self.config_dir, program_name, self.config_ext)) # TODO: exception catching
        print("Reading Config: %s" % program_name)
    
        try:
            config = json.load(fi) # TODO: exception catching
        except json.decoder.JSONDecodeError as msg:
            print("json.decoder.JSONDecodeError: %s" % msg)
        fi.close()
        if config is None:
            return
        
        if not "_module" in config:
            config["_module"] = "%s.%s" % (self.program_directory, program_name)
    
        if not "_class" in config:
            config["_class"] = "Program"
        return config


    def init(self):
        for file in os.listdir(self.config_dir): 
            if not file.endswith(self.config_ext):
                continue
            program_name = os.path.splitext(file)[0]
            config = self.config_load(program_name)
            if config is None:
                continue    
        
            if not config.get("_autoload", False):
                continue
            
            self.program_import(
                module=config["_module"],
                unique_id=program_name,
                classname=config["_class"], 
                config=config,
                plugins=config.get('plugins')
            )
            
        super().init()

    
eugene = Stoner()
eugene.init()