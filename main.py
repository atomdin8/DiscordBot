import discord
import random
import requests
import time
import asyncio
from discord.ext import commands


#defaults
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)
messages = 0



#our statistic recorder function. this may require stats.txt file in this directory.
async def update_stats():
    with open("stats.txt", "a") as f:
        f.write(f"Time: {int(time.time())}, Messages: {messages}\n")


#is our bot active?
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    channel = bot.get_channel(1130847046950191255)  # you should copy your channel ID and paste here.
    if channel:
        await channel.send("Hello! If you get stuck somewhere, just write $code.")


#blocking unwanted names
@bot.event
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count("admin") > 0:
            last = before.nick
            if last:
                await after.edit(nick=last)
            else:
                await after.edit(nick="STOP")


#control the channel message activities
@bot.event
async def on_message(message):
    global messages
    messages += 1
    msg = message.content


    #variables
    sad_words = ["sad", "offended", "angry"]
    happy_responses = ["Don't worry, everything will be alright!", "I can tell a joke that will cheer you up!", "Smiling is always the best medicine!"]
    bad_words = ["swear", "badword", "curse", "profanity"]


    if message.author == bot.user:
        return

    # Reply for sad words
    for word in sad_words:
        if word in msg:
            response = random.choice(happy_responses)
            await message.channel.send(response)
            break

    #reply for bad words            
    for word in bad_words:
        if message.content.count(word) > 0:
            print("A bad word was said")
            await message.channel.purge(limit=1)
            

    await bot.process_commands(message)
    await update_stats()

#help
@bot.command()
async def code(ctx):
    embed = discord.Embed(title="Help on BOT", description="Some useful commands")
    embed.add_field(name="$hello", value="Greets the user")
    embed.add_field(name="$users", value="Prints number of users")
    embed.add_field(name="$clean <num>", value="Deletes messages")
    embed.add_field(name="$roll <num>", value="Rolls the dice")
    embed.add_field(name="$quote", value="Prints inspirational quotes")
    embed.add_field(name="$offline <num>", value="Shutdown the bot or turn of some minutes")
    embed.add_field(name="$guess <num>", value="Number guessing game")
    await ctx.send(embed=embed)

#say hi :D
@bot.command()
async def hello(ctx):
    await ctx.send('Hello! Welcome :D')

#will return the server members.
@bot.command()
async def users(ctx):
    guild = bot.get_guild(1130580376839016488)
    await ctx.send(f"# Members: {guild.member_count}")

#will clean the channel message history.
@bot.command()
async def clean(ctx, limit=10):
    channel = ctx.channel
    await channel.purge(limit=limit + 1)
    await ctx.send(f"{limit} messages deleted.")

#do you need inspiration?
@bot.command()
async def quote(ctx):
    response = requests.get("https://raw.githubusercontent.com/umutgokbayrak/ozlusozler/master/sozler.txt")

    if response.status_code == 200:
        lines = response.text.splitlines()
        quote = random.choice(lines).strip()

        while not quote or len(quote) < 20:
            quote = random.choice(lines).strip()

        await ctx.send(quote)

#to turn off the bot
@bot.command()
async def offline(ctx, num: int = None):
    if num is None:
        await ctx.send("Bot is going completely offline. Goodbye!")
        await bot.change_presence(status=discord.Status.offline, activity=None)
    else:
        await ctx.send(f"Bot is going offline for {num} minute(s). Goodbye!")
        await bot.change_presence(status=discord.Status.offline, activity=None)

        await asyncio.sleep(num * 60)

        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="KODLAND"))
        await ctx.send("Bot is back online!")

#for guess game-------------------------------------------------------------------------------------------
async def start_guessing(ctx, num=None):
    if num is None:
        num = "100"

    if not num.isdigit():
        await ctx.send("Please enter a valid number.")
        return

    number_to_guess = random.randint(1, int(num))
    await ctx.send(f"The number guessing game begins! I kept a number between 1 and {num}. Guess!")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

    attempts = 0
    while True:
        try:
            user_guess = await bot.wait_for('message', check=check, timeout=30)
            user_guess = int(user_guess.content)
            attempts += 1

            if user_guess == number_to_guess:
                await ctx.send(f"Great! You guessed right! Number: {number_to_guess}, Attempts: {attempts}")
                break
            elif user_guess < number_to_guess:
                await ctx.send("Guess a larger number.")
            else:
                await ctx.send("Guess a smaller number.")

        except asyncio.TimeoutError:
            await ctx.send("Time's up! The game is over.")
            break

#guess what :D
@bot.command()
async def guess(ctx, num: str = None):
    await start_guessing(ctx, num)

# Dice roll function --------------------------------------------------------------------------------
async def roll_dice(ctx, num=None):
    if num is None:
        num = 6

    try:
        num = int(num)
    except ValueError:
        await ctx.send("Please enter a valid number.")
        return

    result = random.randint(1, num)
    await ctx.send(f"I rolled the dice! Returned a value between 1 and {num}: {result}")

# Roll komutu
@bot.command()
async def roll(ctx, num: str = None):
    await roll_dice(ctx, num)

#our bot will run with this TOKEN-----------------------------------------------------------------------
bot.run('YOUR TOKEN HERE!')
#you should paste your TOKEN inside the brackets here.