"""Тести для класу Hotel."""

import unittest
from datetime import date

from models.enums import RoomStatus, BookingStatus
from models.guest import Guest
from models.hotel import Hotel
from models.room import StandardRoom, DeluxeRoom, Suite


def _guest() -> Guest:
    return Guest("Олена Коваленко", "AA123456", "olena@example.com", "+380501234567")


class TestHotelBasic(unittest.TestCase):
    """Базові тести Hotel."""

    def setUp(self) -> None:
        self.hotel = Hotel("Grand Hotel", hotel_id="grand")
        self.hotel.add_room(StandardRoom(101))
        self.hotel.add_room(DeluxeRoom(201))
        self.hotel.add_room(Suite(301))

    def test_creation(self) -> None:
        self.assertEqual(self.hotel.name, "Grand Hotel")

    def test_add_room(self) -> None:
        self.assertEqual(len(self.hotel), 3)

    def test_add_duplicate_room(self) -> None:
        with self.assertRaises(ValueError):
            self.hotel.add_room(StandardRoom(101))

    def test_len(self) -> None:
        self.assertEqual(len(self.hotel), 3)

    def test_str(self) -> None:
        self.assertIn("3", str(self.hotel))
        self.assertIn("Grand Hotel", str(self.hotel))


class TestHotelValidation(unittest.TestCase):
    """Тести валідації полів Hotel."""

    def test_empty_name_raises(self) -> None:
        """Порожня назва готелю — ValueError."""
        with self.assertRaises(ValueError):
            Hotel("", hotel_id="test")

    def test_name_type_raises(self) -> None:
        """Назва не рядок — TypeError."""
        with self.assertRaises(TypeError):
            Hotel(123, hotel_id="test")

    def test_description_type_raises(self) -> None:
        """Опис не рядок — TypeError."""
        hotel = Hotel("Test", hotel_id="test")
        with self.assertRaises(TypeError):
            hotel.description = 123

    def test_address_type_raises(self) -> None:
        """Адреса не рядок — TypeError."""
        hotel = Hotel("Test", hotel_id="test")
        with self.assertRaises(TypeError):
            hotel.address = 123

    def test_total_revenue_negative_raises(self) -> None:
        """Від'ємний дохід — ValueError."""
        hotel = Hotel("Test", hotel_id="test")
        with self.assertRaises(ValueError):
            hotel.total_revenue = -100.0

    def test_total_revenue_type_raises(self) -> None:
        """Дохід не число — TypeError."""
        hotel = Hotel("Test", hotel_id="test")
        with self.assertRaises(TypeError):
            hotel.total_revenue = "багато"

    def test_invalid_email_raises(self) -> None:
        """Невалідний email — ValueError."""
        with self.assertRaises(ValueError):
            Hotel("Test", hotel_id="test", email="bad_email")

    def test_invalid_phone_raises(self) -> None:
        """Короткий телефон — ValueError."""
        with self.assertRaises(ValueError):
            Hotel("Test", hotel_id="test", phone="123")

    def test_setter_name_empty_raises(self) -> None:
        """Зміна назви на порожню — ValueError."""
        hotel = Hotel("Test", hotel_id="test")
        with self.assertRaises(ValueError):
            hotel.name = ""


class TestHotelFindAvailable(unittest.TestCase):
    """Тести пошуку вільних номерів."""

    def setUp(self) -> None:
        self.hotel = Hotel("Test", hotel_id="test")
        self.hotel.add_room(StandardRoom(101))
        self.hotel.add_room(StandardRoom(102))
        self.hotel.add_room(DeluxeRoom(201))
        self.guest = _guest()

    def test_find_by_type(self) -> None:
        available = self.hotel.find_available(StandardRoom)
        self.assertEqual(len(available), 2)

    def test_find_by_dates(self) -> None:
        ci, co = date(2026, 5, 1), date(2026, 5, 3)
        available = self.hotel.find_available(check_in=ci, check_out=co)
        self.assertEqual(len(available), 3)

    def test_overlap(self) -> None:
        """Номер зайнятий, якщо дати перетинаються."""
        self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), nights=3)
        available = self.hotel.find_available(StandardRoom, date(2026, 5, 2), date(2026, 5, 5))
        # Лише 102 вільний
        self.assertEqual(len(available), 1)

    def test_adjacent_dates_free(self) -> None:
        """Номер вільний, якщо дати не перетинаються (суміжні)."""
        self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), nights=2)
        # Виїзд 3 травня, заїзд 3 травня — не перетинаються
        available = self.hotel.find_available(StandardRoom, date(2026, 5, 3), date(2026, 5, 5))
        self.assertEqual(len(available), 2)

    def test_none_available(self) -> None:
        """Порожній список, якщо немає вільних."""
        available = self.hotel.find_available(Suite)
        self.assertEqual(len(available), 0)


class TestHotelBooking(unittest.TestCase):
    """Тести бронювання, заселення, виселення."""

    def setUp(self) -> None:
        self.hotel = Hotel("Test", hotel_id="test")
        self.hotel.add_room(StandardRoom(101))
        self.guest = _guest()

    def test_book(self) -> None:
        booking = self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)
        self.assertEqual(self.hotel.rooms[0].status, RoomStatus.RESERVED)

    def test_book_unavailable(self) -> None:
        self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)
        with self.assertRaises(ValueError):
            self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)

    def test_check_in_guest(self) -> None:
        booking = self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)
        self.hotel.check_in_guest(booking)
        self.assertEqual(booking.status, BookingStatus.CHECKED_IN)
        self.assertEqual(self.hotel.rooms[0].status, RoomStatus.OCCUPIED)

    def test_check_out_guest(self) -> None:
        booking = self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)
        self.hotel.check_in_guest(booking)
        self.hotel.check_out_guest(booking)
        self.assertEqual(booking.status, BookingStatus.COMPLETED)
        self.assertEqual(self.hotel.rooms[0].status, RoomStatus.FREE)
        self.assertGreater(self.hotel.total_revenue, 0)

    def test_checkout_adds_loyalty_points(self) -> None:
        booking = self.hotel.book(self.guest, self.hotel.rooms[0], date(2026, 5, 1), 2)
        self.hotel.check_in_guest(booking)
        self.hotel.check_out_guest(booking)
        self.assertGreater(self.guest.loyalty_points, 0)


class TestHotelSerialization(unittest.TestCase):
    """Тести збереження/завантаження."""

    def test_save_load(self) -> None:
        import tempfile, os
        hotel = Hotel("Test Hotel", hotel_id="test",
                      description="Тест", address="Київ", phone="+380441111111", email="t@t.ua")
        hotel.add_room(StandardRoom(101))
        hotel.add_room(DeluxeRoom(201))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "hotel.json")
            hotel.save(path)
            loaded = Hotel.load(path)
            self.assertEqual(loaded.name, "Test Hotel")
            self.assertEqual(len(loaded), 2)


if __name__ == "__main__":
    unittest.main()

