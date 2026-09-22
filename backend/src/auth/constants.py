from enum import IntEnum


class Roles(IntEnum):
    ADMIN = 1
    DOCTOR = 2
    NURSE = 3


class UserStatus(IntEnum):
    ACTIVE = 1
    DEACTIVE = 0
