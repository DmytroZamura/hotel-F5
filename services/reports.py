"""Звіти та статистика."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.hotel import Hotel
    from models.hotel_chain import HotelChain


def hotel_report(hotel: "Hotel") -> dict:
    """Повернути звіт про готель (делегує hotel.get_revenue_report)."""
    return hotel.get_revenue_report()


def chain_report(chain: "HotelChain") -> dict:
    """Повернути агрегований звіт по мережі."""
    return chain.get_chain_report()

