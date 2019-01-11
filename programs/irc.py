import sys
import exceptions
import irclite
from dogma.program import PlugableProgram


class IRCBot(PlugableProgram, irclite.Client):
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


    def trigger_command(self, network, msg, cmd):
        for plugin in self.plugins.values():
            callback = getattr(plugin, '_command_%s' % cmd, None)
            if not callback:
                continue
            if network.getaccess(msg.sender) < getattr(plugin, 'access', {}).get(cmd, 0):
                continue
            ### general catch all, bad stuff
            try:
                callback(network, msg)
            except:
                if sys.exc_type == exceptions.SystemExit:
                    exit()
                print self, str(sys.exc_type), str(sys.exc_value)
                network.privmsg(msg.dest, str(sys.exc_type) + " " + str(sys.exc_value))


    def trigger_event(self, network, msg):
        for plugin in self.plugins.values():
            callback = getattr(plugin, '_event_%s' % msg.type, None)
            if not callback:
                continue
            ### general catch all, bad stuff
            try:
                callback(msg)
            except:
                if sys.exc_type == exceptions.SystemExit:
                    exit()
                print self, str(sys.exc_type), str(sys.exc_value)
