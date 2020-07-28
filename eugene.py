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
import logging
import stoner


stoner.setup_logging( # some of these overrides need to goto specific config files.
    {
        'irclite' : logging.DEBUG,
        'requests': logging.WARNING,
    },

    logging.INFO #getattr(logging, 'DEBUG')
)

eugene = stoner.Stoner()
eugene.init()
