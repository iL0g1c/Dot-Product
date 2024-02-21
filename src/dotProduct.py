import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

from errors import getErrorMessage
from admin import makeSuperuser, savePatrolChannel, saveAutomatedRadarChannel

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_ALPHA_TOKEN")

class DotProductClient(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="=",
            intents=discord.Intents.all()
        )
        
    async def on_ready(self):
        print(f"{self.user} has connected to Discord.")
        activeservers = self.guilds
        for guild in activeservers:
            print(guild.name)

    async def setup_hook(self) -> None:
        print("Starting up...")
        await self._load_extensions()
        print("Loaded Extensions.")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)
        
        print("Synced.")
        print("Complete.")
    
    async def _load_extensions(self):
        for extension in ("patrolLogging","radar"):
            await self.load_extension(f"cogs.{extension}")
            
client = DotProductClient()

@client.event
async def on_guild_join(guild):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add):
        print(f"Joined {guild.name}")
        if entry.target.id == 1145483978799841372:
            channel = await entry.user.create_dm()
            await channel.send("Thank you for adding Dot Product to your server.\n Currently this bot is in beta and it is mad trash, so your patience is valued.")
            break

@client.tree.command(name="ping", description="Check bot connection and latency.")
async def ping(interaction: discord.Interaction):
    delay = round(client.latency * 1000)
    embed = discord.Embed(title="Pong!", description=f":ping_pong: {delay}ms", color=discord.Colour.blue())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="superuser", description="Make a user a superuser.")
@app_commands.describe(action="You can either add or remove a superuser.", user="The user you would like superuser.")
@app_commands.choices(
    action=[
        app_commands.Choice(name="add", value=1),
        app_commands.Choice(name="remove", value=2)
    ]
)
@app_commands.checks.has_permissions(manage_roles=True)
async def superuser(interaction: discord.Interaction, action: app_commands.Choice[int], user: discord.Member):
    error = makeSuperuser(user.id, interaction.guild.id, action.value)

    if error:
        error_msg = getErrorMessage(error)
        embed = discord.Embed(title = error_msg, color = discord.Colour.red())
    else:
        if action.value == 1:
            response = f"Made {user.name} a DotProduct superuser."
        elif action.value == 2:
            response = f"Made {user.name} not a DotProduct superuser."
        embed = discord.Embed(title = response, color = discord.Colour.blue())
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="setchannel", description="Set the channel for patrol logs to be posted in.")
@app_commands.describe(channel="The ID of the channel to recieve patrol logs in.")
@app_commands.choices(
    channel_type=[
        app_commands.Choice(name="Patrol Logs", value=1),
        app_commands.Choice(name="Radar Logs", value=2)
    ]
)
async def setChannel(interaction: discord.Interaction, channel_type: app_commands.Choice[int], channel: discord.TextChannel):
    if channel_type.value == 1:
        savePatrolChannel(channel.id, interaction.guild.id)
    elif channel_type.value == 2:
        saveAutomatedRadarChannel(channel.id, interaction.guild.id)
    embed = discord.Embed(
        title = f"Successfully set the log channel to: {channel.name}",
        color = discord.Colour.red()
    )

    await interaction.response.send_message(embed=embed)

def main():
    client.run(BOT_TOKEN)

if __name__ in "__main__":
    main()