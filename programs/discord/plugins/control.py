# -*- coding: utf-8 -*-

from disco.bot import Plugin
from disco.types.message import MessageEmbed
from dogma.program import ProgramLoadError


def embedReply(title=None, description=None, event=None):
    embed = MessageEmbed()
    embed.title = title
    embed.description = description
    embed.color = '10038562'
    if event:
        event.msg.reply(None, embed=embed)
    return embed

    
class DogmaControl(Plugin):

#    def load(self, ctx):
#        super(DogmaControl, self).load(ctx)


#    def unload(self, ctx):
#        return super(DogmaControl, self).unload(ctx)


#==============================================================================
#
#==============================================================================
    def agent(self):
        return self.parent.agent


    @Plugin.command('load', '<unique_id:str>', group='program', level=1000)
    def on_program_load_command(self, event, unique_id):
        try:
            config = self.agent().config_load(unique_id)
            program = self.agent().program_import(
                module=config["_module"],
                unique_id=unique_id,
                classname=config["_class"], 
                config=config,
                plugins=config.get('plugins')
            )
            program.init()
            event.msg.reply("ok")
        except ProgramLoadError as msg:
            event.msg.reply(f"**ProgramLoadError** `{msg}`")


    @Plugin.command('unload', '<unique_id:str>', group='program', level=1000)
    def on_program_unload_command(self, event, unique_id):
        try:
            self.agent().program_unload(unique_id)
            event.msg.reply("ok")
        except ProgramLoadError as msg:
            event.msg.reply(f"**ProgramLoadError** `{msg}`")
            


    @Plugin.command('reload', '<unique_id:str>', group='program', level=1000)
    def on_program_reload_command(self, event, unique_id):
        try:
            self.agent().program_reload(unique_id)
            event.msg.reply("ok")
        except ProgramLoadError as msg:
            event.msg.reply(f"**ProgramLoadError** `{msg}`")



    @Plugin.command('list', group='program', level=1000)
    def on_program_list_command(self, event):
        event.msg.reply(str([x for x in self.bot.agent.programs.keys()]))



    @Plugin.command('load', '<program:str> <plugin:str>', group='plugin', level=1000)
    def on_plugin_load_command(self, event, program, plugin):
        if program == 'discord':
            try:
                self.bot.add_plugin_module(plugin)
                event.msg.reply("ok")
            except ModuleNotFoundError as msg:
                event.msg.reply(f"**ModuleNotFoundError** `{msg}`")
            return

        pro = self.agent().programs.get(program)
        if not pro:
            event.msg.reply(f"**BadInputError** `can't load plugin for non-loaded program {program}`")
            return
        if not hasattr(pro, 'plugin_import'):
            event.msg.reply(f"**BadInputError** `program {program} is not a instance of PlugableProgram`")
            return

        try:
            pro.plugin_import(plugin, pro.config.get('plugins', {}).get(plugin))
            event.msg.reply("ok")
        except ProgramLoadError as msg:
            event.msg.reply(f"**ProgramLoadError** `{msg}`")

        

    @Plugin.command('unload', '<program:str> <plugin:str>', group='plugin', level=1000)
    def on_plugin_unload_command(self, event, program, plugin):
        pass



    @Plugin.command('reload', '<program:str>  <plugin:str>', group='plugin', level=1000)
    def on_plugin_reload_command(self, event, program, plugin):
        pass


    @Plugin.command('list', '<program:str>', group='plugin', level=1000)
    def on_plugin_list_command(self, event, program):
        if program == 'discord':
            pro = self.bot
        else:
            pro = self.bot.agent.programs.get(program)
        if pro:
            event.msg.reply(str([x for x in pro.plugins.keys()]))


    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        if event.author.id == self.bot.parent.me.id: # ignore ourself.
            return
        
        access = self.bot.get_level(event.author)
        if event.guild is None and access < 1000:
            self.parent.notify("DM Received (%s)" % event.author, event.content)
