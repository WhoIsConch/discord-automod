from enum import IntEnum


class NewUserFilter(IntEnum):
    OFF = 0
    PFP = 1
    USERNAME = 1 << 1
    AGE = 1 << 2
    ANY = 1 << 3


class Punishment(IntEnum):
    OFF = 0
    KICK = 1 << 3
    BAN = 1 << 4
    QUARANTINE = 1 << 5
