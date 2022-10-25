import datetime
from ..database.models import Guild
import discord

__all__ = ["Time"]


class Time:
    @staticmethod
    def current_time() -> datetime.datetime:
        return datetime.datetime.now().replace(microsecond=0)

    @staticmethod
    def time_within(guild: Guild, time: datetime.datetime) -> bool:
        # Check if the time is in the guild's antiraid_after time
        return Time.current_time() - time <= datetime.timedelta(seconds=guild.antiraid_time)


