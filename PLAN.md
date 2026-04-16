# 🏨 План реалізації системи управління готелем

## Огляд проекту

Система автоматизації роботи готелю: бронювання номерів, заселення/виселення гостей, облік доходів.

---

## 📁 Структура проекту

```
hotel-F5/
├── main.py                 # Точка входу, демонстрація роботи
├── models/
│   ├── __init__.py
│   ├── enums.py            # Enum для статусів номера
│   ├── guest.py            # Клас Guest
│   ├── room.py             # Room (абстрактний) + StandardRoom, DeluxeRoom, Suite
│   ├── booking.py          # Клас Booking
│   ├── hotel.py            # Клас Hotel
│   └── hotel_chain.py      # Клас HotelChain (мережа готелів)
├── services/
│   ├── __init__.py
│   ├── loyalty.py          # Система лояльності
│   ├── reports.py          # Звіти та статистика
│   ├── store.py            # Збереження/завантаження даних (JSON)
│   └── html_generator.py   # Генерація HTML-візитівки готелю
├── utils/
│   ├── __init__.py
│   └── validators.py       # Валідатори даних
├── data/                   # Директорія для збереження даних
│   ├── chain.json          # Мережа готелів (загальні дані)
│   ├── hotels/             # Дані окремих готелів
│   │   ├── hotel_kyiv.json
│   │   └── hotel_lviv.json
│   ├── guests.json         # База гостей (спільна для мережі)
│   └── bookings.json       # Історія бронювань
├── output/                 # Згенеровані файли
│   ├── chain_card.html     # HTML-візитівка мережі
│   └── hotels/             # Візитівки окремих готелів
│       ├── hotel_kyiv.html
│       └── hotel_lviv.html
├── templates/              # HTML шаблони
│   ├── hotel_card.html     # Шаблон візитівки готелю
│   └── chain_card.html     # Шаблон візитівки мережі
├── tests/
│   ├── __init__.py
│   ├── test_room.py
│   ├── test_guest.py
│   ├── test_booking.py
│   ├── test_hotel.py
│   ├── test_hotel_chain.py # Тести мережі готелів
│   ├── test_store.py       # Тести збереження/завантаження
│   └── test_html_generator.py # Тести генерації HTML
├── PLAN.md                 # Цей файл
└── README.md               # Документація проекту
```

---

## 🏗️ Архітектура класів

### UML-діаграма (спрощена)

```
┌─────────────────────────────────────────────────────────────────┐
│                           «enum»                                │
│                         RoomStatus                              │
├─────────────────────────────────────────────────────────────────┤
│ FREE, OCCUPIED, RESERVED                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      «abstract» Room                            │
├─────────────────────────────────────────────────────────────────┤
│ - room_number: int                                              │
│ - price_per_night: float                                        │
│ - status: RoomStatus                                            │
│ - current_guest: Guest | None                                   │
├─────────────────────────────────────────────────────────────────┤
│ + check_in(guest: Guest) -> None                                │
│ + check_out() -> None                                           │
│ + get_info() -> str  «abstract»                                 │
│ + to_dict() -> dict                                             │
│ + from_dict(data: dict) -> Room  «classmethod»                  │
│ + __eq__(other) -> bool                                         │
│ + __repr__() -> str                                             │
└─────────────────────────────────────────────────────────────────┘
              △
              │
    ┌─────────┼─────────┐
    │         │         │
┌───┴───┐ ┌───┴───┐ ┌───┴───┐
│Standard│ │Deluxe │ │ Suite │
│ Room   │ │ Room  │ │       │
└────────┘ └───────┘ └───────┘

┌─────────────────────────────────────────────────────────────────┐
│                           Guest                                 │
├─────────────────────────────────────────────────────────────────┤
│ - name: str                                                     │
│ - passport: str                                                 │
│ - contact: str                                                  │
│ - loyalty_points: int                                           │
│ - stay_history: list[Booking]                                   │
├─────────────────────────────────────────────────────────────────┤
│ + add_loyalty_points(points: int) -> None                       │
│ + get_discount() -> float                                       │
│ + to_dict() -> dict                                             │
│ + from_dict(data: dict) -> Guest  «classmethod»                 │
│ + __repr__() -> str                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          Booking                                │
├─────────────────────────────────────────────────────────────────┤
│ - booking_id: str                                               │
│ - guest: Guest                                                  │
│ - room: Room                                                    │
│ - check_in_date: date                                           │
│ - nights: int                                                   │
│ - discount: float                                               │
│ - status: BookingStatus                                         │
├─────────────────────────────────────────────────────────────────┤
│ + total_cost() -> float                                         │
│ + check_out_date() -> date                                      │
│ + to_dict() -> dict                                             │
│ + from_dict(data: dict) -> Booking  «classmethod»               │
│ + __repr__() -> str                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           Hotel                                 │
├─────────────────────────────────────────────────────────────────┤
│ - name: str                                                     │
│ - description: str                                              │
│ - address: str                                                  │
│ - phone: str                                                    │
│ - email: str                                                    │
│ - rooms: list[Room]                                             │
│ - bookings: list[Booking]                                       │
│ - guests: list[Guest]                                           │
│ - total_revenue: float                                          │
├─────────────────────────────────────────────────────────────────┤
│ + add_room(room: Room) -> None                                  │
│ + find_available(room_type: type, check_in: date,               │
│                  check_out: date) -> list[Room]                 │
│ + book(guest, room, check_in_date, nights) -> Booking           │
│ + check_in_guest(booking: Booking) -> None                      │
│ + check_out_guest(booking: Booking) -> None                     │
│ + get_revenue_report() -> dict                                  │
│ + save(filepath: str) -> None                                   │
│ + load(filepath: str) -> Hotel  «classmethod»                   │
│ + generate_html_card(filepath: str) -> None                     │
│ + __len__() -> int                                              │
│ + __str__() -> str                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        HotelChain                               │
├─────────────────────────────────────────────────────────────────┤
│ - name: str                                                     │
│ - description: str                                              │
│ - hotels: dict[str, Hotel]                                      │
│ - guests: dict[str, Guest]  # спільна база (passport -> Guest)  │
├─────────────────────────────────────────────────────────────────┤
│ + add_hotel(hotel: Hotel) -> None                               │
│ + remove_hotel(hotel_id: str) -> None                           │
│ + get_hotel(hotel_id: str) -> Hotel                             │
│ + register_guest(guest: Guest) -> None                          │
│ + get_guest(passport: str) -> Guest                             │
│ + find_available_all(room_type, check_in, check_out) -> dict    │
│ + get_total_revenue() -> float                                  │
│ + get_chain_report() -> dict                                    │
│ + save(dirpath: str) -> None                                    │
│ + load(dirpath: str) -> HotelChain  «classmethod»               │
│ + generate_html_card(filepath: str) -> None                     │
│ + __len__() -> int                                              │
│ + __iter__() -> Iterator[Hotel]                                 │
│ + __getitem__(hotel_id: str) -> Hotel                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Ітерації розробки

### Ітерація 1: Базова структура (MVP)
**Мета:** Створити основні класи та базовий функціонал

#### Завдання:
- [ ] Створити структуру папок проекту
- [ ] Реалізувати `RoomStatus` enum
- [ ] Реалізувати абстрактний клас `Room`
- [ ] Реалізувати конкретні класи номерів (`StandardRoom`, `DeluxeRoom`, `Suite`)
- [ ] Реалізувати клас `Guest`
- [ ] Додати базову валідацію

#### 🧪 Unit-тести (Ітерація 1):
- [ ] `test_room_creation` — створення номерів з коректними параметрами
- [ ] `test_room_invalid_number` — помилка при некоректному номері (≤0)
- [ ] `test_room_invalid_price` — помилка при некоректній ціні (≤0)
- [ ] `test_room_check_in` — успішне заселення гостя
- [ ] `test_room_check_in_occupied` — помилка при заселенні в зайнятий номер
- [ ] `test_room_check_out` — успішне виселення
- [ ] `test_room_equality` — порівняння номерів за `room_number`
- [ ] `test_guest_creation` — створення гостя з коректними даними
- [ ] `test_guest_invalid_passport` — помилка при порожньому паспорті
- [ ] `test_room_status_enum` — перевірка значень enum

#### Очікуваний результат:
```python
room = StandardRoom(101)
guest = Guest("Іван Петренко", "AA123456", "+380501234567")
room.check_in(guest)
print(room.get_info())
```

---

### Ітерація 2: Бронювання
**Мета:** Додати систему бронювань

#### Завдання:
- [ ] Реалізувати клас `Booking`
- [ ] Додати метод `total_cost()`
- [ ] Додати `__repr__` для відлагодження
- [ ] Валідація: кількість ночей >= 1

#### 🧪 Unit-тести (Ітерація 2):
- [ ] `test_booking_creation` — створення бронювання з коректними даними
- [ ] `test_booking_invalid_nights` — помилка при nights < 1
- [ ] `test_booking_total_cost` — правильний розрахунок вартості
- [ ] `test_booking_total_cost_with_discount` — розрахунок зі знижкою
- [ ] `test_booking_check_out_date` — правильна дата виїзду
- [ ] `test_booking_repr` — коректний `__repr__` вивід

#### Очікуваний результат:
```python
booking = Booking(guest, room, date(2026, 4, 10), nights=3)
print(booking.total_cost())  # Ціна номера * 3
print(repr(booking))  # Зручний вивід для debug
```

---

### Ітерація 3: Готель
**Мета:** Об'єднати все в клас Hotel

#### Завдання:
- [ ] Реалізувати клас `Hotel`
- [ ] Метод `find_available(room_type, check_in, check_out)` — пошук вільних номерів на діапазон дат
- [ ] Метод `book(guest, room, nights)` — бронювання
- [ ] Магічний метод `__len__` — кількість номерів
- [ ] Магічний метод `__str__` — інформація про готель
- [ ] Облік доходів

#### 🧪 Unit-тести (Ітерація 3):
- [ ] `test_hotel_creation` — створення готелю
- [ ] `test_hotel_add_room` — додавання номерів
- [ ] `test_hotel_add_duplicate_room` — помилка при дублюванні номера
- [ ] `test_hotel_find_available_by_type` — пошук вільних номерів за типом
- [ ] `test_hotel_find_available_by_dates` — пошук на конкретний діапазон дат
- [ ] `test_hotel_find_available_overlap` — номер зайнятий, якщо дати перетинаються
- [ ] `test_hotel_find_available_adjacent` — номер вільний, якщо дати не перетинаються
- [ ] `test_hotel_find_available_none` — порожній список якщо немає вільних
- [ ] `test_hotel_book` — успішне бронювання
- [ ] `test_hotel_book_unavailable` — помилка бронювання зайнятого номера
- [ ] `test_hotel_check_in_guest` — заселення за бронюванням
- [ ] `test_hotel_check_out_guest` — виселення та оновлення доходів
- [ ] `test_hotel_len` — `__len__` повертає кількість номерів
- [ ] `test_hotel_str` — `__str__` повертає правильний опис

#### Очікуваний результат:
```python
hotel = Hotel("Grand Hotel")
hotel.add_room(StandardRoom(101))
hotel.add_room(DeluxeRoom(201))

# Пошук вільних номерів на конкретні дати
check_in = date(2026, 4, 15)
check_out = date(2026, 4, 18)
available = hotel.find_available(StandardRoom, check_in, check_out)

booking = hotel.book(guest, available[0], check_in, nights=3)

print(len(hotel))  # 2
print(hotel)  # "Grand Hotel: 1 вільних номерів з 2"
```

---

### Ітерація 4: Мережа готелів (HotelChain)
**Мета:** Підтримка декількох готелів в одній системі

#### Завдання:
- [ ] Реалізувати клас `HotelChain`
- [ ] Спільна база гостей для всієї мережі
- [ ] Пошук вільних номерів по всій мережі
- [ ] Агрегований звіт по всіх готелях
- [ ] Магічні методи: `__len__`, `__iter__`, `__getitem__`

#### 🧪 Unit-тести (Ітерація 4):
- [ ] `test_chain_creation` — створення мережі готелів
- [ ] `test_chain_add_hotel` — додавання готелю до мережі
- [ ] `test_chain_remove_hotel` — видалення готелю з мережі
- [ ] `test_chain_get_hotel` — отримання готелю за ID
- [ ] `test_chain_duplicate_hotel` — помилка при дублюванні ID готелю
- [ ] `test_chain_register_guest` — реєстрація гостя в мережі
- [ ] `test_chain_shared_guest` — гість доступний у всіх готелях мережі
- [ ] `test_chain_find_available_all` — пошук вільних номерів по всій мережі
- [ ] `test_chain_total_revenue` — загальний дохід мережі
- [ ] `test_chain_len` — `__len__` повертає кількість готелів
- [ ] `test_chain_iter` — `__iter__` для ітерації по готелях
- [ ] `test_chain_getitem` — `__getitem__` доступ за ID

#### Очікуваний результат:
```python
# Створення мережі
chain = HotelChain("Grand Hotels Ukraine")

# Додавання готелів
hotel_kyiv = Hotel("Grand Hotel Kyiv", hotel_id="kyiv")
hotel_lviv = Hotel("Grand Hotel Lviv", hotel_id="lviv")

chain.add_hotel(hotel_kyiv)
chain.add_hotel(hotel_lviv)

# Спільна база гостей
guest = Guest("Олена Коваленко", "AA123456", "+380501234567")
chain.register_guest(guest)

# Пошук по всій мережі
check_in = date(2026, 4, 15)
check_out = date(2026, 4, 18)
available = chain.find_available_all(DeluxeRoom, check_in, check_out)
# {
#   'kyiv': [Room 201, Room 202],
#   'lviv': [Room 201]
# }

# Бронювання в конкретному готелі
chain['kyiv'].book(guest, available['kyiv'][0], check_in, nights=3)

# Звіт по всій мережі
print(chain.get_chain_report())
# {
#   'total_revenue': 125000.0,
#   'total_bookings': 45,
#   'hotels': {
#     'kyiv': {'revenue': 80000.0, 'bookings': 30},
#     'lviv': {'revenue': 45000.0, 'bookings': 15}
#   }
# }

print(len(chain))  # 2 готелі
for hotel in chain:
    print(hotel.name)
```

---

### Ітерація 5: Система лояльності
**Мета:** Додати знижки та бонуси для постійних клієнтів

#### Завдання:
- [ ] Додати `loyalty_points` до `Guest`
- [ ] Реалізувати систему нарахування балів (1 грн = 1 бал)
- [ ] Рівні лояльності:
  - 🥉 Bronze (0-999 балів) — 0% знижка
  - 🥈 Silver (1000-4999 балів) — 5% знижка
  - 🥇 Gold (5000-9999 балів) — 10% знижка
  - 💎 Platinum (10000+ балів) — 15% знижка
- [ ] Застосування знижки при бронюванні

#### 🧪 Unit-тести (Ітерація 5):
- [ ] `test_guest_initial_loyalty_points` — 0 балів при створенні
- [ ] `test_guest_add_loyalty_points` — додавання балів
- [ ] `test_guest_loyalty_bronze` — 0% знижка (0-999 балів)
- [ ] `test_guest_loyalty_silver` — 5% знижка (1000-4999 балів)
- [ ] `test_guest_loyalty_gold` — 10% знижка (5000-9999 балів)
- [ ] `test_guest_loyalty_platinum` — 15% знижка (10000+ балів)
- [ ] `test_booking_applies_discount` — знижка застосовується при бронюванні
- [ ] `test_loyalty_points_after_checkout` — бали нараховуються після виселення

#### Очікуваний результат:
```python
guest.add_loyalty_points(5000)
print(guest.get_discount())  # 0.10 (10%)
booking = hotel.book(guest, room, date.today(), 2)
# Знижка автоматично застосована
```

---

### Ітерація 6: Історія та звіти
**Мета:** Додати аналітику та історію

#### Завдання:
- [ ] Історія перебувань гостя (`stay_history`)
- [ ] Звіт про доходи готелю
- [ ] Звіт про завантаженість номерів
- [ ] Експорт звітів

#### 🧪 Unit-тести (Ітерація 6):
- [ ] `test_guest_stay_history_empty` — порожня історія при створенні
- [ ] `test_guest_stay_history_add` — додавання до історії після checkout
- [ ] `test_hotel_revenue_report` — правильний звіт про доходи
- [ ] `test_hotel_occupancy_rate` — розрахунок завантаженості
- [ ] `test_hotel_average_stay` — середня тривалість перебування
- [ ] `test_report_export` — експорт звіту в dict/JSON

#### Очікуваний результат:
```python
report = hotel.get_revenue_report()
# {
#   'total_revenue': 15000.0,
#   'bookings_count': 10,
#   'average_stay': 2.5,
#   'occupancy_rate': 0.75
# }
```

---

### Ітерація 7: Збереження даних (Store)
**Мета:** Зберігати стан системи у JSON файлах

#### Завдання:
- [ ] Додати методи `to_dict()` / `from_dict()` до всіх моделей
- [ ] Реалізувати сервіс `StoreService` для роботи з файлами
- [ ] Підтримка збереження мережі готелів (HotelChain)
- [ ] Автоматичне збереження при змінах (опціонально)
- [ ] Створити директорію `data/` для файлів

#### 📁 Структура JSON файлів:

**chain.json** (мережа готелів):
```json
{
  "name": "Grand Hotels Ukraine",
  "description": "Найкраща мережа готелів України",
  "hotels": ["kyiv", "lviv"]
}
```

**hotels/hotel_kyiv.json** (окремий готель):
```json
{
  "hotel_id": "kyiv",
  "name": "Grand Hotel Kyiv",
  "description": "Розкішний готель у серці столиці",
  "address": "вул. Хрещатик, 1, Київ",
  "phone": "+380 44 123 4567",
  "email": "kyiv@grandhotels.ua",
  "total_revenue": 45000.0,
  "rooms": [
    {"type": "StandardRoom", "room_number": 101, "status": "FREE"},
    {"type": "DeluxeRoom", "room_number": 201, "status": "OCCUPIED"}
  ]
}
```

**guests.json** (спільна база гостей):
```json
[
  {
    "passport": "AA123456",
    "name": "Олена Коваленко",
    "contact": "+380501234567",
    "loyalty_points": 2500
  }
]
```

**bookings.json**:
```json
[
  {
    "booking_id": "BK-2026-001",
    "hotel_id": "kyiv",
    "guest_passport": "AA123456",
    "room_number": 201,
    "check_in_date": "2026-04-15",
    "nights": 3,
    "discount": 0.05,
    "status": "CONFIRMED"
  }
]
```

#### 🧪 Unit-тести (Ітерація 7):
- [ ] `test_room_to_dict` — серіалізація номера в dict
- [ ] `test_room_from_dict` — десеріалізація номера з dict
- [ ] `test_guest_to_dict` — серіалізація гостя
- [ ] `test_guest_from_dict` — десеріалізація гостя
- [ ] `test_booking_to_dict` — серіалізація бронювання
- [ ] `test_booking_from_dict` — десеріалізація бронювання
- [ ] `test_hotel_save` — збереження готелю у файл
- [ ] `test_hotel_load` — завантаження готелю з файлу
- [ ] `test_chain_save` — збереження мережі готелів
- [ ] `test_chain_load` — завантаження мережі готелів
- [ ] `test_chain_load_with_hotels` — завантаження мережі з усіма готелями
- [ ] `test_store_data_integrity` — дані не втрачаються після save/load
- [ ] `test_store_file_not_found` — коректна обробка відсутнього файлу
- [ ] `test_store_corrupted_json` — обробка пошкодженого JSON

#### Очікуваний результат:
```python
# Збереження окремого готелю
hotel.save("data/hotels/hotel_kyiv.json")

# Завантаження окремого готелю
hotel = Hotel.load("data/hotels/hotel_kyiv.json")

# Збереження мережі готелів
chain.save("data/")
# Створює:
#   data/chain.json
#   data/hotels/hotel_kyiv.json
#   data/hotels/hotel_lviv.json
#   data/guests.json
#   data/bookings.json

# Завантаження мережі готелів
chain = HotelChain.load("data/")

# Або через сервіс
from services.store import StoreService

store = StoreService("data/")
store.save_chain(chain)
chain = store.load_chain()
```

---

### Ітерація 8: HTML-візитівка готелю та мережі
**Мета:** Генерувати красиві HTML-сторінки з інформацією про готель та мережу

#### Завдання:
- [ ] Додати поля `description`, `address`, `phone`, `email` до `Hotel`
- [ ] Створити HTML-шаблон візитівки готелю
- [ ] Створити HTML-шаблон візитівки мережі (з посиланнями на готелі)
- [ ] Реалізувати `HtmlGenerator` сервіс
- [ ] Метод `generate_html_card()` в класі `Hotel`
- [ ] Метод `generate_html_card()` в класі `HotelChain`
- [ ] Підтримка CSS стилів (вбудовані або окремий файл)

#### 📄 Що містить візитівка:
- 🏨 Назва готелю
- 📝 Опис готелю
- 📍 Адреса
- 📞 Контакти (телефон, email)
- 🛏️ Список типів номерів з описом та цінами
- 🏷️ Зручності кожного типу номера
- 📊 Статистика (кількість номерів кожного типу)

#### 🎨 Приклад HTML-структури:
```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Grand Hotel Kyiv</title>
    <style>
        /* Вбудовані стилі */
    </style>
</head>
<body>
    <header>
        <h1>🏨 Grand Hotel Kyiv</h1>
        <p class="description">Розкішний готель у серці Києва...</p>
    </header>
    
    <section class="contacts">
        <p>📍 вул. Хрещатик, 1, Київ</p>
        <p>📞 +380 44 123 4567</p>
        <p>✉️ info@grandhotel.ua</p>
    </section>
    
    <section class="rooms">
        <h2>Наші номери</h2>
        
        <div class="room-card">
            <h3>Standard Room</h3>
            <p class="price">800 грн/ніч</p>
            <ul class="amenities">
                <li>Wi-Fi</li>
                <li>TV</li>
            </ul>
            <p>Доступно: 5 номерів</p>
        </div>
        
        <!-- Інші типи номерів -->
    </section>
    
    <footer>
        <p>© 2026 Grand Hotel Kyiv</p>
    </footer>
</body>
</html>
```

#### 🧪 Unit-тести (Ітерація 8):
- [ ] `test_html_generator_creates_file` — файл створюється
- [ ] `test_html_generator_contains_hotel_name` — назва готелю присутня
- [ ] `test_html_generator_contains_description` — опис присутній
- [ ] `test_html_generator_contains_contacts` — контакти присутні
- [ ] `test_html_generator_contains_rooms` — інформація про номери
- [ ] `test_html_generator_room_prices` — ціни номерів коректні
- [ ] `test_html_generator_valid_html` — HTML валідний
- [ ] `test_html_generator_custom_template` — підтримка кастомного шаблону
- [ ] `test_html_chain_card_creates_file` — візитівка мережі створюється
- [ ] `test_html_chain_card_contains_hotels` — список готелів присутній
- [ ] `test_html_chain_card_links_to_hotels` — посилання на візитівки готелів
- [ ] `test_html_generate_all` — генерація візитівок для всієї мережі

#### Очікуваний результат:
```python
hotel = Hotel(
    name="Grand Hotel Kyiv",
    description="Розкішний готель у серці столиці",
    address="вул. Хрещатик, 1, Київ",
    phone="+380 44 123 4567",
    email="info@grandhotel.ua"
)

# Додаємо номери...
hotel.add_room(StandardRoom(101))
hotel.add_room(DeluxeRoom(201))
hotel.add_room(Suite(301))

# Генеруємо візитівку
hotel.generate_html_card("output/hotel_card.html")

# Або через сервіс з кастомним шаблоном
from services.html_generator import HtmlGenerator

generator = HtmlGenerator(template_path="templates/custom.html")
generator.generate(hotel, "output/hotel_card.html")

# Генерація візитівки мережі
chain.generate_html_card("output/chain_card.html")

# Генерація всіх візитівок (мережа + всі готелі)
from services.html_generator import HtmlGenerator

generator = HtmlGenerator()
generator.generate_all(chain, "output/")
# Створює:
#   output/chain_card.html
#   output/hotels/hotel_kyiv.html
#   output/hotels/hotel_lviv.html
```

---

### Ітерація 9: Інтеграційні тести та рефакторинг
**Мета:** Перевірити взаємодію компонентів, покращити код

#### Завдання:
- [ ] Інтеграційні тести (повний цикл бронювання)
- [ ] Тести граничних випадків (edge cases)
- [ ] Рефакторинг за результатами тестів
- [ ] Документація (docstrings)
- [ ] Перевірка покриття коду тестами (coverage ≥ 80%)

#### 🧪 Інтеграційні тести (Ітерація 9):
- [ ] `test_full_booking_cycle` — повний цикл: створення → бронювання → заселення → виселення
- [ ] `test_multiple_guests_same_room` — декілька гостей по черзі в одному номері
- [ ] `test_concurrent_bookings` — кілька бронювань одночасно
- [ ] `test_loyalty_accumulation` — накопичення балів за кілька перебувань
- [ ] `test_hotel_with_many_rooms` — готель з 100+ номерами
- [ ] `test_edge_case_checkout_without_checkin` — виселення без заселення

---

### Ітерація 10 (бонусна): Додатковий функціонал
**Мета:** Розширити можливості системи

#### Можливі покращення:
- [ ] Пошук номерів за ціною/датою
- [ ] Скасування бронювання (з штрафом)
- [ ] Раннє заселення / пізній виїзд
- [ ] Додаткові послуги (сніданок, SPA, трансфер)
- [ ] Резервне копіювання даних (backup)
- [ ] CLI інтерфейс для роботи з системою

---

## 📋 Специфікація класів

### RoomStatus (Enum)
| Значення | Опис |
|----------|------|
| `FREE` | Номер вільний |
| `OCCUPIED` | Номер зайнятий |
| `RESERVED` | Номер заброньований |

### Типи номерів та ціни
| Тип | Базова ціна/ніч | Зручності |
|-----|-----------------|-----------|
| `StandardRoom` | 800 грн | Wi-Fi, TV |
| `DeluxeRoom` | 1500 грн | Wi-Fi, TV, Міні-бар, Балкон |
| `Suite` | 3000 грн | Wi-Fi, TV, Міні-бар, Балкон, Джакузі, Вітальня |

### Валідація
| Поле | Правило |
|------|---------|
| `room_number` | int > 0 |
| `price_per_night` | float > 0 |
| `nights` | int >= 1 |
| `passport` | непорожній рядок |
| `name` | непорожній рядок |

---

## 🚀 Швидкий старт

Після завершення всіх ітерацій:

```python
from models import HotelChain, Hotel, Guest, StandardRoom, DeluxeRoom, Suite
from datetime import date

# Створення мережі готелів
chain = HotelChain("Grand Hotels Ukraine", "Найкраща мережа готелів")

# Створення готелів
hotel_kyiv = Hotel(
    name="Grand Hotel Kyiv",
    hotel_id="kyiv",
    description="Розкішний готель у серці столиці",
    address="вул. Хрещатик, 1, Київ",
    phone="+380 44 123 4567",
    email="kyiv@grandhotels.ua"
)

hotel_lviv = Hotel(
    name="Grand Hotel Lviv", 
    hotel_id="lviv",
    description="Затишний готель у центрі Львова",
    address="пл. Ринок, 1, Львів",
    phone="+380 32 123 4567",
    email="lviv@grandhotels.ua"
)

# Додавання номерів
hotel_kyiv.add_room(StandardRoom(101))
hotel_kyiv.add_room(StandardRoom(102))
hotel_kyiv.add_room(DeluxeRoom(201))
hotel_kyiv.add_room(Suite(301))

hotel_lviv.add_room(StandardRoom(101))
hotel_lviv.add_room(DeluxeRoom(201))

# Додавання готелів до мережі
chain.add_hotel(hotel_kyiv)
chain.add_hotel(hotel_lviv)

# Реєстрація гостя (спільна база)
guest = Guest("Олена Коваленко", "АА123456", "+380501234567")
chain.register_guest(guest)

# Пошук вільних номерів по всій мережі
check_in = date(2026, 4, 15)
check_out = date(2026, 4, 18)
available = chain.find_available_all(DeluxeRoom, check_in, check_out)
# {'kyiv': [Room 201], 'lviv': [Room 201]}

# Бронювання в конкретному готелі
booking = chain['kyiv'].book(guest, available['kyiv'][0], check_in, nights=3)
print(f"Заброньовано! Вартість: {booking.total_cost()} грн")

# Заселення та виселення
chain['kyiv'].check_in_guest(booking)
chain['kyiv'].check_out_guest(booking)

# Звіт по всій мережі
print(chain.get_chain_report())

# Збереження даних
chain.save("data/")

# Завантаження даних (при наступному запуску)
chain = HotelChain.load("data/")
# Автоматично завантажує:
#   - chain.json (налаштування мережі)
#   - hotels/*.json (всі готелі)
#   - guests.json (спільна база гостей)
#   - bookings.json (всі бронювання)

# Генерація HTML-візитівок
chain.generate_html_card("output/chain_card.html")
```

---

## ✅ Критерії готовності

- [ ] Всі класи реалізовані згідно специфікації
- [ ] Підтримка мережі готелів (HotelChain)
- [ ] Магічні методи (`__eq__`, `__len__`, `__str__`, `__repr__`, `__iter__`, `__getitem__`) працюють коректно
- [ ] Валідація працює для всіх вхідних даних
- [ ] Система лояльності нараховує бали та знижки
- [ ] Збереження/завантаження даних у JSON (окремі готелі та мережа)
- [ ] Генерація HTML-візитівок (готель та мережа)
- [ ] Тести покривають основний функціонал (coverage ≥ 80%)
- [ ] Код задокументований

---

*Останнє оновлення: 09.04.2026*
