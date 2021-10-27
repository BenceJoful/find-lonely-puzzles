'''
todo:
    search archives and introduce more choices based on reactions (ratings, tags)
    maybe? make username @ (only if able to not mention).  Allowed_mentiond = None
    download all data to allow making top 10 lists based on reactions.
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
    days_to_search = int(os.environ["DAYS_TO_SEARCH"])
    bot_commands_channel_id = int(os.environ['BOT_COMMANDS_CHANNEL_ID'])
    reaction_threshhold = int(os.environ["REACTION_THRESHHOLD"])
    solved_emoji_name = os.environ['SOLVED_EMOJI_NAME']
    broken_emoji_name = os.environ['BROKEN_EMOJI_NAME']
except:
    config= configparser.ConfigParser()
    config.read('localconfig.ini')
    access_token = config['db']['ACCESS_TOKEN']
    guild_id = config['db']['GUILD_ID']
    sudoku_submissions_channel_id = int(config['db']['SUDOKU_SUBMISSIONS_CHANNEL_ID'])
    other_submissions_channel_id = int(config['db']['OTHER_SUBMISSIONS_CHANNEL_ID'])
    max_puzzles_return = int(config['db']['MAX_PUZZLES_RETURN'])
    days_to_search = int(config['db']['DAYS_TO_SEARCH'])
    bot_commands_channel_id = int(config['db']['BOT_COMMANDS_CHANNEL_ID'])
    reaction_threshhold = int(config['db']['REACTION_THRESHHOLD'])
    solved_emoji_name = config['db']['SOLVED_EMOJI_NAME']
    broken_emoji_name = config['db']['BROKEN_EMOJI_NAME']

    
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
            name="search_terms",
            description="Words that are required to exist in the submission",
            required=False,
            option_type=3
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
            name="solved_count",
            description="Number of people who marked it as Solved (default 0)",
            required=False,
            option_type=4
        )
    ]
)
async def _lonelypuzzles(ctx: SlashContext, puzzle_type: str, search_terms: str = "", max_age: int = days_to_search, solved_count: int = 0):
    response = await findLonelyPuzzles(ctx, puzzle_type, search_terms,max_age,solved_count)
    await ctx.send(embed = response[0], hidden = response[1])

@bot.command()
async def lonelypuzzles(ctx,puzzle_type: str, search_terms: str = "", max_age: int = days_to_search, solved_count: int = 0):
    response = await findLonelyPuzzles(ctx, puzzle_type, search_terms,max_age,solved_count)
    if (not response[1]):  #can't do hidden, apparently, so just silently fail in other channels
        await ctx.send(embed = response[0])

async def findLonelyPuzzles(ctx, puzzle_type, search_terms,max_age,solved_count):
    if (ctx.channel.id != bot_commands_channel_id):
        return (discord.Embed(description="I'd love to look for those kinds of puzzles for you, but I can only respond to messages in [#bot-commands](https://discord.com/channels/"+guild_id+"/"+str(bot_commands_channel_id)+"/).  Let's talk over there!"),True)

    search_channel_id = 0
    if puzzle_type == 'sudoku':
        search_channel_id = sudoku_submissions_channel_id

    if puzzle_type == 'other':
        search_channel_id = other_submissions_channel_id

    if search_channel_id > 0:
        replymsg = ''
        foundPuzzles = []

        searchTermsList = search_terms.lower().split()

        from_date = datetime.datetime.now() - datetime.timedelta(days= max_age)
        async for msg in bot.get_channel(search_channel_id).history(after=from_date,limit=None):

            solvedcnt = 0
            brokencnt = 0
            for reaction in msg.reactions:
                if (reaction.custom_emoji):
                    if (reaction.emoji.name == solved_emoji_name):
                        solvedcnt += reaction.count
                    elif (reaction.emoji.name == broken_emoji_name):
                        brokencnt += reaction.count

            if solvedcnt <= reaction_threshhold + solved_count and brokencnt == reaction_threshhold:
                #check search_terms
                msgContentToSearch = msg.content.lower()
                hasAllTerms = True
                if (len(searchTermsList)>0):
                    for term in searchTermsList:
                        if term not in msgContentToSearch:
                            hasAllTerms = False
                            break
                if hasAllTerms:
                    #post first line of text (up to 50 characters) then the message ID.
                    firstLine = msg.content.splitlines()[0].replace("~","").replace("*","").replace("_","")[:50]
                    foundPuzzles.append("\n• [" + firstLine + "](https://discord.com/channels/"+guild_id+"/"+str(msg.channel.id)+"/" + str(msg.id) + ") by "+msg.author.name)

        if len(foundPuzzles) == 0:
            replymsg = "No puzzles found matching the criteria."

        foundPuzzlesCount = len(foundPuzzles)
        listedPuzzlesCount = 0
        while len(foundPuzzles) > 0 and len(replymsg+foundPuzzles[0])<4096 and listedPuzzlesCount < max_puzzles_return:
            replymsg += foundPuzzles.pop(0)
            listedPuzzlesCount += 1

        replytitle = str(foundPuzzlesCount)+' '+("Untested " if solved_count == 0 else '')+ \
            puzzle_type+" puzzle"+("" if foundPuzzlesCount == 1 else "s")+" in the past "+str(max_age)+" day"+("" if max_age == 1 else "s" )+ \
            (" with ≤ "+str(solved_count)+" solve"+(+"" if solved_count == 1 else "s") if solved_count != 0 else "") + \
            ":"
        embed = discord.Embed(title=replytitle)
        embed.description=replymsg
        if len(foundPuzzles) > 0:
            embed.set_footer(text="... and "+str(len(foundPuzzles))+" more")

        return (embed,False)

bot.run(access_token)
