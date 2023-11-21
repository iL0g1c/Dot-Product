# [X] Allow setting log channel
# [X] Allow inputing location and description.
# [X] Fixed DP0001. Top errored when not providing a value for time_span


import discord
from discord import app_commands
from discord.ext import commands
import os
from discord.interactions import Interaction
from dotenv import load_dotenv
from datetime import datetime
import typing

from patrols import patrolOn, patrolOff, deleteDuplicatePatrols
from wins import kill, disable
from top import getLeaderboard
from admin import makeSuperuser, removeEvent, savePatrolChannel, getLogChannel
from errors import getErrorMessage
from userlogs import updatePage

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
        self.author_id = 0
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
        
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(content="This isn't your patrol.", ephemeral=True)
            return False
        return True

class Patrol(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.createView()
        self.author_id = 0
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
                askView.author_id = interaction.user.id
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
            datetime_amount = datetime.now().replace(microsecond=0)
            kill(interaction.user.id, interaction.guild.id, datetime_amount)
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
            datetime_amount = datetime.now().replace(microsecond=0)
            disable(interaction.user.id, interaction.guild.id, datetime_amount)
            self.disables += 1
            disableButton = [x for x in self.patrolView.children if x.custom_id == "disable"][0]
            disableButton.label = f"Disables ({self.disables})"
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
            self.datetime_amount = datetime.now().replace(microsecond=0)
            self.duration, self.start_time, self.event_id, self.patrol_type = patrolOff(interaction.user.id, interaction.guild.id, self.datetime_amount)
            self.patrolView.infoModal = Patrol.InfoModal(self.patrolView, self)
            
            await interaction.response.send_modal(self.patrolView.infoModal)
            

    class InfoModal(discord.ui.Modal):
        def __init__(self, patrolView, patrolStats):
            self.patrolView = patrolView
            self.patrolStats = patrolStats
            super().__init__(
                title="Additional Information",
                timeout=None
            )

            self.location = discord.ui.TextInput(
                style=discord.TextStyle.short,
                label = "Location",
                required = True,
                row = 0
            )
            self.add_item(self.location)

            self.description = discord.ui.TextInput(
                style=discord.TextStyle.long,
                label = "Description",
                required = True,
                row = 1
            )
            self.add_item(self.description)

        async def on_submit(self, interaction: discord.Interaction):
            logEmbed = discord.Embed(
                title = "Patrol Log",
                description = f"{interaction.user.name} has completed their patrol.\n **Location:** {self.location.value}\n **Description:** {self.description.value}",
                color = discord.Colour.blue()
            )
            logEmbed.add_field(name = "Name: ", value = interaction.user.name)
            logEmbed.add_field(name = "Patrol Type", value = self.patrolView.selectedPatrolType)
            logEmbed.add_field(name = "Start Time: ", value = self.patrolStats.start_time)
            logEmbed.add_field(name = "End Time: ", value = self.patrolStats.datetime_amount)
            logEmbed.add_field(name = "Duration: ", value = self.patrolStats.duration)
            logEmbed.add_field(name = "ID: ", value = self.patrolStats.event_id)
            channel_id, error = getLogChannel(interaction.guild.id)
            if error:
                error_msg = getErrorMessage(error)
                errorEmbed = discord.Embed(
                    title = "Your server doesn't have a log channel.",
                    description = "Contact an admin for help. Sending log here.",
                    color = discord.Colour.blue()
                )
                await interaction.response.send_message(embed=errorEmbed)
                await interaction.followup.send(embed=logEmbed)


            else:
                channel = client.get_channel(channel_id)
                successEmbed = discord.Embed(
                    title = "Patrol Complete",
                    description = f"Your log has been stored in {channel.name}",
                    color = discord.Colour.blue()
                )
                await interaction.response.send_message(embed=successEmbed)
                await channel.send(embed=logEmbed)

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
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(content="This isn't your patrol.", ephemeral=True)
            return False
        return True
        

@client.tree.command(name="patrol", description="Create a patrol.")
async def patrol(interaction: discord.Interaction):
    view = Patrol()
    view.author_id = interaction.user.id

    embed = discord.Embed(
        title=f"{interaction.user.name}'s Patrol",
        color = discord.Colour.blue()
    )
    await interaction.response.send_message(embed=embed, view=view)

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
    if time_span == None:
        time_span = app_commands.Choice(name="month", value="month")
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

class UserLogs(discord.ui.View):
    def __init__(self, user, server_id, mode, items):
        self.user = user
        self.mode = mode
        self.author_id = 0
        self.items = int(items)
        self.page = 1
        super().__init__()
        description, edge_alert, error = updatePage(self.user.id, server_id, self.mode, self.items, self.page)
        if error:
            self.page -= 1
            error_msg = getErrorMessage(error)
            self.embed = discord.Embed(title = error_msg, color = discord.Colour.red())
            return
        else:
            self.embed = discord.Embed(
                title = f"{self.user}'s {self.mode} log",
                description = description,
                color = discord.Colour.blue()
            )
            self.createView(edge_alert)
        
    def createView(self, edge_alert):
        UserLogs.BackwardButton(self)
        UserLogs.ForwardButton(self)

        forwardButton = [x for x in self.children if x.custom_id == "forward"][0]
        if edge_alert:
            forwardButton.disabled = True

    class ForwardButton(discord.ui.Button):
        def __init__(self, userlogsView):
            self.userlogsView = userlogsView
            super().__init__(
                style=discord.ButtonStyle.grey,
                label="Next",
                custom_id="forward",
                row=1
            )
            self.userlogsView.add_item(self)
    
        async def callback(self, interaction: discord.Interaction):
            self.userlogsView.page += 1
            description, edge_alert, error = updatePage(self.userlogsView.user.id, interaction.guild.id, self.userlogsView.mode, self.userlogsView.items, self.userlogsView.page)
            if error == 5:
                self.userlogsView.page -= 1

            backwardButton = [x for x in self.userlogsView.children if x.custom_id == "back"][0]
            if self.userlogsView.page >= 1:
                backwardButton.disabled = False

            forwardButton = [x for x in self.userlogsView.children if x.custom_id == "forward"][0]
            if edge_alert:
                forwardButton.disabled = True

            self.userlogsView.embed = discord.Embed(
                title = f"{self.userlogsView.user.name}'s {self.userlogsView.mode} logs",
                description = description,
                color = discord.Colour.blue()
            )
            await interaction.response.edit_message(embed=self.userlogsView.embed, view=self.userlogsView)

    class BackwardButton(discord.ui.Button):
        def __init__(self, userlogsView):
            self.userlogsView = userlogsView
            super().__init__(
                style=discord.ButtonStyle.grey,
                label="Back",
                custom_id="back",
                row=1,
                disabled=True
            )
            self.userlogsView.add_item(self)
        
        async def callback(self, interaction: discord.Interaction):
            self.userlogsView.page -= 1
            description, edge_alert, error = updatePage(self.userlogsView.user.id, interaction.guild.id, self.userlogsView.mode, self.userlogsView.items, self.userlogsView.page)

            if error == 4:
                self.userlogsView.page += 1                

            backwardButton = [x for x in self.userlogsView.children if x.custom_id == "back"][0]
            if self.userlogsView.page <= 1:
                backwardButton.disabled = True

            forwardButton = [x for x in self.userlogsView.children if x.custom_id == "forward"][0]
            if not edge_alert:
                forwardButton.disabled = False

            self.userlogsView.embed = discord.Embed(
                title = f"{self.userlogsView.user.name}'s {self.userlogsView.mode} logs",
                description = description,
                color = discord.Colour.blue()
            )
            await interaction.response.edit_message(embed=self.userlogsView.embed, view=self.userlogsView)
            
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(content="This isn't your patrol.", ephemeral=True)
            return False
        return True


@client.tree.command(name="userlogs", description="View the event logs for each user.")
@app_commands.describe(
    user="The user you want to view logs for.",
    mode="The type of event you would like to query.",
    items="The number of items per page."
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="flight_patrols", value="flights"),
        app_commands.Choice(name="radar_patrols", value="radars"),
        app_commands.Choice(name="kills", value="kills"),
        app_commands.Choice(name="disables", value="disables"),
        app_commands.Choice(name="sars", value="sars")
    ]
)
async def userlogs(interaction: discord.Interaction, user: discord.Member, mode: app_commands.Choice[str], items: typing.Optional[str]):
    if items == None:
        items = 10
    view = UserLogs(user, interaction.guild.id, mode.value, items)
    view.author_id = interaction.user.id

    await interaction.response.send_message(embed=view.embed, view=view)

@client.tree.command(name="remev", description="Remove an event (patrol/kill/etc) from your server.")
@app_commands.describe(event_id="Event IDs are listed using the userlogs command.")
async def remev(interaction: discord.Interaction, event_id: int):
    error = removeEvent(interaction.user.id, interaction.guild.id, event_id)
    if error:
        error_msg = getErrorMessage(error)
        embed = discord.Embed(
            title = error_msg,
            color = discord.Colour.red()
        )
    else:
        embed = discord.Embed(
            title=f"Removed event **{event_id}** from the database.",
            color=discord.Colour.red()
        )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="setchannel", description="Set the channel for patrol logs to be posted in.")
@app_commands.describe(channel="The ID of the channel to recieve patrol logs in.")
async def setChannel(interaction: discord.Interaction, channel: discord.TextChannel):
    savePatrolChannel(channel.id, interaction.guild.id)
    embed = discord.Embed(
        title = f"Successfully set the log channel to: {channel.name}",
        color = discord.Colour.red()
    )

    await interaction.response.send_message(embed=embed)

client.run(BOT_TOKEN)