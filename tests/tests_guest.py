from unittest import TestCase

from models.guest import Guest


class TestGuest(TestCase):
    """Тестування класу Guest"""

    def setUp(self) -> None:
        self.base_dict = {
            "name": "Василь Петренко",
            "passport": "AB123456",
            "email": "v.p@gmail.com",
            "phone_number": "+380505050530",
        }

    def test_guest(self):
        """Тестування створення екземпляра класу Guest"""

        guest = Guest(**self.base_dict)

        self.assertEqual(guest.name, self.base_dict["name"])
        self.assertEqual(guest.email, self.base_dict["email"])
        self.assertEqual(guest.phone_number, self.base_dict["phone_number"])
        self.assertEqual(guest.passport, self.base_dict["passport"])
        self.assertEqual(guest.loyalty_points, 0)
        self.assertEqual(guest.stay_history, [])

    def test_repr(self):
        """Тестування методу __repr__ класу Guest
        Перевіряємо що повертаються всі атрибути необхідні для створення класу Guest
        """
        guest = Guest(**self.base_dict)
        self.assertEqual(
            repr(guest),
            f"Guest(name='{self.base_dict['name']}', "
            f"passport='{self.base_dict['passport']}', "
            f"email='{self.base_dict['email']}', "
            f"phone_number='{self.base_dict['phone_number']}')"
        )

    def test_str(self):
        """Тестування методу __str__ класу Guest
        """
        guest = Guest(**self.base_dict)
        self.assertEqual(
            str(guest),
            f"Гість - ПІБ={self.base_dict['name']}, "
            f"email={self.base_dict['email']}, "
            f"номер телефону={self.base_dict['phone_number']}, "
            f"паспорт={self.base_dict['passport']}, "
            f"бали лояльності={guest.loyalty_points}"
        )

    def test_add_loyalty_points(self):
        """Тестування методу add_loyalty_points класу Guest
        Перевіряємо що бали лояльності додаються коректно
        """
        guest = Guest(**self.base_dict)
        guest.add_loyalty_points(100)
        self.assertEqual(guest.loyalty_points, 100)

        guest.add_loyalty_points(50)
        self.assertEqual(guest.loyalty_points, 150)

    def test_to_dict(self):
        """Тестування методу to_dict класу Guest"""
        guest = Guest(**self.base_dict)
        self.assertEqual(guest.to_dict(), {
            **self.base_dict,
            "loyalty_points": 0,
            "stay_history": [],
        })

    def test_from_dict(self):
        """Тестування методу from_dict класу Guest"""
        guest = Guest(**self.base_dict)
        new_dict = {
            **self.base_dict,
            "loyalty_points": 100,
            "name": "Петро Василенко",
        }

        guest.from_dict(new_dict)
        self.assertEqual(guest.name, new_dict["name"])


    def test_discount_percent(self):
        """Тестування властивості discount_percent класу Guest"""
        guest = Guest(**self.base_dict)

        self.assertEqual(guest.discount_percent, 0)

        guest.add_loyalty_points(100)
        self.assertEqual(guest.discount_percent, 5)

        guest.add_loyalty_points(400)
        self.assertEqual(guest.discount_percent, 10)

        guest.add_loyalty_points(500)
        self.assertEqual(guest.discount_percent, 15)


    def test_validate_name(self):
        """Тестування валідації імені гостя"""
        new_dict = {
            **self.base_dict,
            "name": ""
        }
        with self.assertRaises(ValueError) as context:
            Guest(**new_dict)

        self.assertEqual(str(context.exception), "Ім'я гостя не може бути порожнім")

    def test_validate_email(self):
        """Тестування валідації email гостя"""
        new_dict = {
            **self.base_dict,
            "email": "invalid_email"
        }
        with self.assertRaises(ValueError) as context:
            Guest(**new_dict)

        self.assertEqual(str(context.exception), "Невалідна email адреса")


    def test_validate_phone_number(self):
        """Тестування валідації номера телефона гостя"""
        new_dict = {
            **self.base_dict,
            "phone_number": "12345"
        }
        with self.assertRaises(ValueError) as context:
            Guest(**new_dict)

        self.assertEqual(str(context.exception), "Номер телефону має бути не менше 10 цифр")

    def test_validate_passport(self):
        """Тестування валідації номера паспорта гостя"""
        new_dict = {
            **self.base_dict,
            "passport": ""
        }
        with self.assertRaises(ValueError) as context:
            Guest(**new_dict)

        self.assertEqual(str(context.exception), "Номер паспорта не може бути порожнім")

    # --- Тести валідації типів ---

    def test_name_type_validation(self):
        """Ім'я має бути рядком — TypeError."""
        new_dict = {**self.base_dict, "name": 123}
        with self.assertRaises(TypeError):
            Guest(**new_dict)

    def test_passport_type_validation(self):
        """Паспорт має бути рядком — TypeError."""
        new_dict = {**self.base_dict, "passport": 123}
        with self.assertRaises(TypeError):
            Guest(**new_dict)

    def test_loyalty_points_negative(self):
        """Від'ємні бали лояльності — ValueError."""
        guest = Guest(**self.base_dict)
        with self.assertRaises(ValueError):
            guest.loyalty_points = -10

    def test_loyalty_points_type(self):
        """Бали лояльності мають бути int — ValueError."""
        guest = Guest(**self.base_dict)
        with self.assertRaises(ValueError):
            guest.loyalty_points = "сто"

    def test_setter_name_empty(self):
        """Зміна імені на порожній рядок через сетер — ValueError."""
        guest = Guest(**self.base_dict)
        with self.assertRaises(ValueError):
            guest.name = ""

    def test_setter_email_invalid(self):
        """Зміна email на невалідний через сетер — ValueError."""
        guest = Guest(**self.base_dict)
        with self.assertRaises(ValueError):
            guest.email = "bad_email"

    def test_setter_phone_short(self):
        """Зміна телефону на короткий через сетер — ValueError."""
        guest = Guest(**self.base_dict)
        with self.assertRaises(ValueError):
            guest.phone_number = "123"

