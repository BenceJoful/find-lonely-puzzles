'''
todo:
    search archives and introduce more choices based on reactions (ratings, tags)
    maybe? make username @ (only if able to not mention).  Allowed_mentiond = None
    download all data to allow making top 10 lists based on reactions.
    minimum age (0 days default?)

'''

import os
import datetime
import configparser
from re import search
import traceback
import discord
from discord import channel
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

try:
    access_token= os.environ["ACCESS_TOKEN"]
    guild_id = os.environ["GUILD_ID"]
    sudoku_submissions_channel_id = int(os.environ["SUDOKU_SUBMISSIONS_CHANNEL_ID"])
    other_submissions_channel_id = int(os.environ["OTHER_SUBMISSIONS_CHANNEL_ID"])
    word_submissions_channel_id = int(os.environ["WORD_SUBMISSIONS_CHANNEL_ID"])
    max_puzzles_return = int(os.environ["MAX_PUZZLES_RETURN"])
    days_to_search = int(os.environ["DAYS_TO_SEARCH"])
    reaction_threshhold = int(os.environ["REACTION_THRESHHOLD"])
    solved_emoji_name = os.environ['SOLVED_EMOJI_NAME']
    broken_emoji_name = os.environ['BROKEN_EMOJI_NAME']
    calling_bot_id = int(os.environ['CALLING_BOT_ID'])
    log_channel_id = int(os.environ['LOG_CHANNEL_ID'])
except:
    config = configparser.ConfigParser()
    config.read('localconfig.ini')
    access_token = config['db']['ACCESS_TOKEN']
    guild_id = config['db']['GUILD_ID']
    sudoku_submissions_channel_id = int(config['db']['SUDOKU_SUBMISSIONS_CHANNEL_ID'])
    other_submissions_channel_id = int(config['db']['OTHER_SUBMISSIONS_CHANNEL_ID'])
    word_submissions_channel_id = int(config['db']["WORD_SUBMISSIONS_CHANNEL_ID"])
    max_puzzles_return = int(config['db']['MAX_PUZZLES_RETURN'])
    days_to_search = int(config['db']['DAYS_TO_SEARCH'])
    reaction_threshhold = int(config['db']['REACTION_THRESHHOLD'])
    solved_emoji_name = config['db']['SOLVED_EMOJI_NAME']
    broken_emoji_name = config['db']['BROKEN_EMOJI_NAME']
    calling_bot_id = int(config['db']['CALLING_BOT_ID'])
    log_channel_id = int(config['db']['LOG_CHANNEL_ID'])

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default(),help_command=None)
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
                manage_commands.create_choice(
                    name="Word Puzzles",
                    value="word"
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
                ),
                manage_commands.create_choice(
                    name="Year",
                    value=365
                )
            ]
        ),
        manage_commands.create_option(
            name="solved_count",
            description="Number of people who marked it as Solved (0 default)",
            required=False,
            option_type=4
        )
    ]
)
async def _lonelypuzzles(ctx: SlashContext, puzzle_type: str, search_terms: str = "", max_age: int = days_to_search, solved_count: int = 0):
    send_channel = ctx.author.dm_channel
    if (send_channel is None):
        send_channel = await ctx.author.create_dm()

    await ctx.reply("I'm finding lonely puzzles, please check your DMs for details",hidden=True)
    
    response = await findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count,ctx.author.name)
    await send_channel.send(embed = response)

'''@bot.command()
async def lonelypuzzles(ctx,puzzle_type: str, search_terms: str = "", max_age: int = days_to_search, solved_count: int = 0):
    if (ctx.channel.id == bot_commands_channel_id):
        response = await findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count)
        await ctx.send(embed = response)'''

@bot.listen()
async def on_message(message):
    #print(message.author.id)
    #if it mentions me, process like a command.
    if (bot.user in message.mentions and bot.user != message.author):
        args = message.content.split()
        if (message.author.id == calling_bot_id and args[1]=="echo"):
            send_channel = message.author.dm_channel
            if (send_channel is None):
                send_channel = await message.author.create_dm()

            await message.channel.send(embed=discord.Embed(description=send_channel.id))

            return
        if (message.author.id == calling_bot_id and len(args)==2 and args[1]=="updatepins"):
            #updates pins in this channel
            for msg in await message.channel.pins():
                if (msg.pinned and msg.author == bot.user and len(msg.embeds)>0):
                    titleargs = msg.embeds[0].title.split(' ')
                    
                    puzzle_type=''
                    max_age=7
                    solved_count=0
                    search_terms=[]
                    finding_search_terms=False
                    while len(titleargs)>0:
                        arg = titleargs.pop(0)
                        if (puzzle_type == '' and arg in ['sudoku','other','word']):
                            puzzle_type = arg
                        elif(arg == 'past'):
                            max_age = int(titleargs.pop(0))
                        elif(arg == '≤'):
                            solved_count = int(titleargs.pop(0))
                        elif(arg[0] == '"'):
                            finding_search_terms = True

                        if (finding_search_terms):
                            if (arg[-1]=='"'):
                                finding_search_terms=False
                                search_terms.append(arg[:-1])
                                search_terms[0]=search_terms[0][1:]
                            elif (arg[-2]=='"'):
                                finding_search_terms=False
                                search_terms.append(arg[:-2])
                                search_terms[0]=search_terms[0][1:]
                            else:
                                search_terms.append(arg)

                    response = await findLonelyPuzzles(puzzle_type, ' '.join(search_terms),max_age,solved_count,"updating pins")
                    await msg.edit(embed = response)

            return
        else:
            send_channel = message.channel
            if (message.author.id != calling_bot_id):
                send_channel = message.author.dm_channel
                if (send_channel is None):
                    send_channel = await message.author.create_dm()

            helpmsg = "Format message like: ```@PuzzleDigestBot lonelypuzzles puzzle_type max_age solved_count search terms```\npuzzle_type is 'sudoku', 'word', or 'other'  \nmax_age and solved_count must be integers.  \nSearch terms are optional, and not in quotes."

            if len(args) > 4:
                if args[1] == 'lonelypuzzles':
                    puzzle_type = args[2]
                    max_age = 0
                    try:
                        max_age = int(args[3])
                    except ValueError:
                        await send_channel.send(embed = discord.Embed(description='max_age is not an integer.\n'+helpmsg))
                        return

                    solved_count = 0
                    try:
                        solved_count = int(args[4])
                    except ValueError:
                        await send_channel.send(embed = discord.Embed(description='solved_count is not an integer.\n'+helpmsg))
                        return

                    search_terms = " ".join(args[5:])
                    response = await findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count,message.author.name)
                    await send_channel.send(embed = response)
                else:
                    await send_channel.send(embed = discord.Embed(description='No command given.\n'+helpmsg))
            else:
                await send_channel.send(embed = discord.Embed(description='Insufficient arguments given.\n'+helpmsg))

async def findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count, author):
    search_channel_id = 0
    if puzzle_type == 'sudoku':
        search_channel_id = sudoku_submissions_channel_id

    if puzzle_type == 'other':
        search_channel_id = other_submissions_channel_id

    if puzzle_type == 'word':
        search_channel_id = word_submissions_channel_id

    if search_channel_id > 0:
        replymsg = ''
        foundPuzzles = []

        searchTermsList = search_terms.lower().split()

        from_date = datetime.datetime.now() - datetime.timedelta(days= max_age)
        async for msg in bot.get_channel(search_channel_id).history(after=from_date,limit=None):
            try:
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
                        #post first line of text (up to 50 characters) linking to the message.
                        firstLine = msg.content.splitlines()[0].replace("~","").replace("*","").replace("_","")[:50]
                        foundPuzzles.append("\n• "+("("+str(solvedcnt - reaction_threshhold)+") " if solved_count > 0 else "")+ \
                            "[" + firstLine + "](https://discord.com/channels/"+guild_id+"/"+str(msg.channel.id)+"/" + str(msg.id) + ") by "+msg.author.name)
            except:
                print("Failed to process message:")
                print(msg)
                traceback.print_exc()

        if len(foundPuzzles) == 0:
            replymsg = "No puzzles found matching the criteria."

        foundPuzzlesCount = len(foundPuzzles)
        listedPuzzlesCount = 0
        while len(foundPuzzles) > 0 and len(replymsg+foundPuzzles[0])<4096 and listedPuzzlesCount < max_puzzles_return:
            replymsg += foundPuzzles.pop(0)
            listedPuzzlesCount += 1

        replytitle = str(foundPuzzlesCount)+' '+("Untested " if solved_count == 0 else '') + \
            puzzle_type+" puzzle"+("" if foundPuzzlesCount == 1 else "s") + \
            " in the past "+str(max_age)+" day" + ("" if max_age == 1 else "s" ) + \
            (' containing "' + search_terms +'"' if search_terms != "" else "") + \
            (" with ≤ "+str(solved_count)+" solve" + ("" if solved_count == 1 else "s") if solved_count != 0 else "") + \
            ":"
        embed = discord.Embed(title=replytitle)
        embed.description=replymsg
        if len(foundPuzzles) > 0:
            embed.set_footer(text="... and "+str(len(foundPuzzles))+" more")

        await logUsage(puzzle_type, search_terms, max_age, solved_count, author, foundPuzzlesCount)
        return embed

@bot.event
async def on_ready():
    print('{0.user} has logged in'.format(bot))

async def logUsage(puzzle_type, search_terms, max_age, solved_count, author, found_count):
    log_channel = await bot.fetch_channel(log_channel_id)
    #get most recent Log message by this bot there.  Either edit it or create new one.
    log_title = "Log "+datetime.datetime.now(datetime.timezone.utc).strftime("%m/%d/%Y")
    log_message = None

    async for msg in log_channel.history():
        if (msg.author == bot.user and len(msg.embeds)>0 and msg.embeds[0].title == log_title):
            log_message = msg
            break

    embed = discord.Embed(title=log_title)
    embed.description=datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")+" "+author+" " +"("+str(found_count)+"): "+puzzle_type + " " + str(max_age) + " " + str(solved_count) + " " + search_terms

    if (log_message == None or len(log_message.embeds[0].description) > 3500):
        await log_channel.send(embed = embed)
    else:
        embed.description=log_message.embeds[0].description+'\n'+embed.description
        await log_message.edit(embed = embed)
        #await log_message.delete()

bot.run(access_token)