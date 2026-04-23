"""Клас Booking — бронювання номера гостем."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from models.enums import BookingStatus
from models.guest import Guest
from models.room import Room
from utils.validators import validate_min_int, validate_non_empty_string, validate_type


class Booking:
    """Бронювання номера в готелі.

    Attributes:
        booking_id: Унікальний ідентифікатор бронювання.
        guest: Гість, який бронює номер.
        room: Номер, що бронюється.
        check_in_date: Дата заїзду.
        nights: Кількість ночей.
        status: Статус бронювання.
    """

    def __init__(
        self,
        guest: Guest,
        room: Room,
        check_in_date: date,
        nights: int,
        booking_id: str | None = None,
        status: BookingStatus = BookingStatus.CONFIRMED,
    ) -> None:
        self.booking_id = booking_id or f"BK-{uuid.uuid4().hex[:8]}"
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.nights = nights
        self.status = status

    # ---- Property-сетери з валідацією ----

    @property
    def booking_id(self) -> str:
        """Унікальний ідентифікатор бронювання."""
        return self._booking_id

    @booking_id.setter
    def booking_id(self, value: str) -> None:
        self._booking_id = validate_non_empty_string(value, "ID бронювання")

    @property
    def guest(self) -> Guest:
        """Гість бронювання."""
        return self._guest

    @guest.setter
    def guest(self, value: Guest) -> None:
        self._guest = validate_type(value, Guest, "Гість бронювання")

    @property
    def room(self) -> Room:
        """Номер бронювання."""
        return self._room

    @room.setter
    def room(self, value: Room) -> None:
        self._room = validate_type(value, Room, "Номер бронювання")

    @property
    def check_in_date(self) -> date:
        """Дата заїзду."""
        return self._check_in_date

    @check_in_date.setter
    def check_in_date(self, value: date) -> None:
        self._check_in_date = validate_type(value, date, "Дата заїзду")

    @property
    def nights(self) -> int:
        """Кількість ночей."""
        return self._nights

    @nights.setter
    def nights(self, value: int) -> None:
        self._nights = validate_min_int(value, 1, "Кількість ночей")

    @property
    def status(self) -> BookingStatus:
        """Статус бронювання."""
        return self._status

    @status.setter
    def status(self, value: BookingStatus) -> None:
        self._status = validate_type(value, BookingStatus, "Статус бронювання")

    # ---- Розрахунки ----

    def total_cost(self) -> float:
        """Загальна вартість бронювання з урахуванням знижки гостя."""
        # Знижка береться напряму з профілю гостя (discount_percent повертає %)
        discount = self.guest.discount_percent / 100
        return self.room.price_per_night * self.nights * (1 - discount)

    @property
    def check_out_date(self) -> date:
        """Дата виїзду."""
        return self.check_in_date + timedelta(days=self.nights)

    # ---- Серіалізація ----

    def to_dict(self) -> dict:
        """Серіалізувати бронювання у словник."""
        return {
            "booking_id": self.booking_id,
            "guest_passport": self.guest.passport,
            "room_number": self.room.number,
            "room_type": self.room.__class__.__name__,
            "check_in_date": self.check_in_date.isoformat(),
            "nights": self.nights,
            "status": self.status.value,
        }

    # ---- Магічні методи ----

    def __repr__(self) -> str:
        return (
            f"Booking(id={self.booking_id!r}, guest={self.guest.name!r}, "
            f"room={self.room.number}, nights={self.nights}, "
            f"total={self.total_cost():.2f} грн, status={self.status.value})"
        )

    def __str__(self) -> str:
        return (
            f"Бронювання {self.booking_id}: {self.guest.name}, "
            f"номер {self.room.number}, {self.check_in_date} — "
            f"{self.check_out_date} ({self.nights} ночей), "
            f"вартість: {self.total_cost():.2f} грн"
        )
