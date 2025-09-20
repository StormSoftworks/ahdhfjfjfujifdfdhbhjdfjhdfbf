import sqlite3
import random
import string
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import has_guild_permissions, MissingPermissions
from discord.ui import View, Button, Modal, TextInput
from colorama import Fore

client = commands.Bot(command_prefix='.',
                      intents=discord.Intents.all(),
                      help_command=None)

TOKEN = "MTQxODYyMTc3OTAyMjQ1MDc5MQ.GzXI9N.AIIFIy4U8hraXZ8L9XcD-FKoF_07g4k5us4_aU"
ModLogsId = 1418627395635646544
MODERATOR_ROLE_ID = 1418654116904964149
DB_WARNINGS = "warnings.db"
DB_LOA = "loadb.db"

time_units = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "mo": 2592000
}


def parse_time(time_str):
    """Parses a time string and returns the duration in seconds.

    Args:
        time_str: The time string to parse (e.g., "10m", "2d", "3w").

    Returns:
        int: The duration in seconds, or None if the input is invalid.
    """
    try:
        time_str = time_str.strip().lower()
        if time_str[-1].isalpha():
            amount = int(time_str[:-1])
            unit = time_str[-1]
            return amount * time_units[unit]
        else:
            return int(time_str)  # Handle pure numbers as seconds
    except (ValueError, KeyError):
        return None  # Invalid time format


def init_warnings_db():
    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    punishment TEXT,
                    warning_threshold INTEGER,
                    mute_duration TEXT
                )''')
    conn.commit()
    conn.close()

def init_loa_db():
    conn = sqlite3.connect(DB_LOA)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS loas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER,
                    guild_id INTEGER,
                    starting_date TEXT,
                    ending_date TEXT,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

# Initialize databases
init_warnings_db()
init_loa_db()

# ----------------------
# Warnings Functions
# ----------------------
def add_warning(user_id, guild_id, reason):
    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute("INSERT INTO warnings (user_id, guild_id, reason) VALUES (?, ?, ?)",
              (user_id, guild_id, reason))
    conn.commit()
    conn.close()

def remove_warnings(user_id, guild_id, number):
    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute("SELECT id FROM warnings WHERE user_id=? AND guild_id=? ORDER BY timestamp ASC LIMIT ?",
              (user_id, guild_id, number))
    rows = c.fetchall()
    if rows:
        c.executemany("DELETE FROM warnings WHERE id=?", rows)
        conn.commit()
    conn.close()
    return len(rows)

# ----------------------
# LOA Functions
# ----------------------
def add_loa(member_id, guild_id, start, end, reason):
    conn = sqlite3.connect(DB_LOA)
    c = conn.cursor()
    c.execute("INSERT INTO loas (member_id, guild_id, starting_date, ending_date, reason) VALUES (?, ?, ?, ?, ?)",
              (member_id, guild_id, start, end, reason))
    loa_id = c.lastrowid
    conn.commit()
    conn.close()
    return loa_id

def remove_loa(loa_id):
    conn = sqlite3.connect(DB_LOA)
    c = conn.cursor()
    c.execute("DELETE FROM loas WHERE id=?", (loa_id,))
    conn.commit()
    conn.close()


# events
@client.event
async def on_ready():
    print("Logged in as {}".format(client.user))
    print(Fore.GREEN + "[✅]: Bot is running successfully!")
    activity = discord.Game(name="Playing Sector17")
    await client.change_presence(status=discord.Status.online,
                                 activity=activity)


# commands
@client.command()
async def cmds(ctx):
    embed = discord.Embed(title="Commands",
                          description="List of available commands:")
    embed.add_field(
        name="How to setup:",
        value=
        "Ensure moderator role's have access to <application_commands_permission> in order to use the bot",
        inline=False)
    embed.add_field(
        name="Prefix",
        value=
        "The prefix is <.>\n------------------------------------------------",
        inline=False)
    embed.add_field(
        name=
        ".modaction <robloxusername:text> <discordprofile:ping> <reason:text> <action:text> <proof:attachment>",
        value="Log's an moderation activity within the moderation logs.",
        inline=False)
    embed.add_field(
        name=".ssuping <time:string> <note:string> <reactrequirements:string>",
        value="Announce's an upcomming potentional ssu.",
        inline=False)
    embed.add_field(name=".ban <member:ping> <reason:string>",
                    value="Ban's an member from Sector 17 with an reason.",
                    inline=False)
    embed.add_field(name=".kick <member:ping> <reason:string>",
                    value="Kick's an member from Sector 17 with an reason.",
                    inline=False)
    embed.add_field(
        name=".RWarning <user:ping> <reduce:number>",
        value="Reduces the number of warnings for a specified user.",
        inline=False)
    embed.add_field(name=".warn <user:ping> <reason:string>",
                    value="Warn's the specified user.",
                    inline=False)
    embed.add_field(name=".warnings",
                    value="Show's all the warnings in this server.",
                    inline=False)
    embed.add_field(
        name=
        ".loa_request <add> <member:ping> <start_date:string> <end_date:string> <reason:string>",
        value=
        "Adds a Leave of Absence (LOA) for a member. Requires LOA Moderator role approval.",
        inline=False)
    embed.add_field(
        name=".loa_request <remove> <LOA_ID:integer>",
        value=
        "Removes a Leave of Absence (LOA) by its ID. Requires LOA Moderator role approval.",
        inline=False)
    embed.add_field(
        name=".list_loa",
        value=
        "List's all the active LOA's.",
        inline=False)
    embed.add_field(
        name=".codename <member:ping> <codename:string>",
        value=
        "Set's an codename for yourself.",
        inline=False)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(use_application_commands=True)
async def modaction(ctx, robloxusername: str, discordprofile: discord.Member,
                    *, reason_action: str):
    """
    Usage: !modaction <robloxusername> <@discordprofile> <reason and action>
    Attach proof as a file to the message
    """

    # Split reason and action intelligently:
    # We assume the last "word(s)" are action, everything before is reason
    # Here we split by the last occurrence of " | " if the user used a delimiter
    if " | " in reason_action:
        reason, action = map(str.strip, reason_action.rsplit(" | ", 1))
    else:
        # If no delimiter, try splitting by last word
        parts = reason_action.strip().split()
        if len(parts) > 1:
            reason = " ".join(parts[:-1])
            action = parts[-1]
        else:
            reason = reason_action
            action = "No action specified"

    # Handle attachment
    proof_file = ctx.message.attachments[0] if ctx.message.attachments else None
    proof_url = proof_file.url if proof_file else "No proof attached."

    # Build embed
    embed = discord.Embed(title="🛡️ Moderation Action", )
    embed.add_field(name="[👤]: Roblox Username",
                    value=robloxusername,
                    inline=False)
    embed.add_field(name="[💬]: Discord Profile",
                    value=discordprofile.mention,
                    inline=False)
    embed.add_field(name="[📄]: Reason", value=reason, inline=False)
    embed.add_field(name="[⚡]: Action", value=action, inline=False)
    embed.add_field(name="[📷]: Proof", value=proof_url, inline=False)
    embed.set_footer(
        text=f"Action taken by {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    # Send to mod logs channel
    channel = client.get_channel(ModLogsId)
    if channel:
        if proof_file:
            file = await proof_file.to_file()
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(embed=embed)

        # Confirmation embed
        confirm_embed = discord.Embed(
            title="✅ Moderation Logged",
            description=
            f"Action against {discordprofile.mention} has been logged in <#{ModLogsId}>.",
            color=discord.Color.green())
        confirm_embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await ctx.send(embed=confirm_embed)
    else:
        await ctx.send(embed=discord.Embed(
            description=
            "❌ Could not find the mod logs channel. Please check the ID.",
            color=discord.Color.red()))


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


@client.command()
@commands.has_permissions(use_application_commands=True)
async def ssuping(ctx, time: str, note: str, requirements: str):
    """
    Send an SSU announcement with reactions and formatted embed.
    Usage: !ssuping <time> <note> <requirements>
    """

    # Build the message content with separators
    ssu_message = (
        f"Server Start Up Host: {ctx.author.mention} is hosting an SSU! Vote for this SSU to be hosted.\n"
        "------------------------------------------------\n"
        f"Reaction Requirement: {requirements}\n"
        f"Time: {time}\n"
        "------------------------------------------------\n"
        "Casual: 1️⃣\n"
        "Semi-Serious: 2️⃣\n"
        "Serious: 3️⃣")

    # Build the embed
    embed = discord.Embed(
        title="SSU Announcement",
        description="Get ready to vote for the next SSU!",
    )

    embed.add_field(name="SSU Message", value=ssu_message, inline=False)
    embed.add_field(name="📅 Scheduled Time", value=time, inline=False)
    embed.add_field(name="📌 Notes", value=note, inline=False)

    embed.set_footer(
        text=f"Hosted by {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)
    await ctx.send("@everyone")


@client.command()
@commands.has_permissions(use_application_commands=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    memberembed = discord.Embed(
        title="Sector 17",
        description=
        "You we're banned from Sector 17 by an moderator. The argument's are listed below.",
    )

    memberembed.add_field(name="Reason", value=reason, inline=False)
    memberembed.add_field(name="Moderator", value=ctx.author, inline=False)

    await member.send(embed=memberembed)

    embed = discord.Embed(
        title="Command Report",
        description="Successfully executed: ban",
    )

    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Member", value=member, inline=False)

    embed.set_footer(
        text=f"Moderated by {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)
    await member.ban(reason=reason or "No reason provided")


@client.command()
@commands.has_permissions(use_application_commands=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    memberembed = discord.Embed(
        title="Sector 17",
        description=
        "You we're kicked from Sector 17 by an moderator. The argument's are listed below.",
    )

    memberembed.add_field(name="Reason", value=reason, inline=False)
    memberembed.add_field(name="Moderator", value=ctx.author, inline=False)

    await member.send(embed=memberembed)

    embed = discord.Embed(
        title="Command Report",
        description="Successfully executed: kick",
    )

    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Member", value=member, inline=False)

    embed.set_footer(
        text=f"Moderated by {ctx.author}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)
    await member.kick(reason=reason or "No reason provided")

@client.command()
@commands.has_permissions(use_application_commands=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    reason = reason or "No reason provided"
    add_warning(member.id, ctx.guild.id, reason)

    embed = discord.Embed(title="⚠️ User Warned")
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)

    # Check punishment config
    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute("SELECT punishment, warning_threshold, mute_duration FROM config WHERE guild_id=?",
              (ctx.guild.id,))
    config = c.fetchone()
    conn.close()

    if config:
        punishment, threshold, mute_duration = config
        conn = sqlite3.connect(DB_WARNINGS)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM warnings WHERE user_id=? AND guild_id=?",
                  (member.id, ctx.guild.id))
        count = c.fetchone()[0]
        conn.close()

        if count >= threshold:
            if punishment == "kick":
                await member.kick(reason=f"Reached {threshold} warnings.")
                await ctx.send(f"{member.mention} has been kicked.")
            elif punishment == "ban":
                await member.ban(reason=f"Reached {threshold} warnings.")
                await ctx.send(f"{member.mention} has been banned.")
            elif punishment == "mute":
                seconds = parse_time(mute_duration) or 3600
                for ch in ctx.guild.channels:
                    if isinstance(ch, discord.TextChannel):
                        overwrite = ch.overwrites_for(member)
                        overwrite.send_messages = False
                        await ch.set_permissions(member, overwrite=overwrite)
                await ctx.send(f"{member.mention} has been muted for {mute_duration}.")
                await asyncio.sleep(seconds)
                for ch in ctx.guild.channels:
                    if isinstance(ch, discord.TextChannel):
                        overwrite = ch.overwrites_for(member)
                        overwrite.send_messages = None
                        await ch.set_permissions(member, overwrite=overwrite)
                await ctx.send(f"{member.mention} has been unmuted.")

@client.command()
@commands.has_permissions(use_application_commands=True)
async def warnings(ctx):
    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute("SELECT user_id, COUNT(*) FROM warnings WHERE guild_id=? GROUP BY user_id",
              (ctx.guild.id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return await ctx.send(f"No warnings in {ctx.guild.name}")

    embed = discord.Embed(title=f"Warnings in {ctx.guild.name}")
    for uid, count in rows:
        user = await client.fetch_user(uid)
        embed.add_field(name=user.name, value=f"{count} warning(s)", inline=False)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(use_application_commands=True)
async def RWarning(ctx, member: discord.Member, number: int):
    removed = remove_warnings(member.id, ctx.guild.id, number)
    await ctx.send(f"Removed {removed} warnings from {member.mention}.")

@client.command()
@commands.has_permissions(use_application_commands=True)
async def config_Warnings(ctx, punishment: str, warning_threshold: int, mute_duration: str = None):
    if punishment.lower() not in ["kick", "mute", "ban"]:
        return await ctx.send("Invalid punishment. Use kick, mute, or ban.")

    conn = sqlite3.connect(DB_WARNINGS)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (guild_id, punishment, warning_threshold, mute_duration) VALUES (?, ?, ?, ?)",
              (ctx.guild.id, punishment.lower(), warning_threshold, mute_duration))
    conn.commit()
    conn.close()
    await ctx.send(f"Warnings configured: {punishment} at {warning_threshold} warnings.")

# ----------------------
# LOA Command
# ----------------------
@client.command()
async def loa_request(ctx, action: str, target: str = None, starting_date: str = None, ending_date: str = None, *, reason: str = None):
    # Role check
    if MODERATOR_ROLE_ID not in [role.id for role in ctx.author.roles]:
        return await ctx.send("❌ You do not have permission to manage LOAs.")

    # ADD LOA
    if action.lower() == "add":
        if not target or not starting_date or not ending_date or not reason:
            return await ctx.send("❌ Please provide member, start date, end date, and reason.")

        try:
            member = await commands.MemberConverter().convert(ctx, target)
        except commands.MemberNotFound:
            return await ctx.send("❌ Could not find that member.")

        view = View(timeout=60)

        add_embed = discord.Embed(
            title="⚠️ Confirm LOA Addition",
            description=f"Add LOA for {member.mention}?\n**Start:** {starting_date}\n**End:** {ending_date}\n**Reason:** {reason}",
            color=discord.Color.yellow()
        )

        async def confirm_callback(interaction):
            loa_id = add_loa(member.id, ctx.guild.id, starting_date, ending_date, reason)
            str_id = str(loa_id)
            embed = discord.Embed(
                title="✅ LOA Added",
                description=f"{member.mention} now has an LOA.\n**Start:** {starting_date}\n**End:** {ending_date}\n**Reason:** {reason}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"LOA ID: {str(loa_id)}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await interaction.response.edit_message(embed=embed, view=None)

        async def cancel_callback(interaction):
            embed = discord.Embed(
                title="❌ LOA Addition Cancelled",
                description="No changes were made.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)

        view.add_item(Button(label="Confirm", style=discord.ButtonStyle.green))
        view.add_item(Button(label="Cancel", style=discord.ButtonStyle.red))
        view.children[0].callback = confirm_callback
        view.children[1].callback = cancel_callback

        await ctx.send(embed=add_embed, view=view)

    # REMOVE LOA
    elif action.lower() == "remove":
        if not target:
            return await ctx.send("❌ Please provide the LOA ID to remove.")

        try:
            loa_id = int(target)
        except ValueError:
            return await ctx.send("❌ LOA ID must be a number.")

        view = View(timeout=60)

        remove_embed = discord.Embed(
            title="⚠️ Confirm LOA Removal",
            description=f"Remove LOA ID `{loa_id}`?",
            color=discord.Color.yellow()
        )

        async def confirm_remove(interaction):
            remove_loa(loa_id)
            embed = discord.Embed(
                title="✅ LOA Removed",
                description=f"LOA ID `{loa_id}` has been removed.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)

        async def cancel_remove(interaction):
            embed = discord.Embed(
                title="❌ LOA Removal Cancelled",
                description="No changes were made.",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)

        view.add_item(Button(label="Confirm", style=discord.ButtonStyle.green))
        view.add_item(Button(label="Cancel", style=discord.ButtonStyle.red))
        view.children[0].callback = confirm_remove
        view.children[1].callback = cancel_remove

        await ctx.send(embed=remove_embed, view=view)

    else:
        await ctx.send("❌ Invalid action. Use `add` or `remove`.")

@client.command()
@commands.has_permissions(use_application_commands=True)
async def list_loa(ctx):
    """Lists all current LOAs in the server."""
    conn = sqlite3.connect(DB_LOA)
    c = conn.cursor()
    c.execute("SELECT id, member_id, starting_date, ending_date, reason FROM loas WHERE guild_id=?", (ctx.guild.id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return await ctx.send("❌ There are no current LOAs in this server.")

    embed = discord.Embed(title=f"Current LOAs in {ctx.guild.name}")

    for loa_id, member_id, start, end, reason in rows:
        try:
            member = await client.fetch_user(member_id)
            member_name = member.name
        except:
            member_name = f"User ID {member_id}"

        embed.add_field(
            name=f"LOA ID: {loa_id} | {member_name}",
            value=f"Start: {start}\nEnd: {end}\nReason: {reason}",
            inline=False
        )

    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_nicknames=True)
async def codename(ctx, member: discord.Member, *, codename: str):
    """Assign a codename to a member."""
    current_nick = member.nick or member.name
    new_nick = f"[-| {codename} |-] {current_nick}"

    try:
        await member.edit(nick=new_nick)
        embed = discord.Embed(
            title="✅ Codename Assigned",
            description=f"{member.mention} has been given codename **{codename}**",
            color=discord.Color.green()
        )
        embed.set_footer(
            text=f"Assigned by {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ I don’t have permission to change this member’s nickname.")



if TOKEN:
    client.run(TOKEN)
else:
    print(Fore.RED +
          "[❌]: An error has occured, please check your token and try again.")
