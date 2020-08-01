# -*- coding: utf-8 -*-
import re
import logging
import gevent
import lupa
from disco.bot import Plugin

# TODO: limit instance runtime

DEFAULT_ALLOW = [
    'assert',
    'tostring',
    'tonumber',
    'ipairs',
    'pairs',
    'print',
    'unpack',
    'table',
    '_VERSION',
    'next',
    'math',
    '_G',
    'select',
    'string',
    'type',
    'getmetatable',
    'setmetatable',
    ]

logger = logging.getLogger(__name__)

class LuaPlugin(Plugin):
    instances = None
    lua = None

    def load(self, ctx):
        super(LuaPlugin, self).load(ctx)
        self.config.setdefault('sandbox', True)
        self.config.setdefault('max_instances', 5)
        self.config.setdefault('allowlist', DEFAULT_ALLOW[:])

        self.instances = []
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True) # pylint: disable=E1101
        self.sandbox_instance(self.lua)



    def agent(self):
        return self.bot.parent.agent


    def sandbox_instance(self, lua):
        for x in lua.globals().keys():
            if not x in self.config['allowlist']:
                lua.globals()[x] = None


    def create_instance(self, sandbox=True):
        logger.debug("Creating new lua instance")
        lua = lupa.LuaRuntime(unpack_returned_tuples=True) # pylint: disable=E1101
        if sandbox:
            self.sandbox_instance(lua)

        return lua


    def spawn_instance(self, **kwargs):
        if len(self.instances) >= self.config['max_instances']:
            return
        logger.info("Spawning greenlet for lua instance")

        self.instances.append(gevent.spawn(self._run_instance, **kwargs))


    def _run_instance(self, callback, lua=None, code='', **kwargs):
        if lua is None:
            lua = self.create_instance(self.config['sandbox'])

        result = None

        try:
            result = str(lua.execute(code))

        except lupa._lupa.LuaSyntaxError as msg: # pylint: disable=W0212
            result = f"**LuaSyntaxError:** `{msg}`"

        except lupa._lupa.LuaError as msg: # pylint: disable=W0212
            result = f"**LuaError:** `{msg}`"

        try:
            self.instances.remove(gevent.getcurrent())
        except ValueError:
            pass

        logger.debug("Instance run finished")
        callback(result, **kwargs)


    def return_result(self, result, reply, **kwargs):
        reply(result)


#==============================================================================
#
#==============================================================================

    @Plugin.command('reset', group="lua", level=1000)
    def on_lua_reset_command(self, event):
        self.lua = self.create_instance(self.config['owner_sandbox'])
        event.msg.reply("ok.")



#    @Plugin.command('eval', '<code:str...>', group="lua", level=1000)
#    def on_lua_eval_command(self, event, args):
#        try:
#            event.msg.reply(str(lua.eval(args)))
#        except lupa._lupa.LuaSyntaxError as msg:
#            event.msg.reply(f"**LuaSyntaxError:** `{msg}`")
#        except lupa._lupa.LuaError as msg:
#            event.msg.reply(f"**LuaError:** `{msg}`")


    @Plugin.command('exec', '<code:str...>', group="lua", level=1000)
    def on_lua_exec_command(self, event, code):
        instance = self.lua
        self.spawn_instance(code=code, callback=self.return_result, reply=event.reply, lua=instance)


    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.author.id == self.bot.parent.me.id: # ignore ourself.
            return

        access = self.bot.get_level(event.author)
        if event.is_mentioned(self.bot.parent.me.id):
            instance = None
            if access == 1000:
                instance = self.lua
                # drop 1 indentation level to open public access
                for code in re.findall('```lua(.+?)```', event.content, re.S):
                    self.spawn_instance(
                        code=code,
                        callback=self.return_result,
                        reply=event.reply,
                        lua=instance)
