from discord import Interaction, app_commands
from discord.ext import commands
from loguru import logger


class PiglooCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def register(self, inter: Interaction):
        await inter.response.send_message(f"Registering {inter.channel_id}!")

    @app_commands.command()
    async def unregister(self, inter: Interaction):
        await inter.response.send_message(f"Unregistering {inter.channel_id}!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PiglooCog(bot))
