import discord
import asyncio
import signal
import traceback
from contextlib import suppress
from discord.ext.commands import Bot
from loguru import logger
from pigloo.config import config


class PiglooBot(Bot):
    def __init__(self, *, intents: discord.Intents = None):
        if intents is None:
            intents = discord.Intents.default()
            intents.members = True
            intents.message_content = True

        super().__init__(command_prefix=config.get('BOT', 'prefix'), intents=intents)
        self.add_commands()
    
    async def start(self):
        logger.success("Starting Pigloo...")
        await super().start(config.get('DISCORD', 'Token'))
    
    async def close(self):
        logger.success("Stopping Pigloo...")
        await super().close()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} ({self.user.id})')

    async def on_error(self, event, *args, **kwargs):
        logger.error(f"Event {event}. {traceback.format_exc()}")

    def add_commands(self):
        @self.command(name="ping")
        async def ping(ctx):
            logger.info("Pong!")
            await ctx.channel.send("Pong!")


bot = PiglooBot()


async def exit_app(signame):
    logger.info(f"Received signal {signame.name}. Shutting down...")

    # Cancel all tasks except the current one
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    for task in tasks:
        logger.debug("Cancelling task " + task.get_name())
        task.cancel()
        # Cancelled task raises asyncio.CancelledError that we can suppress:
        with suppress(asyncio.CancelledError):
            await task

    # Stop the bot
    await bot.close()

    asyncio.get_event_loop().stop()



async def main():
    loop = asyncio.get_event_loop()
    
    # Catch SIGINT signal (Ctrl-C) and SIGTERM signal (kill)
    for signame in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signame, lambda signame=signame: asyncio.create_task(exit_app(signame)))

    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        logger.info("Bot task was cancelled")
    except Exception as e:
        logger.error(f"Encountered exception while running the bot: {e}")