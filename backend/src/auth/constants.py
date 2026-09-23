from enum import IntEnum


class Roles(IntEnum):
    ADMIN = 1
    DOCTOR = 2
    NURSE = 3
    USER = 4  # default


class UserStatus(IntEnum):
    ACTIVE = 1
    DEACTIVE = 0


JWT_ALGORITHM = "HS256"
