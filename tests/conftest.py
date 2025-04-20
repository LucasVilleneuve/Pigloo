import glob
import os

import discord
import discord.ext.test as dpytest
import pytest_asyncio
from discord.client import _LoopSentinel

import pigloo.bot


@pytest_asyncio.fixture
async def bot(request):
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    b = pigloo.bot.PiglooBot(intents=intents)

    # set up the loop
    if isinstance(b.loop, _LoopSentinel):
        await b._async_setup_hook()

    # Loading cogs
    # for filename in os.listdir("./pigloo/cogs"):
    #     if filename.endswith(".py"):
    #         print("Loading cogs " + f"pigloo.cogs.{filename[:-3]}")
    #         await b.load_extension(f"pigloo.cogs.{filename[:-3]}")

    dpytest.configure(b)

    yield b

    # Teardown
    await dpytest.empty_queue()  # empty the global message queue as test teardown


def pytest_sessionfinish(session, exitstatus):
    """Code to execute after all tests."""

    # dat files are created when using attachements
    print("\n-------------------------\nClean dpytest_*.dat files")
    fileList = glob.glob("./dpytest_*.dat")
    for filePath in fileList:
        try:
            os.remove(filePath)
        except Exception:
            print("Error while deleting file : ", filePath)
