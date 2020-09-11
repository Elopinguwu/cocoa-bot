

import discord
from discord.ext import tasks, commands
import asyncio
import json
import os
import random

from discord.ext import commands
bot = commands.Bot(command_prefix='/', case_insensitive=True)
bot.load_extension('cogs.music')

### Shop


{"name":"Taiga_Aisaka","price":500,"description":"Generate 10 Chocolates per minute"}
mainshop = [{"name":"Taiga_Aisaka","price":500,"description":"Generate 10 Chocolates per minute"}]


### Idle Chocolates

###@tasks.loop(seconds=60.0)



### On Ready
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name='Made by Eloping using Python for "The Chocolate Factory"'))

### Cancer
#@bot.event
#async def on_message(message):
#    if message.author.id == 244796688341008384:
#        await message.delete()

### Welcome Message
@bot.event
async def on_member_join(member):
    ment = member.mention
    channel = bot.get_channel(727830175877693443)
    await channel.send(f'{ment} has joined **The Chocolate Factory** ! Welcome !')

### Error Handlers
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is on cooldown, please try again in {:.2f}s :chocolate_bar:'.format(error.retry_after)
        await ctx.send(msg)
    else:
        raise error

### Clear
@bot.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx,  nombre : int):
    channel = bot.get_channel(727830175877693443)
    messages = await ctx.channel.history(limit = nombre + 1).flatten()
    await channel.send(f'I deleted {nombre} messages ! :chocolate_bar:')
    for message in messages:
        await message.delete()

### Music





### Kick
@bot.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, user : discord.User, *reason):
    reason = " ".join(reason)
    await ctx.guild.kick(user, reason = reason)
    await ctx.send(f"{user} has been kicked from the server <a:hoemoving:752283886376976474>\nReason : {reason}")

### Send
@bot.command()
async def send(ctx,member:discord.Member,amount = None):
    await openwallet(ctx.author)
    await openwallet(member)

    if amount == None:
        await ctx.send("Please enter the amount you want to send :chocolate_bar:")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You don't have that much chocolates! <a:hoemoving:752283886376976474>")
        return
    if amount < 0:
        await ctx.send("Amount must be positive ! <a:hoemoving:752283886376976474>")
        return

    await update_bank(ctx.author, -1 * amount,"bank")
    await update_bank(member,amount,"bank")
    await ctx.send(f"You gave {amount} chocolates to {member} :chocolate_bar: !")

### Ban
@bot.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, user : discord.User, *reason):
    reason = " ".join(reason)
    try:
        await ctx.guild.ban(user, reason = reason)
        await ctx.send(f"{user} has been banned from the server <a:hoemoving:752283886376976474>\nReason : {reason}")
    except:
        await ctx.send("You dont have enough permissions to execute this command :chocolate_bar:")

### Shop
@bot.command()
async def shop (ctx):
    em = discord.Embed(title =  "Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"Price : {price} Chocolates | {desc}")
        em.set_image(url="https://i.imgur.com/VJJZY2N.jpg")

    await ctx.send(embed = em)

### Buy
@bot.command()
async def buy(ctx,item,amount = 1,):
    await openwallet(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there! <a:hoemoving:752283886376976474>")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item} <a:hoemoving:752283886376976474>")
            return


    await ctx.send(f"You just bought {amount} {item} ! <a:hoemoving:752283886376976474>")


### Def Buy_This
async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Inventory"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["Inventory"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["Inventory"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["Inventory"] = [obj]

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]

### Def Inventory
@bot.command()
async def Inventory(ctx):
    await openwallet(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        Inventory = users[str(user.id)]["Inventory"]
    except:
        Inventory = []


    em = discord.Embed(title = "Inventory")
    for item in Inventory:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)

    await ctx.send(embed = em)
### Bal
@bot.command()
async def bal(ctx):
    await openwallet(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance",color = discord.Color.purple())
    em.add_field(name = "Wallet",value = wallet_amt)
    em.add_field(name = "Bank",value = bank_amt)
    await ctx.send(embed = em)

### Withdraw
@bot.command()
async def withdraw(ctx,amount = None):
    await openwallet(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount you want to withdraw :chocolate_bar:")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that much chocolates! :chocolate_bar:")
        return
    if amount<0:
        await ctx.send("Amount must be positive ! :chocolate_bar:")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")
    await ctx.send(f"You withdrew {amount} chocolates :chocolate_bar: !")

### Deposit
@bot.command()
async def deposit(ctx,amount = None):
    await openwallet(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount you want to deposit :chocolate_bar:")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You don't have that much chocolates! :chocolate_bar:")
        return
    if amount<0:
        await ctx.send("Amount must be positive ! :chocolate_bar:")
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,"bank")
    await ctx.send(f"You deposited {amount} chocolates :chocolate_bar: !")

### Slots
@commands.cooldown(1,30, commands.BucketType.user)
@bot.command()
async def slots(ctx,amount = None):
    await openwallet(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount you want to deposit :chocolate_bar:")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You don't have that much chocolates! :chocolate_bar:")
        return
    if amount < 0:
        await ctx.send("Amount must be positive ! :chocolate_bar:")
        return

    final = []
    for i in range(3):
        a = random.choice(['chocolate:bar:',':sushi:',':cupcake:'])
        final.append(a)
    await ctx.send(str(final))
    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:

        await update_bank(ctx.author,2*amount)
        await ctx.send("You won ! :chocolate_bar:")
    else:
        await update_bank(ctx.author,-1*amount)
        await ctx.send("You lost :( :chocolate_bar:")

### Pickpocket
@commands.cooldown(1,3600, commands.BucketType.user)
@bot.command()
async def pickpocket(ctx,member:discord.Member):
    await openwallet(ctx.author)
    await openwallet(member)

    bal = await update_bank(member)

    if bal[0]<100:
        await ctx.send("No ! It wont be worth it , they dont have much chocolates !:chocolate_bar:")
        return
    earnings = random.randrange(0,bal[0])
    await update_bank(ctx.author,earnings)
    await update_bank(member,-1*earnings)
    await ctx.send(f"You stole {earnings} chocolates from  :chocolate_bar: !")

### Daily
@commands.cooldown(1,86400, commands.BucketType.user)
@bot.command()
async def daily(ctx):
    await openwallet(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    earnings = 350
    await ctx.send(f"You got 350 chocolates from your daily reward ! <a:hoemoving:752283886376976474>")
    await update_bank(ctx.author,earnings)

### Work
@commands.cooldown(1,900, commands.BucketType.user)
@bot.command()
async def work(ctx):
    await openwallet(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(80)
    await ctx.send(f"You worked for {earnings} chocolates :chocolate_bar:")
    users[str(user.id)]["wallet"] += earnings
    with open("mainbank.json", "w") as f:
        json.dump(users,f)

async def openwallet(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 200
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json","w") as f:
        json.dump(users,f)
    return True

async def get_bank_data():
    with open("mainbank.json","r") as f:
        users = json.load(f)

    return users

async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal


bot.run('NzUyMjcyMTEzOTI2NDA2MTk0.X1VOAA.Ah7kVJoPnyy1tAXHVg2QGhb5P-I')

