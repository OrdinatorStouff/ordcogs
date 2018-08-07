
from random import choice as randchoice
from datetime import datetime as dt
from discord.ext import commands
import discord
import asyncio
from .menu import Menu
from .utils.dataIO import dataIO
from .utils import checks
import os

try:
    import patreon as patreon
    patreonInstalled = True
except:
    patreonInstalled = False


class Patreon():
    """
    Cog for interacting with Patreon API
    
    https://docs.patreon.com
    https://github.com/Patreon/patreon-python
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.menu = self.get_menu()
        self.settings_file = 'data/ordpatreon/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        #if 'consumer_key' in list(self.settings.keys()):
        #    self.consumer_key = self.settings['consumer_key']
        #if 'consumer_secret' in list(self.settings.keys()):
        #    self.consumer_secret = self.settings['consumer_secret']
        #if 'access_token' in list(self.settings.keys()):
        #    self.access_token = self.settings['access_token']
        #if 'access_secret' in list(self.settings.keys()):
        #    self.access_secret = self.settings['access_secret']

    def get_menu(self):
        return Menu(self.bot)
            
    def authenticate(self):
        """Authenticate with Patreon API"""
        #auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        #auth.set_access_token(self.access_token, self.access_secret)
        #return tw.API(auth)







def check_folder():
    if not os.path.exists("data/ordpatreon"):
        print("Creating data/ordpatreon folder")
        os.makedirs("data/ordpatreon")


def check_file():
    # data = {'consumer_key': '', 'consumer_secret': '',
    #        'access_token': '', 'access_secret': '', 'servers': {}}
    f = "data/ordpatreon/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    if not patreonInstalled:
        bot.pip_install("patreon")
        import patreon as patreon
    n = Patreon(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(n.user_loop())
    bot.add_cog(n)
