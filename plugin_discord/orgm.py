#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:28:51 2018

@author: wolf
"""
import re
from disco.bot import Plugin
from disco.types.message import MessageEmbed
import zomboid.LuaManager as LuaManager
from zomboid.TranslationManager import getText
import zomboid.ScriptManager as ScriptManager
#import zomboid.Inventory as InventoryItemFactory
import zomboid.util as util

ORGM = LuaManager.instance.globals().ORGM
Firearm = ORGM.Firearm
Ammo = ORGM.Ammo

ClassStrings = {}
DisplayStrings = {
    'Firearm':{},
    'Component':{},
    'Ammo':{},
}

DESCRIPTION = """
Adds over 100 real world firearms and realistic firearm mechanics to Project Zomboid.

[TIS Forum Thread](https://github.com/FWolfe/RealGunsMod)
[Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=514618604)
[FAQ](https://zomboid.tekagis.ca/orgm-faq.php)
[Changelog](https://zomboid.tekagis.ca/api/manual/changelog.txt.html)
[Introductory Tutorial Video](https://www.youtube.com/watch?v=YO4b1Es0gl0) (by Ghul King)

[Github Page](https://github.com/FWolfe/RealGunsMod)
[API Documentation](https://zomboid.tekagis.ca/api/)
[Direct Download](https://downloads.tekagis.ca/ProjectZomboidMods/ORGM.zip)
"""

#==============================================================================
#   Embedded Message functions
#==============================================================================
def embedReply(title=None, description=None, event=None):
    embed = MessageEmbed()
    embed.title = title
    embed.description = description
    embed.color = '10038562'
    if event:
        event.msg.reply(None, embed=embed)
    return embed

def getStatField():
    return [
        u"Barrel",
        u"Class",
        u"Ammo",
        u"Weight",
        u"Capacity",
        u"Range",
        u'MinDamage',
        u'MaxDamage',
        u"Acquisition Speed",
        u"Recoil",
        u"Noise",
        u"Accuracy",
        u"Critical",
        u"Movement Bonus",
    ]

def getItemStatsField(item, gunData):
    data = item.getModData()
    return [
        unicode(data.barrelLength),
        getText(gunData.classification),
        Ammo.getData(data.lastRound).instance.getDisplayName().replace("Rounds", ""),
        item.getWeight(),
        data.maxCapacity,
        item.getMaxRange(),
        item.getMinDamage(),
        item.getMaxDamage(),
        item.getSwingTime(),
        item.getRecoilDelay(),
        item.getSoundRadius(),
        item.getHitChance(),
        item.getCriticalChance(),
        item.getAimingTime(),
    ]


#==============================================================================
#   Item Functions
#==============================================================================
def create_firearm_from_string(event, item):
    args = re.split(' *, *', item)
    item = args.pop(0)

    results = search_firearms(item)
    if not check_search_results(results, item, event):
        return None
    item = results[0]

    defaultBarrel = True
    ammo = None
    components = []
    for a in args:
        if a.startswith('barrel='):
            try:
                defaultBarrel = float(a[7:])
            except ValueError:
                pass #TODO: Warn and exit
        elif a.startswith('ammo='):
            cresult = search_ammo(a[5:])
            cresult = [x for x in Ammo.itemGroup(item, True).values() if x in cresult]
            if not check_search_results(cresult, a[5:], event):
                return
            ammo = cresult[0]

        else:
            cresult = search_components(a)
            if not check_search_results(cresult, a, event):
                return
            components.append(cresult[0])

    item = util.spawnFirearm(item, defaultBarrel=defaultBarrel,
                             loaded=True, ammo=ammo, semiAutoMode=True,
                             components=components)
    return item

#def getItem(name):
#    return Firearm.getData(name).instance

def get_firearm_info(name):
    data = Firearm.getData(name)
    item = data.instance

    text = [
        u"**Class:**  %s" % getText(data.classification),
        u"**Manufacturer:**  %s *(%s)*" % (getText(data.manufacturer), getText(data.country)),
        u"**Weight:**  %s" % item.getWeight(),
        u"**Barrel Length**:  %s" % (data.barrelLengthOpt and ', '.join([(y == data.barrelLengthOpt[len(data.barrelLengthOpt)] and "or " or "") + str(y) for y in data.barrelLengthOpt.values()]) or str(data.barrelLength)) + " inches",
        u"**Ammo:**  %s" % ScriptManager.instance.FindItem("ORGM."+ item.getAmmoType()).getDisplayName(),
        u"**Capacity:**  %s" % item.getClipSize(),
        '',
        getText(data.description).replace("<LINE> ", "\n")
    ]
    embed = embedReply(title=item.getDisplayName(), description="\n".join(text))
    return embed


#==============================================================================
#   Search Functions
#==============================================================================
def search_classes(value):
    return [k for k, v in Firearm.getTable().items() if v.classification == value]


def search_name(value, table):
    value = value.lower()
    value = value.replace("_", " ")
    results = []
    for name in table:
        if name.lower() == value:
            return [table[name]]
        if value in name.lower():
            results.append(table[name])
    return results

def search_firearms(value):
    return search_name(value, DisplayStrings['Firearm'])

def search_components(value):
    return search_name(value, DisplayStrings['Component'])

def search_ammo(value):
    return search_name(value, DisplayStrings['Ammo'])

def check_search_results(results, search, event):
    if len(results) == 0:
        embedReply(title="No matches found for '%s'." % search, event=event)
        #event.msg.reply("No matching items found: %s" % search)
        return False
    elif len(results) != 1:
        #display = [getItem(r).getDisplayName() for r in results]
        display = [ScriptManager.instance.FindItem("ORGM." + r).getDisplayName() for r in results]
        display.sort()
        embedReply(title="Multiple matches found for %s. Specificy:" % search,
                   description="\n".join(display), event=event)
        return False
    return True

#
#def findBy(key, value, dataType=None):
#    results = []
#    table = Firearm.getTable()
#
#    for name, data in table.items():
#        if not data:
#            print "No data for ",name
#            return results
#        check = data[key]
#        if not isinstance(check, dataType):
#            print name, key, "=", str(check), " is not type", str(dataType)
#            continue
#        if dataType == str and check.lower() == value.lower():
#            results.append(name)
#        elif check == value:
#            results.append(name)
#    return results

#==============================================================================
#   Plugin Class
#==============================================================================
class OrgmPlugin(Plugin):
    is_busy = False
        
    def load(self, ctx):
        super(OrgmPlugin, self).load(ctx)
        #self.data = ctx.get('data', {})
        table = ORGM.Firearm.getTable()
        for name, data in table.items():
            DisplayStrings['Firearm'][data.instance.getDisplayName()] = name
            #DisplayStrings[data.instance.getDisplayName()] = name

            if not data.classification:
                continue
            ClassStrings[getText(data.classification)] = data.classification
        table = ORGM.Component.getTable()
        for name, data in table.items():
            DisplayStrings['Component'][data.instance.getDisplayName()] = name
            #DisplayStrings[data.instance.getDisplayName()] = name
        table = ORGM.Ammo.getTable()
        for name, data in table.items():
            DisplayStrings['Ammo'][data.instance.getDisplayName()] = name


    def unload(self, ctx):
        #ctx['data'] = self.data
        return super(OrgmPlugin, self).unload(ctx)


#==============================================================================
#
#==============================================================================
    @Plugin.command('version')
    def on_version_command(self, event):
        embed = MessageEmbed()
        embed.set_author(name="ORGM Rechambered v%s" % ORGM.BUILD_HISTORY[ORGM.BUILD_ID],
                         url='https://steamcommunity.com/sharedfiles/filedetails/?id=514618604', icon_url='https://steamuserimages-a.akamaihd.net/ugc/883133402202604197/BE49D1836C7C61AADDFE0CD3B8A6E4C74B9308BB/')
        embed.title = "OrMntMan's Real Guns Mod"
        embed.url = "https://github.com/FWolfe/RealGunsMod"
        #embed.add_field(name='type', value=text1, inline=True)
        #embed.add_field(name='count', value=text2, inline=True)

        stats = ", ".join([
            "**%s** *Firearms*" % len([x for x in Firearm.getTable().keys()]),
            "**%s** *Magazines*" % len([x for x in ORGM.Magazine.getTable().keys()]),
            "**%s** *Caliber/Bullet Combos*" % len([x for x in Ammo.getTable().keys()]),
            "\n**%s** *Components/Attachments*" % len([x for x in ORGM.Component.getTable().keys()]),
            "**%s** *Maintance Kits*" % len([x for x in ORGM.Maintance.getTable().keys()])
            ])
        embed.add_field(name='Mod Stats:', value=stats, inline=False)
        embed.description = DESCRIPTION
        #embed.timestamp = datetime.utcnow().isoformat()
        embed.set_footer(text="v%s" % ORGM.BUILD_HISTORY[ORGM.BUILD_ID])
        embed.color = '10038562'
        event.msg.reply(None, embed=embed)


#==============================================================================
#
#==============================================================================
    @Plugin.command('info', '<item:str...>')
    def on_info_command(self, event, item):
        results = search_firearms(item)
        if not check_search_results(results, item, event):
            return
        event.msg.reply(None, embed=get_firearm_info(results[0]))


#==============================================================================
#
#==============================================================================
    @Plugin.command('stats', '<item:str...>')
    def on_stats_command(self, event, item):
        item = create_firearm_from_string(event, item)
        if item is None:
            return
        gunData = Firearm.getData(item)
        description = [
            "Stats are generated using ORGM's Lua code, with a round in the chamber. All values shown are in semi-auto mode for select-fire models."
        ]
        embed = embedReply(title=item.getDisplayName(), description="\n".join(description))

        embed.add_field(name='Stat:', value="\n".join(getStatField()), inline=True)
        results = getItemStatsField(item, gunData)
        embed.add_field(name="Value", value="\n".join([unicode(x) for x in results]), inline=True)

        att = ORGM.Component.getAttached(item)
        if len([x for x in att.keys()]) > 0:
            embed.add_field(name='Attachments:',
                            value="\n".join([x.getDisplayName() for x in att.values()]),
                            inline=False)

        event.msg.reply(None, embed=embed)




#==============================================================================
#
#==============================================================================
    @Plugin.command('compare', '<args:str...>')
    def on_compare_command(self, event, args):
        args = re.split(' *; *', args)
        if len(args) != 2:
            embedReply(title='Error:', description="\n".join([
                'Items to compare must be seperated by a ;',
                'Any additional arguments (like attachments) can be specfied after the item in a comma seperated list.',
                '.compare m16, red dot, sling ; m4, rifle laser'
                ]), event=event)
            return

        item1 = create_firearm_from_string(event, args[0])
        item2 = create_firearm_from_string(event, args[1])
        gunData1 = Firearm.getData(item1)
        gunData2 = Firearm.getData(item2)

        description = [
            "Stats are generated using ORGM's Lua code, with a round in the chamber. Ammo used is the first entry in that firearm's caliber group.",
            "All values shown are in semi-auto mode for select-fire models, and default barrel lengths are used.",
        ]
        embed = embedReply(title='Comparison Results:', description="\n".join(description))

        def compare(a, b):
            for i, av in enumerate(a):
                bv = b[i]
                if not isinstance(av, (float, int)):
                    continue
                av, bv = float(av), float(bv)
                if av < bv:
                    a[i] = str('')
                    b[i] = "+%s percent" % (round(float(bv/av)*100-100, 3))
                elif av > bv:
                    b[i] = str('')
                    a[i] = "+%s percent" % (round(float(av/bv)*100-100, 3))
                else:
                    a[i] = str('')
                    b[i] = str('')

        def trim(string):
            if len(string) > 20:
                return string[0:20]+"..."
            return string

        embed.add_field(name='Stat:', value="\n".join(getStatField()), inline=True)
        results1 = getItemStatsField(item1, gunData1)
        results2 = getItemStatsField(item2, gunData2)
        compare(results1, results2)
        embed.add_field(name=trim(item1.getDisplayName()),
                        value="\n".join(results1).replace(' percent', '%'),
                        inline=True)
        embed.add_field(name=trim(item2.getDisplayName()),
                        value="\n".join(results2).replace(' percent', '%'),
                        inline=True)


        att1 = ORGM.Component.getAttached(item1)
        att2 = ORGM.Component.getAttached(item2)
        if len([x for x in att1.keys()]) > 0 or len([x for x in att2.keys()]) > 0:

            embed.add_field(name='Attachments:', value="\n".join([
                'sights', 'recoil', 'stock', 'sling', 'barrel', 'rails'
                ]), inline=True)
            embed.add_field(name='A', value="\n".join([
                (att1.Scope and att1.Scope.getDisplayName() or '-'),
                (att1.Recoilpad and att1.Recoilpad.getDisplayName() or '-'),
                (att1.Stock and att1.Stock.getDisplayName() or '-'),
                (att1.Sling and att1.Sling.getDisplayName() or '-'),
                (att1.Canon and att1.Canon.getDisplayName() or '-'),
                (att1.Clip and att1.Clip.getDisplayName() or '-'),
                ]), inline=True)
            embed.add_field(name='B', value="\n".join([
                (att2.Scope and att2.Scope.getDisplayName() or '-'),
                (att2.Recoilpad and att2.Recoilpad.getDisplayName() or '-'),
                (att2.Stock and att2.Stock.getDisplayName() or '-'),
                (att2.Sling and att2.Sling.getDisplayName() or '-'),
                (att2.Canon and att2.Canon.getDisplayName() or '-'),
                (att2.Clip and att2.Clip.getDisplayName() or '-'),
                ]), inline=True)

        event.msg.reply(None, embed=embed)



#==============================================================================
#
#==============================================================================
    @Plugin.command('class', '[classification:str...]')
    def on_class_command(self, event, classification=None):
        classkeys = ClassStrings.keys()
        classkeys.sort()
        if not classification:
            embedReply(title="Valid classifications are:",
                       description="\n".join(classkeys), event=event)
            return

        listclasses = {}
        for string in ClassStrings:
            if classification.lower() in string.lower():
                tr_name = ClassStrings[string]
                results = search_classes(tr_name)
                if not results:
                    continue
                results.sort()
                listclasses[string] = listclasses.get(string, [])
                for name in results:
                    listclasses[string].append(ORGM.Firearm.getData(name).instance.getDisplayName())
        if not listclasses:
            embedReply(title="Valid classifications are:",
                       description="\n".join(classkeys), event=event)
            return
        classes = listclasses.keys()
        classes.sort()
        for cl in classes:
            fal = listclasses[cl]
            embedReply(title=cl +"s:", description="\n".join(fal), event=event)


#==============================================================================
#
#==============================================================================
    @Plugin.command('ballistics', '<field:str> <ammoTypes:str...>')
    def on_ballistics_command(self, event, field, ammoTypes):
        if self.is_busy:
            return

        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        #if field.lower() == "recoil":
        #    field = "Recoil"
        if field.lower() == "range":
            field = "Range"
        elif field.lower() == "maxdamage":
            field = "MaxDamage"
        elif field.lower() == "mindamage":
            field = "MinDamage"
        else:
            embedReply(title="Error",
                       description="Invalid field (Range, MinDamage, MaxDamage).",
                       event=event)
            return

        ammoDatas = re.split(' *, *', ammoTypes)
        if len(ammoDatas) > 6:
            embedReply(title="Error",
                       description="Maximum of 6 ammo types can be specified.",
                       event=event)
            return

        for index, ammoType in enumerate(ammoDatas):

            cresult = search_ammo(ammoType)
            #TODO: instead of check_search_results, we could just actually use the results
            if not check_search_results(cresult, ammoType, event):
                return
            ammoType = cresult[0]

            ammoDatas[index] = ORGM.Ammo.getData(ammoType)

        self.is_busy = True
        calc = lambda length, optimal: ((((float(optimal)-float(length))/float(optimal))**3)**2)

        plt.figure(figsize=(9, 4))
        plt.title("Barrel Length vs %s" % field)
        plt.ylabel(field)
        plt.xlabel('Barrel Length')
        mlength = max([int((a.OptimalBarrel or 30)*0.6) for a in ammoDatas])
        if mlength > 30:
            mlength = 30

        for ammoData in ammoDatas:
            optimal = ammoData.OptimalBarrel or 30
            value = ammoData[field]
            results = [value - value * calc(i+4, optimal+4) for i in range(2, mlength+2, 2)]
            plt.plot(range(2, mlength+2, 2), results, label=ammoData.instance.getDisplayName())
        plt.legend()
        plt.savefig('temp.png')
        fi = open('temp.png', "rb")
        data = fi.read()
        fi.close()
        event.msg.reply(None, attachments=[('temp.png', data)])
        self.is_busy = False
