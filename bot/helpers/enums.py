from enum import IntEnum


class NewUserFilter(IntEnum):
    OFF = 0b0
    PFP = 0b1
    USERNAME = 0b01
    AGE = 0b001


class Punishment(IntEnum):
    OFF = 0b0
    KICK = 0b1
    BAN = 0b01
    QUARANTINE = 0b001
