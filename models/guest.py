from utils.validators import validate_non_empty_string, validate_email, validate_phone_number, validate_min_int


class Guest:
    """Клас для опису гостя готелю"""
    def __init__(self, name: str, passport: str, email: str, phone_number: str) -> None:
        self.name = validate_non_empty_string(name, "Ім'я гостя")
        self.passport = validate_non_empty_string(passport, "Номер паспорта")
        self.email = validate_email(email)
        self.phone_number = validate_phone_number(phone_number)
        self.loyalty_points: int = 0
        self.stay_history: list[dict] = []

    def __repr__(self) -> str:
        return (
            f"Guest(name={self.name!r}, passport={self.passport!r}, email={self.email!r}, phone_number={self.phone_number!r})"

        )

    def __str__(self):
        return f"Гість - ПІБ={self.name}, email={self.email}, номер телефону={self.phone_number}, паспорт={self.passport}, бали лояльності={self.loyalty_points}"

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
