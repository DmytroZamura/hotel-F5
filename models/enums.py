from enum import Enum


class RoomStatus(Enum):
    """Статус номера."""
    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"



