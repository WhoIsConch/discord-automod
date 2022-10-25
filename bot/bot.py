from abc import ABC

import discord
import os
import logging
from helpers import GuildJoins, GuildList, GuildRoles


class Bot(discord.Bot, ABC):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            intents=intents
        )

        # Create a logger for our bot
        self.logger = logging.getLogger("automod")
        self._joins = GuildList()
        self._role_management = GuildList()

    @property
    def joins(self) -> GuildList:
        return self._joins

    @property
    def role_management(self) -> GuildList:
        return self._role_management

    def get_guild_joins(self, guild_id: int) -> GuildJoins:
        return self.joins.get(guild_id, GuildJoins())

    def get_guild_roles(self, guild_id: int) -> GuildRoles:
        return self.role_management.get(guild_id, GuildRoles())

    def load_cogs(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")
                self.logger.info(f"Loaded {filename[:-3]}")

    def run(self, token) -> None:
        self.load_cogs()
        super().run(token, reconnect=True)
