#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 14:36:09 2018

@author: wolf
"""

from dogma.program import Plugin

def try_calling (o, trap=False,glob=None,local=None):
    """tries calling the arg a number of different ways. If 'trap' is False, returns
    True or False, depending on if the execution succeeds or not. If trap is True,
    returns the return value of the execution
    """
    if glob == None : glob = globals()
    if local == None  : local = locals()
    if callable(o) :
        r = o()
        if trap : return r
        return True
    elif isinstance(o,(list,tuple)) and  callable(o[0]) :
        if isinstance(o[1], (list, tuple)) :
            r = o[0](*o[1])
            if trap : return r
            return True
        elif isinstance(o[1], dict) :
            r = o[0](**o[1])
            if trap : return r
            return True
        else :
            r = o[0](o[1])
            if trap : return r
            return True
    elif isinstance(o, str) :
        try :
            r = eval(o, glob, local)
            if trap : return r
            return True
        except SyntaxError :
            pass

        exec(o, glob, local)
        return True
    return False


class Control(Plugin):
    access = {
        'ev' : 1000,
        'join' : 90,
        'part' : 90,
    }
    def __init__(self, client):
        Plugin.__init__(self, client)


    def load(self, config=None, state=None):
        Plugin.load(self, config, state)
        self.config = config

#    def _event_JOIN(self, msg):
#        print "GOT JOIN MSG!"

    def _command_join(self, network, msg):
        network.join(msg.as_command())

    def _command_part(self, network, msg):
        network.part(msg.as_command())

    def _command_ev(self, network, msg):
        network.privmsg(msg.dest, try_calling( msg.as_command(), True, globals(), locals() ))
