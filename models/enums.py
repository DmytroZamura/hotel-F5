from enum import Enum


class RoomStatus(Enum):
    """Статус номера."""
    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class BookingStatus(Enum):
    """Статус бронювання."""
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"



