"""Точка входу — демонстрація роботи системи управління готелем."""

from datetime import date, timedelta
from zoneinfo import available_timezones

from models import (
    HotelChain, Hotel, Guest,
    StandardRoom, DeluxeRoom, Suite, Booking,
)

import uuid

from services.html_generator import HtmlGenerator


def main() -> None:
    """Головна функція демонстрації."""
    #
    # room1 = StandardRoom(
    #     number=101,
    # )
    #
    # room2 = StandardRoom(102)
    #
    # room3 = DeluxeRoom(202)
    # room4 = Suite(203)
    #
    # guest1 = Guest(
    #     "Павло Тичина",
    #     "AAA333",
    #     "pt@gmail.com",
    #     "+390502023211",
    # )
    #
    # guest1.add_loyalty_points(1000)
    #
    guest2 = Guest(
        "Василь Перебійніс",
        "AХ34544",
        "vttt@gmail.com",
        "+390602023411"

    )
    #
    # hotel1 = Hotel("Готель Київ", hotel_id="kyiv", description="Найкращій готель Києва")
    # hotel1.add_room(room1)
    # hotel1.add_room(room2)
    # hotel1.add_room(room3)
    # hotel1.add_room(room4)
    #
    # hotel2 = Hotel("Готель Львів", hotel_id="lviv", description="Найкращій готель Львова")
    # hotel2.add_room(StandardRoom(101))
    # hotel2.add_room(StandardRoom(102))
    # hotel2.add_room(StandardRoom(103))
    # hotel2.add_room(DeluxeRoom(201))
    # hotel2.add_room(Suite(202))
    # hotel2.add_room(Suite(203))
    # hotel2.add_room(Suite(204))
    #
    # chain = HotelChain("Grand Hotels", "Найкраща мережа готелів України")
    # chain.add_hotel(hotel1)
    # chain.add_hotel(hotel2)
    #
    # available_rooms = chain.find_available_all(StandardRoom, date.today(), date.today() + timedelta(days=5))
    # booking = chain.hotels["kyiv"].book(guest1,available_rooms["kyiv"][0], date.today(), 5)
    # chain.hotels["kyiv"].check_in_guest(booking)


    chain = HotelChain.load("data")

    available_rooms = chain.find_available_all(StandardRoom, date.today(), date.today() + timedelta(days=5))
    booking = chain.hotels["kyiv"].book(guest2, available_rooms["kyiv"][0], date.today(), 5)
    chain.hotels["kyiv"].check_in_guest(booking)

    generator = HtmlGenerator("templates")
    generator.generate_all(chain, "output")



if __name__ == "__main__":
    main()
