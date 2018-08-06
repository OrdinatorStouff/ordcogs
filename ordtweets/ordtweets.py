from random import choice as randchoice
from datetime import datetime as dt
from discord.ext import commands
import discord
import asyncio
import shlex
from .menu import Menu
from .utils.dataIO import dataIO
from .utils import checks
try:
    import tweepy as tw
    twInstalled = True
except:
    twInstalled = False
import os


#Originally taken/modified from https://github.com/palmtree5/palmtree5-cogs

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class Tweets():
    """Cog for displaying info from Twitter's API"""
    def __init__(self, bot):
        self.bot = bot
        self.menu = self.get_menu()
        self.settings_file = 'data/ordtweets/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        if 'consumer_key' in list(self.settings.keys()):
            self.consumer_key = self.settings['consumer_key']
        if 'consumer_secret' in list(self.settings.keys()):
            self.consumer_secret = self.settings['consumer_secret']
        if 'access_token' in list(self.settings.keys()):
            self.access_token = self.settings['access_token']
        if 'access_secret' in list(self.settings.keys()):
            self.access_secret = self.settings['access_secret']

    def get_menu(self):
        return Menu(self.bot)
            
    def authenticate(self):
        """Authenticate with Twitter's API"""
        auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        return tw.API(auth)

    async def tweet_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        colour =\
            ''.join([randchoice('0123456789ABCDEF')
                     for x in range(6)])
        colour = int(colour, 16)
        created_at = s.created_at
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        post_url =\
            "https://twitter.com/{}/status/{}".format(s.user.screen_name, s.id)
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(title="Tweet by {}".format(s.user.name),
                           colour=discord.Colour(value=colour),
                           url=post_url,
                           description=desc)
        em.add_field(name="Text", value=s.text)
        em.add_field(name="Retweet count", value=str(s.retweet_count))
        if hasattr(s, "extended_entities"):
            em.set_image(url=s.extended_entities["media"][0]["media_url"] + ":thumb")
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            return await self.tweet_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.tweet_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)




    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_server=True)
    async def tweet1(self, ctx, account=None, *tweetmsg):
        """Send a Tweet"""
        
        #setup working vars, mostly just for convenience
        message = ctx.message
        channel = message.channel
        author = message.author
        author_name = author.name if author.name else author.display_name 
        msg_time = message.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        maxlen = 140
        
        #BASIC PASS CHECK
        #parse "account" var that it a valid condition
        valid_accts = ["ATM", "ATC"]
        account = account.upper()
        if not account in valid_accts:
            return await self.bot.delete_message(message)
            await self.bot.say("__**ERROR:** {}, your tweet could not be sent.__\n You must specify which acct to tweet to.\nValid choices are: **{}**\n\n`!tweet1 <account> <your text to tweet>`".format(author.mention, ", ".join(valid_accts)))
        
        #BASIC PASS CHECK
        #make sure there is SOMETHING to be tweeted
        if not tweetmsg:
            await self.bot.say("__**ERROR:** {}, your tweet could not be sent.__\n You must specify some text to tweet:\n\n`!tweet1 <account> <your text to tweet>`".format(author.mention))
            return await self.bot.delete_message(message)
        
        #supposedly this is "twitter blue" ¯\_(ツ)_/¯
        color = int("4099FF", 16)
        
        #an image for "in progress tweet waiting to be confirmed"
        img_compose = r"https://g.twimg.com/about/feature-corporate/image/composetweet.png"
        
        #parse the tweet message -- code taken/adapted from rhino bot
        #TODO: clean this up or do it a different way IF it becomes buggy
        """
        try:
            tweetmsg = shlex.split(' '.join(tweetmsg))
        except ValueError:
            return await self.bot.say("Please quote the tweet message properly (ie surround tweet with \"double-quotes\")")
        """
        if tweetmsg[0][0] in '\'"':
            lchar = tweetmsg[0][0]
            tweetmsg[0] = tweetmsg[0].lstrip(lchar)
            tweetmsg[-1] = tweetmsg[-1].rstrip(lchar)
        tweetmsg = ' '.join(tweetmsg)
        tweetlen = len(tweetmsg)
        
        #BASIC PASS CHECK
        #make sure message is not past twitter limits, warn/stop if it is
        if (tweetlen > maxlen):
            extrachars = tweetlen - maxlen
            lefttweet = tweetmsg[:maxlen]
            righttweet = tweetmsg[-extrachars:]
            await self.bot.say("__**ERROR:** {}, your tweet could not be sent.__\n Message must be __{}__ characters or less (*message was {}; {} too many*):\n\n`{}` ***~~`{}`~~***".format(author.mention, maxlen, tweetlen, extrachars, lefttweet, righttweet))
            return await self.bot.delete_message(message)

        #instanciate twitter login
        #TODO: switch conditions for multiple accounts
        twitter_api = self.authenticate()
        tw_user = str(twitter_api.me().screen_name)
        
        #create embed for "ask for confirmation" message
        compose_em = discord.Embed(title="Confirm Tweet to __{}__?".format(tw_user),
                           color=discord.Color(value=color),
                           url=r"http://twitter.com/",
                           description=" ",
                           type="rich")
        #compose_em.set_thumbnail(url=img_compose, width=32, height=32)
        compose_em.add_field(inline=False, name="**\"**", value="**{}**".format(tweetmsg))
        compose_em.add_field(inline=False, name="**\"**", value="*{} Characters*".format(str(tweetlen)))
        compose_em.set_footer(text="Invoked by {} at ~{}".format(author_name, msg_time))
        
        #send the message with tweet details
        confirm_message = await self.bot.send_message(channel, embed=compose_em)
        
        #delete the invoking command message (bot needs manage messages permission)
        await self.bot.delete_message(message)
        
        #create object on that message waiting for response
        confirm_answer = await self.menu.menu(ctx, _type=2, timeout=30, messages=confirm_message)

        #to keep things tidy we're going to edit the original "confirm" message prompt       
        if confirm_answer == True:
            await self.bot.edit_message(message=confirm_message, new_content="Tweet confirmed... Sending to Twitter...")
            #await self.bot.clear_reactions(message=confirm_message)
            #wait self.bot.say("Confirmed")
        else:
            await self.bot.edit_message(message=confirm_message, new_content="Tweet Cancelled or timed out...")
            return await self.bot.delete_message(confirm_message)
            #await self.bot.clear_reactions(message=confirm_message)
            #await self.bot.say("Cancelled")
            

        #DEBUG: Test url of one of our own tweets
        #https://twitter.com/AllTheMods/status/875022206677508097
        
        ### THIS WILL POST A TWEET LIFE -- UN-COMMENT AT RISK OF PAIN AND SUFFERING
        tweet = twitter_api.update_status(status = tweetmsg)
        
        #DEBUG: use old status for testing;
        #tweet = twitter_api.get_status(875022206677508097)
        
        tweet_time = tweet.created_at #datetime
        tweet_time = tweet_time.strftime("%Y-%m-%d %H:%M:%S")
        tweet_user = tweet.user.screen_name #api user
        tweet_thumb = tweet.user.profile_image_url
        tweet_text = tweet.text
        tweet_url = "https://twitter.com/{}/status/{}".format(tweet_user, tweet.id)
        
        tweet_em = discord.Embed(title="Tweet SENT to __{}__".format(tweet_user),
                           color=discord.Color(value=color),
                           url=tweet_url,
                           description=tweet_text,
                           type="rich")
        #tweet_em.set_thumbnail(url=img_compose, width=32, height=32)
        tweet_em.set_thumbnail(url=tweet_thumb)
        if hasattr(tweet, "extended_entities"):
            em.set_image(url=tweet.extended_entities["media"][0]["media_url"] + ":thumb")
        tweet_em.set_footer(text="Invoked by {}, Tweet time: {} UTC".format(author_name, tweet_time))
        
        #DEBUG LINE TO REMOVE:
        #await self.bot.say("**DEBUG:** *The below tweet is an \"example\" since this code is not connected \"live\" yet*")
        
        await self.bot.send_message(channel, embed=tweet_em)
        await self.bot.delete_message(confirm_message)
        

        """
        ###FROM tweets cog
        created_at = s.created_at
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
        post_url =\
            "https://twitter.com/{}/status/{}".format(s.user.screen_name, s.id)
        desc = "Created at: {}".format(created_at)
        em = discord.Embed(title="Tweet by {}".format(s.user.name),
                           colour=discord.Colour(value=colour),
                           url=post_url,
                           description=desc)
        em.add_field(name="Text", value=s.text)
        em.add_field(name="Retweet count", value=str(s.retweet_count))
        if hasattr(s, "extended_entities"):
            em.set_image(url=s.extended_entities["media"][0]["media_url"] + ":thumb")
        """




    @commands.group(pass_context=True, no_pm=True, name='tweets')
    @checks.admin_or_permissions(manage_server=True)
    async def _tweets(self, ctx):
        """Gets various information from Twitter's API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)



    @_tweets.command(pass_context=True, no_pm=True, name='getuser')
    @checks.admin_or_permissions(manage_server=True)
    async def get_user(self, ctx, username: str):
        """Get info about the specified user"""
        message = ""
        if username is not None:
            api = self.authenticate()
            user = api.get_user(username)

            colour =\
                ''.join([randchoice('0123456789ABCDEF')
                     for x in range(6)])
            colour = int(colour, 16)
            url = "https://twitter.com/" + user.screen_name
            emb = discord.Embed(title=user.name,
                                colour=discord.Colour(value=colour),
                                url=url,
                                description=user.description)
            emb.set_thumbnail(url=user.profile_image_url)
            emb.add_field(name="Followers", value=user.followers_count)
            emb.add_field(name="Friends", value=user.friends_count)
            if user.verified:
                emb.add_field(name="Verified", value="Yes")
            else:
                emb.add_field(name="Verified", value="No")
            footer = "Created at " + user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            emb.set_footer(text=footer)
            await self.bot.send_message(ctx.message.channel, embed=emb)
        else:
            message = "Uh oh, an error occurred somewhere!"
            await self.bot.say(message)

    @_tweets.command(pass_context=True, no_pm=True, name='gettweets')
    @checks.admin_or_permissions(manage_server=True)
    async def get_tweets(self, ctx, username: str, count: int):
        """Gets the specified number of tweets for the specified username"""
        cnt = count
        if count > 25:
            cnt = 25

        if username is not None:
            if cnt < 1:
                await self.bot.say("I can't do that, silly! Please specify a \
                    number greater than or equal to 1")
                return
            msg_list = []
            api = self.authenticate()
            try:
                for status in\
                        tw.Cursor(api.user_timeline, id=username).items(cnt):
                    if not status.text.startswith("@"):
                        msg_list.append(status)
            except tw.TweepError as e:
                await self.bot.say("Whoops! Something went wrong here. \
                    The error code is " + str(e))
                return
            if len(msg_list) > 0:
                await self.tweet_menu(ctx, msg_list, page=0, timeout=30)
            else:
                await self.bot.say("No tweets available to display!")
        else:
            await self.bot.say("No username specified!")
            return


def check_folder():
    if not os.path.exists("data/ordtweets"):
        print("Creating data/ordtweets folder")
        os.makedirs("data/ordtweets")


def check_file():
    data = {'consumer_key': '', 'consumer_secret': '',
            'access_token': '', 'access_secret': '', 'servers': {}}
    f = "data/ordtweets/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    if not twInstalled:
        bot.pip_install("tweepy")
        import tweepy as tw
    n = Tweets(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(n.user_loop())
    bot.add_cog(n)
