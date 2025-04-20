import uuid
from datetime import datetime, timezone

import discord
import discord.ext.test as dpytest
import pytest
from logot import Logot, logged

from pigloo.bot import PiglooBot
from pigloo.config import config
from pigloo.embed import create_embed_from_feed, send_embed
from pigloo.feed import Feed, Media, Service, User


@pytest.mark.asyncio
async def test_send_embed(bot):
    guild = bot.guilds[0]
    channel_0 = guild.channels[0]

    service = Service(id=uuid.uuid4(), name="AniList")
    user = User(id=uuid.uuid4(), name="user1", service=service)
    media = Media(
        id=uuid.uuid4(),
        name="Anime1",
        type="Anime",
        service=service,
        max_progress=6,
        url="https://docs.pydantic.dev/latest/logo-white.svg",
        image="https://docs.pydantic.dev/latest/logo-white.svg",
    )
    feed = Feed(
        id=uuid.uuid4(), user=user, service=service, media=media, progress=2, datetime=datetime.now().astimezone()
    )

    embed = create_embed_from_feed(feed)

    assert embed is not None

    await send_embed(embed, channel_0)

    assert dpytest.verify().message().embed(embed)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "embed",
    [
        (discord.Embed(title="Test Embed 1")),  # Test with a simple embed
        (discord.Embed(title="Test Embed 2", description="A description")),  # Test with a description
        (discord.Embed(title="Test Embed 3", url="https://example.com")),  # Test with a URL
    ],
    ids=["simple_embed", "embed_with_description", "embed_with_url"],
)
async def test_send_embed(bot: PiglooBot, logot: Logot, embed: discord.Embed):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.channels[0]
    assert channel is not None

    # Act
    await send_embed(embed, channel)

    # Assert
    assert dpytest.verify().message().embed(embed)
    logot.assert_logged(logged.info(f"Message sent in channel: {channel.id}"))


@pytest.mark.asyncio
async def test_send_embed_empty(bot: PiglooBot, logot: Logot):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.channels[0]

    # Act
    await send_embed(None, channel)

    # Assert
    logot.assert_logged(logged.info(f"Message sent in channel: {channel.id}"))
    dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_send_embed_incorrect_channel(bot: PiglooBot, logot: Logot):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.get_channel(-1)  # Invalid channel ID
    assert channel is None

    # Act
    await send_embed(None, channel)

    # Assert
    logot.assert_logged(logged.error("Channel is None, cannot send embed."))
    dpytest.verify().message().nothing()


@pytest.mark.asyncio
async def test_send_embed_with_missing_rights(bot: PiglooBot, logot: Logot):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.channels[0]
    # Disable send messages permission for the default role
    # This is a workaround to simulate the permission issue
    # In a real scenario, you would need to set up the channel permissions in Discord
    # to ensure the bot doesn't have permission to send messages.
    await dpytest.set_permission_overrides(guild.default_role, channel, send_messages=False)

    # Act
    embed = discord.Embed(title="Test Embed 4")
    await send_embed(embed, channel)

    # Assert
    assert dpytest.verify().message().nothing()
    logot.assert_logged(logged.error(f"Impossible to send a message on '{channel.id}': 403 %s"))


@pytest.mark.parametrize(
    "media_name, media_url, media_type, progress, max_progress, user_name, service_name, expected_description",
    [
        (
            "Anime1",
            "https://example.com/anime1",
            "TV",
            3,
            12,
            "User1",
            "AniList",
            "[Anime1](https://example.com/anime1) - TV\n```Watching | 3 of 12 episodes```",
        ),
        (
            "Manga2",
            "https://example.com/manga2",
            "Manga",
            10,
            50,
            "User2",
            "MangaDex",
            "[Manga2](https://example.com/manga2) - Manga\n```Watching | 10 of 50 episodes```",
        ),  # Different media type
        (
            "Long Anime Title",
            "https://example.com/long-anime-title",
            "Movie",
            1,
            1,
            "UserWithLongName",
            "MyAnimeList",
            "[Long Anime Title](https://example.com/long-anime-title) - Movie\n```Watching | 1 of 1 episodes```",
        ),  # Long names and movie type
    ],
    ids=["basic_anime", "manga_example", "long_names_movie"],
)
def test_create_embed_from_feed(
    media_name, media_url, media_type, progress, max_progress, user_name, service_name, expected_description
):
    # Arrange
    service = Service(id=uuid.uuid4(), name=service_name)
    user = User(id=uuid.uuid4(), name=user_name, service=service)
    media = Media(
        id=uuid.uuid4(),
        name=media_name,
        url=media_url,
        type=media_type,
        service=service,
        max_progress=max_progress,
        image="https://example.com/image.jpg",
    )
    feed = Feed(
        id=uuid.uuid4(),
        user=user,
        service=service,
        media=media,
        progress=progress,
        datetime=datetime.now(timezone.utc),
    )

    # Act
    embed = create_embed_from_feed(feed)

    # Assert
    assert embed is not None
    assert embed.description == expected_description
    assert embed.colour.value == 0xEED000
    assert embed.thumbnail.url == "https://example.com/image.jpg"
    assert embed.author.name == f"{user_name}'s {service_name}"
    assert embed.author.url == f"{config.get('ANILIST', 'profile_url')}{user_name}"
    assert embed.author.icon_url == config.get("ANILIST", "icon_url")
    assert embed.footer.text == config.get("BOT", "name")
    assert embed.footer.icon_url == config.get("ANILIST", "icon_url")


@pytest.mark.parametrize(
    "media_name, media_url, media_type, progress, max_progress, user_name, service_name, expected_description",
    [
        (
            "Anime1",
            "https://example.com/anime1",
            "TV",
            3,
            12,
            "User1",
            "AniList",
            "[Anime1](https://example.com/anime1) - TV\n```Watching | 3 of 12 episodes```",
        ),
        (
            "Manga2",
            "https://example.com/manga2",
            "Manga",
            10,
            50,
            "User2",
            "MangaDex",
            "[Manga2](https://example.com/manga2) - Manga\n```Watching | 10 of 50 episodes```",
        ),  # Different media type
        (
            "Long Anime Title",
            "https://example.com/long-anime-title",
            "Movie",
            1,
            1,
            "UserWithLongName",
            "MyAnimeList",
            "[Long Anime Title](https://example.com/long-anime-title) - Movie\n```Watching | 1 of 1 episodes```",
        ),  # Long names and movie type
    ],
    ids=["basic_anime", "manga_example", "long_names_movie"],
)
@pytest.mark.asyncio
async def test_send_feed(
    bot: PiglooBot,
    logot: Logot,
    media_name,
    media_url,
    media_type,
    progress,
    max_progress,
    user_name,
    service_name,
    expected_description,
):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.channels[0]
    service = Service(id=uuid.uuid4(), name=service_name)
    user = User(id=uuid.uuid4(), name=user_name, service=service)
    media = Media(
        id=uuid.uuid4(),
        name=media_name,
        url=media_url,
        type=media_type,
        service=service,
        max_progress=max_progress,
        image="https://example.com/image.jpg",
    )
    feed = Feed(
        id=uuid.uuid4(),
        user=user,
        service=service,
        media=media,
        progress=progress,
        datetime=datetime.now(timezone.utc),
    )

    # Act
    embed = create_embed_from_feed(feed)
    await send_embed(embed, channel)

    # Assert
    assert embed is not None
    assert embed.description == expected_description
    assert dpytest.verify().message().embed(embed)
    logot.assert_logged(logged.info(f"Message sent in channel: {channel.id}"))
