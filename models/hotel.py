"""Клас Hotel — управління готелем."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from models.booking import Booking
from models.enums import RoomStatus, BookingStatus
from models.guest import Guest
from models.room import Room
from utils.slug import get_slug
from utils.validators import (
    validate_non_empty_string,
    validate_optional_string,
    validate_email,
    validate_phone_number,
    validate_non_negative_float,
)


class Hotel:
    """Готель: містить номери, бронювання та гостей.

    Attributes:
        name: Назва готелю.
        hotel_id: Унікальний ідентифікатор (slug).
        description: Опис готелю.
        address: Адреса.
        phone: Телефон.
        email: Email.
        rooms: Список номерів.
        bookings: Список бронювань.
        guests: Список гостей.
        total_revenue: Загальний дохід.
    """

    def __init__(
        self,
        name: str,
        hotel_id: str = "",
        description: str = "",
        address: str = "",
        phone: str = "",
        email: str = "",
    ) -> None:
        self.name = name
        self.hotel_id = hotel_id or get_slug(name)
        self.description = description
        self.address = address
        self.phone = phone
        self.email = email
        self.rooms: list[Room] = []
        self.bookings: list[Booking] = []
        self.guests: list[Guest] = []
        self.total_revenue = 0.0

    # ---- Property-сетери з валідацією ----

    @property
    def name(self) -> str:
        """Назва готелю."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_non_empty_string(value, "Назва готелю")

    @property
    def hotel_id(self) -> str:
        """Унікальний ідентифікатор готелю (slug)."""
        return self._hotel_id

    @hotel_id.setter
    def hotel_id(self, value: str) -> None:
        self._hotel_id = validate_non_empty_string(value, "ID готелю")

    @property
    def description(self) -> str:
        """Опис готелю."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = validate_optional_string(value, "Опис готелю")

    @property
    def address(self) -> str:
        """Адреса готелю."""
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        self._address = validate_optional_string(value, "Адреса готелю")

    @property
    def phone(self) -> str:
        """Телефон готелю."""
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        # Телефон необов'язковий, але якщо вказаний — валідуємо
        if value:
            self._phone = validate_phone_number(value)
        else:
            self._phone = ""

    @property
    def email(self) -> str:
        """Email готелю."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        # Email необов'язковий, але якщо вказаний — валідуємо
        if value:
            self._email = validate_email(value)
        else:
            self._email = ""

    @property
    def total_revenue(self) -> float:
        """Загальний дохід готелю."""
        return self._total_revenue

    @total_revenue.setter
    def total_revenue(self, value: float) -> None:
        self._total_revenue = validate_non_negative_float(value, "Дохід")

    # ---- Управління номерами ----

    def add_room(self, room: Room) -> None:
        """Додати номер до готелю. Дублювання номера заборонено."""
        if any(r.number == room.number for r in self.rooms):
            raise ValueError(f"Номер {room.number} вже існує в готелі")
        self.rooms.append(room)

    def find_available(
        self,
        room_type: type[Room] | None = None,
        check_in: date | None = None,
        check_out: date | None = None,
    ) -> list[Room]:
        """Знайти вільні номери за типом та діапазоном дат.

        Args:
            room_type: Тип номера (StandardRoom, DeluxeRoom, Suite) або None для всіх.
            check_in: Дата заїзду (включно).
            check_out: Дата виїзду (не включно).

        Returns:
            Список вільних номерів.
        """
        # Дати пошуку не можуть бути в минулому
        today = date.today()
        if check_in is not None and check_in < today:
            check_in = today
        if check_out is not None and check_out <= today:
            check_out = None
            check_in = None

        result: list[Room] = []
        for room in self.rooms:
            # Фільтр за типом
            if room_type and not isinstance(room, room_type):
                continue
            # Перевірка, чи номер вільний на запитані дати
            if self._is_room_available(room, check_in, check_out):
                result.append(room)
        return result

    def _is_room_available(
        self, room: Room, check_in: date | None, check_out: date | None
    ) -> bool:
        """Перевірити, чи номер вільний на вказаний діапазон дат."""
        if check_in is None or check_out is None:
            return room.status == RoomStatus.FREE

        for booking in self.bookings:
            if booking.room.number != room.number:
                continue
            if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
                continue
            # Перевірка перетину дат
            b_start = booking.check_in_date
            b_end = booking.check_out_date
            if check_in < b_end and check_out > b_start:
                return False
        return True

    # ---- Бронювання ----

    def book(
        self,
        guest: Guest,
        room: Room,
        check_in_date: date,
        nights: int,
    ) -> Booking:
        """Забронювати номер для гостя.

        Returns:
            Створене бронювання.

        Raises:
            ValueError: Якщо номер недоступний на вказані дати.
        """
        from datetime import timedelta

        check_out = check_in_date + timedelta(days=nights)
        if not self._is_room_available(room, check_in_date, check_out):
            raise ValueError(
                f"Номер {room.number} недоступний на дати "
                f"{check_in_date} — {check_out}"
            )

        booking = Booking(
            guest=guest,
            room=room,
            check_in_date=check_in_date,
            nights=nights,
        )
        room.status = RoomStatus.RESERVED
        self.bookings.append(booking)

        if guest not in self.guests:
            self.guests.append(guest)

        return booking

    def check_in_guest(self, booking: Booking) -> None:
        """Заселити гостя за бронюванням."""
        if booking.status != BookingStatus.CONFIRMED:
            raise RuntimeError(
                f"Неможливо заселити — статус бронювання: {booking.status.value}"
            )
        booking.room.check_in(booking.guest)
        booking.status = BookingStatus.CHECKED_IN

    def check_out_guest(self, booking: Booking) -> None:
        """Виселити гостя за бронюванням та нарахувати дохід/бали."""
        if booking.status != BookingStatus.CHECKED_IN:
            raise RuntimeError(
                f"Неможливо виселити — статус бронювання: {booking.status.value}"
            )
        cost = booking.total_cost()
        booking.room.check_out()
        booking.status = BookingStatus.COMPLETED
        self.total_revenue += cost

        # Нарахування балів лояльності (1 грн = 1 бал)
        booking.guest.add_loyalty_points(int(cost))

        # Додаємо до історії перебувань
        booking.guest.stay_history.append(booking.to_dict())

    # ---- Звіти ----

    def get_revenue_report(self) -> dict:
        """Звіт про доходи та завантаженість готелю."""
        # Активні бронювання — все, крім скасованих
        active = [
            b for b in self.bookings
            if b.status != BookingStatus.CANCELLED
        ]
        completed = [
            b for b in self.bookings if b.status == BookingStatus.COMPLETED
        ]
        total_nights = sum(b.nights for b in completed)
        avg_stay = total_nights / len(completed) if completed else 0.0

        occupied_count = sum(
            1 for r in self.rooms if r.status == RoomStatus.OCCUPIED
        )
        occupancy = occupied_count / len(self.rooms) if self.rooms else 0.0

        # Очікуваний дохід від незавершених бронювань
        pending_revenue = sum(
            b.total_cost() for b in active if b.status != BookingStatus.COMPLETED
        )

        return {
            "total_revenue": self.total_revenue,
            "pending_revenue": round(pending_revenue, 2),
            "bookings_count": len(active),
            "completed_count": len(completed),
            "average_stay": round(avg_stay, 2),
            "occupancy_rate": round(occupancy, 2),
        }

    # ---- Серіалізація / збереження ----

    def to_dict(self) -> dict:
        """Серіалізувати готель у словник."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "total_revenue": self.total_revenue,
            "rooms": [r.to_dict() for r in self.rooms],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Hotel":
        """Створити готель зі словника."""
        hotel = cls(
            name=data["name"],
            hotel_id=data.get("hotel_id", ""),
            description=data.get("description", ""),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
        )
        hotel.total_revenue = data.get("total_revenue", 0.0)
        for room_data in data.get("rooms", []):
            hotel.rooms.append(Room.create_room_from_dict(room_data))
        return hotel

    def save(self, filepath: str) -> None:
        """Зберегти готель у JSON-файл."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Hotel":
        """Завантажити готель з JSON-файлу."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    # ---- Магічні методи ----

    def __len__(self) -> int:
        return len(self.rooms)

    def __str__(self) -> str:
        free_count = sum(1 for r in self.rooms if r.status == RoomStatus.FREE)
        return f"{self.name}: {free_count} вільних номерів з {len(self.rooms)}"

    def __repr__(self) -> str:
        return f"Hotel(name={self.name!r}, id={self.hotel_id!r}, rooms={len(self.rooms)})"

