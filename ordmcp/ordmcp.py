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
from urllib.parse import urlparse
from cogs.utils.settings import Settings

#TODO -- many imports here are not needed, trim list


__author__ = "Ordinator"


class ORDMCP:
    """Custom basic MCP search by Ordinator"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/ordmcp/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        
        """ # OLD CODE
        if 'fields' in list(self.settings.keys()):
            self.fieldsUrl = self.settings['fields']
        if 'methods' in list(self.settings.keys()):
            self.methodUrl = self.settings['methods']
        if 'params' in list(self.settings.keys()):
            self.paramsUrl = self.settings['params']
        """
        
        self.data_files = self.settings['data_files']
        self.maxDataAgeMinutes = self.settings['maxDataAgeMinutes']
        self.timestamp = self.settings['timestamp']
        
        # default data age setting if too low or missing
        if isInt(self.maxDataAgeMinutes):
            if int(self.maxDataAgeMinutes) < 1:
                self.maxDataAgeMinutes = 180
        else:
            self.maxDataAgeMinutes = 180
    
    
    def is_command(self, msg):
        for m in self.bot.settings.get_prefixes(msg.server):
            if msg.content.startswith(m):
                return True
        return False

    
    async def remove_file(self, filename):
        try:
            os.remove(filename)
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occurred


    async def download(self, url, fileName):
        """ https://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way """
        r = urllib2.urlopen(urllib2.Request(url))
        try:
            with open(fileName, 'wb') as f:
                shutil.copyfileobj(r,f)
        finally:
            r.close()
        
        
    async def update_csvs(self):
        """ Download/update CSVs if so much time has passed since last update """
        
        self.timestamp = self.settings['timestamp']
        self.maxDataAgeMinutes = self.settings['maxDataAgeMinutes']

        age_delta = epoch_now() - self.timestamp
        
        if (age_delta < self.maxDataAgeMinutes):
            return True
            
        print('Updating MCP data file extracts...')
        
        for url in self.data_files:
            fileName = fileName or os.path.basename(urlparse.urlsplit(url)[2])
            tempName = fileName + ".tmp"
            await download(url, tempName)
            self.remove_file(self, fileName)
            os.rename(tempName, fileName)

        return True

        
    async def search_csv(self, csvfile, searchterm):
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
        """
            Searches MCP across all 3 csvs at the same time
        """
        
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if message is None:
            return await self.bot.say('You must specify a search term')
        
        csv_check = await self.update_csvs()
        
        if not csv_check:
            return await self.bot.say('There was an error downloading the csv files from mcp')
        
        fieldsResults = await self.search_csv("data/ordmcp/fields.csv", message)
        methodsResults = await self.search_csv("data/ordmcp/methods.csv", message)
        paramsResults = await self.search_csv("data/ordmcp/params.csv", message)
        
        response = "Found the following: \nFields:```\n{}\n```\nMethods:```\n{}\n```\nFields:```\n{}\n```".format("\n".join(fieldsResults), "\n".join(methodsResults), "\n".join(paramsResults))
        
        return await self.bot.say(response)


def epoch_now():
    """
    Creates an integer representing current timestamp from epoch date
    Returns a value where 1 = one minute    
    """
    
    epoch = datetime.datetime.utcfromtimestamp(0)
    now = datetime.datetime.utcnow()
    delta = now - epoch
    return int(delta.total_seconds() / 60)


def isInt(v):
    try:     i = int(v)
    except:  return False
    return True


def check_folder():
    theDir = "data/ordmcp"
    if not os.path.exists(theDir):
        print("Creating {} folder".format(theDir))
        os.makedirs(theDir)


def check_file():
    data = {'data_files': {
                'http://export.mcpbot.bspk.rs/fields.csv', 
                'http://export.mcpbot.bspk.rs/methods.csv',
                'http://export.mcpbot.bspk.rs/params.csv'
                },
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
