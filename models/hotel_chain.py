"""Клас HotelChain — мережа готелів."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterator

from models.guest import Guest
from models.hotel import Hotel
from models.room import Room
from utils.validators import validate_non_empty_string, validate_optional_string


class HotelChain:
    """Мережа готелів зі спільною базою гостей.

    Attributes:
        name: Назва мережі.
        description: Опис мережі.
        hotels: Словник готелів (hotel_id → Hotel).
        guests: Словник гостей (passport → Guest).
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self.hotels: dict[str, Hotel] = {}
        self.guests: dict[str, Guest] = {}

    # ---- Property-сетери з валідацією ----

    @property
    def name(self) -> str:
        """Назва мережі."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_non_empty_string(value, "Назва мережі")

    @property
    def description(self) -> str:
        """Опис мережі."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = validate_optional_string(value, "Опис мережі")

    # ---- Управління готелями ----

    def add_hotel(self, hotel: Hotel) -> None:
        """Додати готель до мережі."""
        if hotel.hotel_id in self.hotels:
            raise ValueError(f"Готель з ID '{hotel.hotel_id}' вже існує в мережі")
        self.hotels[hotel.hotel_id] = hotel

    def remove_hotel(self, hotel_id: str) -> None:
        """Видалити готель з мережі."""
        if hotel_id not in self.hotels:
            raise KeyError(f"Готель з ID '{hotel_id}' не знайдено")
        del self.hotels[hotel_id]

    def get_hotel(self, hotel_id: str) -> Hotel:
        """Отримати готель за ID."""
        if hotel_id not in self.hotels:
            raise KeyError(f"Готель з ID '{hotel_id}' не знайдено")
        return self.hotels[hotel_id]

    # ---- Управління гостями ----

    def register_guest(self, guest: Guest) -> None:
        """Зареєструвати гостя у спільній базі мережі."""
        if guest.passport in self.guests:
            raise ValueError(f"Гість з паспортом '{guest.passport}' вже зареєстрований")
        self.guests[guest.passport] = guest

    def get_guest(self, passport: str) -> Guest:
        """Отримати гостя за номером паспорта."""
        if passport not in self.guests:
            raise KeyError(f"Гостя з паспортом '{passport}' не знайдено")
        return self.guests[passport]

    # ---- Пошук ----

    def find_available_all(
        self,
        room_type: type[Room] | None = None,
        check_in: date | None = None,
        check_out: date | None = None,
    ) -> dict[str, list[Room]]:
        """Знайти вільні номери по всій мережі.

        Returns:
            Словник {hotel_id: [список вільних номерів]}.
        """
        result: dict[str, list[Room]] = {}
        for hotel_id, hotel in self.hotels.items():
            available = hotel.find_available(room_type, check_in, check_out)
            if available:
                result[hotel_id] = available
        return result

    # ---- Звіти ----

    def get_total_revenue(self) -> float:
        """Загальний дохід по всій мережі."""
        return sum(h.total_revenue for h in self.hotels.values())

    def get_chain_report(self) -> dict:
        """Агрегований звіт по всій мережі."""
        hotels_report: dict[str, dict] = {}
        total_bookings = 0
        for hid, hotel in self.hotels.items():
            report = hotel.get_revenue_report()
            hotels_report[hid] = {
                "revenue": report["total_revenue"],
                "bookings": report["bookings_count"],
            }
            total_bookings += report["bookings_count"]

        return {
            "total_revenue": self.get_total_revenue(),
            "total_bookings": total_bookings,
            "hotels": hotels_report,
        }

    # ---- Збереження / завантаження ----

    def save(self, dirpath: str) -> None:
        """Зберегти всю мережу у директорію.

        Створює:
            dirpath/chain.json
            dirpath/hotels/<hotel_id>.json
            dirpath/guests.json
            dirpath/bookings.json
        """
        base = Path(dirpath)
        base.mkdir(parents=True, exist_ok=True)

        # chain.json
        chain_data = {
            "name": self.name,
            "description": self.description,
            "hotels": list(self.hotels.keys()),
        }
        with open(base / "chain.json", "w", encoding="utf-8") as f:
            json.dump(chain_data, f, ensure_ascii=False, indent=2)

        # Готелі
        hotels_dir = base / "hotels"
        hotels_dir.mkdir(exist_ok=True)
        for hotel in self.hotels.values():
            hotel.save(str(hotels_dir / f"{hotel.hotel_id}.json"))

        # Гості
        guests_data = [g.to_dict() for g in self.guests.values()]
        with open(base / "guests.json", "w", encoding="utf-8") as f:
            json.dump(guests_data, f, ensure_ascii=False, indent=2)

        # Бронювання
        bookings_data: list[dict] = []
        for hotel in self.hotels.values():
            for b in hotel.bookings:
                d = b.to_dict()
                d["hotel_id"] = hotel.hotel_id
                bookings_data.append(d)
        with open(base / "bookings.json", "w", encoding="utf-8") as f:
            json.dump(bookings_data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, dirpath: str) -> HotelChain:
        """Завантажити мережу з директорії."""
        base = Path(dirpath)

        with open(base / "chain.json", "r", encoding="utf-8") as f:
            chain_data = json.load(f)

        chain = cls(
            name=chain_data["name"],
            description=chain_data.get("description", ""),
        )

        # Гості
        guests_path = base / "guests.json"
        if guests_path.exists():
            with open(guests_path, "r", encoding="utf-8") as f:
                for g_data in json.load(f):
                    guest = Guest(
                        name=g_data["name"],
                        passport=g_data["passport"],
                        email=g_data["email"],
                        phone_number=g_data["phone_number"],
                    )
                    guest.loyalty_points = g_data.get("loyalty_points", 0)
                    guest.stay_history = g_data.get("stay_history", [])
                    chain.guests[guest.passport] = guest

        # Готелі
        for hotel_id in chain_data.get("hotels", []):
            hotel_path = base / "hotels" / f"{hotel_id}.json"
            if hotel_path.exists():
                hotel = Hotel.load(str(hotel_path))
                chain.hotels[hotel.hotel_id] = hotel

        # Бронювання
        bookings_path = base / "bookings.json"
        if bookings_path.exists():
            from models.booking import Booking
            from models.enums import BookingStatus, RoomStatus
            with open(bookings_path, "r", encoding="utf-8") as f:
                for b_data in json.load(f):
                    hotel_id = b_data.get("hotel_id")
                    hotel = chain.hotels.get(hotel_id)
                    if hotel is None:
                        continue

                    # Знайти гостя за паспортом
                    guest = chain.guests.get(b_data["guest_passport"])
                    if guest is None:
                        continue

                    # Знайти номер за номером кімнати
                    room = next(
                        (r for r in hotel.rooms if r.number == b_data["room_number"]),
                        None,
                    )
                    if room is None:
                        continue

                    status = BookingStatus(b_data["status"])
                    booking = Booking(
                        guest=guest,
                        room=room,
                        check_in_date=date.fromisoformat(b_data["check_in_date"]),
                        nights=b_data["nights"],
                        booking_id=b_data["booking_id"],
                        status=status,
                    )
                    hotel.bookings.append(booking)

                    # Відновлюємо статус номера відповідно до бронювання
                    if status == BookingStatus.CHECKED_IN:
                        room.status = RoomStatus.OCCUPIED
                        room.guest = guest
                    elif status == BookingStatus.CONFIRMED:
                        room.status = RoomStatus.RESERVED

        return chain

    # ---- HTML-візитівка ----

    def generate_html_card(self, filepath: str) -> None:
        """Згенерувати HTML-візитівку мережі."""
        from services.html_generator import HtmlGenerator
        generator = HtmlGenerator()
        generator.generate_chain_card(self, filepath)

    # ---- Магічні методи ----

    def __len__(self) -> int:
        return len(self.hotels)

    def __iter__(self) -> Iterator[Hotel]:
        return iter(self.hotels.values())

    def __getitem__(self, hotel_id: str) -> Hotel:
        return self.get_hotel(hotel_id)

    def __repr__(self) -> str:
        return f"HotelChain(name={self.name!r}, hotels={len(self.hotels)})"

    def __str__(self) -> str:
        return f"Мережа «{self.name}»: {len(self.hotels)} готелів"

