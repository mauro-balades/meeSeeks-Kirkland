import discord
from discord.ext import commands
import asyncio

from os import environ as env
import json

color = int(env["COLOR"])

class Eventos():
    def __init__(self, bot):
        self.bot = bot

    async def abrir(self, iniciador, destinatario):
        with open("./src/json/chats.json", "r") as f:
            chats = json.load(f)

        if not str(iniciador.id) in chats:
            chats[f"{iniciador.id}"] = {}
            chats[f"{iniciador.id}"]["dest"] = destinatario.id
            chats[f"{destinatario.id}"] = {}
            chats[f"{destinatario.id}"]["dest"] = destinatario.id
        else:
            if chats[f"{iniciador.id}"] == {}:
                return "Usuario ya en chat"

        with open("./src/json/chats.json", "w") as f:
            json.dump(chats, f)

    async def inicio(self, ctx, iniciador=None, dest=None):
        if dest is not None:
            j = await self.abrir(iniciador, dest)
            if j == "Usuario ya en chat":
                return await ctx.send("Ese usuario ya esta en un chat...")
            await iniciador.send(embed=discord.Embed(title="Se ha iniciado un chat", description=f"Hola, {iniciador.mention} se ha creado un chat con **{dest.name}**",color=color).set_footer(text="Si se tarda mas de 30 minutos en responder el chat se cierra (Pon 'cerrarchat' para terminar la conversacion)"))
            await dest.send(embed=discord.Embed(title="Se ha iniciado un chat", description=f"Hola, {dest.mention} **{iniciador.name}** ha creado un chat para hablar",color=color).set_footer(text="Si se tarda mas de 30 minutos en responder el chat se cierra (Pon 'cerrarchat' para terminar la conversacion)"))
        else: return await ctx.send("Ese usuario no existe. Creo...")

class ChatApp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases="startchat,start_chat,chat_start,chatstart".split(","), description="Inicia un chat con una persona", usage="<id del usuario NO MENCIONES>", name="chat")
    async def __start_chat(self, ctx):
        destinatario = ctx.message.mentions[0]

        iniciador = ctx.author
        
        chat = True

        Ev = Eventos(self.bot)

        await Ev.inicio(ctx, iniciador, destinatario)

        # while chat:
        #     try:
        #         msg = await self.bot.wait_for('message', timeout=30.0)
        #         print(msg)
        #     except asyncio.TimeoutError:
        #         await destinatario.send()
        #         return await iniciador.send(embed=discord.Embed(title="Se ha cerrado la conexion", description="Razon: El tiempo se ha agotado", color=color))


def setup(bot):
    bot.add_cog(ChatApp(bot))