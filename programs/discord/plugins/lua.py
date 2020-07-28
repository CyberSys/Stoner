# -*- coding: utf-8 -*-
from disco.bot import Plugin
import lupa
lua = None
import re


def sandbox(instance):
    whitelist = [
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
    for x in lua.globals().keys():
        if not x in whitelist:
            lua.globals()[x] = None

class LuaPlugin(Plugin):

    def load(self, ctx):
        global lua
        super(LuaPlugin, self).load(ctx)
        lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        sandbox(lua)


    def unload(self, ctx):
        return super(LuaPlugin, self).unload(ctx)

    def agent(self):
        return self.bot.parent.agent

#==============================================================================
#
#==============================================================================

    @Plugin.command('reset', group="lua", level=1000)
    def on_lua_reset_command(self, event):
        lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        sandbox(lua)
        event.msg.reply("ok.")



    @Plugin.command('eval', '<args:str...>', group="lua", level=1000)
    def on_lua_eval_command(self, event, args):
        try:
            event.msg.reply(str(lua.eval(args)))
        except lupa._lupa.LuaSyntaxError as msg:
            event.msg.reply(f"**LuaSyntaxError:** `{msg}`")
        except lupa._lupa.LuaError as msg:
            event.msg.reply(f"**LuaError:** `{msg}`")


    @Plugin.command('exec', '<args:str...>', group="lua", level=1000)
    def on_lua_exec_command(self, event, args):
        try:
            event.msg.reply(str(lua.execute(args)))
        except lupa._lupa.LuaSyntaxError as msg:
            event.msg.reply(f"**LuaSyntaxError:** `{msg}`")
        except lupa._lupa.LuaError as msg:
            event.msg.reply(f"**LuaError:** `{msg}`")


    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.author.id == self.bot.parent.discord_id: # ignore ourself.
            return
        access = self.bot.get_level(event.author)
        if event.is_mentioned(self.bot.parent.discord_id):
            if access == 1000:
                for code in re.findall('```lua(.+?)```', event.content, re.S):
                    try:
                        result = lua.execute(code)
                        if result:
                            event.reply(str(result))
                    except lupa._lupa.LuaSyntaxError as msg:
                        event.reply(f"**LuaSyntaxError:** `{msg}`")
                    except lupa._lupa.LuaError as msg:
                        event.reply(f"**LuaError:** `{msg}`")

