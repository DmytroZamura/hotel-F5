"""Клас Guest — гість готелю."""

from __future__ import annotations

from utils.validators import (
    validate_non_empty_string,
    validate_email,
    validate_phone_number,
    validate_min_int,
)


class Guest:
    """Гість готелю.

    Attributes:
        name: Повне ім'я гостя.
        passport: Номер паспорта (унікальний ідентифікатор).
        email: Електронна пошта.
        phone_number: Номер телефону.
        loyalty_points: Бали лояльності.
        stay_history: Історія перебувань.
    """

    def __init__(
        self,
        name: str,
        passport: str,
        email: str,
        phone_number: str,
        loyalty_points: int = 0,
        stay_history: list[dict] | None = None,
    ) -> None:
        self.name = name
        self.passport = passport
        self.email = email
        self.phone_number = phone_number
        self.loyalty_points = loyalty_points
        self.stay_history: list[dict] = stay_history or []

    # ---- Property-сетери з валідацією ----

    @property
    def name(self) -> str:
        """Повне ім'я гостя."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_non_empty_string(value, "Ім'я гостя")

    @property
    def passport(self) -> str:
        """Номер паспорта."""
        return self._passport

    @passport.setter
    def passport(self, value: str) -> None:
        self._passport = validate_non_empty_string(value, "Номер паспорта")

    @property
    def email(self) -> str:
        """Електронна пошта."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = validate_email(value)

    @property
    def phone_number(self) -> str:
        """Номер телефону."""
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: str) -> None:
        self._phone_number = validate_phone_number(value)

    @property
    def loyalty_points(self) -> int:
        """Бали лояльності."""
        return self._loyalty_points

    @loyalty_points.setter
    def loyalty_points(self, value: int) -> None:
        self._loyalty_points = validate_min_int(value, 0, "Бали лояльності")

    # ---- Методи ----

    def add_loyalty_points(self, points: int) -> None:
        """Нарахувати бали лояльності."""
        points = validate_min_int(points, 0, "Бали лояльності")
        self.loyalty_points += points

    def to_dict(self) -> dict:
        """Повернути словник з даними гостя (для збереження)."""
        return {
            "name": self.name,
            "passport": self.passport,
            "email": self.email,
            "phone_number": self.phone_number,
            "loyalty_points": self.loyalty_points,
            "stay_history": self.stay_history,
        }

    def from_dict(self, data: dict) -> None:
        """Заповнити дані гостя зі словника (для завантаження)."""
        self.name = data["name"]
        self.passport = data["passport"]
        self.email = data["email"]
        self.phone_number = data["phone_number"]
        self.loyalty_points = data.get("loyalty_points", 0)
        self.stay_history = data.get("stay_history", [])

    @property
    def discount_percent(self) -> int:
        """Знижка (%) на основі балів лояльності.

        0-99 балів  → 0 %
        100-499     → 5 %
        500-999     → 10 %
        1000+       → 15 %
        """
        if self.loyalty_points >= 1000:
            return 15
        if self.loyalty_points >= 500:
            return 10
        if self.loyalty_points >= 100:
            return 5
        return 0

    # ---- Магічні методи ----

    def __repr__(self) -> str:
        return (
            f"Guest(name={self.name!r}, passport={self.passport!r}, "
            f"email={self.email!r}, phone_number={self.phone_number!r})"
        )

    def __str__(self) -> str:
        return (
            f"Гість - ПІБ={self.name}, email={self.email}, "
            f"номер телефону={self.phone_number}, паспорт={self.passport}, "
            f"бали лояльності={self.loyalty_points}"
        )
