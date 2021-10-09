import os
import discord
#import pandas as pd

client = discord.Client()
guild = discord.Guild


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/list-unsolved-sudoku-submissions'):
        #comment="""
        #data = pd.DataFrame(columns=['content', 'time', 'author'])
        
        replymsg = "Unsolved puzzles since "
        foundPuzzles = 0

        async for msg in client.get_channel(896187693728419850).history(limit=100):
            reactioncnt = 0
            for reaction in msg.reactions:
                reactioncnt+=reaction.count

            #print (reactioncnt)

            if reactioncnt == 2:
                #todo: post first line of text (up to 50 characters) then the message ID.
                replymsg += "\n" + msg.content.splitlines()[0][:50] + " (https://discord.com/channels/896180948108976228/896187693728419850/" + str(msg.id) + ")"
            
            foundPuzzles += 1
            if foundPuzzles == 10:
                break

#            data = data.append({'content': msg.content,
                                #'time': msg.created_at,
                                #'reactions': msg.reactions.count}, ignore_index=True)
            
        #file_location = "data.csv" # Set the string to where you want the file to be saved to
        #data.to_csv(file_location)
        #"""
        if foundPuzzles > 0:
            await client.get_channel(896186189533560883).send(replymsg)
        else:
            await client.get_channel(896186189533560883).send("No unsolved puzzles found in the most recent 100 submissions")
        
        await msg.delete()
        #await message.channel

access_token= os.environ["ACCESS_TOKEN"]

client.run(access_token)


