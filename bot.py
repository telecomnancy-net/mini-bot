import discord
from discord import app_commands
import datetime
import os

default_intents = discord.Intents.all()
bot = discord.Client(intents=default_intents)
TOKEN = open("secrettoken.txt", "r").read()
tree = app_commands.CommandTree(bot)

channelCitationsID = 692060978342395904
serverID = 691683236534943826
serverChannelID = {}

def get_channel_id(serverID):
    try:
        return serverChannelID[serverID]
    except:
        return None

def set_channel_id(serverID, channelID):
    serverChannelID[serverID] = channelID

def save_channel_id():
    with open("channelID.txt", "w") as f:
        for serverID in serverChannelID:
            f.write(str(serverID) + " " + str(serverChannelID[serverID]) + "\n")

def load_channel_id():
    with open("channelID.txt", "r") as f:
        for line in f:
            serverID, channelID = line.split(" ")
            serverChannelID[int(serverID)] = int(channelID)

async def reac(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    
    if not user.bot and len(message.embeds) > 0 and len(message.reactions) == 4 and message.author.id == bot.user.id:
        Lreac = []
        for r in message.reactions:
            Lreac.append((r.count,r.emoji))
        Lreac.sort()
        authorid = message.embeds[0].author.icon_url.split('/')[4]
        if Lreac[3][0] > 1 and Lreac[3][0] != Lreac[2][0]:
            if Lreac[3][1] == '⚫':
                col = "31373D"
                valeurs = (1, message.embeds[0].description, authorid)
            elif Lreac[3][1] == '🔴':
                col = "DD2E44"
                valeurs = (2, message.embeds[0].description, authorid)
            elif Lreac[3][1] == '\U0001f7e0':
                col = "F4900C"
                valeurs = (3, message.embeds[0].description, authorid)
            elif Lreac[3][1] == '\U0001f7e2':
                col = "78B159"
                valeurs = (4, message.embeds[0].description, authorid)
        else:
            col = "FFFFFF"
            valeurs = (0, message.embeds[0].description, authorid)
                    
        embedVar = discord.Embed(title="", color=discord.Colour(int(col, 16)), description=message.embeds[0].description)
        embedVar.set_author(name=message.embeds[0].author.name, icon_url=message.embeds[0].author.icon_url)
        
        await message.edit(embed=embedVar)

@bot.event
async def on_message(message):
    if message.channel.type is discord.ChannelType.private and not message.author.bot:
        await envoyer_au_bureau(message)

@tree.command(
    name='setchannel',
    description="Définir le salon où envoyer les citations"
)
async def setchannel(ctx: discord.Interaction):
    if ctx.guild is None:
        await ctx.response.send_message("Cette commande n'est pas disponible en message privé.", ephemeral=True)
        return
    if ctx.user.guild_permissions.manage_channels:
        set_channel_id(ctx.guild.id, ctx.channel.id)
        save_channel_id()
        await ctx.response.send_message(f"Le salon où envoyer les citations a été défini à #{ctx.channel.name}", ephemeral=True)
    else:
        await ctx.response.send_message("Vous n'avez pas la permission de gérer les salons.", ephemeral=True)

@tree.command(
    name='post',
    description="Poster une citation"
)
@app_commands.describe(message="La citation à poster")
@app_commands.rename(message="citation")
@app_commands.describe(minitel="Si la citation doit être envoyée au bureau")
@app_commands.rename(minitel="envoyer")
async def post(ctx: discord.Interaction, message: str, minitel: bool):
    if ctx.guild is None:
        await ctx.response.send_message("Merci pour ta contribution, message transféré au bureau !\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.\n*Astuce : Tu n'es pas obligé.e d'utiliser /post dans les DMs du bot, tu peux juste y écrire ta citation !*", ephemeral=True)
        await envoyer_au_bureau_via_post(ctx.user, message)
        return
    if get_channel_id(ctx.guild.id) is None:
        await ctx.response.send_message("Le salon où envoyer les citations n'a pas été défini. Utilisez la commande **/setchannel** pour le définir.", ephemeral=True)
        return
    await envoyer_dans_channel_dedie(ctx.user, message, ctx.guild.id, minitel)
    if minitel:
        await ctx.response.send_message(f"**Citation envoyée !** (Le bureau **est** au courant)\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.", ephemeral=True)
        await envoyer_au_bureau_via_post(ctx.user, message)
    else:
        await ctx.response.send_message(f"**Citation envoyée !** (Le bureau n'est **pas** au courant)", ephemeral=True)

@tree.command(
    name='dump',
    description="Dump toutes les citations dans la console"
)
@app_commands.describe(days="Le nombre de jours à remonter dans le passé")
@app_commands.rename(days="nbjours")
@app_commands.guild_only()
@app_commands.guilds(serverID) # Marche pas ??!??§,?§,!,§?,,??????
async def dump(ctx: discord.Interaction, days: int):
    if ctx.guild is None:
        await ctx.response.send_message("Cette commande n'est pas disponible en message privé.", ephemeral=True)
        return
    if ctx.guild_id != serverID:
        await ctx.response.send_message(f"Cette commande n'est pas disponible sur ce serveur.", ephemeral=True)
        return
    if ctx.user.guild_permissions.administrator:
        quote_file = await dump_all_quotes(days)
        await ctx.response.send_message("Dump effectué", file=discord.File(quote_file), ephemeral=True)
    else:
        await ctx.response.send_message("Vous n'avez pas la permission pour utiliser cette commande.", ephemeral=True)

async def envoyer_au_bureau(message):
    channelCitations = bot.get_channel(channelCitationsID)
    print(message.content)
    embedVar = discord.Embed(title="", color=discord.Colour(int("FFFFFF", 16)), description=message.content)
    embedVar.set_author(name=message.author.name, icon_url=message.author.avatar)
    msgembed = await channelCitations.send(embed=embedVar)
    await message.channel.send(content="Merci pour ta contribution, message transféré au bureau !\n\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.")
    await msgembed.add_reaction('⚫')
    await msgembed.add_reaction('🔴')
    await msgembed.add_reaction('🟠')
    await msgembed.add_reaction('🟢')
    valeurs = (message.content, message.content, 0, 0, message.author.id)

async def envoyer_au_bureau_via_post(author, content):
    channelCitations = bot.get_channel(channelCitationsID)
    embedVar = discord.Embed(title="", color=discord.Colour(int("FFFFFF", 16)), description=content)
    embedVar.set_author(name=author.name, icon_url=author.avatar)
    msgembed = await channelCitations.send(embed=embedVar)
    await msgembed.add_reaction('⚫')
    await msgembed.add_reaction('🔴')
    await msgembed.add_reaction('🟠')
    await msgembed.add_reaction('🟢')
    valeurs = (content, content, 0, 0, author.id)

async def envoyer_dans_channel_dedie(author, content, serverid, minitel):
    channelCitations = bot.get_channel(get_channel_id(serverid))
    if minitel:
        embedVar = discord.Embed(title="", color=discord.Colour(int("734F96", 16)), description=content)
    else :
        embedVar = discord.Embed(title="", color=discord.Colour(int("FFFFFF", 16)), description=content)
    embedVar.set_author(name=author.name, icon_url=author.avatar)
    msgembed = await channelCitations.send(embed=embedVar)
    valeurs = (content, content, 0, 0, author.id)

async def dump_all_quotes(days):
    now = discord.utils.utcnow()
    start_date = now - datetime.timedelta(days=days)
    filename = f"dump/{int(now.timestamp())}.txt"
    sortie = open(filename, "x", encoding="utf-8")
    sortie.write(f"-- Dump du {now.day}/{now.month}/{now.year}\n")
    sortie.write(f"-- À partir du {start_date.day}/{start_date.month}/{start_date.year}\n")
    sortie.write("==== DEBUT DE DUMP ====\n")
    channelCitations = bot.get_channel(channelCitationsID)
    history = channelCitations.history(limit=None, after=start_date, oldest_first=True)
    messages = [m async for m in history if len(m.embeds) > 0 and m.embeds[0].colour == discord.Colour(int("78B159", 16))]
    for message in messages:
        sortie.write(message.embeds[0].description + "\n")
    sortie.write("==== FIN DE DUMP ====")
    sortie.close()
    return filename

@bot.event
async def on_raw_reaction_add(payload):    
    await reac(payload)
    
@bot.event
async def on_raw_reaction_remove(payload):    
    await reac(payload)

@bot.event
async def on_ready():
    load_channel_id()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="vos citations"))
    await tree.sync()
    await tree.sync(guild=discord.Object(serverID))
    print("Le bot est prêt")

bot.run(TOKEN)