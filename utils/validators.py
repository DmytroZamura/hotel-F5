from typing import Any


def validate_non_empty_string(value: str, field_name: str) -> str:
    """Перевірити, що рядок не порожній, і повернути stripped версію.

    Args:
        value: Значення для перевірки.
        field_name: Назва поля (для повідомлення про помилку).
    Returns:
        Очищений рядок (stripped).
    Raises:
        ValueError: Якщо рядок порожній або складається лише з пробілів.
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} не може бути порожнім")
    return value.strip()


def validate_positive_int(value: int, field_name: str) -> int:
    """Перевірити, що значення — ціле додатне число (> 0).
    Raises:
        ValueError: Якщо значення не int или <= 0.
    """
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} має бути цілим додатним числом")
    return value


def validate_min_int(value: int, minimum: int, field_name: str) -> int:
    """Перевірити, що ціле значення >= minimum.
    Raises:
        ValueError: Якщо значення не int или < minimum.
    """
    if not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field_name} має бути >= {minimum}")
    return value


def validate_positive_float(value: float, field_name: str) -> float:
    """Перевірити, що числове значення > 0.
    Raises:
        ValueError: Якщо значення <= 0.
    """
    if value <= 0:
        raise ValueError(f"{field_name} має бути більше 0")
    return float(value)


def validate_range(value: float, low: float, high: float, field_name: str) -> float:
    """Перевірити, що значення знаходиться в діапазоні [low, high].
    Raises:
        ValueError: Якщо значення поза діапазоном.
    """
    if not (low <= value <= high):
        raise ValueError(f"{field_name} має бути від {low} до {high}")
    return float(value)


def validate_type(value: Any, expected_type: type, field_name: str) -> Any:
    """Перевірити, що значення є екземпляром expected_type.
    Raises:
        ValueError:.
    """
    if not isinstance(value, expected_type):
        raise ValueError(f"{field_name} має бути типу {expected_type.__name__}")
    return value


def validate_email(email: str) -> str:
    """Перевірити, що рядок є валидным email."""
    email = validate_non_empty_string(email, "Email")
    if "@" not in email or "." not in email:
        raise ValueError("Невалідна email адреса")
    return email


def validate_phone_number(phone: str) -> str:
    """Перевірити, що рядок є валидным номером телефона."""
    phone = validate_non_empty_string(phone, "Номер телефона")
    if len(phone) < 10:
        raise ValueError("Номер телефону має бути не менше 10 цифр")
    return phone


