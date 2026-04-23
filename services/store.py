"""Сервіс збереження / завантаження даних (JSON)."""

from __future__ import annotations

from models.hotel_chain import HotelChain


class StoreService:
    """Обгортка для зручного збереження та завантаження мережі готелів.

    Args:
        dirpath: Шлях до директорії з даними.
    """

    def __init__(self, dirpath: str) -> None:
        self.dirpath = dirpath

    def save_chain(self, chain: HotelChain) -> None:
        """Зберегти мережу готелів."""
        chain.save(self.dirpath)

    def load_chain(self) -> HotelChain:
        """Завантажити мережу готелів."""
        return HotelChain.load(self.dirpath)

