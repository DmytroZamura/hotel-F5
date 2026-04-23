"""Система лояльності — утилітні функції."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.guest import Guest


# Рівні лояльності: (мін. балів, знижка %, назва)
LOYALTY_LEVELS: list[tuple[int, int, str]] = [
    (10_000, 15, "💎 Platinum"),
    (5_000, 10, "🥇 Gold"),
    (1_000, 5, "🥈 Silver"),
    (0, 0, "🥉 Bronze"),
]


def get_loyalty_level(guest: "Guest") -> str:
    """Повернути назву рівня лояльності гостя."""
    for min_pts, _, name in LOYALTY_LEVELS:
        if guest.loyalty_points >= min_pts:
            return name
    return "🥉 Bronze"


def get_discount(guest: "Guest") -> float:
    """Повернути знижку (0.0 – 0.15) на основі балів лояльності."""
    return guest.discount_percent / 100

