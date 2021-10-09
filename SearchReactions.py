import os
import datetime
import discord

client = discord.Client()
access_token= os.environ["ACCESS_TOKEN"]
guild_id = os.environ["GUILD_ID"]
sudoku_submissions_channel_id = int(os.environ["SUDOKU_SUBMISSIONS_CHANNEL_ID"])
other_submissions_channel_id = int(os.environ["OTHER_SUBMISSIONS_CHANNEL_ID"])
sudoku_keyword = os.environ["SEARCH_SUDOKU_KEYWORD"]
others_keyword = os.environ["SEARCH_OTHERS_KEYWORD"]
max_puzzles_return = int(os.environ["MAX_PUZZLES_RETURN"])
reaction_threshhold = int(os.environ["REACTION_THRESHHOLD"])
days_to_search = int(os.environ["DAYS_TO_SEARCH"])

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    search_channel_id = 0
    replymsg = ""
    if sudoku_keyword in message.content:
        search_channel_id = sudoku_submissions_channel_id
        replymsg = "sudoku"

    if others_keyword in message.content:
        search_channel_id = other_submissions_channel_id
        replymsg = "other"

    if search_channel_id > 0:
        replymsg = "Unsolved "+replymsg+"puzzles in past week:"
        foundPuzzles = 0

        from_date = datetime.datetime.now() - datetime.timedelta(days= days_to_search )
        async for msg in client.get_channel(search_channel_id).history(after=from_date):
            reactioncnt = 0
            for reaction in msg.reactions:
                reactioncnt+=reaction.count

            if reactioncnt <= reaction_threshhold:
                #post first line of text (up to 50 characters) then the message ID.
                replymsg += "\n    " + msg.content.splitlines()[0][:50] + " (https://discord.com/channels/"+guild_id+"/"+msg.channel.id+"/" + str(msg.id) + ")"
            
            foundPuzzles += 1
            if foundPuzzles == max_puzzles_return:
                break

        if foundPuzzles == 0:
            replymsg = "No unsolved puzzles in past week."

        await message.channel.send(content=replymsg, reference=message)
        return

    #on mention, 
    if client.user in message.mentions:
        await message.channel.send(content="Try "+sudoku_keyword +" or "+others_keyword, reference=message)



client.run(access_token)


