"""Тести для класу Booking."""

import unittest
from datetime import date

from models.booking import Booking
from models.enums import BookingStatus
from models.guest import Guest
from models.room import StandardRoom, DeluxeRoom


def _guest() -> Guest:
    return Guest("Олена Коваленко", "AA123456", "olena@example.com", "+380501234567")


def _room() -> StandardRoom:
    return StandardRoom(101)


class TestBookingCreation(unittest.TestCase):
    """Тести створення бронювання."""

    def test_creation(self) -> None:
        """Бронювання створюється з коректними параметрами."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=3)
        self.assertEqual(b.nights, 3)
        self.assertEqual(b.status, BookingStatus.CONFIRMED)

    def test_invalid_nights(self) -> None:
        """nights < 1 — ValueError."""
        with self.assertRaises(ValueError):
            Booking(_guest(), _room(), date(2026, 4, 15), nights=0)

    def test_invalid_guest_type(self) -> None:
        """Рядок замість Guest — TypeError."""
        with self.assertRaises(TypeError):
            Booking("не гість", _room(), date(2026, 4, 15), nights=2)

    def test_invalid_room_type(self) -> None:
        """Рядок замість Room — TypeError."""
        with self.assertRaises(TypeError):
            Booking(_guest(), "не номер", date(2026, 4, 15), nights=2)

    def test_invalid_check_in_date_type(self) -> None:
        """Рядок замість date — TypeError."""
        with self.assertRaises(TypeError):
            Booking(_guest(), _room(), "2026-04-15", nights=2)


    def test_invalid_status_type(self) -> None:
        """Рядок замість BookingStatus — TypeError."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=2)
        with self.assertRaises(TypeError):
            b.status = "confirmed"

    def test_setter_nights_invalid(self) -> None:
        """Зміна nights на 0 через сетер — ValueError."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=2)
        with self.assertRaises(ValueError):
            b.nights = 0

    def test_total_cost(self) -> None:
        """Вартість = ціна × ночі."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=3)
        self.assertAlmostEqual(b.total_cost(), 800.0 * 3)

    def test_total_cost_with_discount(self) -> None:
        """Вартість зі знижкою 5% (гість із 100+ балами лояльності)."""
        guest = Guest("Олена Коваленко", "AA123456", "olena@example.com", "+380501234567", loyalty_points=100)
        b = Booking(guest, _room(), date(2026, 4, 15), nights=2)
        self.assertAlmostEqual(b.total_cost(), 800.0 * 2 * 0.95)

    def test_check_out_date(self) -> None:
        """Дата виїзду = заїзд + nights днів."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=3)
        self.assertEqual(b.check_out_date, date(2026, 4, 18))

    def test_repr(self) -> None:
        """__repr__ містить ключову інформацію."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=3)
        self.assertIn("Booking", repr(b))
        self.assertIn("101", repr(b))

    def test_to_dict(self) -> None:
        """Серіалізація у словник."""
        b = Booking(_guest(), _room(), date(2026, 4, 15), nights=2, booking_id="BK-001")
        d = b.to_dict()
        self.assertEqual(d["booking_id"], "BK-001")
        self.assertEqual(d["room_number"], 101)
        self.assertEqual(d["nights"], 2)


if __name__ == "__main__":
    unittest.main()

