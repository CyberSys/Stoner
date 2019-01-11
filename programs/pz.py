#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 09:50:27 2018

@author: wolf
"""


import zomboid.settings as settings
import zomboid.LuaManager as LuaManager
import zomboid.ScriptManager as ScriptManager
import zomboid.EventManager as EventManager
import zomboid.GameManager as GameManager
import zomboid.TranslationManager as TranslationManager

#import gevent
from dogma.program import Program
from collections import namedtuple

Score = namedtuple('Score',('wins', 'winning_streak', 'losses', 'losing_streak', 'revolver', 'rounds'))
PLAYERDB = {}
class Player(object):
    def __init__(self, name):
        from zomboid.Character import IsoPlayer
        self.name = name
        self.revolver = None
        self.player = IsoPlayer()
        self.storage = {}

    def set_revolver(self, itemType):
        self.revolver = self.storage.get(itemType, self.new_revolver(itemType))

    def new_revolver(self, itemType):
        import zomboid.util as util
        revolver = util.spawnFirearm(itemType, defaultBarrel=False, loaded=False, ammo=None, semiAutoMode=True, components=None)
        self.storage[itemType] = revolver
        return revolver

    def setcapacity(self, value):
        ORGM = LuaManager.instance.globals().ORGM
        Reloadable = ORGM.ReloadableWeapon
        data = self.revolver.getModData()
        value = value < data.maxCapacity and value or data.maxCapacity - 1

        self.player.getInventory().AddItems("ORGM."+ ORGM.Ammo.itemGroup(self.revolver, True)[1],value)
        if Reloadable.Reload.valid(data, self.player) and data.currentCapacity < value:
            Reloadable.Reload.start(data, self.player, self.revolver)

        while Reloadable.Reload.valid(data, self.player) and data.currentCapacity < value:
            Reloadable.Reload.perform(data, self.player, self.revolver)
            print data.currentCapacity, "rounds in chamber"

        if Reloadable.Rack.valid(data, self.player):
            print "Racking Close.."
            Reloadable.Rack.start(data, self.player, self.revolver)
            Reloadable.Rack.perform(data, self.player, self.revolver)


    def roulette(self):
        ORGM = LuaManager.instance.globals().ORGM
        Reloadable = ORGM.ReloadableWeapon
        data = self.revolver.getModData()

        if data.currentCapacity == 0:
            print "Empty gun"
            self.setcapacity(1)
        
        if Reloadable.Rack.valid(data, self.player):
            print "Racking..(hammer)?"
            Reloadable.Rack.start(data, self.player, self.revolver)
            Reloadable.Rack.perform(data, self.player, self.revolver)
        
        print "spinning... %s >" % data.cylinderPosition,
        Reloadable.Cylinder.rotate(data, 0, self.player, False, self.revolver)
        print data.cylinderPosition

        if Reloadable.Fire.valid(data) and Reloadable.Fire.pre(data, self.player, self.revolver):
            Reloadable.Fire.post(data, self.player, self.revolver)
            data.losses = (data.losses or 0) + 1
            data.losing_streak = (data.losing_streak or 0) + 1
            data.winning_streak = 0
            print "Bang! %s wins (%s in a row), %s losses (%s in a row), %s (%s rounds in chamber)" % (
                    data.wins, data.winning_streak, data.losses, data.losing_streak, self.revolver.getDisplayName(), data.currentCapacity)
            return True

        else: # dryfire
            Reloadable.Fire.dry(data, self.player, self.revolver)
            data.wins = (data.wins or 0) + 1
            data.winning_streak = (data.winning_streak or 0) + 1
            data.losing_streak = 0
            print "Click! %s wins (%s in a row), %s losses (%s in a row), %s (%s rounds in chamber)" % (
                    data.wins, data.winning_streak, data.losses, data.losing_streak, self.revolver.getDisplayName(), data.currentCapacity)

            self.setcapacity(data.currentCapacity+1)
            print data.currentCapacity, "rounds in chamber"
            return False


    def get_score(self):
        data = self.revolver.getModData()
        return Score(
                    data.wins,
                    data.winning_streak,
                    data.losses,
                    data.losing_streak,
                    self.revolver.getDisplayName(),
                    data.currentCapacity,
                )

class Zomboid(Program):
    def __init__(self, agent):
        Program.__init__(self, agent)
        self.lua = None
        self.G = None

    def load(self, config=None, state=None):
        Program.load(self, config, state)
        settings.pzdir = config['dir']
        settings.cache = config['cache']
        GameManager.addMod('ORGM')
        ScriptManager.init()
        LuaManager.init()

        TranslationManager.init()
        LuaManager.loadSharedLua()
        LuaManager.loadClientLua()
        EventManager.Trigger('OnLoadSoundBanks')
        EventManager.Trigger('OnGameBoot')

        LuaManager.loadServerLua()
        EventManager.Trigger('OnPreDistributionMerge')
        EventManager.Trigger('OnDistributionMerge')
        EventManager.Trigger('OnPostDistributionMerge')
        self.lua = LuaManager.instance
        self.G = self.lua.globals()

    def run(self):
        print "Zomboid in run loop, nothing to do..."

    def newplayer(self, player):
        if not PLAYERDB.has_key(player):
            PLAYERDB[player] = Player(player)
        return PLAYERDB[player]

    def getplayer(self, player):
        return PLAYERDB.get(player)

    def roulette(self, player, firearm):
        player = self.newplayer(player)
        player.set_revolver(firearm)
        return player.roulette()