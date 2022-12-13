import discord
import typing
from typing import TYPE_CHECKING
from ..helpers import (GuildJoins,
                       Time,
                       stringify_dangerous_user,
                       stringify_new_user_filter,
                       GuildRoles
                       )
from ..helpers.enums import NewUserFilter, Punishment
from ..database.models import User, Guild
import string

if TYPE_CHECKING:
    from ..bot import Bot


class AntiRaid(discord.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @property
    def get_guild_joins(self) -> typing.Callable:
        return self.bot.get_guild_joins

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = await Guild.get(id=member.guild.id)
        guild_joins: GuildJoins = self.get_guild_joins(guild.id)

        user = User.get_or_none(id=member.id)

        if not user:
            user = await User.add_user(member)

        if guild_joins:
            for join_time, users in guild_joins.items():
                if not Time.time_within(guild, join_time):
                    del guild_joins[join_time]

        guild_joins.setdefault(Time.current_time(), []).append(member.id)

        if guild.antiraid:
            for join_time, users in guild_joins.items():
                if len(users) >= guild.antiraid_after:
                    if Time.time_within(guild, join_time):
                        if guild.antiraid_action == Punishment.KICK:
                            await member.kick(reason=f"Automod: Antiraid triggered")

                        elif guild.antiraid_action == Punishment.BAN:
                            await member.ban(reason=f"Automod: Antiraid triggered")

                        elif guild.antiraid_action == Punishment.QUARANTINE:
                            await self.quarantine(member, guild, None, "Automod: Antiraid triggered")

        if guild.dangerous_users:
            await user.fetch_related("bans")

            if len(user.bans) >= guild.dangerous_users_after:
                await guild.fetch_related("logs")
                channel = self.bot.get_channel(guild.logs.dangerous_users_log)

                if guild.dangerous_users & Punishment.BAN:
                    await member.ban(reason=f"Automod: Dangerous user (Banned in {len(user.bans)} other guilds)")

                elif guild.dangerous_users & Punishment.KICK:
                    await member.kick(reason=f"Automod: Dangerous user (Banned in {len(user.bans)} other guilds)")

                elif guild.dangerous_users & Punishment.QUARANTINE:
                    await self.quarantine(member, guild, None,
                                          f"Automod: Dangerous user (Banned in {len(user.bans)} other guilds)")

                embed = discord.Embed(
                    title="Dangerous User Detected",
                    description=f""
                                f"{member} has been banned in {len(user.bans)} other guilds."
                                f"\n**Action Taken** - {stringify_dangerous_user(guild.dangerous_users)}"
                )

        if guild.new_user_quarantine:
            checks = []
            for check in NewUserFilter:
                if guild.new_user_quarantine & check:
                    if check.name == "pfp" and not member.avatar:
                        checks.append(not member.avatar)

                    elif check.name == "age":
                        checks.append(
                            (member.created_at.timestamp() + guild.new_user_quarantine_after) > Time.current_time()
                        )

                    elif check.name == "username":
                        # TODO: Make this more reliable
                        for char in member.name:
                            if char not in string.printable:
                                checks.append(True)

            if guild.new_user_quarantine & NewUserFilter.ANY:
                check_func = any
            else:
                check_func = all
                
            if check_func(checks):
                await self.quarantine(member, guild, None, "Automod: New user quarantine")

    async def quarantine(
            self, member: discord.Member, guild: discord.Guild | Guild,
            actor: discord.Member | None, reason: str | None):

        if isinstance(guild, discord.Guild):
            guild = await Guild.get(id=guild.id)

            quarantine_role = self.bot.get_guild(guild.id).get_role(guild.quarantine_role)

        else:
            quarantine_role = guild.get_role(guild.quarantine_role)

        if quarantine_role:
            roles = []
            for role in member.roles:
                if role >= quarantine_role:
                    continue

                await member.remove_roles(role, reason=reason)
                roles.append(role.id)

            self.bot.role_management.add_user(guild.id, member.id, roles)

            await member.add_roles(quarantine_role, reason=f"{actor or 'Automod'}: {reason}")

    async def remove_quarantine(self, member: discord.Member, guild: discord.Guild | Guild):
        if isinstance(guild, discord.Guild):
            guild = await Guild.get(id=guild.id)

            quarantine_role = self.bot.get_guild(guild.id).get_role(guild.quarantine_role)

        else:
            quarantine_role = guild.get_role(guild.quarantine_role)

        if quarantine_role:
            roles = self.bot.get_guild_roles(guild.id).get_user_roles(member.id)

            if roles:
                for role in roles:
                    await member.add_roles(self.bot.get_guild(guild.id).get_role(role),
                                           reason="Automod: Removed quarantine")

                self.bot.role_management.remove_user(guild.id, member.id)

            await member.remove_roles(quarantine_role, reason="Automod: Removed quarantine")
