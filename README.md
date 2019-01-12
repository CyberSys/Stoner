# Stoner

Stereotypical Ordinary Normal Everyday Robot

A example of using the [dogma framework](https://github.com/FWolfe/dogma),
as used in the ORGM discord/irc bot.
This example uses several 'dogma programs' (located in the programs directory):

* discord - a discord bot component, using disco-py. Capable of loading plugins
(see plugin_discord)

* irc - a minimal irc client, using irclite. Capable of loading plugins
(see plugin_irc)

* pz - a component that uses pyZomboid to load and execute Project Zomboid's lua files
Plugins are not used by this component.

* wsgi - a minimal wsgi web server, capable of serving dynamic or static files
Capable of loading plugins (see plugin_wsgi)



Requirements:

* [dogma framework](https://github.com/FWolfe/dogma)

Optional Requirements (depending on programs loaded)

* [irclite](https://github.com/FWolfe/irclite) for the IRC client

* [pyZomboid](https://github.com/FWolfe/pyZomboid) for the Project Zomboid component

* [disco](https://github.com/b1naryth1ef/disco) for the discord bot
