import discord
from discord import app_commands
import datetime
import io

default_intents = discord.Intents.all()
bot = discord.Client(intents=default_intents)
TOKEN = open("secrettoken.txt", "r").read()
tree = app_commands.CommandTree(bot)

channelCitationsID = 692060978342395904
mainServerID = 691683236534943826
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

emojis_couleurs = ['⚫', '🔴', '\U0001f7e0', '\U0001f7e2']

async def reac(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    
    if not user.bot and len(message.embeds) > 0 and len(message.reactions) >= 4 and message.author.id == bot.user.id:
        Lreac = {}
        for r in message.reactions:
            if r.emoji in emojis_couleurs: Lreac[r.emoji] = r.count
        col = process_react(Lreac)
                    
        embedVar = discord.Embed(title="", color=discord.Colour(int(col, 16)), description=message.embeds[0].description)
        embedVar.set_author(name=message.embeds[0].author.name, icon_url=message.embeds[0].author.icon_url)
        embedVar.set_footer(text=message.embeds[0].footer.text)
        
        await message.edit(embed=embedVar)

def process_react(Lreac):
    max_reac = max(Lreac.values())
    if max_reac == 1: return 'FFFFFF'
    if '⚫' in Lreac and Lreac['⚫'] > 1: return '31373D'
    majority = [emoji for emoji in Lreac if Lreac[emoji] == max_reac]
    if len(majority) == 1:
        if majority[0] == '🔴': return 'DD2E44'
        if majority[0] == '\U0001f7e0': return 'F4900C'
        if majority[0] == '\U0001f7e2': return '78B159'
    elif '🔴' in majority: return 'DD2E44'
    else: return 'FFFFFF'
    

@bot.event
async def on_message(message):
    if message.channel.type is discord.ChannelType.private and not message.author.bot:
        await envoyer_au_bureau(message)

@tree.command(
    name='help',
    description="Afficher l'aide"
)
async def help(ctx: discord.Interaction):
    await ctx.response.send_message("""
## Commande /post
- **Description :** Permet de poster une citation
- **Utilisation :** `/post [citation] [envoyer]`
- **Arguments :**
  - **citation :** La citation à poster
  - **envoyer :** Si la citation doit être envoyée au bureau pour potentiellement apparaître dans le prochain numéro.
Les citations envoyées à l'aide de la commande post seront envoyées dans le salon défini par la commande /setchannel.
Il est **impossible** de poster une citation sans qu'un salon ne soit défini.
## Commande /setchannel
- **Description :** Définir le salon actuel comme salon où envoyer les citations
- **Utilisation :** `/setchannel`
- **Arguments :** Aucun
Vous pouvez toujours envoyer des citations en message privé au bot, elles seront automatiquement transférées au bureau.
""", ephemeral=True)

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
        await envoyer_au_bureau_via_post(ctx.user, message, "Message privé")
        await ctx.response.send_message("Merci pour ta contribution, message transféré au bureau !\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.\n*Astuce : Tu n'es pas obligé.e d'utiliser /post dans les DMs du bot, tu peux juste y écrire ta citation !*", ephemeral=True)
        return
    if get_channel_id(ctx.guild.id) is None:
        await ctx.response.send_message("Le salon où envoyer les citations n'a pas été défini. Utilisez la commande **/setchannel** pour le définir.", ephemeral=True)
        return
    await envoyer_dans_channel_dedie(ctx.user, message, ctx.guild.id, minitel)
    if minitel:
        await envoyer_au_bureau_via_post(ctx.user, message, "Serveur via /post")
        await ctx.response.send_message(f"**Citation envoyée !** (Le bureau **est** au courant)\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.", ephemeral=True)
    else:
        await ctx.response.send_message(f"**Citation envoyée !** (Le bureau n'est **pas** au courant)", ephemeral=True)

@tree.command(
    name='dump',
    description="Dump toutes les citations dans la console"
)
@app_commands.describe(days="Le nombre de jours à remonter dans le passé")
@app_commands.rename(days="nbjours")
@app_commands.guild_only()
@app_commands.guilds(mainServerID)
async def dump(ctx: discord.Interaction, days: int):
    if ctx.guild is None:
        await ctx.response.send_message("Cette commande n'est pas disponible en message privé.", ephemeral=True)
        return
    if ctx.guild_id != mainServerID:
        await ctx.response.send_message(f"Cette commande n'est pas disponible sur ce serveur.", ephemeral=True)
        return
    if ctx.user.guild_permissions.administrator:
        await ctx.response.defer(ephemeral=True)
        quote_file, quote_filename = await dump_all_quotes(days)
        await ctx.followup.send("**Dump effectué !**\nLe fichier est sous format TSV, il est possible de l'ouvrir dans un tableur en définissant les tabulations comme les séparateurs.",
                                        file=discord.File(fp=io.StringIO(quote_file), filename=quote_filename), ephemeral=True)
    else:
        await ctx.response.send_message("Vous n'avez pas la permission pour utiliser cette commande.", ephemeral=True)

async def envoyer_au_bureau(message):
    await envoyer_embed_et_reactions(
        author=message.author,
        content=message.content,
        footer_text="Message privé",
        channel_id=channelCitationsID
    )
    await message.channel.send(content="Merci pour ta contribution, message transféré au bureau !\n\n**Rappel :** Si toi ou la/les personne(s) concernée(s) souhaitez retirer cette contributaion avant qu'elle ne paraisse dans un Mini Tel', contacte le bureau.")

async def envoyer_au_bureau_via_post(author, content, server_name):
    await envoyer_embed_et_reactions(
        author=author,
        content=content,
        footer_text=server_name,
        channel_id=channelCitationsID
    )

async def envoyer_embed_et_reactions(author, content, footer_text, channel_id):
    channel = bot.get_channel(channel_id)
    content = content.replace("; ", "\n")
    embedVar = discord.Embed(title="", color=discord.Colour(int("FFFFFF", 16)), description=content)
    if author.avatar is None:
        embedVar.set_author(name=author.name)
    else:
        embedVar.set_author(name=author.name, icon_url=author.avatar)
    embedVar.set_footer(text=footer_text)
    msgembed = await channel.send(embed=embedVar)
    for emoji in emojis_couleurs:
        await msgembed.add_reaction(emoji)
    valeurs = (content, content, 0, 0, author.id)

async def envoyer_dans_channel_dedie(author, content, serverid, minitel):
    channelCitations = bot.get_channel(get_channel_id(serverid))
    content = content.replace("; ", "\n")
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
    filename = f"{int(now.timestamp())}.tsv"
    sortie = ""
    sortie += f"-- Dump du {now.day}/{now.month}/{now.year}\n"
    sortie += f"-- À partir du {start_date.day}/{start_date.month}/{start_date.year}\n"
    sortie += "==== DEBUT DE DUMP ====\n"
    sortie += "Citation\tAuteur\tCouleur\n"
    channelCitations = bot.get_channel(channelCitationsID)
    history = channelCitations.history(limit=None, after=start_date, oldest_first=True)
    messages = [m async for m in history if len(m.embeds) > 0 and m.embeds[0].description is not None]
    for message in messages:
        sortie += message.embeds[0].description.replace("\n", "; ") + "\t"
        sortie += message.embeds[0].author.name + "\t"
        sortie += get_couleur(message.embeds[0].color) + "\n"
    sortie += "==== FIN DE DUMP ===="
    return sortie, filename

def get_couleur(col: discord.Colour):
    col = str(col)[1:].upper()
    if col == "31373D":
        return 'Noir'
    elif col == "DD2E44":
        return 'Rouge'
    elif col == "F4900C":
        return 'Orange'
    elif col == "78B159":
        return 'Vert'
    else:
        return 'Blanc'

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
    await tree.sync(guild=discord.Object(mainServerID))
    print("Le bot est prêt")

bot.run(TOKEN)