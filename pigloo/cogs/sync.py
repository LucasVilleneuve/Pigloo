from typing import Literal, Optional

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from loguru import logger


class SyncCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _sync_guild(
        self, ctx: commands.Context, guild: Optional[discord.Object] = None
    ) -> list[app_commands.AppCommand]:
        return await ctx.bot.tree.sync(guild=guild)

    async def _copy_global_to_guild(self, ctx: commands.Context) -> list[app_commands.AppCommand]:
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        return await ctx.bot.tree.sync(guild=ctx.guild)

    async def _clear_guild_commands(self, ctx: commands.Context) -> list[app_commands.AppCommand]:
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        return await self._sync_guild(ctx, ctx.guild)

    async def _sync_no_guilds(self, ctx: commands.Context, option: Optional[Literal["~", "*", "^"]] = None) -> None:
        """Synchronizes commands when no specific guilds are provided.

        Handles command synchronization based on the provided `option` argument,
        which determines whether to sync to the current guild or globally.
        """
        if option == "~":
            synced_commands = await self._sync_guild(ctx, ctx.guild)
            sync_scope = "to the current guild"
        elif option == "*":
            synced_commands = await self._copy_global_to_guild(ctx)
            sync_scope = "to the current guild"
        elif option == "^":
            synced_commands = await self._clear_guild_commands(ctx)
            sync_scope = "to the current guild"
        else:
            synced_commands = await self._sync_guild(ctx)
            sync_scope = "globally"

        logger.info(f"Synced {len(synced_commands)} commands {sync_scope}.")
        await ctx.send(f"Synced {len(synced_commands)} commands {sync_scope}.")

    async def _sync_multiple_guilds(self, ctx: commands.Context, guilds: list[discord.Object]) -> None:
        synced_guild_count = 0
        for guild in guilds:
            try:
                await self._sync_guild(ctx, guild)
                synced_guild_count += 1
            except discord.HTTPException as e:
                logger.error(f"Failed to sync commands to guild {guild.id}: {e}")

        logger.info(f"Synced commands to {synced_guild_count}/{len(guilds)} guilds.")
        await ctx.send(f"Synced the tree to {synced_guild_count}/{len(guilds)}.")

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        option: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """Synchronizes the bot's application commands with Discord.

        This command allows syncing commands globally, to specific guilds,
        copying global commands to a guild, or clearing guild commands.

        Example usage:
        - `!sync` - Syncs commands globally.
        - `!sync ~` - Syncs commands to the current guild.
        - `!sync *` - Copies global commands to the current guild.
        - `!sync ^` - Clears commands in the current guild.
        - `!sync <guild_id>` - Syncs commands to the specified guild.
        - `!sync <guild_id1> <guild_id2>` - Syncs commands to multiple specified guilds.
        """
        if not guilds:
            await self._sync_no_guilds(ctx, option)
        else:
            await self._sync_multiple_guilds(ctx, guilds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCog(bot))
