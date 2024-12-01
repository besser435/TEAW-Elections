import discord
from discord.ext import commands, tasks
from discord import app_commands

import logging
import sqlite3
import hashlib
from datetime import datetime, timezone
import os

import bot_secrets

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = "../../db/TEAW_E_1.db"
VOTE_FORM_URL = "https://forms.gle/fAtceQycitem1oCCA"
BOT_TOKEN = bot_secrets.BOT_TOKEN

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# NOTE Message embeds
def create_voter_id_message(voter_id: str) -> discord.Embed:
    embed = discord.Embed(
        title="Voter Registration Successful",
        description=f"""
        You have successfully registered to vote in the TEAW Presidential Election.
        
        You can vote [here]({VOTE_FORM_URL}).
        """,
        color=discord.Color.green()
    )
    embed.add_field(name="Your Voter ID", value=f"`{voter_id}`", inline=False)
    embed.add_field(
        name="Important Reminder",
        value="Keep your voter ID safe. It is a secret and will be needed for voting. If someone else has your voter ID, they can vote on your behalf.",
        inline=False
    )
    embed.set_thumbnail(url="https://emojicdn.elk.sh/🎉")
    embed.set_footer(text="Thank you for keeping TEAW democratic!")
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

def create_vote_notification(ballot) -> discord.Embed:
    # For successful_vote_notification()
    pass


# NOTE Helper functions
def create_voter_id(user_id, time_registered, salt):
    return hashlib.sha256(f"{user_id}{time_registered}{salt}".encode()).hexdigest()[:8]


# NOTE Commands
@bot.tree.command(name="register", description="Registers you to vote.")
@app_commands.describe(voter_salt="A unique identifier for voter registration (minimum 4 characters). Do not share this value.")
async def register(interaction: discord.Interaction, voter_salt: str):
    if len(voter_salt) < 4:
        embed = create_bad_salt_message()
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    discord_id = interaction.user.id
    discord_username = interaction.user.name # NOTE: This is purely for human reference, it should not be used for anything secure. Usernames can be changed.
    time_registered = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM voters WHERE discord_id = ?", (discord_id,))
            existing_voter = cursor.fetchone()

            if existing_voter:
                embed = create_voter_id_message(existing_voter[0])
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:   # TODO: should maybe just allow users to create a new voter ID if their old one leaked or something. Ensure to delete the old one.
                new_voter_id = create_voter_id(discord_id, time_registered, voter_salt)

                cursor.execute(
                    "INSERT INTO voters (voter_id, discord_id, discord_username, time_registered) VALUES (?, ?, ?, ?)",
                    (new_voter_id, discord_id, discord_username, time_registered),
                )
                conn.commit()

                embed = create_voter_id_message(new_voter_id)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error registering voter: {e}")
            await interaction.response.send_message("An error occurred while registering. Please try again later.", ephemeral=True)


# NOTE Tasks
@tasks.loop(seconds=60)
async def update_message():
    # This will post a message in a channel if it does not exist. 
    # It will then edit the message as the database gets updates.
    pass

async def successful_vote_notification():
    # This will DM the user who voted to confirm their vote.
    # It will reply with their ballot.
    pass


# Init
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
    logging.info(f"Logged in as {bot.user.name}")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the TEAW Election"))

bot.run(BOT_TOKEN)
