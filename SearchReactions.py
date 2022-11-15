from dis import dis
from discord.ext import commands
import discord
from discord import app_commands
import interactions
import datetime

import traceback

import os
import configparser

from azure.cosmos import CosmosClient
from discord.ext.commands import CommandNotFound

try:
    access_token= os.environ["ACCESS_TOKEN"]
    other_access_token= os.environ["OTHER_ACCESS_TOKEN"]
    guild_id = os.environ["GUILD_ID"]
    sudoku_submissions_channel_id = int(os.environ["SUDOKU_SUBMISSIONS_CHANNEL_ID"])
    other_submissions_channel_id = int(os.environ["OTHER_SUBMISSIONS_CHANNEL_ID"])
    word_submissions_channel_id = int(os.environ["WORD_SUBMISSIONS_CHANNEL_ID"])
    archive_channel_id = int(os.environ["ARCHIVE_CHANNEL_ID"])
    monthly_archive_channel_id = int(os.environ["MONTHLY_ARCHIVE_CHANNEL_ID"])
    max_puzzles_return = int(os.environ["MAX_PUZZLES_RETURN"])
    days_to_search = int(os.environ["DAYS_TO_SEARCH"])
    reaction_threshhold = int(os.environ["REACTION_THRESHHOLD"])
    solved_emoji_name = os.environ['SOLVED_EMOJI_NAME']
    broken_emoji_name = os.environ['BROKEN_EMOJI_NAME']
    calling_bot_id = int(os.environ['CALLING_BOT_ID'])
    developer_id = int(os.environ['DEVELOPER_ID'])
    log_channel_id = int(os.environ['LOG_CHANNEL_ID'])
    sql_uri = os.environ['SQL_URI']
    sql_key = os.environ['SQL_KEY']
    server_mod_id = int(os.environ['SERVER_MOD_ID'])

except:
    config = configparser.ConfigParser()
    config.read('localconfig.ini')
    access_token = config['db']['ACCESS_TOKEN']
    other_access_token= config['db']["OTHER_ACCESS_TOKEN"]
    guild_id = config['db']['GUILD_ID']
    sudoku_submissions_channel_id = int(config['db']['SUDOKU_SUBMISSIONS_CHANNEL_ID'])
    other_submissions_channel_id = int(config['db']['OTHER_SUBMISSIONS_CHANNEL_ID'])
    word_submissions_channel_id = int(config['db']["WORD_SUBMISSIONS_CHANNEL_ID"])
    archive_channel_id = int(config['db']["ARCHIVE_CHANNEL_ID"])
    monthly_archive_channel_id = int(config['db']["MONTHLY_ARCHIVE_CHANNEL_ID"])
    max_puzzles_return = int(config['db']['MAX_PUZZLES_RETURN'])
    days_to_search = int(config['db']['DAYS_TO_SEARCH'])
    reaction_threshhold = int(config['db']['REACTION_THRESHHOLD'])
    solved_emoji_name = config['db']['SOLVED_EMOJI_NAME']
    broken_emoji_name = config['db']['BROKEN_EMOJI_NAME']
    calling_bot_id = int(config['db']['CALLING_BOT_ID'])
    developer_id = int(config['db']['DEVELOPER_ID'])
    log_channel_id = int(config['db']['LOG_CHANNEL_ID'])
    sql_uri = config['db']['SQL_URI']
    sql_key = config['db']['SQL_KEY']
    server_mod_id = int(config['db']['SERVER_MOD_ID'])

class SignUpButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Sign Up for Secret Santa', style=discord.ButtonStyle.green, custom_id='persistent_view:SignUpButton')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message('Show the modal feedback screen.', ephemeral=True)
        await interaction.response.send_modal(SignUpFormModal())

async def message_Bence(text, embed = None):
    await bot.get_user(developer_id).send(text, embed=embed)

_dbcontainers = {}
def db_items(container_name):
    if (container_name not in _dbcontainers):
        client = CosmosClient(sql_uri, sql_key)
        database = client.get_database_client("Puzzles")
        _dbcontainers[container_name] = database.get_container_client(container_name)
    return _dbcontainers[container_name]

class SignUpFormModal(discord.ui.Modal, title='Sign Up for Secret Puzzle Santa 2022'):

    form_realName = discord.ui.TextInput(
        label='Real Name (Optional)',
        required=False,
        style=discord.TextStyle.short,
        max_length=100
    )

    form_aboutYou = discord.ui.TextInput(
        #label='Please tell us a little about yourself, which could help your Santa understand you better!',
        label='Please tell Santa a little about yourself!',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_puzzlesEnjoyed = discord.ui.TextInput(
        label='Tell us about what kind of puzzles you enjoy',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_favoritePuzzleTypes = discord.ui.TextInput(
        label='Name some of your favourite puzzle types',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_anythingElse = discord.ui.TextInput(
        label='Anything else you would like to tell Santa!',
        style=discord.TextStyle.long,
        required=False,
        max_length=800
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            name = interaction.user.name
            if self.form_realName.value != "":
                name += f" (real name {self.form_realName.value})"

            embed = discord.Embed(description=f"Name: {name}"+ \
                f"\n\nAbout You: {self.form_aboutYou.value}"+ \
                f"\n\nPuzzles You Enjoy: {self.form_puzzlesEnjoyed.value}"+ \
                f"\n\nFavorite Puzzle Types: {self.form_favoritePuzzleTypes.value}"+ \
                f"\n\nAnything Else: {self.form_anythingElse.value}")

            #send back to user for verification
            await interaction.response.send_message("OK, you are all signed up!  \nHere's the information I received. If you need to change any of it, feel free to hit the Sign Up button and fill in the whole form again - we'll only use the newest entry.  \n\nIf you need to cancel for any reason, please contact @punchingcatto#9553 as soon as possible. \n\nLooking forward to it!", embed=embed)

            #save in database
            puzzlemessage = {
                    "id" : str(interaction.user.id),
                    "username": interaction.user.name,
                    "signup_realname": self.form_realName.value,
                    "signup_about_you": self.form_aboutYou.value,
                    "signup_puzzles_enjoyed": self.form_puzzlesEnjoyed.value,
                    "signup_favorite_puzzle_types": self.form_favoritePuzzleTypes.value,
                    "signup_anything_else": self.form_anythingElse.value,
                }
            db_items("Santas2022").upsert_item(body=puzzlemessage)

            #send to BenceJoful as backup
            await message_Bence('Sign up by '+str(interaction.user.id), embed=discord.Embed(description=str(puzzlemessage)))
        except:
            await message_Bence('Error in processing sign up form submission', embed=discord.Embed(description=traceback.format_exc()))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        await message_Bence('Error in sign up form', embed=discord.Embed(description=traceback.format_exc(error)))

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)

class SantaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def setup_hook(self) -> None:
        #register the views for listening
        self.add_view(SignUpButtonView())

    async def on_ready(self):
        guild = bot.get_guild(int(guild_id))
        await bot.tree.sync(guild=guild)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = SantaBot()

@bot.command()
@commands.is_owner()
async def SendMessages(ctx: commands.Context):
    """Sends DMs to users based on messages created in the database."""
    #todo: error handling
    try:
        messages_container = db_items("Messages")
        messages = list(messages_container.query_items(
            query="SELECT * FROM c where c.message_sent = 0",
            enable_cross_partition_query=True
        ))

        guild = bot.get_guild(int(guild_id))
        for message in messages:
            try:
                user = guild.get_member_named(message['username']) #BenceJoful#8715
                
                if message['is_SignUpButton_message'] == 1:
                    await user.send(message['text'], view=SignUpButtonView())
                elif message['is_SubmitGiftButton_message'] == 1:
                    await user.send(message['text'])
                    #await user.send(message['text'], view=SubmitGiftButtonView())
                else:
                    await user.send(message['text'])

                message["message_sent"] = 1
                db_items("Messages").upsert_item(body=message)
            except:
                await message_Bence('Error sending message '+str(message), embed=discord.Embed(description=traceback.format_exc()))

    except:
        await message_Bence('Error getting messages ', embed=discord.Embed(description=traceback.format_exc()))

@bot.hybrid_command(
    name="lonelypuzzles", description="Search for puzzles which need testing", 
    options=[
        interactions.Option(
            name="puzzle_type",
            description="Puzzle Type",
            required=True,
            type=3,
            choices=[
                interactions.Choice(
                    name="Sudoku",
                    value="sudoku"
                ),
                interactions.Choice(
                    name="Other Puzzles",
                    value="other"
                ),
                interactions.Choice(
                    name="Word Puzzles",
                    value="word"
                ),
            ],
        ),
        interactions.Option(
            name="search_terms",
            description="Words that are required to exist in the submission",
            required=False,
            type=3
        ),
        interactions.Option(
            name="max_age",
            description="Maximum age (1 week default)",
            required=False,
            type=4,
            choices=[
                interactions.Choice(
                    name="Day",
                    value=1
                ),
                interactions.Choice(
                    name="Week",
                    value=7
                ),
                interactions.Choice(
                    name="Month",
                    value=30
                ),
                interactions.Choice(
                    name="Year",
                    value=365
                )
            ]
        ),
        interactions.command.Option(
            name="solved_count",
            description="Number of people who marked it as Solved (0 default)",
            required=False,
            type=4
        )
    ]
)
async def _lonelypuzzles(ctx: interactions.CommandContext, puzzle_type: str, max_age: int = days_to_search, solved_count: int = 0, search_terms: str = ""):
    send_channel = ctx.channel
    if not (ctx.author.id in (calling_bot_id,developer_id)):
        send_channel = ctx.author.dm_channel
        if (send_channel is None):
            send_channel = await ctx.author.create_dm()
        await ctx.reply("I'm finding lonely puzzles, please check your DMs for details",ephemeral=True)
    
    response = await findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count,ctx.author.name)
    await send_channel.send(embed = response)

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
                    if (reaction.is_custom_emoji()):
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
                        if msg.content != "":
                            firstLine = msg.content.splitlines()[0].replace("~","").replace("*","").replace("_","")[:50]
                        else:
                            firstLine = ""
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

        await logUsage(author, foundPuzzlesCount, "lonelypuzzles " + puzzle_type + " " + str(max_age) + " " + str(solved_count) + " " + search_terms)
        return embed

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound) and ctx.invoked_with.lower() == "updatepins":
        return
    raise error

async def logUsage(author, found_count, command_message):
    log_title = "Log "+datetime.datetime.now(datetime.timezone.utc).strftime("%m/%d/%Y")
    log_message = None

    embed = discord.Embed(title=log_title)
    embed.description=datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")+" "+author+" " +"("+str(found_count)+"): "+command_message

    dev_user = bot.get_user(developer_id)
    log_channel = dev_user.dm_channel
    if (log_channel is None):
        log_channel = await dev_user.create_dm()

    if log_channel != None:
        #get most recent Log message by this bot there.  Either edit it or create new one.

        from_date = datetime.datetime.now() - datetime.timedelta(days=2)
        async for msg in log_channel.history(after=from_date):
            if (msg.author == bot.user and len(msg.embeds)>0 and msg.embeds[0].title == log_title):
                log_message = msg
                break

        if (log_message == None or len(log_message.embeds[0].description) > 3500):
            await log_channel.send(embed = embed)
        else:
            embed.description=log_message.embeds[0].description+'\n'+embed.description
            await log_message.edit(embed = embed)
            #await log_message.delete()
    else:
        print("Failed to log message, could not get log channel:")
        print(embed.description)

@bot.listen()
async def on_message(message):

    #check for archive numbers incrementing properly.
    if message.channel.id == archive_channel_id:
        puzzle_id = 0
        warning_msg = ""
        if message.content.startswith("["):
            try:
                puzzle_id = int(message.content.split("]")[0].lstrip("["))
            except:
                return
                
            async for msg in message.channel.history(limit=2):
                if message.id != msg.id:
                    previous_puzzle_id = int(msg.content.split("]")[0].lstrip("["))
                    if puzzle_id != previous_puzzle_id + 1:
                        warning_msg = "Your recent submission to the puzzle archive has an invalid Entry #.  Your post must begin with '["+str(previous_puzzle_id+1)+"]'.  Please edit your post to have the correct entry number.  Thanks!"
        if warning_msg != "":
            send_channel = message.author.dm_channel
            if (send_channel is None):
                send_channel = await message.author.create_dm()
            await send_channel.send(warning_msg)
            
            server_mod = bot.get_user(server_mod_id) 
            send_channel = server_mod.dm_channel
            if (send_channel is None):
                send_channel = await server_mod.create_dm()
            await send_channel.send("Message sent to "+message.author.name+": \n"+warning_msg)

    #print(message.author.id)
    #if it mentions me, process like a command.
    if (bot.user in message.mentions and bot.user != message.author):
        send_channel = message.channel
        if (message.author.id not in (calling_bot_id,developer_id)):
            send_channel = message.author.dm_channel
            if (send_channel is None):
                send_channel = await message.author.create_dm()
                
        args = message.content.split()
        if (message.author.id in (developer_id,calling_bot_id) and args[1]=="echo"):

            await message.channel.send(embed=discord.Embed(description=message.content))

            return
        elif (message.author.id in (developer_id,calling_bot_id) and len(args)==2 and args[1]=="updatepins"):
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
            helpmsg = "Format message like: ```@PuzzleDigestBot lonelypuzzles puzzle_type max_age solved_count search terms```\npuzzle_type is 'sudoku', 'word', or 'other'  \nmax_age and solved_count must be integers.  \nSearch terms are optional, and not in quotes."

            if len(args) > 4:
                if args[1] == 'lonelypuzzles':
                    pass #now handled by the hybrid command
                    # puzzle_type = args[2]
                    # max_age = 0
                    # try:
                    #     max_age = int(args[3])
                    # except ValueError:
                    #     await send_channel.send(embed = discord.Embed(description='max_age is not an integer.\n'+helpmsg))
                    #     return

                    # solved_count = 0
                    # try:
                    #     solved_count = int(args[4])
                    # except ValueError:
                    #     await send_channel.send(embed = discord.Embed(description='solved_count is not an integer.\n'+helpmsg))
                    #     return

                    # search_terms = " ".join(args[5:])
                    # response = await findLonelyPuzzles(puzzle_type, search_terms,max_age,solved_count,message.author.name)
                    # await send_channel.send(embed = response)
                else:
                    await send_channel.send(embed = discord.Embed(description='No command given.\n'+helpmsg))
            else:
                await send_channel.send(embed = discord.Embed(description='Insufficient arguments given.\n'+helpmsg))

bot.run(access_token)