"""Генерація HTML-візитівок готелю та мережі.

Шаблони та стилі зберігаються у директорії templates/:
    - style.css        — CSS-стилі
    - hotel_card.html  — шаблон візитівки готелю
    - chain_card.html  — шаблон візитівки мережі

Шаблони використовують плейсхолдери виду {{ ключ }},
які замінюються на реальні значення під час генерації.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.hotel import Hotel
    from models.hotel_chain import HotelChain
    from models.room import Room

from models.enums import RoomStatus

# Шлях до директорії з шаблонами (поруч із кореневою папкою проєкту)
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _read_template(name: str) -> str:
    """Прочитати файл-шаблон із директорії templates/.

    Args:
        name: Ім'я файлу шаблону (наприклад, 'hotel_card.html').

    Returns:
        Вміст файлу як рядок.

    Raises:
        FileNotFoundError: Якщо файл шаблону не знайдено.
    """
    path = _TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Шаблон '{name}' не знайдено за шляхом: {path}")
    return path.read_text(encoding="utf-8")


class HtmlGenerator:
    """Генератор HTML-візитівок для готелів і мережі.

    Читає шаблони з директорії templates/.
    Можна вказати альтернативну директорію через template_dir.

    Args:
        template_dir: Шлях до директорії з шаблонами (необов'язково).
    """

    def __init__(self, template_dir: str | None = None) -> None:
        self._tpl_dir = Path(template_dir) if template_dir else _TEMPLATES_DIR

    # ---- Допоміжний метод читання шаблону ----

    def _read(self, name: str) -> str:
        """Прочитати шаблон із поточної директорії шаблонів."""
        path = self._tpl_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Шаблон '{name}' не знайдено: {path}")
        return path.read_text(encoding="utf-8")

    def _css(self) -> str:
        """Прочитати CSS-стилі."""
        return self._read("style.css")

    # ---- Візитівка одного готелю ----

    def generate(self, hotel: "Hotel", filepath: str) -> None:
        """Згенерувати HTML-візитівку готелю та зберегти у файл."""
        html = self._render_hotel(hotel)
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    # ---- Візитівка мережі ----

    def generate_chain_card(self, chain: "HotelChain", filepath: str) -> None:
        """Згенерувати HTML-візитівку мережі."""
        html = self._render_chain(chain)
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    # ---- Генерація всіх візитівок ----

    def generate_all(self, chain: "HotelChain", output_dir: str) -> None:
        """Згенерувати візитівки для мережі та всіх готелів."""
        base = Path(output_dir)
        self.generate_chain_card(chain, str(base / "chain_card.html"))
        hotels_dir = base / "hotels"
        hotels_dir.mkdir(parents=True, exist_ok=True)
        for hotel in chain:
            self.generate(hotel, str(hotels_dir / f"{hotel.hotel_id}.html"))

    # ---- Внутрішні методи рендерингу ----

    def _render_hotel(self, hotel: "Hotel") -> str:
        """Побудувати HTML-рядок для одного готелю на основі шаблону."""
        template = self._read("hotel_card.html")
        rooms_html = self._render_rooms_section(hotel)

        # Заміна плейсхолдерів на реальні значення
        return (
            template
            .replace("{{ hotel_name }}", hotel.name)
            .replace("{{ description }}", hotel.description)
            .replace("{{ address }}", hotel.address)
            .replace("{{ phone }}", hotel.phone)
            .replace("{{ email }}", hotel.email)
            .replace("{{ rooms_html }}", rooms_html)
            .replace("{{ css }}", self._css())
        )

    def _render_rooms_section(self, hotel: "Hotel") -> str:
        """Згрупувати номери за типом і побудувати HTML-картки."""
        from collections import Counter

        type_counts: Counter[str] = Counter()
        type_samples: dict[str, "Room"] = {}
        for room in hotel.rooms:
            cls_name = room.__class__.__name__
            type_counts[cls_name] += 1
            if cls_name not in type_samples:
                type_samples[cls_name] = room

        parts: list[str] = []
        for cls_name, sample in type_samples.items():
            free = sum(
                1
                for r in hotel.rooms
                if r.__class__.__name__ == cls_name and r.status == RoomStatus.FREE
            )
            parts.append(
                f"""        <div class="room-card">
            <h3>{cls_name}</h3>
            <p class="price">{sample.price_per_night:.0f} грн/ніч</p>
            <p>Всього: {type_counts[cls_name]}, вільних: {free}</p>
        </div>"""
            )
        return "\n".join(parts)

    def _render_chain(self, chain: "HotelChain") -> str:
        """Побудувати HTML-рядок для мережі на основі шаблону."""
        template = self._read("chain_card.html")

        hotels_list = ""
        for hotel in chain:
            link = f"hotels/{hotel.hotel_id}.html"
            hotels_list += (
                f'            <li><a href="{link}">{hotel.name}</a>'
                f" — {len(hotel.rooms)} номерів</li>\n"
            )

        return (
            template
            .replace("{{ chain_name }}", chain.name)
            .replace("{{ description }}", chain.description)
            .replace("{{ hotels_list }}", hotels_list)
            .replace("{{ css }}", self._css())
        )
