"""Класи номерів готелю: Room (базовий), StandardRoom, DeluxeRoom, Suite."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.enums import RoomStatus
from models.guest import Guest
from utils.validators import validate_positive_int, validate_positive_float, validate_type


class Room(ABC):
    """Абстрактний базовий клас номера.

    Attributes:
        number: Номер кімнати.
        price_per_night: Ціна за ніч (грн).
        status: Статус номера.
        guest: Поточний гість (або None).
    """

    def __init__(
            self,
            number: int,
            price_per_night: float,
            status: RoomStatus = RoomStatus.FREE,
            current_guest: Guest | None = None,
    ) -> None:
        self.number = number
        self.price_per_night = price_per_night
        self.status = status
        self.guest = current_guest

    # ---- Property-сетери з валідацією ----

    @property
    def number(self) -> int:
        """Номер кімнати."""
        return self._number

    @number.setter
    def number(self, value: int) -> None:
        self._number = validate_positive_int(value, "Номер кімнати")

    @property
    def price_per_night(self) -> float:
        """Ціна за ніч (грн)."""
        return self._price_per_night

    @price_per_night.setter
    def price_per_night(self, value: float) -> None:
        self._price_per_night = validate_positive_float(value, "Ціна за ніч")

    @property
    def status(self) -> RoomStatus:
        """Статус номера."""
        return self._status

    @status.setter
    def status(self, value: RoomStatus) -> None:
        self._status = validate_type(value, RoomStatus, "Статус номера")

    @property
    def guest(self) -> Guest | None:
        """Поточний гість номера."""
        return self._guest

    @guest.setter
    def guest(self, value: Guest | None) -> None:
        if value is not None:
            validate_type(value, Guest, "Гість")
        self._guest = value

    # ---- Абстрактний метод ----

    @abstractmethod
    def get_info(self) -> str:
        """Повернути рядок з інформацією про номер."""
        raise NotImplementedError()

    # ---- Заселення / виселення ----

    def check_in(self, guest: Guest) -> None:
        """Заселити гостя до номера."""
        if self.status == RoomStatus.OCCUPIED:
            raise RuntimeError(f"Номер {self.number} вже зайнятий ({self.guest})")
        self.guest = guest
        self.status = RoomStatus.OCCUPIED
        print(f"✅ Гість {guest.name} заселений у номер {self.number}")

    def check_out(self) -> None:
        """Виселити гостя з номера."""
        if self.status != RoomStatus.OCCUPIED or self.guest is None:
            raise RuntimeError(f"Номер {self.number} не зайнятий — нікого виселяти")
        guest_name = self.guest.name
        self.guest = None
        self.status = RoomStatus.FREE
        print(f"👋 Гість {guest_name} виселений з номера {self.number}")

    # ---- Серіалізація ----

    def to_dict(self) -> dict:
        """Повернути словник з даними номера (для збереження)."""
        return {
            "type": self.__class__.__name__,
            "number": self.number,
            "price_per_night": self.price_per_night,
            "status": self.status.value,
            "guest": self.guest.to_dict() if self.guest else None,
        }

    @classmethod
    def create_room_from_dict(cls, data: dict) -> "Room":
        """Створити номер потрібного типу зі словника."""
        room_types: dict[str, type[Room]] = {
            "StandardRoom": StandardRoom,
            "DeluxeRoom": DeluxeRoom,
            "Suite": Suite,
        }
        room_cls = room_types.get(data["type"])
        if room_cls is None:
            raise ValueError(f"Невідомий тип номера: {data['type']}")
        room = room_cls(number=data["number"], price_per_night=data["price_per_night"])
        room.status = RoomStatus(data["status"])
        guest_data = data.get("guest", {})
        if guest_data:
            room.guest = Guest(**guest_data)
        return room

    # ---- Магічні методи ----

    def __repr__(self) -> str:
        return (
            f"Room(number={self.number!r}, price_per_night={self.price_per_night!r}, "
            f"status={self.status!r}, guest={self.guest!r})"
        )

    def __str__(self) -> str:
        return (
            f"Номер {self.number} - ціна за ніч: {self.price_per_night} грн, "
            f"статус: {self.status.value}, "
            f"гість: {self.guest.name if self.guest else 'немає'}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Room):
            return NotImplemented
        return self.number == other.number


# --------------- Конкретні типи номерів ---------------

# Базові ціни за замовчуванням
_DEFAULT_PRICES: dict[str, float] = {
    "StandardRoom": 800.0,
    "DeluxeRoom": 1500.0,
    "Suite": 3000.0,
}


class StandardRoom(Room):
    """Стандартний номер — Wi-Fi, TV."""

    def __init__(self, number: int, price_per_night: float = _DEFAULT_PRICES["StandardRoom"], **kw) -> None:
        super().__init__(number, price_per_night, **kw)

    def get_info(self) -> str:
        return (f"Стандартний номер №{self.number}, ціна {self.price_per_night} грн"
                f", статус: {self.status.value}, гість: {self.guest.name if self.guest else 'немає'}"
                ", зручності: Wi-Fi, телевізор, кондиціонер, двомісна ліжко")


class DeluxeRoom(Room):
    """Номер Делюкс — Wi-Fi, TV, міні-бар, балкон."""

    def __init__(self, number: int, price_per_night: float = _DEFAULT_PRICES["DeluxeRoom"], **kw) -> None:
        super().__init__(number, price_per_night, **kw)

    def get_info(self) -> str:
        return (f"Делюкс номер №{self.number}, ціна {self.price_per_night} грн"
                f", статус: {self.status.value}, гість: {self.guest.name if self.guest else 'немає'}"
                ", зручності: Wi-Fi, TV, міні-бар, балкон")


class Suite(Room):
    """Люкс — Wi-Fi, TV, міні-бар, балкон, джакузі, вітальня."""

    def __init__(self, number: int, price_per_night: float = _DEFAULT_PRICES["Suite"], **kw) -> None:
        super().__init__(number, price_per_night, **kw)

    def get_info(self) -> str:
        return (f"Люкс №{self.number}, ціна {self.price_per_night} грн"
                f", статус: {self.status.value}, гість: {self.guest.name if self.guest else 'немає'}"
                ", зручності: Wi-Fi, TV, міні-бар, балкон, джакузі, вітальня")


