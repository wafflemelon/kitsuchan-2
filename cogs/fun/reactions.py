#!/usr/bin/env python3

"""Contains a cog for various weeb reaction commands."""

import json
import random

import discord
from discord.ext import commands

SYSTEMRANDOM = random.SystemRandom()

BASE_URL_API = "https://rra.ram.moe/i/r?type={0}"
BASE_URL_IMAGE = "https://cdn.ram.moe{0[path]}"

EMOJIS_KILL = (":gun:", ":knife:", ":eggplant:", ":bear:", ":fox:", ":wolf:", ":snake:",
               ":broken_heart:", ":crossed_swords:", ":fire:")


async def _generate_message(ctx, kind: str=None, user: discord.User=None):
    """Generate a message based on the user."""
    if not kind:
        message = ""
    elif user.id == ctx.bot.user.id:
        message = f"Aw, thank you. Here, have one back. :3"
    elif user.id == ctx.author.id:
        message = SYSTEMRANDOM.choice(("Okay. :3",
                                       f"Sorry to see you're alone, have a {kind} anyway. :<",
                                       f"I'll {kind} your face alright. :3",
                                       ":<"))
    else:
        message = f"**{user.display_name}**, you got a {kind} from **{ctx.author.display_name}!**"
    return message


async def _send_image(ctx, url_image, message: str=""):
    """A helper function that creates an embed with an image and sends it off."""
    if isinstance(url_image, (tuple, list)):
        url_image = SYSTEMRANDOM.choice(url_image)
    embed = discord.Embed()
    embed.description = message
    embed.set_image(url=url_image)
    await ctx.send(embed=embed)


class Reactions:
    """Weeb reaction commands."""

    def __init__(self, bot):
        """Procedurablly build reaction commands."""

        with open("reactions.json") as fobject:
            self.data = json.load(fobject)

        count = 0
        # TODO Add a help field to this mess.
        for key in self.data:

            # Avoid duplicate commands.
            if key in bot.all_commands.keys():
                continue

            # Avoid non-dictionary values.
            # Make sure that there exists a value with key "images", and that it's a list.
            elif (not isinstance(self.data[key], dict) or
                  not isinstance(self.data[key].get("images"), list)):
                continue

            # This signifies the type of message to be sent.
            message_indicator = self.data[key].get("message")

            # No message.
            if message_indicator is None:
                helptext = f"{key.capitalize()}!"

                async def callback(self, ctx):
                    await _send_image(ctx, self.data[ctx.command.name]["images"])

            # Zero-length string.
            elif not message_indicator:
                helptext = f"{key.capitalize()} a user!"

                async def callback(self, ctx, *, user: str):
                    message = await _generate_message(ctx, ctx.command.name, user)
                    await _send_image(ctx, self.data[ctx.command.name]["images"], message)

            # Custom message.
            else:
                helptext = f"{key.capitalize()}!"

                async def callback(self, ctx):
                    await _send_image(ctx, self.data[ctx.command.name]["images"],
                                      self.data[ctx.command.name]["message"])

            # Ew, gross.
            aliases = self.data[key].get("aliases", [])
            for alias in aliases:
                if alias in bot.all_commands.keys():
                    aliases.remove(alias)
            command = commands.command(name=key, help=helptext, aliases=aliases)(callback)
            command = commands.cooldown(6, 12, commands.BucketType.channel)(command)
            command.instance = self
            setattr(self, key, command)
            count += 1

    @commands.command(aliases=["murder"])
    @commands.cooldown(6, 12, commands.BucketType.channel)
    async def kill(self, ctx, *, user: discord.Member):
        """Kill a user!

        * user - The user to kill."""
        if not user:
            raise commands.CommandError("Member not found.")
        is_owner = await ctx.bot.is_owner(user)
        if user.id == ctx.bot.user.id:
            await ctx.send("Kon kon, I'm invincible! :3")
        elif is_owner:
            await ctx.send("I refuse. :<")
        else:
            emoji = SYSTEMRANDOM.choice(EMOJIS_KILL)
            await ctx.send((f"**{user.display_name}** was killed via {emoji}!"))


def setup(bot):
    """Setup function for reaction images."""
    try:
        bot.add_cog(Reactions(bot))
    except Exception:
        pass