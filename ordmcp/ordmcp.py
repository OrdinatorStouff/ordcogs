import discord
import operator
import datetime
import os
import re
import asyncio
import requests
import aiohttp
from discord.ext import commands
from __main__ import send_cmd_help, user_allowed
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box, pagify, escape_mass_mentions
from random import choice
from copy import deepcopy
from cogs.utils.settings import Settings

#TODO -- many imports here are not needed, trim list


__author__ = "Ordinator"





class ORDMCP:
    """Custom basic MCP search by Ordinator"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/ordmcp/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        if 'fields' in list(self.settings.keys()):
            self.fieldsUrl = self.settings['fields']
        if 'methods' in list(self.settings.keys()):
            self.methodUrl = self.settings['methods']
        if 'params' in list(self.settings.keys()):
            self.paramsUrl = self.settings['params']
        if 'timestamp' in list(self.settings.keys()):
            self.timestamp = self.settings['timestamp']
        if 'maxDataAgeMinutes' in list(self.settings.keys()):
            self.maxDataAgeMinutes = self.settings['maxDataAgeMinutes']
            
    def is_command(self, msg):
        for m in self.bot.settings.get_prefixes(msg.server):
            if msg.content.startswith(m):
                return True
        return False

    def remove_file(filename):
        try:
            os.remove(filename)
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred

    def download_file(url, filepath):
        try:
            r = requests.get(url, allow_redirects=True)
            open(filepath, 'wb').write(r.content)
        except:
            return false
            raise
            
        return true

    async def on_message(self, message): #currently boilerplate
        channel = message.channel
        author = message.author
        server = message.server
        
        if self.is_command(message):
            return
        
        if message.server is None:
            return
        
        if author == self.bot.user:
            return
        
        if not user_allowed(message):
            return
        
        return
        
        
    def update_csvs(self):
        """ Download/update CSVs if so much time has passed since last update """
        
        self.timestamp = self.settings['timestamp']
        self.maxDataAgeMinutes = self.settings['maxDataAgeMinutes']
        
        if not self.maxDataAgeMinutes:
            if self.maxDataAgeMinutes < 1:
                self.maxDataAgeMinutes = 180
        
        age_delta = epoch_now() - self.timestamp
        
        if (age_delta < self.maxDataAgeMinutes):
            return true
        
        if download_file(self.settings['fields'], "data/ordmcp/fields_dl.csv"):
            remove_file("data/ordmcp/fields.csv")
            os.rename("data/ordmcp/fields_dl.csv", "data/ordmcp/fields.csv")
        else:
            return false
        
        if download_file(self.settings['methods'], "data/ordmcp/methods_dl.csv"):
            remove_file("data/ordmcp/methods.csv")
            os.rename("data/ordmcp/methods_dl.csv", "data/ordmcp/methods.csv")        
        else:
            return false
        
        if download_file(self.settings['params'], "data/ordmcp/params_dl.csv"):
            remove_file("data/ordmcp/params.csv")
            os.rename("data/ordmcp/params_dl.csv", "data/ordmcp/params.csv")
        else:
            return false
        
        return true
        
    def search_csv(csvfile, searchterm):
        results = []
        with open(csvfile) as f:
            reader = csv.reader(f)
            next(reader, None) # discard the header
            for row in reader:
                for field in row:
                    if searchterm in field:
                        results.append(row)
        return results

    @commands.command(no_pm=True, pass_context=True)
    #@checks.admin_or_permissions(manage_roles=True)
    async def mcp(self, ctx, message=None):
        """Adds a role to multiple users,
        
        rolebulk <add/remove> <"rollname"> <@mention1, @mention2, ...>

        Role name must be in quotes if there are spaces."""
        
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if message is None:
            return await self.bot.say('You must specify a search term')
        
        if method.lower() not in {"fields", "methods", "params"}:
            return await self.bot.say('You must specify either "fields", "methods", or "params"')
        
        if not update_csvs():
            return await self.bot.say('There was an error downloading the csv files from mcp')
        
        fieldsResults = search_csv("data/ordmcp/fields.csv", message)
        methodsResults = search_csv("data/ordmcp/methods.csv", message)
        paramsResults = search_csv("data/ordmcp/params.csv", message)
        
        response = "Found the following: \nFields:```\n{}\n```\nMethods:```\n{}\n```\nFields:```\n{}\n```".format("\n".join(fieldsResults), "\n".join(methodsResults), "\n".join(paramsResults))
        
        return await self.bot.say(response)


    @commands.command(no_pm=True, pass_context=True)
    #@checks.admin_or_permissions(manage_roles=True)
    async def mcp2(self, ctx, method, rolename, message=None):
        """STILL IN TESTING/DEVELOPMENT"""
        
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if message is None:
            return
        
        if method.lower() not in {"fields", "methods", "params"}:
            return await self.bot.say('You must specify either "fields", "methods", or "params"')
        
        if (method.lower() == "fields"):
            return
        elif (method.lower() == "methods"):
            return
        elif (method.lower() == "params"):
            return

def epoch_now():
    """
    Creates an integer representing current timestamp from epoch date
    Returns a value where 1 = one minute    
    """
    
    epoch = datetime.datetime.utcfromtimestamp(0)
    now = datetime.datetime.utcnow()
    delta = now - epoch
    return int(delta.total_seconds() / 60)


def check_folder():
    theDir = "data/ordmcp"
    if not os.path.exists(theDir):
        print("Creating {} folder".format(theDir))
        os.makedirs(theDir)


def check_file():
    data = {'fields': 'http://export.mcpbot.bspk.rs/fields.csv', 
            'methods': 'http://export.mcpbot.bspk.rs/methods.csv',
            'params': 'http://export.mcpbot.bspk.rs/params.csv', 
            'maxDataAgeMinutes': 240,
            'timestamp': epoch_now()
            }
    f = "data/ordmcp/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)



def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(ORDMCP(bot))
