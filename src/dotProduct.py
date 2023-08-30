#DP001 Consecutive patrols trigger patrol deletion

import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime
import typing

from patrols import patrolOn, patrolOff, deleteDuplicatePatrols
from wins import kill, disable
from top import getLeaderboard

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        
    async def on_ready(self):
        print(f"{self.user} has connected to Discord.")
        activeservers = self.guilds
        for guild in activeservers:
            print(guild.name)

    async def setup_hook(self) -> None:
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

client = MyClient()

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

class DeleteOpenPatrols(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        style = discord.ButtonStyle.green,
        label = "Yes",
    )
    async def yes(self, interaction: discord.Interaction, button: discord.ui.button):
        embed = discord.Embed(
            title = "Deletion Complete",
            description = "Try opening a patrol again.",
            color = discord.Colour.blue()
        )
        deleteDuplicatePatrols(interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        style = discord.ButtonStyle.red,
        label = "No"
    )
    async def no(self, interaction: discord.Interaction, button: discord.ui.button):
        embed = discord.Embed(
            title = "Deletion Declined",
            color = discord.Colour.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class Patrol(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.createView()
        self.selectedPatrolType = None
        
    def createView(self):
        Patrol.StartPatrolButton(self)
        Patrol.PatrolTypeSelect(self)

    def generatePatrolButtons(self):
        Patrol.KillButton(self)
        Patrol.DisableButton(self)
        Patrol.EndPatrolButton(self)

    class StartPatrolButton(discord.ui.Button):
        def __init__(self, patrolView):
            self.patrolView = patrolView
            super().__init__(
                style=discord.ButtonStyle.green,
                label="Start Patrol",
                disabled=True,
                custom_id="start",
                row=1
            )
            self.patrolView.add_item(self)

        async def callback(self, interaction: discord.Interaction):
            datetime_amount = datetime.now().replace(microsecond=0)
            event_id, error = patrolOn(interaction.user.id, interaction.guild.id, datetime_amount, self.patrolView.selectedPatrolType)
            if error == 1:
                askView = DeleteOpenPatrols()
                embed = discord.Embed(
                    title="You already have a patrol open.",
                    description="Would you like to delete it?",
                    color = discord.Colour.blue()
                )
                await interaction.response.edit_message(embed=embed, view=askView)
                return

            self.patrolView.remove_item(self)

            patrolTypeButton = [x for x in self.patrolView.children if x.custom_id == "type"][0]
            patrolTypeButton.disabled = True

            self.patrolView.generatePatrolButtons()

            await interaction.response.edit_message(view=self.patrolView)
        async def delete_button(self):
            self.patrolView.remove_item(self)

    class KillButton(discord.ui.Button):
        def __init__(self, patrolView):
            self.patrolView = patrolView
            super().__init__(
                style=discord.ButtonStyle.gray,
                label="Kills (0)",
                row=1,
                custom_id="kill"
            )
            self.patrolView.add_item(self)
            self.kills = 0
            
        async def callback(self, interaction: discord.Interaction):
            kill(interaction.user.id, interaction.guild.id)
            self.kills += 1
            killButton = [x for x in self.patrolView.children if x.custom_id == "kill"][0]
            killButton.label = f"Kills ({self.kills})"
            await interaction.response.edit_message(view=self.patrolView)

    class DisableButton(discord.ui.Button):
        def __init__(self, patrolView):
            self.patrolView = patrolView
            super().__init__(
                style=discord.ButtonStyle.gray,
                label="Disables (0)",
                row=1,
                custom_id="disable"
            )
            self.patrolView.add_item(self)
            self.disables = 0

        async def callback(self, interaction: discord.Interaction):
            disable(interaction.user.id, interaction.guild.id)
            self.disables += 1
            disableButton = [x for x in self.patrolView.children if x.custom_id == "disable"][0]
            disableButton.label = f"Dissables ({self.disables})"
            await interaction.response.edit_message(view=self.patrolView)

    class EndPatrolButton(discord.ui.Button):
        def __init__(self, patrolView):
            self.patrolView = patrolView
            super().__init__(
                style=discord.ButtonStyle.red,
                label="End Patrol",
                row=1
            )
            self.patrolView.add_item(self)
    
        async def callback(self, interaction: discord.Interaction):
            datetime_amount = datetime.now().replace(microsecond=0)
            duration, start_time, event_id, patrol_type = patrolOff(interaction.user.id, interaction.guild.id, datetime_amount)

            embed = discord.Embed(
                title = "Patrol Log",
                description = f"{interaction.user.name} has completed their patrol.",
                color = discord.Colour.blue()
            )
            embed.add_field(name = "Name: ", value = interaction.user.name)
            embed.add_field(name = "Patrol Type", value = self.patrolView.selectedPatrolType)
            embed.add_field(name = "Start Time: ", value = start_time)
            embed.add_field(name = "End Time: ", value = datetime_amount)
            embed.add_field(name = "Duration: ", value = duration)
            await interaction.response.send_message(embed=embed)

    class PatrolTypeSelect(discord.ui.Select):
        def __init__(self, patrolView):
            self.patrolView = patrolView
            super().__init__(
                options=[
                    discord.SelectOption(
                        label="Flight Patrol",
                        value="flight"
                    ),
                    discord.SelectOption(
                        label="Radar Patrol",
                        value="radar"
                    )
                ],
                disabled=False,
                custom_id="type",
                placeholder="Select a patrol type.",
                row=0
            )
            self.patrolView.add_item(self)
        async def callback(self, interaction: discord.Interaction):
            self.patrolView.selectedPatrolType = self.values[0]
            startPatrolButton = [x for x in self.patrolView.children if x.custom_id == "start"][0]
            startPatrolButton.disabled = False
            await interaction.response.edit_message(view=self.patrolView)

@client.tree.command(name="patrol", description="Create a patrol.")
async def patrol(interaction: discord.Interaction):
    view = Patrol()

    embed = discord.Embed(
        title=f"{interaction.user.name}'s Patrol",
        color = discord.Colour.blue()
    )
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@client.tree.command(name="top", description="View your forces statistics.")
@app_commands.describe(mode="The type of event you would like to query.", time_span="The time span you would like to query.")
@app_commands.choices(
    mode=[
        app_commands.Choice(name="flight_patrols", value="flights"),
        app_commands.Choice(name="radar_patrols", value="radars"),
        app_commands.Choice(name="kills", value="kills"),
        app_commands.Choice(name="disables", value="disables"),
        app_commands.Choice(name="sars", value="sars")
    ],
    time_span=[
        app_commands.Choice(name="day", value="day"),
        app_commands.Choice(name="week", value="week"),
        app_commands.Choice(name="month", value="month"),
        app_commands.Choice(name="all", value="all")
    ]
)
async def top(interaction: discord.Interaction, mode: app_commands.Choice[str], time_span: typing.Optional[app_commands.Choice[str]]):
    raw_events = getLeaderboard(interaction.guild.id, mode.value, time_span.value)
    leaderboard = ""
    for i in range(len(raw_events)):
        member = interaction.guild.get_member(raw_events[i]["user_id"])
        if member == None:
            continue
        leaderboard += f"{i+1}. {member.display_name} | {mode.value}: {raw_events[i]['counts']}\n"

    if leaderboard == "":
        leaderboard = f"There are no {mode.value} in the selected time period."

    embed = discord.Embed(
        title = f"{mode.value} leaderboard",
        description = leaderboard,
        color = discord.Colour.blue()
    )
    await interaction.response.send_message(embed=embed)

client.run(BOT_TOKEN)