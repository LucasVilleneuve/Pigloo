from typing import Optional

import discord
from loguru import logger

from pigloo.config import config
from pigloo.feed import Feed


def create_embed_from_feed(feed: Feed) -> Optional[discord.Embed]:
    """Creates a Discord embed from a given feed.

    Constructs an embed message containing information from the feed, such as
    media details, user, service, and progress.
    """
    try:
        description = f"[{feed.media.name}]({feed.media.url}) - {feed.media.format}\n"
        description += f"```{feed.status.label} | {feed.media.build_progress_str(feed.progress)}```"
        embed = discord.Embed(colour=0xEED000, description=description, timestamp=feed.datetime)
        embed.set_thumbnail(url=feed.media.image)
        author_name = f"{feed.user.name}'s {feed.service.name}"
        author_url = f"{config.get('ANILIST', 'profile_url')}{feed.user.name}"
        embed.set_author(name=author_name, url=author_url, icon_url=config.get("ANILIST", "icon_url"))
        embed.set_footer(
            text=config.get("BOT", "name"), icon_url=config.get("ANILIST", "icon_url")
        )  # TODO Use correct icon url

        return embed
    except Exception as e:
        logger.error(f"Error when generating the embed: {str(e)}")
        return


async def send_embed(embed: discord.Embed, channel: discord.channel) -> None:
    """
    Sends an embed message to a specified Discord channel.
    """
    if channel is None:
        logger.error("Channel is None, cannot send embed.")
        return

    try:
        await channel.send(embed=embed)
        logger.info(f"Message sent in channel: {channel.id}")
    except Exception as e:
        logger.error(f"Impossible to send a message on '{channel.id}': {e}")
        return
