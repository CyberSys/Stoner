# Stoner

Stereotypical Ordinary Normal Everyday Robot

A example of using the [dogma framework](https://github.com/FWolfe/dogma),
as used in the ORGM discord/irc bot.
This example uses several 'dogma programs' (located in the programs directory):

* discord - a discord bot component, using disco-py. Capable of loading plugins
(see the plugin_discord directory)

* irc - a minimal irc client, using irclite. Capable of loading plugins
(see the plugin_irc directory)

* pz - a component that uses pyZomboid to load and execute Project Zomboid's lua files
Plugins are not used by this component.

* wsgi - a very minimal example of a wsgi webserver, able to serve dynamic or static files
Capable of loading plugins (see the plugin_wsgi directory)



Requirements:

* [dogma framework](https://github.com/FWolfe/dogma)

Optional Requirements (depending on programs loaded)

* [irclite](https://github.com/FWolfe/irclite) for the IRC client

* [pyZomboid](https://github.com/FWolfe/pyZomboid) for the Project Zomboid component

* [disco](https://github.com/b1naryth1ef/disco) for the discord bot
