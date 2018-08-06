import discord
import operator
import datetime
import os
import re
import asyncio
import aiohttp
from discord.ext import commands
from __main__ import send_cmd_help, user_allowed
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box, pagify, escape_mass_mentions
from random import choice
from copy import deepcopy
from cogs.utils.settings import Settings

import PIL
from PIL.Image import core as _imaging
from PIL import Image

#try:
    #from PIL import Image
    #PIL = True
#except:
    #PIL = False

__author__ = "Ordinator"


def plain_uname(user: discord.Member=None):
    if user:
        name = user.display_name
        uid = user.id
        nick = user.name
        pat = '(?<=^b\').*?(?=\'$)'
        #trim = unidecode.unidecode(name)
        trim = str(unidecode(user.display_name).encode('ascii', 'ignore'))
        #trim = str(name.encode('ascii', 'ignore'))
        trim = ' '.join(re.findall(pat,trim)).strip()
        #trim = "``\n**UID**: {} \n**Type**: {} \n**Name**: {}\n**Name No-Emote**: {} \n**Pattern**: {} \n``".format(uid, nick, name, trim, pat)
        return trim
    else:
        return ""



def titlecase(s, exceptions=['a', 'an', 'of', 'the', 'is']):
    word_list = re.split(' ', s)       # re.split behaves as expected
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in exceptions else word.capitalize())
    return " ".join(final)


class Ordcustom:
    """Custom stuff from Ordinator"""

    def __init__(self, bot):
        self.bot = bot
        self.allemojis = []
        self.update_all_emoji_list()

    def _role_from_string(self, server, rolename, roles=None):
        if roles is None:
            roles = server.roles

        roles = [r for r in roles if r is not None]
        role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(),
                                  roles)

        return role    
    
    async def attempt_cleanup(self, messages):
        try:
            if len(messages) > 1:
                await self.bot.delete_messages(messages)
            else:
                await self.bot.delete_message(messages[0])
        except:
            pass

    def update_all_emoji_list(self):
        self.allemojis = self.bot.get_all_emojis()
        return
    
    async def get_emojis_from_message(self, message):
        celserver = self.bot.get_server("99607063012843520")
        if not message.server == celserver:
            return
        
        strin = message.content
        if not strin:
            return

        pnglist = []
        repat = re.compile(r"<:([^:]*):(\d*)>", re.IGNORECASE)
        #https://cdn.discordapp.com/emojis/306256699134705665.png
        path = r"data/ordcustom/emojis/"
        option = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        
        msg_iter = repat.finditer(strin)
        for match in msg_iter:
            emoji_name = match.group(1)
            emoji_id = match.group(2)
            url = "https://cdn.discordapp.com/emojis/{}.png".format(emoji_id)
            full_filename_path = path+"{}.{}".format(emoji_name, url[-3:])
            pnglist.append(full_filename_path)
            
            try:
                async with aiohttp.get(url, headers=option) as r:
                    emote = await r.read()
                    with open(full_filename_path, 'wb') as f:
                        f.write(emote)
            except Exception as e:
                print(e)
                return
        
        if pnglist and len(pnglist) > 1:
            ims = "data/ordcustom/" + self.imgprocess(pnglist)
            await self.bot.send_file(message.channel, ims)
        elif pnglist:
            await self.bot.send_file(message.channel, pnglist[0])
    
    def is_command(self, msg):
        for m in self.bot.settings.get_prefixes(msg.server):
            if msg.content.startswith(m):
                return True
        return False

    def elaborate_response(self, trigger, r):
        if trigger.owner != settings.owner:
            return "text", r
        if not r.startswith("file:"):
            return "text", r
        else:
            path = r.replace("file:", "").strip()
        path = os.path.join("data", "trigger", "files", path)
        print(path)
        if os.path.isfile(path):
            return "file", path
        else:
            return "text", r

    async def on_server_emojis_update(self, before, after):
        if (before or after):
            oldnotinnew = list(set(before) - set(after))
            newnotinold = list(set(after) - set(before))
        
        #server = discord.utils.get(discord.client.servers, name='GamerCeleste')
        #server = before.server
        
        if (len(before) == 0):
            if (len(after) == 0):
                return
            else:
                server = after[0].server
        else:
            server = before[0].server
        
        oldstr = '\nAn emoji has been removed from this server:\t'
        newstr = '\nA new emoji has just been added:\t'
        msg = ""
        
        if (len(oldnotinnew) > 0):
            #stuff deleted
            oldnotinnew.sort(key=operator.attrgetter('name'))

            for e in oldnotinnew:
                oldstr = oldstr + str(e) + '\t`:' + e.name + ':`\n' + e.url
            msg = oldstr

        if (len(newnotinold) > 0):
            #stuff added
            newnotinold.sort(key=operator.attrgetter('name'))
            for e in newnotinold:
                newstr = newstr + str(e) + '\t`:' + e.name + ':`\n' + e.url
            msg = newstr

        if msg:
            return #await self.bot.send_message(server, msg)


    async def on_message(self, message):
        channel = message.channel
        author = message.author
        celserver = self.bot.get_server("99607063012843520")
        
        if self.is_command(message):
            return
        
        if message.server is None:
            return
        
        if author == self.bot.user:
            return
        
        if not user_allowed(message):
            return        
        
        
        if (message.clean_content == "CEASE ALL MOTOR FUNCTIONS"):
            await self.bot.add_reaction(message, u"\U0001F480")
            return await self.bot.send_message(channel, "As you wish.")
        
        
        await self.get_emojis_from_message(message)
        
        if ("poop".lower() in message.content.lower().split()):
            await self.bot.add_reaction(message, u"\U0001F4A9")
        
        if message.server == celserver:
        
            if ("shit".lower() in message.content.lower().split()):
                await self.bot.add_reaction(message, u"\U0001F4A9")
        
            modchan = discord.utils.find(lambda c: "mods" in c.name, celserver.channels)
            musicchan = discord.utils.find(lambda c: "requests" in c.name, celserver.channels)
            newschan = discord.utils.find(lambda c: "announcements" in c.name, celserver.channels)
            genchan = discord.utils.find(lambda c: "general" in c.name, celserver.channels)
            devchan = discord.utils.find(lambda c: "bot-dev" in c.name, celserver.channels)
            
            #COPY MESSAGES FROM #ANNOUNCEMENTS custom code:
            if (channel == newschan):
                return await self.bot.send_message(genchan, "New Announcement: " + message.content)

            #AUTO-MODERATE words custom code:
            if ("amber".lower() in message.content.lower().split()):
                await self.bot.delete_message(message)
                if message.channel != musicchan:
                    await self.bot.send_message(modchan, "The following message by " + message.author.mention + " in the " + message.channel.mention + " channel was deleted for containing the \"*A word*\" in it:\n\n" + message.content)
                    # await self.bot.send_message(message.author, "You have had a message automatically deleted in the **" + message.server.name + "** server. \nIf you need more info please contact a moderator or admin")
                return
                



    @commands.command(pass_context=True)
    async def emoji(self, ctx):
        """Lists all emoji's on this server"""
        message = ctx.message
        channel = message.channel
        allemo = ''
        emolist = message.server.emojis
        emolist.sort(key=operator.attrgetter('name'))
        for e in message.server.emojis:
            allemo = allemo + '' + str(e) + '\t`:' + e.name + ':`\n'
        await self.bot.send_message(channel, "\nEmotes\nAll **" + message.server.name + "** Emojis: \n\n" + allemo)
        return          

    @commands.command(pass_context=True)
    async def testmessage(self, ctx):
        await self.bot.say(ctx.message.clean_content.upper())
                
        botmem = discord.utils.find(lambda m: m.name == self.bot.user.name, ctx.message.channel.server.members)
        botnick = self.bot.user.display_name        
        if botmem.nick:
            botnick = botmem.nick
        
        await self.bot.say(botnick)
        await self.bot.say(ctx.message.clean_content.replace(botnick,""))

        
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def saychan(self, ctx, sendchan=None, sendmsg=None):
        """Sends text to a specified channel,
        
        saychan <channel> <message>"""
        
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        
        if message is None:
            return
        
        if sendmsg is None:
            return
        
        if sendchan is None:
            return
        
        return await self.bot.send_message(sendchan, sendmsg)
        
        
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def rolebulk(self, ctx, method, rolename, message=None):
        """Adds a role to multiple users,
        
        rolebulk <add/remove> <"rollname"> <@mention1, @mention2, ...>

        Role name must be in quotes if there are spaces."""
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if message is None:
            return
        
        if method.lower() not in {"add", "remove"}:
            return await self.bot.say('You must specify either "add" or "remove"')
        
        if (method.lower() == "add"):
            addbool = True
        else:
            addbool = False

        role = self._role_from_string(server, rolename)
        
        #try:
        #    self.bot.say("Role {} found from rolename {}".format(
        #        role.name, rolename))
        #except:
        #    log.debug("Role not found for rolename {}".format(rolename))

        if role is None:
            await self.bot.say('That role cannot be found.')
            return

        allnames = ctx.message.mentions
        
        if len(allnames) < 1:
            return await self.bot.say('Please mention users; no user mentions were found in the command')
        
        if not channel.permissions_for(server.me).manage_roles:
            await self.bot.say('I don\'t have manage_roles.')
            return
        
        for mem in allnames:
            if addbool:
                await self.bot.add_roles(mem, role)
            else:
                await self.bot.remove_roles(user, role)

        return await self.bot.say('Complete')
        
        
    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def rolemerge(self, ctx, rolename, rolename2):
        """Adds a role to multiple users,
        
        rolebulk <add/remove> <"rollname"> <@mention1, @mention2, ...>

        Role name must be in quotes if there are spaces."""
        message = ctx.message
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if message is None:
            return


        role = self._role_from_string(server, rolename)
        role2 = self._role_from_string(server, rolename2)
        
        #try:
        #    self.bot.say("Role {} found from rolename {}".format(
        #        role.name, rolename))
        #except:
        #    log.debug("Role not found for rolename {}".format(rolename))

        if role is None:
            await self.bot.say('That role cannot be found.')
            return

        if role2 is None:
            await self.bot.say('That role cannot be found.')
            return

        if not channel.permissions_for(server.me).manage_roles:
            await self.bot.say('I don\'t have manage_roles.')
            return

        allnames = server.members
        
        for mem in allnames:
            memrole = discord.utils.find(role2, mem.roles)
            if memrole:
                add_roles(mem, role)
                remove_roles(role2, mem)

            
        return await self.bot.say('Complete')

        
    def imgprocess(self, listed):
        images = [Image.open(i) for i in listed]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new("RGBA", (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        cat = "test.png"
        new_im.save("data/ordcustom/" + cat)
        return cat


def check_folders():
    paths = ("data/ordcustom", "data/ordcustom/emojis")
    for path in paths:
        if not os.path.exists(path):
            print("Creating {} folder...".format(path))
            os.makedirs(path)

def setup(bot):
    check_folders()
    bot.add_cog(Ordcustom(bot))
