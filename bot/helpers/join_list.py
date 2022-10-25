import datetime
from ..helpers import Time

__all__ = ["GuildList", "GuildJoins", "GuildRoles"]


class GuildList(dict):
    def add_guild(self, guild_id: int):
        self.setdefault(guild_id, GuildJoins())

    def add_user(self, guild_id: int, user_id: int, join_time):
        if not self.get(guild_id):
            self.add_guild(guild_id)

        self[guild_id].add_user(user_id, join_time)

    def remove_user(self, guild_id: int, user_id: int):
        if not self.get(guild_id):
            self.add_guild(guild_id)

        self[guild_id].remove_user(user_id)


class GuildRoles(dict):
    def add_user(self, user_id: int):
        self.setdefault(user_id, [])

    def remove_user(self, user_id: int):
        if self.get(user_id):
            del self[user_id]

    def add_role(self, user_id: int, role_id: int):
        self.add_user(user_id)
        self[user_id].append(role_id)

    def remove_role(self, user_id: int, role_id: int):
        if self.get(user_id):
            self[user_id].remove(role_id)

    def get_user_roles(self, user_id: int):
        return self.get(user_id, [])


class GuildJoins(dict):
    def add_user(self, user_id: int):
        # Get the time for the current minute
        time = Time.current_time()
        self.setdefault(time.timestamp(), []).append(user_id)

    def get_joins(self, time: datetime.datetime):
        return self.get(time.timestamp(), [])

    def get_current_joins(self):
        return self.get_joins(Time.current_time())

    def get_joins_before(self, time: datetime.datetime):
        return [users for join_time, users in self.items() if join_time < time.timestamp()]

    def get_joins_after(self, time: datetime.datetime):
        return [users for join_time, users in self.items() if join_time >= time.timestamp()]

    def get_joins_since(self, time: datetime.datetime):
        return [users for join_time, users in self.items() if join_time >= time.timestamp()]

    def get_joins_between(self, start_time: datetime.datetime, end_time: datetime.datetime):
        return [
            users for join_time, users in self.items() if start_time.timestamp() <= join_time < end_time.timestamp()
        ]


