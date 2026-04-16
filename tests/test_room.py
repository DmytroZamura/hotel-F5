"""Тести для класу Room та його методів."""

import unittest

from models.enums import RoomStatus
from models.guest import Guest
from models.room import Room, StandardRoom


# --- Допоміжний конкретний підклас (бо Room — абстрактний) ---

class ConcreteRoom(Room):
    """Конкретна реалізація Room для тестування."""

    def get_info(self) -> str:
        return f"Кімната №{self.number}, ціна {self.price_per_night} грн"


def _make_guest() -> Guest:
    """Створити тестового гостя."""
    return Guest(
        name="Іван Іванов",
        passport="АА123456",
        email="ivan@example.com",
        phone_number="+380501234567",
    )


# --- Тести створення ---

class TestRoomCreation(unittest.TestCase):
    """Тести ініціалізації номера."""

    def setUp(self) -> None:
        self.room = ConcreteRoom(number=101, price_per_night=1200.0)

    def test_default_status_is_free(self) -> None:
        """Новий номер має статус FREE."""
        self.assertEqual(self.room.status, RoomStatus.FREE)

    def test_default_guest_is_none(self) -> None:
        """Новий номер не має гостя."""
        self.assertIsNone(self.room.guest)

    def test_attributes(self) -> None:
        """Перевірка збережених атрибутів."""
        self.assertEqual(self.room.number, 101)
        self.assertEqual(self.room.price_per_night, 1200.0)

    def test_invalid_number_negative_raises(self) -> None:
        """Від'ємний номер кімнати — ValueError."""
        with self.assertRaises(ValueError):
            ConcreteRoom(number=-1, price_per_night=500.0)

    def test_invalid_number_zero_raises(self) -> None:
        """Нульовий номер кімнати — ValueError."""
        with self.assertRaises(ValueError):
            ConcreteRoom(number=0, price_per_night=500.0)

    def test_invalid_number_string_raises(self) -> None:
        """Рядок замість номера кімнати — ValueError."""
        with self.assertRaises(ValueError):
            ConcreteRoom(number="abc", price_per_night=500.0)

    def test_invalid_number_float_raises(self) -> None:
        """Дробове число замість номера кімнати — ValueError."""
        with self.assertRaises(ValueError):
            ConcreteRoom(number=1.5, price_per_night=500.0)

    def test_invalid_number_none_raises(self) -> None:
        """None замість номера кімнати — ValueError."""
        with self.assertRaises(ValueError):
            ConcreteRoom(number=None, price_per_night=500.0)


# --- Тести заселення ---

class TestCheckIn(unittest.TestCase):
    """Тести методу check_in."""

    def setUp(self) -> None:
        self.room = ConcreteRoom(number=101, price_per_night=1200.0)
        self.guest = _make_guest()

    def test_check_in_sets_guest(self) -> None:
        """Після заселення гість зберігається в номері."""
        self.room.check_in(self.guest)
        self.assertIs(self.room.guest, self.guest)

    def test_check_in_sets_status_occupied(self) -> None:
        """Після заселення статус — OCCUPIED."""
        self.room.check_in(self.guest)
        self.assertEqual(self.room.status, RoomStatus.OCCUPIED)

    def test_check_in_occupied_room_raises(self) -> None:
        """Заселення у зайнятий номер — RuntimeError."""
        self.room.check_in(self.guest)
        another_guest = Guest("Петро Петров", "ВВ654321", "petro@example.com", "+380509876543")
        with self.assertRaises(RuntimeError):
            self.room.check_in(another_guest)

    def test_check_in_not_guest_raises(self) -> None:
        """Заселення не-Guest об'єкта — AttributeError."""
        with self.assertRaises(AttributeError):
            self.room.check_in("не гість")


# --- Тести виселення ---

class TestCheckOut(unittest.TestCase):
    """Тести методу check_out."""

    def setUp(self) -> None:
        self.room = ConcreteRoom(number=101, price_per_night=1200.0)
        self.guest = _make_guest()

    def test_check_out_clears_guest(self) -> None:
        """Після виселення гість — None."""
        self.room.check_in(self.guest)
        self.room.check_out()
        self.assertIsNone(self.room.guest)

    def test_check_out_sets_status_free(self) -> None:
        """Після виселення статус — FREE."""
        self.room.check_in(self.guest)
        self.room.check_out()
        self.assertEqual(self.room.status, RoomStatus.FREE)

    def test_check_out_free_room_raises(self) -> None:
        """Виселення з вільного номера — RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.room.check_out()

    def test_check_out_reserved_room_no_guest_raises(self) -> None:
        """Виселення з номера зі статусом RESERVED без гостя — RuntimeError."""
        self.room.status = RoomStatus.RESERVED
        with self.assertRaises(RuntimeError):
            self.room.check_out()

    def test_double_check_out_raises(self) -> None:
        """Повторне виселення — RuntimeError."""
        self.room.check_in(self.guest)
        self.room.check_out()
        with self.assertRaises(RuntimeError):
            self.room.check_out()


# --- Тести серіалізації ---

class TestSerialization(unittest.TestCase):
    """Тести to_dict / from_dict."""

    def setUp(self) -> None:
        self.room = ConcreteRoom(number=101, price_per_night=1200.0)
        self.guest = _make_guest()

    def test_to_dict_free_room(self) -> None:
        """Словник вільного номера містить правильні дані."""
        data = self.room.to_dict()
        self.assertEqual(data, {
            "number": 101,
            "price_per_night": 1200.0,
            "status": "free",
            "guest": None,
        })

    def test_to_dict_occupied_room(self) -> None:
        """Словник зайнятого номера містить дані гостя."""
        self.room.check_in(self.guest)
        data = self.room.to_dict()
        self.assertEqual(data["status"], "occupied")
        self.assertEqual(data["guest"]["name"], self.guest.name)

    def test_from_dict_restores_room(self) -> None:
        """from_dict відновлює стан номера зі словника."""
        source = ConcreteRoom(number=202, price_per_night=800.0)
        source.check_in(self.guest)
        data = source.to_dict()

        self.room.from_dict(data)
        self.assertEqual(self.room.number, 202)
        self.assertEqual(self.room.price_per_night, 800.0)
        self.assertEqual(self.room.status, RoomStatus.OCCUPIED)
        self.assertIsNotNone(self.room.guest)
        self.assertEqual(self.room.guest.name, self.guest.name)

    def test_from_dict_without_guest(self) -> None:
        """from_dict коректно працює без гостя."""
        data = {"number": 303, "price_per_night": 600.0, "status": "free"}
        self.room.from_dict(data)
        self.assertIsNone(self.room.guest)
        self.assertEqual(self.room.status, RoomStatus.FREE)

    def test_from_dict_invalid_status_raises(self) -> None:
        """from_dict з невалідним статусом — ValueError."""
        data = {"number": 1, "price_per_night": 100.0, "status": "unknown"}
        with self.assertRaises(ValueError):
            self.room.from_dict(data)

    def test_to_dict_round_trip(self) -> None:
        """Дані після to_dict → from_dict зберігаються коректно."""
        self.room.check_in(self.guest)
        data = self.room.to_dict()
        new_room = ConcreteRoom(number=999, price_per_night=1.0)
        new_room.from_dict(data)
        self.assertEqual(new_room.to_dict(), data)


# --- Тести __eq__, __str__, __repr__ ---

class TestDunderMethods(unittest.TestCase):
    """Тести магічних методів."""

    def setUp(self) -> None:
        self.room = ConcreteRoom(number=101, price_per_night=1200.0)

    def test_eq_same_number(self) -> None:
        """Номери з однаковим number рівні."""
        r1 = ConcreteRoom(number=1, price_per_night=100.0)
        r2 = ConcreteRoom(number=1, price_per_night=999.0)
        self.assertEqual(r1, r2)

    def test_eq_different_number(self) -> None:
        """Номери з різним number — не рівні."""
        r1 = ConcreteRoom(number=1, price_per_night=100.0)
        r2 = ConcreteRoom(number=2, price_per_night=100.0)
        self.assertNotEqual(r1, r2)

    def test_eq_not_room_returns_not_implemented(self) -> None:
        """Порівняння з не-Room повертає NotImplemented."""
        self.assertIs(self.room.__eq__("not a room"), NotImplemented)

    def test_str_contains_number(self) -> None:
        """__str__ містить номер кімнати."""
        self.assertIn("101", str(self.room))

    def test_repr_contains_class(self) -> None:
        """__repr__ містить 'Room'."""
        self.assertIn("Room", repr(self.room))

    def test_get_info(self) -> None:
        """get_info повертає рядок з інформацією."""
        info = self.room.get_info()
        self.assertIn("101", info)


class TestStandardRoom(unittest.TestCase):

    def test_get_info(self) -> None:
        room = StandardRoom(number=101, price_per_night=1200.0)
        self.assertEqual(room.number, 101)
        self.assertEqual(room.price_per_night, 1200.0)
        self.assertEqual(room.status, RoomStatus.FREE)
        self.assertIsNone(room.guest)
        self.assertEqual(room.get_info(),
                         "Стандартний номер №101, ціна 1200.0 грн, "
                         "статус: free, гість: немає, зручності: Wi-Fi, "
                         "телевізор, кондиціонер, двомісна ліжко"
                         )


if __name__ == "__main__":
    unittest.main()
