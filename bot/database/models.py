from __future__ import annotations

from tortoise import models
from tortoise.fields import (BigIntField,
                             JSONField,
                             TextField,
                             ManyToManyField,
                             BooleanField,
                             IntField,
                             BinaryField)
import os
import discord
from ..helpers import NewUserFilter as NUF, Punishment

_host = os.getenv("DB_HOST")
_port = os.getenv("DB_PORT")
_user = os.getenv("DB_USER")
_password = os.getenv("DB_PASSWORD")


class DatabaseConfig:
    DEV = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.aiosqlite",
                "credentials": {
                    "file_path": "database.db"
                },
            },
        },
        "apps": {
            "models": {
                "models": ["bot.database.models"],
                "default_connection": "default",
            },
        },
    }
    PROD = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": _host,
                    "port": _port,
                    "user": _user,
                    "password": _password,
                    "database": "automod",
                },
            },
        },
        "apps": {
            "models": {
                "models": ["bot.database.models"],
                "default_connection": "default",
            },
        },
    }


class User(models.Model):
    id = BigIntField(pk=True)
    guilds = ManyToManyField("models.Guild", related_name="users")
    bans = ManyToManyField("models.Guild", related_name="banned_users")
    username_history = JSONField(default=[])
    display_name_history = JSONField(default={})

    @classmethod
    async def add_user(cls, member: discord.Member | discord.User) -> User:
        user = await cls.create(
            id=member.id
        )
        await user.guilds.add(member.guild)
        user.username_history.append(member.name)

        await user.save()

        return user

    class Meta:
        table = "users"


class Guild(models.Model):
    id = BigIntField(pk=True)
    users = ManyToManyField("models.User", related_name="guilds")
    join_history = JSONField(default={})
    logs = ManyToManyField("models.GuildLogs", related_name="guild")

    mute_role = BigIntField(null=True)
    quarantine_role = BigIntField(null=True)

    antiraid = BooleanField(default=False)  # Whether the antiraid system is enabled
    antiraid_after = IntField(default=5)  # How many users within a certain amount of time to trigger antiraid
    antiraid_time = IntField(default=30)  # How many seconds to wait before resetting the antiraid counter
    antiraid_action = BinaryField(default=Punishment.OFF)
    banned_users = ManyToManyField("models.User", related_name="bans")
    dangerous_users = BooleanField(default=False)
    dangerous_users_after = IntField(default=3)
    new_user_quarantine = BinaryField(default=NUF.OFF)
    new_user_quarantine_after = IntField(default=3)

    class Meta:
        table = "guilds"


class GuildLogs(models.Model):
    guild = ManyToManyField("models.Guild", related_name="logs", pk=True)

    dangerous_users_log = BigIntField(default=0)
    raid_log = BigIntField(default=0)
    new_user_log = BigIntField(default=0)
