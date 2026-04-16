from abc import ABC, abstractmethod

from models.enums import RoomStatus
from models.guest import Guest
from utils.validators import validate_positive_int, validate_positive_float, validate_type


class Room(ABC):
    """Абстрактний базовий клас номера."""

    def __init__(
            self,
            number: int,
            price_per_night: float,
            status: RoomStatus = RoomStatus.FREE,
            current_guest: Guest | None = None,
    ) -> None:
        self.number = validate_positive_int(number, 'Номер кімнати')
        self.price_per_night = validate_positive_float(price_per_night, "Ціна за ніч")
        self.status = status
        self.guest = validate_type(current_guest, Guest, "Гість") if current_guest else None

    @abstractmethod
    def get_info(self):
        """Повернути рядок з інформацією про номер."""
        raise NotImplementedError()

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

    def __repr__(self):
        return f"Room(number={self.number!r}, price_per_night={self.price_per_night!r}, status={self.status!r}, guest={self.guest!r})"

    def __str__(self):
        return f"Номер {self.number} - ціна за ніч: {self.price_per_night} грн, статус: {self.status.value}, гість: {self.guest.name if self.guest else 'немає'}"

    def to_dict(self) -> dict:
        """Повернути словник з даними номера (для збереження)."""
        return {
            "number": self.number,
            "price_per_night": self.price_per_night,
            "status": self.status.value,
            "guest": self.guest.to_dict() if self.guest else None,
        }

    def from_dict(self, data: dict) -> None:
        """Заповнити дані номера зі словника (для завантаження)."""
        self.number = data["number"]
        self.price_per_night = data["price_per_night"]
        self.status = RoomStatus(data["status"])
        guest_data = data.get("guest", {})
        if guest_data:
            from models.guest import Guest  # Імпорт тут, щоб уникнути циклічної залежності
            self.guest = Guest(
                name=guest_data["name"],
                passport=guest_data["passport"],
                email=guest_data["email"],
                phone_number=guest_data["phone_number"],
            )
            self.guest.from_dict(guest_data)
        else:
            self.guest = None

    def __eq__(self, other) -> bool:
        if not isinstance(other, Room):
            return NotImplemented
        return self.number == other.number


class StandardRoom(Room):
    """Стандартний номер."""

    def get_info(self) -> str:
        return (f"Стандартний номер №{self.number}, ціна {self.price_per_night} грн"
                f", статус: {self.status.value}, гість: {self.guest.name if self.guest else 'немає'}"
                ", зручності: Wi-Fi, телевізор, кондиціонер, двомісна ліжко")
