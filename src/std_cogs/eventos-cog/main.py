import discord
from discord.ext import commands
import json
import time
from os import environ as env
from App import eliminar_prefix
import re
from termcolor import cprint
import aiohttp

async def cerrar(iniciador=None, destinatario:int=None):
    with open(env["JSON_DIR"] + "chats.json", "r") as f:
        chats = json.load(f)

    if str(iniciador.id) in chats["chats"]:
        del chats["chats"][f"{iniciador.id}"]
        del chats["chats"][f"{destinatario}"]

        with open(env["JSON_DIR"] + "chats.json", "w") as f:
            json.dump(chats, f)

def EncontrarUrl(string: str = None):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]

color = int(env["COLOR"])

class Servidor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        with open(env["JSON_DIR"] + "chats.json", "r") as f:
            chats = json.load(f)

        try:
            if not message.guild:
                if str(message.author.id) in chats["chats"]:
                    dest = chats["chats"][f"{message.author.id}"]["dest"]
                    # print(dest)
                    if str(dest) in chats["chats"]:
                        destid, dest = int(dest), self.bot.get_user(int(dest))
                        if len(message.attachments) > 0:
                            return await message.author.send(embed=discord.Embed(title="No se pueden los adjuntos", color=color, description=f"Las imagenes, tts, etc no estan permitidos en el chat de <@730124969132163093>"))
                        if EncontrarUrl(message.content):
                            await message.author.send(embed=discord.Embed(color=color, description="Se le ha enviado el link al usuario de forma como spoiler"))
                            msg = await dest.send(embed=discord.Embed(title="Un link", description=f"{message.author.mention} Se ha enviado un link, esta en modo spoiler por si acaso", color=color).add_field(name="Url:", value=f"||{EncontrarUrl(message.content)[0]}||"))
                            return
                        if message.content == "cerrarchat":
                            await cerrar(message.author, destid)
                            await message.author.send(embed=discord.Embed(title="El chat esta cerrado", description=f"{message.author.mention} se ha cerrado la conexion con **{dest.mention}**", color=color))
                            await dest.send(embed=discord.Embed(title="El chat esta cerrado", description=f"{dest.mention}, **{message.author.mention}** Ha cerrado la conexion con el chat.", color=color))
                            return
                        else: 
                            cprint(f"[Log] Mensage de ({message.author.name}) | ({dest.name}): {message.content}", "cyan")
                            return await dest.send(f"**{message.author.name}**`#{message.author.discriminator}`**:**  {message.content}")
                else:
                    return await message.author.send(embed=discord.Embed(title="No...", description=f"{message.author.mention} not puedes usar comandos dentro de los mensages de MD o hablar por aqui **(Solo puedes si estas en un chat con alguien m-help ChatApp)**", color=0xf15069))
        except Exception as e:
            return cprint(f"[Log] Un error en on_message: {e}", "red")

        with open(env["JSON_DIR"] + "chats.json", "w") as f:
            json.dump(chats, f)

        with open(env["JSON_DIR"] + "mute.json", 'r') as f:
            userm = json.load(f)

        # print(message.author.id)
        if str(message.author.id) in userm:
            await message.delete()

        if message.content == f"<@!{self.bot.user.id}>":
            await message.channel.send(embed=discord.Embed(title="Deja que me presente",
                                                           url="https://maubot.maucode.com", 
                                                           description="<:maubot:774967705831997501> Hola, mi nombre es Maubot. Si quieres conocer todos mis comandos, usa la ayuda de comandos, es bastante fácil usar todos mis comandos y dominarlos. Si quieres usar todos mis comandos, mis prefijos son (**<@!730124969132163093> prefijos**) Y para ver mis commandos solo pon **m.help**", 
                                                           colour=color).set_thumbnail(url="https://raw.githubusercontent.com/maubg-debug/maubot/main/docs/maubot-icon.png").add_field(name="Mis comandos", value="¿No saves que hacer? Puedes poner `m.help [Seccion]` y veras todos mis comandos disponibles. Si tienes cosas que decir siempre puedes poner `&rate_bot <Reseña>` y te responderemos **lo mas rapido** posible").add_field(name="¿Para que sirvo?", value="Mi dever en tu servidor es hacer que la gente se divierta con mis memes, que la gente le guste la musica y mi sistema de dinero, que el servidor sea bonito y **¡Mucho mas!**", inline=False))

        # .set_thumbnail(url="https://raw.githubusercontent.com/maubg-debug/maubot/main/docs/maubot_white.gif").set_image(url="https://raw.githubusercontent.com/maubg-debug/maubot/main/docs/maubot-icon.png")

        if message.content == f"<@!{self.bot.user.id}> prefijos":
                    await message.channel.send(embed=discord.Embed(title="Mis prefijos", 
                                                description="<:maubot:774967705831997501> Mis prefijos son `& (O custom m.prefix [prefijo])`, `m-`, `m.` - O tambien puedes poner <@!730124969132163093> ", 
                                                colour=color).set_image(url="https://raw.githubusercontent.com/maubg-debug/maubot/main/docs/maubot-help-prefix.png"))


        with open(env["JSON_DIR"] + "userslvl.json", "r") as f:
            users = json.load(f)

        await self.update_data(users, message.author)
        await self.add_experience(users, message.author, 5)
        await self.level_up(self.bot, users, message.author, message.channel)

        with open(env["JSON_DIR"] + "userslvl.json", "w") as f:
            json.dump(users, f)
        # await self.bot.process_commands(message)

    async def update_data(self, users, user):
        if not str(user.id) in users:
            users[str(user.id)] = {}
            users[str(user.id)]["experience"] = 0
            users[str(user.id)]["level"] = 1
            users[str(user.id)]["last_message"] = 0

    async def add_experience(self, users, user, exp):
        users[str(user.id)]["experience"] += exp
        users[str(user.id)]["last_message"] = time.time()

    async def level_up(self, bot, users, user, channel):
        experience = users[str(user.id)]["experience"]
        lvl_start = users[str(user.id)]["level"]
        lvl_end = int(experience ** (1/4))
        try:
            with open(env["JSON_DIR"] + "userslvl.json") as f:
                f = json.load(f)
            guilds = f["active"][str(channel.guild.id)]
        except:
            guilds = False

        if lvl_start < lvl_end:
            if guilds == True:
                await channel.send(embed=discord.Embed(title=f':tada: ¡felicidades!', description=f'{user.mention}, has subido al nivel {lvl_end}! :champagne_glass: ', colour=color).set_footer(text="Si quieres desactivarlo puedes poner m.levels para desactivarlo"))
                users[str(user.id)]['level'] = lvl_end
        
    @commands.command(description="Cambia los si quieres recivir notificaciones de niveles")
    @commands.has_permissions(manage_channels=True)
    async def levels(self, ctx):
        with open(env["JSON_DIR"] + "userslvl.json", "r") as f:
            guilds = json.load(f)

        if not str(ctx.guild.id) in guilds["active"]:
            guilds["active"][str(ctx.guild.id)] = True
        else:
            guilds["active"][str(ctx.guild.id)] = not guilds["active"][str(ctx.guild.id)]

        await ctx.send(embed=discord.Embed(title=f"Se ha cambiado el sistema de los niveles a | {guilds['active'][str(ctx.guild.id)]}", color=color))

        with open(env["JSON_DIR"] + "userslvl.json", "w") as f:
            json.dump(guilds, f)

    @commands.command(description="Mira tu nivel de mensajes", usage="[usuario]")
    async def rank(self, ctx, user: discord.Member = None):
        with open(env["JSON_DIR"] + "userslvl.json", "r") as f:
            users = json.load(f)

        if not str(ctx.guild.id) in users["active"]:
            users["active"][str(ctx.guild.id)] = False
        if users["active"][str(ctx.guild.id)] is None or users["active"][str(ctx.guild.id)] is False:
            return await ctx.send(embed=discord.Embed(title="No se permiten los niveles", description=f"{ctx.author.mention} En este servidor no se admiten los niveles", color=color).set_footer(text="puedes poner m.levels para activarlo".capitalize()))

        if user is None:
            user = ctx.author

        experience = users[str(user.id)]["experience"]
        lvl_start = users[str(user.id)]["level"]
        lvl_end = int(experience ** (1/4))
        print(int(experience / lvl_end))
        
        # url = f'https://vacefron.nl/api/rankcard?username={user.name}&avatar={user.avatar_url}&level={users[str(user.id)]["level"]}&currentxp={experience - lvl_end}&rank=1&nextlevelxp={experience}&previouslevelxp={lvl_end}&custombg=https://cdn.discordapp.com/attachments/740416020761804821/741310178330148894/1596811604088.png&xpcolor=FFFFFF&isboosting=true'.replace(" ", "%20")

        if not str(user.id) in users:
            await ctx.send(f"El usuario {user} aun no tiene un rango.")
        else:
            embed = discord.Embed(colour=color)
            embed.set_author(name=f"nivel - {user.name}", icon_url=user.avatar_url)
            embed.add_field(name="nivel", value=users[str(user.id)]["level"], inline=True)
            embed.add_field(name="exp", value=users[str(user.id)]["experience"], inline=True)
            await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        eliminar_prefix(guild)
        bots = [member for member in guild.members if member.bot]

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(env["WEBHOOK_URL_SALIDA"], adapter = discord.AsyncWebhookAdapter(session))
            await webhook.send(content = ':outbox_tray: **Quitado de un servidor** `' + guild.name.strip('`') + '` (`' + str(guild.id) + '`)\n  Total: **' + str(guild.member_count) + '** | Usuarios: **' + str(guild.member_count - len(bots)) + '** | Bots: **' + str(len(bots)) + '**')

    @commands.Cog.listener() 
    async def on_ready(self):
    	for guild in self.bot.guilds:
    		if guild.member_count > 20:
    			bots = [member for member in guild.members if member.bot]
    			result = (len(bots) / guild.member_count) * 100
    			if result > 70.0:
    				await guild.leave()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.member_count > 20:
            bots = [member for member in member.guild.members if member.bot]
            result = (len(bots) / member.guild.member_count) * 100
            if result > 70.0:
                await member.guild.leave()
                
    @commands.Cog.listener()
    async def on_member_remove(self, member):
    	if member.guild.member_count > 20:
    		bots = [member for member in member.guild.members if member.bot]
    		result = (len(bots) / member.guild.member_count) * 100
    		if result > 70.0:
    			await member.guild.leave()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        if guild.member_count > 20:
            bots = [member for member in guild.members if member.bot]
            result = (len(bots) / guild.member_count) * 100
            if result > 70.0:
                return await guild.leave()

        bots = [member for member in guild.members if member.bot]

        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(env["WEBHOOK_URL_ENTRADA"], adapter = discord.AsyncWebhookAdapter(session))
                await webhook.send(content = ':inbox_tray: **Añadido a un servidor** `' + guild.name.strip('`') + '` (`' + str(guild.id) + '`)\n  Total: **' + str(guild.member_count) + '** | Usuarios: **' + str(guild.member_count - len(bots)) + '** | Bots: **' + str(len(bots)) + '**' + '<:maubot:774967705831997501>')
        except:
            pass

        try:
            def check(event):
                return event.target.id == self.bot.user.id
            bot_entry = await guild.audit_logs(action=discord.AuditLogAction.bot_add).find(check)
            msg_ent = await bot_entry.user.send(embed=discord.Embed(title="Holaaaaaa ", description=f"""<:maubot:774967705831997501> ¡Hola! Mi nombre es **{self.bot.user.name}**, Mi dever es hacer que tu servidor como tu se diviertan los mas posible
                Estoy seguro de que tu y yo seremos los mejores socios de la historia asique, gracias por invitarme a\n-> **{guild.name}**.

                **Los prefijos de los comandos son: `&`, `m.`, `m-`, `@mencion`** - `&` Es custom\n
                Esos son mis prefijos, siempre puedes hacerme menciones con **{self.bot.user.mention}**. 
                Si otro bot esta usando el mismo prefijo. `deves anikilarlo` es broma
                para cambiar de prefijo tienes que poner **m.prefix <nuevo prefijo>** (NO USES LOS BRACKETS).
                Para una lista de commando solo tienes que poner **m.help** y te saldran tooodos los comandos. 
                
                ¡Y se enviara un mensaje a mi desarroyador si pones `m.rate_bot <descripcion>`, `m.report <error>`, `m.request <cosa nueva>`! Cada uno de los comandos seran respectivos a los nombres
                {self.bot.user.name} ¿¡A que esperas!? (https://discord.gg/mwDBgubwdP)
                
                Puedes verme en:
                -> **[top.gg](https://top.gg/bot/730124969132163093)**
                -> **[blist.xyz](https://blist.xyz/bot/730124969132163093/)**
                -> **[Discord.Bots.gg](https://discord.bots.gg/bots/730124969132163093)**
                -> **[discord.boats](https://discord.boats/bot/730124969132163093)**
                -> **[botlist.space](https://botlist.space/bot/730124969132163093)**
                -> **[botsdatabase](https://botsdatabase.com/bot/730124969132163093)**    
                -> **[arcane](https://arcane-center.xyz/bot/730124969132163093)**    
                -> **[Delly](https://discordextremelist.xyz/bots/730124969132163093)**    
                -> **[botsfordiscord](https://botsfordiscord.com/bot/730124969132163093)**


                -> **[Web de Maubot](https://maubot.maucode.com)**
                """, colour=color))
            await msg_ent.add_reaction("<:maubot:774967705831997501>")
        except: pass
    
        with open(env["JSON_DIR"] + 'prefix.json', 'r') as f:
            prefixes = json.load(f)
        
        prefixes[str(guild.id)] = '&'

        with open(env["JSON_DIR"] + 'prefix.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        channel = discord.utils.get(guild.text_channels)

        embed1 = discord.Embed(title="Maubot - el mejor bot de la historia", description="<:maubot:774967705831997501> Maubot es un bot para que tu puedas hacer cosas diversas en tu servidor.\n\nMaubot tiene muchas funciones como: divertirte, puedes cambiar el prefijo del bot (por si quieres) y **mas** cosas, muchas cosas mas. Si quieres saber mas tu solo pon `m.help` o con el prefijo que tu le ayas puesto.\n\n", colour=color)
        embed1.set_author(name='Maubot', icon_url="https://img.icons8.com/nolan/64/launched-rocket.png")
        embed1.add_field(name="¿Necesitas ayuda?", value=f"Puedes poner **m.help** para conseguir una lista de los comandos mas guays del mundo desde diversion hasta musica y economia. La lista de comandos estan separadas por secciones asi que podrias poner `m.help [seccion]` para descubrir mas comandos super chulos. o si no puedes poner **<@730124969132163093>** .", inline=True)
        embed1.add_field(name="Diversion atope", value=f"Maubot tiene muchos comando para divertirse con manipulacion de imagenes a juegos como el `conecta4`, `rps` y mucho mas. Maubot tambien tiene un sistema de economia muy avanzado para ser millonarios y dominar el mundo 🤤...", inline=True)
        embed1.add_field(name="Legal", value=f"Escribe `&copyright` para ver el copyright de Maubot.", inline=False)
        embed1.add_field(name="¿Aun no te has enterado?", value=f"Puedes ver un tutorial de como usar Maubot poniendo <@730124969132163093>", inline=False)
        embed1.set_footer(text="Maubot - Puedes escribir @Maubot para mas info")

        msg_h1 = await channel.send(content="Hola, gracias por meterme en este servidor. \nlos mensajes de abajo os explicaran algunas características sobre mi.\nSi alguien quiere apoyar mi servidor por favor dale a este link **(https://discord.gg/mwDBgubwdP)**", embed=embed1)

def setup(bot):
    bot.add_cog(Servidor(bot))