import discord
from discord.ext import commands, tasks
from discord import app_commands

import logging
import sqlite3
import hashlib
from datetime import datetime, timezone
import os
import sys
import traceback
import random
import time 

import bot_secrets

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Python not looking in parent directories for common files you might want to use is stupid
sys.path.append("../")
from common.results import get_votes_by_party



BOT_TOKEN = bot_secrets.BOT_TOKEN
DB_FILE = "../../db/teaw_election_1.db"
UPDATE_MESSAGE_FILE = "../../db/update_message.txt"
ROLE_ID = 1319149115543781489   # I voted role for Dec. 2024 election
UPDATE_CHANNEL_ID = 1319130252739608727
ELECTION_END_TIME = 1735369140  # This is when the program will kill itself

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

logger = logging.getLogger()
logger.setLevel(logging.INFO)



# NOTE Message embeds
def create_voter_id_message(voter_id, time_registered: str) -> discord.Embed:
    embed = discord.Embed(
        title="Voter Registration Successful",
        description=f"""
        You have successfully registered to vote in the TEAW Presidential Election.
        
        You can vote with the `/vote` command.
        """,
        color=discord.Color.green()
    )
    embed.add_field(name="Your Voter ID", value=f"`{voter_id}`", inline=True)
    embed.add_field(name="Registration Date", value=f"`{time_registered}`", inline=True)
    embed.add_field(
        name="Important Reminder",
        value="Keep your Voter ID safe. It is a secret and will be needed for voting. If someone else has your voter ID, they can vote on your behalf.",
        inline=False
    )
    return embed

def create_bad_salt_message() -> discord.Embed:
    embed = discord.Embed(
        title="Invalid Salt",
        description="Your salt must be at least 4 characters long!",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Why is this important?",
        value="A salt helps keep your voter ID secure. Do not share the salt."
    )
    return embed

def create_invalid_voter_id_message() -> discord.Embed:
    embed = discord.Embed(
        title="Invalid Voter ID",
        description="Your voter ID is invalid. Please register to vote first with `/register`.",
        color=discord.Color.red()
    )
    return embed

def create_invalid_candidate_message() -> discord.Embed:
    embed = discord.Embed(
        title="Invalid Candidate",
        description="You have entered an invalid candidate. Please choose from the provided options.",
        color=discord.Color.red()
    )
    return embed

def create_vote_notification(time_voted) -> discord.Embed:
    embed = discord.Embed(
        title="Vote Cast",
        description=f"""
        You have successfully cast your ballot to vote in the TEAW Presidential Election.
        
        Repeat votes will overwrite your previous vote.
        """,
        color=discord.Color.green()
    )
    embed.add_field(name="Vote Date", value=f"`{time_voted}`", inline=True)
    
    embed.set_thumbnail(url="https://emojicdn.elk.sh/🎉")
    embed.set_footer(text="Thank you for keeping TEAW democratic! You have been given a voter role!")
    return embed

def election_results_message(results: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"TEAW Presidential Election Results as of <t:{int(time.time())}:R>",
        description=f"Updates every 5 minutes. \nThe election will end <t:{ELECTION_END_TIME}:R>!",
        color=discord.Color.blue()
    )

    for party, data in results.items():
        president_tag = f"<@{data['president_discord_id']}>"
        vp_tag = f"<@{data['vp_discord_id']}>"
        votes = data['votes']

        embed.add_field(
            name=f"{party} Party:",
            value=f"President: {president_tag} VP: {vp_tag} \n{votes} votes",
            inline=False
        )

    embed.set_footer(text="Thank you for participating in the election!")
    return embed



# NOTE Helper functions
def create_voter_id(user_id, time_registered, salt):
    return hashlib.sha256(f"{user_id}{time_registered}{salt}".encode()).hexdigest()[:8]

def get_candidates() -> dict:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT party_name, president_discord_id, vp_discord_id FROM candidates")
        candidates = cursor.fetchall()

    return {party_name: (president_id, vp_id) for party_name, president_id, vp_id in candidates}

def verify_voter_id(voter_id: str) -> bool: # See note in README.md
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT voter_id FROM voters WHERE voter_id = ?", (voter_id,))
        return cursor.fetchone() is not None



# NOTE Commands
@bot.tree.command(name="register", description="Registers you to vote.")
@app_commands.describe(voter_salt="A unique identifier for voter registration (minimum 4 characters). Do not share this value.")
async def register_voter(interaction: discord.Interaction, voter_salt: str):
    if len(voter_salt) < 4:
        embed = create_bad_salt_message()
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    discord_id = interaction.user.id
    discord_username = interaction.user.name # NOTE: This is purely for human reference, it should not be used for anything secure. Usernames can be changed.
    time_registered = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT voter_id, time_registered FROM voters WHERE discord_id = ?", (discord_id,))
            existing_voter = cursor.fetchone()

            if existing_voter:
                embed = create_voter_id_message(existing_voter[0], existing_voter[1])
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:   # TODO: should maybe just allow users to create a new voter ID if their old one leaked or something. Ensure to delete the old one.
                new_voter_id = create_voter_id(discord_id, time_registered, voter_salt)

                cursor.execute(
                    "INSERT INTO voters (voter_id, discord_id, discord_username, time_registered) VALUES (?, ?, ?, ?)",
                    (new_voter_id, discord_id, discord_username, time_registered),
                )
                conn.commit()

                embed = create_voter_id_message(new_voter_id, time_registered)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"Error registering voter: {e}")
            await interaction.response.send_message("An error occurred while registering. Please try again later.", ephemeral=True)

@bot.tree.command(name="vote", description="Submits your vote for a political party.")
@app_commands.describe(voter_id="Your voter ID.")
@app_commands.describe(candidate="The party you are voting for.")
async def vote(interaction: discord.Interaction, voter_id: str, candidate: str):
    if not verify_voter_id(voter_id):
        embed = create_invalid_voter_id_message()
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if candidate not in candidates:
        embed = create_invalid_candidate_message()
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


    time_voted = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ballots (voter_id, party, time_voted)
            VALUES (?, ?, ?)
            ON CONFLICT(voter_id) DO UPDATE SET
                party = excluded.party,
                time_voted = excluded.time_voted
            """, (voter_id, candidate, time_voted)
        )
        conn.commit()

    embed = create_vote_notification(time_voted)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    voter_role = discord.utils.get(interaction.guild.roles, id=ROLE_ID)
    await interaction.user.add_roles(voter_role, reason="Voted in a TEAW election")

candidates = list(get_candidates().keys())
@vote.autocomplete("candidate")
async def candidate_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    random.shuffle(candidates)  # Makes it more fair for each candidate
    
    return [
        app_commands.Choice(name=candidate, value=candidate)
        for candidate in candidates if current.lower() in candidate.lower()
    ]



# NOTE Tasks
@tasks.loop(seconds=300)
async def update_message():
    channel = bot.get_channel(UPDATE_CHANNEL_ID)
    if channel is None:
        print("Channel not found. Check the CHANNEL_ID")
        return

    message_id = None
    if os.path.exists(UPDATE_MESSAGE_FILE):
        with open(UPDATE_MESSAGE_FILE, "r") as file:
            message_id = int(file.read().strip())

    embed = election_results_message(get_votes_by_party())

    try:
        if message_id:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
        else:
            message = await channel.send(embed=embed)
            with open(UPDATE_MESSAGE_FILE, "w") as file:
                file.write(str(message.id))

    except discord.NotFound:    
        print("Message not found. Posting a new message")

        message = await channel.send(embed=embed)
        with open(UPDATE_MESSAGE_FILE, "w") as file:
            file.write(str(message.id))

    except Exception as e:
        print(f"Error updating message: {e}")

@tasks.loop(seconds=1)
async def end_election() -> None:
    if int(time.time()) > ELECTION_END_TIME:
        update_message()
        await bot.get_channel(UPDATE_CHANNEL_ID).send("The election has ended. These results are final!")

        print("Election has ended. Exiting...")

        bot.close()
        sys.exit(0)



# Init
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
    logging.info(f"Logged in as {bot.user.name}")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the TEAW Election"))


    update_message.start()
    end_election.start()

    print("Bot is ready")

bot.run(BOT_TOKEN)
