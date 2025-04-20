import discord
from loguru import logger
from typing import Optional
from pigloo.feed import Feed

def create_embed_from_feed(feed: Feed) -> Optional[discord.Embed]:
    try:
        embed = discord.Embed(colour=0xEED000, description=feed.media.name+ "\n```" + str(feed.progress) + " - " + str(feed.media.max_progress) + "```", timestamp=feed.datetime)
        embed.set_thumbnail(url=feed.media.image)
        embed.set_author(name=feed.user.name, url="https://myanimelist.net/profile/" + feed.user.name, icon_url="") #TODO icon_url
        embed.set_footer(text="Pigloo", icon_url="") # TODO icon_url
        
        return embed
    except Exception as e:
        logger.error("Error when generating the embed: " + str(e))
        return


async def send_embed(embed: discord.Embed, channel: discord.channel) -> None:
    try:
        await channel.send(embed=embed)
        logger.info(f"Message sent in channel: {channel.id}")
    except Exception as e:
        logger.debug(f"Impossible to send a message on '{channel.id}': {e}") 
        return