'''
todo:
    search archives and introduce more choices based on reactions (ratings, tags)
'''

import os
import datetime
import configparser
import discord
from discord import colour
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

try:
    access_token= os.environ["ACCESS_TOKEN"]
    guild_id = os.environ["GUILD_ID"]
    sudoku_submissions_channel_id = int(os.environ["SUDOKU_SUBMISSIONS_CHANNEL_ID"])
    other_submissions_channel_id = int(os.environ["OTHER_SUBMISSIONS_CHANNEL_ID"])
    max_puzzles_return = int(os.environ["MAX_PUZZLES_RETURN"])
    reaction_threshhold = int(os.environ["REACTION_THRESHHOLD"])
    days_to_search = int(os.environ["DAYS_TO_SEARCH"])
    bot_commands_channel_id = int(os.environ['BOT_COMMANDS_CHANNEL_ID'])
except:
    config= configparser.ConfigParser()
    config.read('localconfig.ini')
    access_token = config['db']['ACCESS_TOKEN']
    guild_id = config['db']['GUILD_ID']
    sudoku_submissions_channel_id = int(config['db']['SUDOKU_SUBMISSIONS_CHANNEL_ID'])
    other_submissions_channel_id = int(config['db']['OTHER_SUBMISSIONS_CHANNEL_ID'])
    max_puzzles_return = int(config['db']['MAX_PUZZLES_RETURN'])
    reaction_threshhold = int(config['db']['REACTION_THRESHHOLD'])
    days_to_search = int(config['db']['DAYS_TO_SEARCH'])
    bot_commands_channel_id = int(config['db']['BOT_COMMANDS_CHANNEL_ID'])
    
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(
    name="lonelypuzzles", description="Search for puzzles which need testing", 
    options=[
        manage_commands.create_option(
            name="puzzle_type",
            description="Puzzle Type",
            required=True,
            option_type=3,
            choices=[
                manage_commands.create_choice(
                    name="Sudoku",
                    value="sudoku"
                ),
                manage_commands.create_choice(
                    name="Other Puzzles",
                    value="other"
                ),
            ],
        ),
        manage_commands.create_option(
            name="max_age",
            description="Maximum age (1 week default)",
            required=False,
            option_type=4,
            choices=[
                manage_commands.create_choice(
                    name="Day",
                    value=1
                ),
                manage_commands.create_choice(
                    name="Week",
                    value=7
                ),
                manage_commands.create_choice(
                    name="Month",
                    value=30
                )
            ]
        ),
        manage_commands.create_option(
            name="reaction_count",
            description="Number of people who marked it as Solved / Attempted / Broken (default 0)",
            required=False,
            option_type=4
        )
    ]
)
async def _lonelypuzzles(ctx: SlashContext, puzzle_type: str, max_age: int = days_to_search, reaction_count: int = 0):
    if (ctx.channel_id != bot_commands_channel_id):
        await ctx.send("I'd love to look for those kinds of puzzles for you, but I can only respond to messages in [#bot-commands](https://discord.com/channels/"+guild_id+"/"+str(bot_commands_channel_id)+"/).  Let's talk over there!",hidden=True)
        return

    search_channel_id = 0
    if puzzle_type == 'sudoku':
        search_channel_id = sudoku_submissions_channel_id

    if puzzle_type == 'other':
        search_channel_id = other_submissions_channel_id

    if search_channel_id > 0:
        replymsg = ''
        foundPuzzles = 0

        from_date = datetime.datetime.now() - datetime.timedelta(days= max_age)
        async for msg in bot.get_channel(search_channel_id).history(after=from_date,limit=None):
            reactioncnt = 0
            for reaction in msg.reactions:
                reactioncnt+=reaction.count

            if reactioncnt <= reaction_threshhold + reaction_count:
                #post first line of text (up to 50 characters) then the message ID.
                firstLine = msg.content.splitlines()[0].replace("~~","").replace("*","").replace("_","")
                msg_data = "\n• [" + firstLine[:50] + "](https://discord.com/channels/"+guild_id+"/"+str(msg.channel.id)+"/" + str(msg.id) + ") by "+msg.author.name
                if (len(replymsg+msg_data)<4096):
                    replymsg += msg_data    
                    foundPuzzles += 1
                else:
                    break

            if foundPuzzles == max_puzzles_return:
                break

        if foundPuzzles == 0:
            replymsg = "No puzzles found matching the criteria."

        
        replytitle = str(foundPuzzles)+' '+("Untested " if reaction_count == 0 else '')+ \
            puzzle_type+" puzzles in the past "+str(max_age)+" days"+ \
            (" with ≤ "+str(reaction_count)+" reactions" if reaction_count != 0 else "") + \
            ":"
        embed = discord.Embed(title=replytitle)
        embed.description=replymsg

        await ctx.send(embed=embed)

'''
@slash.slash(name="test", description="test desc")
async def _test(ctx: SlashContext):
    if (ctx.channel_id == bot_commands_channel_id):
        await ctx.send("ok")
    else:
        await ctx.send("it's hidden here:",hidden=True)
    #print(ctx.channel)
'''

bot.run(access_token)