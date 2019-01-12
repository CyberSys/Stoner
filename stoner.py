#!/usr/bin/env python2
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

import dogma
dog = dogma.Agent()
dog.program_new('programs.pz', {
    'dir' : '/home/USERNAME/local/Project Zomboid/game/projectzomboid/',
    'cache' : '/home/USERNAME/Zomboid/'
})
dog.program_new('programs.discord', {
    'token' : u'ENTER YOUR DISCORD TOKEN HERE',
    # 'plugins' : ['plugin_discord.orgm']
})

dog.program_new('programs.irc', {
    'nick' : 'Dogma',
    'altnick' : 'Dogma_',
    'ident' : 'Dogma',
    'realname' : 'Dogma',
    'debug' : False,
    'plugins' : ['plugin_irc.control'],
    'networks' : (
        {
            'name' : 'MyNetwork',
            'host' : 'irc.MyNetwork.com',
            'port' : '6667',
        },
    ),
    'onconnect' : [
        lambda net: net.name == "MyNetwork" and net.join('#Chat'),
    ],
     # set a access levels for users, if plugin_irc.control is loaded
    'access' : {
        # 'nick!user@host' : 100,
    }
})

dog.init()
