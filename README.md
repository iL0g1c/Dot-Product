# Dot-Product
DukePrime Remastered
## What is Dot-Product
Dot Product is the successor for DukePrime. DukePrime was built using an earlier version of the discord api before slash commands. Additionally, it did not use a database and instead stored the user data in jsonlines files. Dot-Product is a more elegant and user friendly version of this using: slash commands, embeds, interactables, and modals.
Dot-Product takes on the past role of dukeprime, by allowing patrol logging and allowing users to view logs from the database.

## How to add this bot to your server
Currently, DotProduct is in beta and not ready for release.
If you would like to beta test this bot, please send a request to me on discord.

## Commands
### User Commands
These are commands that any body is able to use.
#### ```/ping```
This command allows you to test if the bot is online and view your latency.

#### ```/patrol```
This command allows users to start and manage your patrol.
- First, you must select the type of patrol you would like to start
  - A flight patrol involves flying your aircraft on GeoFS preforming standard air force protocol.
  - A radar patrol involves watching the GeoFS map for enemy aircraft without actually flying a plane.
- Next, you can take off. During your patrol the embed has buttons for kills/disables as well as a button for ending your patrol.
- When you end your patrol, a modal will pop up asking for additional information.
- Finally, a patrol log will be sent to the channel set with ```setChannel```.

#### ```/top <MODE>```
This command allows you to view the leaderboards for a specific type of event. Buttons at the bottom of the embed allow you to scroll through the different pages.
The event mode has four options:
- flight_parrol
- radar_patrol
- kills
- disables
