"""Тести для класу HotelChain."""

import unittest
import tempfile
import os
from datetime import date

from models.guest import Guest
from models.hotel import Hotel
from models.hotel_chain import HotelChain
from models.room import StandardRoom, DeluxeRoom


def _guest() -> Guest:
    return Guest("Олена Коваленко", "AA123456", "olena@example.com", "+380501234567")


class TestHotelChain(unittest.TestCase):
    """Тести мережі готелів."""

    def setUp(self) -> None:
        self.chain = HotelChain("Grand Hotels", "Опис мережі")
        self.h1 = Hotel("Kyiv", hotel_id="kyiv")
        self.h1.add_room(StandardRoom(101))
        self.h1.add_room(DeluxeRoom(201))
        self.h2 = Hotel("Lviv", hotel_id="lviv")
        self.h2.add_room(StandardRoom(101))

    def test_creation(self) -> None:
        self.assertEqual(self.chain.name, "Grand Hotels")


class TestHotelChainValidation(unittest.TestCase):
    """Тести валідації полів HotelChain."""

    def test_empty_name_raises(self) -> None:
        """Порожня назва мережі — ValueError."""
        with self.assertRaises(ValueError):
            HotelChain("")

    def test_name_type_raises(self) -> None:
        """Назва не рядок — TypeError."""
        with self.assertRaises(TypeError):
            HotelChain(123)

    def test_description_type_raises(self) -> None:
        """Опис не рядок — TypeError."""
        chain = HotelChain("Test")
        with self.assertRaises(TypeError):
            chain.description = 123

    def test_setter_name_empty_raises(self) -> None:
        """Зміна назви на порожню — ValueError."""
        chain = HotelChain("Test")
        with self.assertRaises(ValueError):
            chain.name = ""


class TestHotelChainOperations(unittest.TestCase):
    """Тести операцій мережі готелів."""

    def setUp(self) -> None:
        self.chain = HotelChain("Grand Hotels", "Опис мережі")
        self.h1 = Hotel("Kyiv", hotel_id="kyiv")
        self.h1.add_room(StandardRoom(101))
        self.h1.add_room(DeluxeRoom(201))
        self.h2 = Hotel("Lviv", hotel_id="lviv")
        self.h2.add_room(StandardRoom(101))

    def test_add_hotel(self) -> None:
        self.chain.add_hotel(self.h1)
        self.assertEqual(len(self.chain), 1)

    def test_duplicate_hotel(self) -> None:
        self.chain.add_hotel(self.h1)
        with self.assertRaises(ValueError):
            self.chain.add_hotel(self.h1)

    def test_remove_hotel(self) -> None:
        self.chain.add_hotel(self.h1)
        self.chain.remove_hotel("kyiv")
        self.assertEqual(len(self.chain), 0)

    def test_get_hotel(self) -> None:
        self.chain.add_hotel(self.h1)
        self.assertIs(self.chain.get_hotel("kyiv"), self.h1)

    def test_getitem(self) -> None:
        self.chain.add_hotel(self.h1)
        self.assertIs(self.chain["kyiv"], self.h1)

    def test_register_guest(self) -> None:
        guest = _guest()
        self.chain.register_guest(guest)
        self.assertIs(self.chain.get_guest("AA123456"), guest)

    def test_find_available_all(self) -> None:
        self.chain.add_hotel(self.h1)
        self.chain.add_hotel(self.h2)
        result = self.chain.find_available_all(StandardRoom)
        self.assertIn("kyiv", result)
        self.assertIn("lviv", result)

    def test_iter(self) -> None:
        self.chain.add_hotel(self.h1)
        self.chain.add_hotel(self.h2)
        names = [h.name for h in self.chain]
        self.assertEqual(len(names), 2)

    def test_len(self) -> None:
        self.chain.add_hotel(self.h1)
        self.assertEqual(len(self.chain), 1)

    def test_total_revenue(self) -> None:
        self.h1.total_revenue = 5000
        self.h2.total_revenue = 3000
        self.chain.add_hotel(self.h1)
        self.chain.add_hotel(self.h2)
        self.assertEqual(self.chain.get_total_revenue(), 8000)

    def test_save_load(self) -> None:
        self.chain.add_hotel(self.h1)
        self.chain.add_hotel(self.h2)
        guest = _guest()
        self.chain.register_guest(guest)

        with tempfile.TemporaryDirectory() as tmpdir:
            self.chain.save(tmpdir)
            loaded = HotelChain.load(tmpdir)
            self.assertEqual(loaded.name, "Grand Hotels")
            self.assertEqual(len(loaded), 2)
            self.assertIn("AA123456", loaded.guests)

    def test_save_load_with_bookings(self) -> None:
        """Бронювання зберігаються та завантажуються коректно."""
        self.chain.add_hotel(self.h1)
        guest = _guest()
        self.chain.register_guest(guest)

        # Створюємо бронювання
        booking = self.h1.book(guest, self.h1.rooms[0], date(2026, 5, 1), nights=2)
        self.assertEqual(len(self.h1.bookings), 1)

        with tempfile.TemporaryDirectory() as tmpdir:
            self.chain.save(tmpdir)
            loaded = HotelChain.load(tmpdir)

            # Перевіряємо що бронювання завантажилось
            loaded_hotel = loaded["kyiv"]
            self.assertEqual(len(loaded_hotel.bookings), 1)

            loaded_booking = loaded_hotel.bookings[0]
            self.assertEqual(loaded_booking.booking_id, booking.booking_id)
            self.assertEqual(loaded_booking.nights, 2)
            self.assertEqual(loaded_booking.guest.passport, "AA123456")
            self.assertEqual(loaded_booking.room.number, 101)


if __name__ == "__main__":
    unittest.main()

