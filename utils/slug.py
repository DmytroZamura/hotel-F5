"""Утиліта для створення slug-ідентифікаторів із тексту."""

import re
import unicodedata


def get_slug(text: str) -> str:
    """Перетворити довільний рядок у slug (URL-безпечний ідентифікатор).

    Алгоритм:
        1. Транслітерація Unicode → ASCII (наприклад, «é» → «e»).
        2. Приведення до нижнього регістру.
        3. Заміна пробілів та спецсимволів на дефіс.
        4. Видалення повторних дефісів і обрізання країв.

    Args:
        text: Вхідний рядок (назва готелю тощо).

    Returns:
        Slug-рядок, наприклад ``"grand-hotel-kyiv"``.

    Examples:
        >>> get_slug("Grand Hotel Kyiv")
        'grand-hotel-kyiv'
        >>> get_slug("  Hello   World!  ")
        'hello-world'
    """
    # Транслітерація Unicode → ASCII
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    # Нижній регістр, заміна не-алфавітних символів на дефіс
    slug = ascii_text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Видалення зайвих дефісів з країв
    return slug.strip("-")

