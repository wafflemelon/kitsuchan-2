#!/usr/bin/env python3

"""jisho.org query command."""

import urllib.parse

from discord.ext import commands

BASE_URL_JISHO_API = "http://jisho.org/api/v1/search/words?{0}"


class Jisho:
    """A Japanese translation command."""

    @commands.command(aliases=["jp"])
    @commands.cooldown(6, 12)
    async def jisho(self, ctx, query, *args):
        """Translate a word into Japanese.

        Example usage:
        jisho test
        """
        query = f"{query} {' '.join(args)}"
        params = urllib.parse.urlencode({"keyword": query})
        url = BASE_URL_JISHO_API.format(params)
        async with ctx.bot.session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if not data["data"]:
                    await ctx.send("No result found.")

                japanese = data["data"][0]["japanese"][0]
                sense = data["data"][0]["senses"][0]
                english_string = ", ".join(sense["english_definitions"])
                message = [
                    "Kanji: " + str(japanese.get("word")),
                    "Kana: " + str(japanese.get("reading")),
                    "English: " + english_string
                ]
                await ctx.send("\n".join(message))
            else:
                await ctx.send("Couldn't reach Jisho.org. x.x")


def setup(bot):
    """Set up the extension."""
    bot.add_cog(Jisho())
