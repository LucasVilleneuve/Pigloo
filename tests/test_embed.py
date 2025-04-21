import uuid
from datetime import datetime, timezone

import discord
import discord.ext.test as dpytest
import pytest
from logot import Logot, logged

from pigloo.bot import PiglooBot
from pigloo.config import config
from pigloo.embed import create_embed_from_feed, send_embed
from pigloo.feed import Anime, Feed, FeedStatus, Manga, Service, User


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
    "feed, expected_description, expected_author_name, expected_author_url",
    [
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Anime(
                    id=uuid.uuid4(),
                    name="Test Anime",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=12,
                    url="https://anilist.co/anime/1",
                    image="https://img.anili.st/media/anime/1.jpg",
                    format="TV",
                ),
                progress=5,
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Watching ..."),
            ),
            "[Test Anime](https://anilist.co/anime/1) - TV\n```Watching | 5 of 12 episodes```",
            "testuser's AniList",
            "https://anilist.co/user/testuser",
        ),
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser2", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Manga(
                    id=uuid.uuid4(),
                    name="Test Manga",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=24,
                    url="https://anilist.co/manga/2",
                    image="https://img.anili.st/media/manga/2.jpg",
                    format="Manga",
                ),
                progress=24,
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Reading ..."),
            ),
            "[Test Manga](https://anilist.co/manga/2) - Manga\n```Reading | 24 of 24 chapters```",
            "testuser2's AniList",
            "https://anilist.co/user/testuser2",
        ),
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser3", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Anime(
                    id=uuid.uuid4(),
                    name="Test Anime 2",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=3,  # Testing None for max_progress
                    url="https://anilist.co/anime/3",
                    image="https://img.anili.st/media/anime/3.jpg",
                    format="ONA",
                ),
                progress=None,  # Testing None for progress
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Plan to Watch"),
            ),
            "[Test Anime 2](https://anilist.co/anime/3) - ONA\n```Plans to watch | None of 3 episodes```",
            "testuser3's AniList",
            "https://anilist.co/user/testuser3",
        ),
    ],
    ids=["anime_watching_some_progress", "manga_reading_full_progress", "anime_plan_to_watch_no_progress"],
)
def test_create_embed_from_feed(feed, expected_description, expected_author_name, expected_author_url):
    # Act
    embed = create_embed_from_feed(feed)

    # Assert
    assert embed is not None
    assert embed.description == expected_description
    assert embed.author.name == expected_author_name
    assert embed.author.url == expected_author_url
    assert embed.thumbnail.url == str(feed.media.image)


@pytest.mark.parametrize(
    "feed, expected_description",
    [
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Anime(
                    id=uuid.uuid4(),
                    name="Test Anime",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=12,
                    url="https://anilist.co/anime/1",
                    image="https://img.anili.st/media/anime/1.jpg",
                    format="TV",
                ),
                progress=5,
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Watching ..."),
            ),
            "[Test Anime](https://anilist.co/anime/1) - TV\n```Watching | 5 of 12 episodes```",
        ),
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser2", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Manga(
                    id=uuid.uuid4(),
                    name="Test Manga",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=24,
                    url="https://anilist.co/manga/2",
                    image="https://img.anili.st/media/manga/2.jpg",
                    format="Manga",
                ),
                progress=24,
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Reading ..."),
            ),
            "[Test Manga](https://anilist.co/manga/2) - Manga\n```Reading | 24 of 24 chapters```",
        ),
        (
            Feed(
                id=uuid.uuid4(),
                user=User(id=uuid.uuid4(), name="testuser3", service=Service(id=uuid.uuid4(), name="AniList")),
                service=Service(id=uuid.uuid4(), name="AniList"),
                media=Anime(
                    id=uuid.uuid4(),
                    name="Test Anime 2",
                    service=Service(id=uuid.uuid4(), name="AniList"),
                    max_progress=3,  # Testing None for max_progress
                    url="https://anilist.co/anime/3",
                    image="https://img.anili.st/media/anime/3.jpg",
                    format="ONA",
                ),
                progress=None,  # Testing None for progress
                datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
                status=FeedStatus(label="Plan to Watch"),
            ),
            "[Test Anime 2](https://anilist.co/anime/3) - ONA\n```Plans to watch | None of 3 episodes```",
        ),
    ],
    ids=["anime_watching_some_progress", "manga_reading_full_progress", "anime_plan_to_watch_no_progress"],
)
@pytest.mark.asyncio
async def test_send_feed(bot: PiglooBot, logot: Logot, feed, expected_description):
    # Arrange
    guild = bot.guilds[0]
    channel = guild.channels[0]

    # Act
    embed = create_embed_from_feed(feed)
    await send_embed(embed, channel)

    # Assert
    assert embed is not None
    assert embed.description == expected_description
    assert dpytest.verify().message().embed(embed)
    logot.assert_logged(logged.info(f"Message sent in channel: {channel.id}"))
