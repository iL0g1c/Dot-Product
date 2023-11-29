import discord
from discord import app_commands
from discord.ext import tasks, commands
from discord.interactions import Interaction

from dotProduct import DotProductClient
from radarToolkit import RadarToolkit


class AutomatedRadar(commands.Cog):
    def __init__(self, bot: DotProductClient):
        self.client = bot
        self.toolkit = RadarToolkit()
        self.scanTerrain.start()

    @app_commands.command(name="toggleradar", description="Toggle the Automated Radar System on/off")
    async def toggleRadar(self, interaction: Interaction):
        server_id = interaction.guild_id
        isEnabled = self.toolkit.radarEnabled(server_id)
        print(isEnabled)
        if isEnabled:
            radarLogChannelID = self.toolkit.setRadar(False, server_id)
            status = "DISABLED"
        elif not isEnabled:
            radarLogChannelID = self.toolkit.setRadar(True, server_id)
            status = "ENABLED"

        radarLogChannel = self.client.get_channel(radarLogChannelID)
        embed = discord.Embed(
            title=f"Automated Radar System {status}",
            description=f"Radar Log Channel: **{radarLogChannel.name}**",
            color = discord.Colour.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addkeyword", description="Add air foce identifier keywords to radar detection.")
    @app_commands.describe(relationship="Roughly translates to the threat level of the keyword.", keyword="The four letter force identifier you want to search callsigns for.")
    @app_commands.choices(
            relationship=[
                app_commands.Choice(name="Ally", value=1),
                app_commands.Choice(name="Friendly", value=2),
                app_commands.Choice(name="Neutral", value=3),
                app_commands.Choice(name="Unfriendly", value=4),
                app_commands.Choice(name="Hostile", value=5)
            ]
    )
    async def addForceKeywords(self, interaction: Interaction, relationship: app_commands.Choice[int], keyword: str):
        pass

    async def cog_unload(self):
        self.scanTerrain.cancel()

    @tasks.loop(minutes=2.0)
    async def scanTerrain(self):
        # Gather all users from GeoFS
        # load aircraft role sheet
        # Remove non military aircraft
        # Get users that have enabled radar.
        # Load relations data for those guilds
        # Sort and remove remaining callsigns

        pilots = self.toolkit.fetchGeoFSUsers()
        radarActiveGuilds = self.toolkit.getRadarActiveGuilds()
        for guild in radarActiveGuilds:
            pass

    @scanTerrain.before_loop
    async def before_scanTerrain(self):
        print("Waiting to start global radar...")
        await self.bot.wait_until_ready()
        print("Global radar loop initiated.")

    @scanTerrain.after_loop
    async def after_scaneTerrain(self):
        print("Global radar loop terminated.")

    

async def setup(bot: DotProductClient):
    await bot.add_cog(AutomatedRadar(bot))