
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
        if 'client_id' in list(self.settings.keys()):
            self.client_id = self.settings['client_id']
        if 'client_secret' in list(self.settings.keys()):
            self.client_secret = self.settings['client_secret']
        if 'creator_id' in list(self.settings.keys()):
            self.creator_id = self.settings['creator_id']

    def get_menu(self):
        return Menu(self.bot)

    def authenticate(self):
        """Authenticate with Patreon API"""
        oauth_client = patreon.OAuth(self.client_id, self.client_secret)
        tokens = oauth_client.get_tokens(request.args.get('code'), '/oauth/redirect')
        access_token = tokens['access_token']
        api_client = patreon.API(access_token)
        return api_client

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_server=True)
    async def pattest1(self, ctx):
        """Patreon Test Command"""
        
        #setup working vars, mostly just for convenience
        message = ctx.message
        channel = message.channel
        author = message.author
        author_name = author.name if author.name else author.display_name 
        msg_time = message.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        
        api_client = self.authenticate()
        user_response = api_client.fetch_user()
        user = user_response.data()
        pledges = user.relationship('pledges')
        pledge = pledges[0] if pledges and len(pledges) > 0 else None
        
        await self.bot.say(user)
        await self.bot.say(pledge)
        
        return





def check_folder():
    if not os.path.exists("data/ordpatreon"):
        print("Creating data/ordpatreon folder")
        os.makedirs("data/ordpatreon")

def check_file():
    data = {'client_id': '', 'client_secret': '',
            'creator_id': '', 'servers': {}}
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
    bot.add_cog(n)
