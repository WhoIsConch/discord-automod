import discord
import typing
from typing import TYPE_CHECKING
from ..helpers import GuildJoins

if TYPE_CHECKING:
    from ..bot import Bot


class Database(discord.Cog):
    """
    Handles all database operations that are triggered via Discord events, such as guild joins and users.
    """
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot

    @property
    def get_guild_joins(self) -> typing.Callable[[...], GuildJoins]:
        return self.bot.get_guild_joins

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Adds a user to the member join log, and checks for any outdated times in the log.
        """
        guild_joins: GuildJoins = self.get_guild_joins(member.guild.id)

        if guild_joins:
            for join_time, users in guild_joins.items():
                if join_time < (member.joined_at.timestamp() - 300):
                    del guild_joins[join_time]

        guild_joins.setdefault(member.joined_at.timestamp(), []).append(member.id)

