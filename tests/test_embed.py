import pytest
import uuid
from datetime import datetime
from pigloo.feed import Feed, Media, User, Service
from pigloo.embed import *
import discord.ext.test as dpytest

def test_embed():
    service = Service(id=uuid.uuid4(), name="AniList")
    user = User(id=uuid.uuid4(), name="user1", service=service)
    media = Media(id=uuid.uuid4(), name="Anime1", service=service, max_progress=6, image="https://docs.pydantic.dev/latest/logo-white.svg")
    feed = Feed(id=uuid.uuid4(), user=user, service=service, media=media, progress=2, datetime=datetime.now().astimezone())
    
    embed = create_embed_from_feed(feed)
    
    assert embed != None
    assert int(embed.colour) == 0xEED000

@pytest.mark.asyncio
async def test_send_embed(bot):
    guild = bot.guilds[0]
    channel_0 = guild.channels[0]

    service = Service(id=uuid.uuid4(), name="AniList")
    user = User(id=uuid.uuid4(), name="user1", service=service)
    media = Media(id=uuid.uuid4(), name="Anime1", service=service, max_progress=6, image="https://docs.pydantic.dev/latest/logo-white.svg")
    feed = Feed(id=uuid.uuid4(), user=user, service=service, media=media, progress=2, datetime=datetime.now().astimezone())
    
    embed = create_embed_from_feed(feed)
    
    assert embed != None

    await send_embed(embed, channel_0)

    assert dpytest.verify().message().embed(embed)