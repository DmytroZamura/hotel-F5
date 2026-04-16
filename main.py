from models.enums import RoomStatus
from models.guest import Guest

if __name__ == '__main__':
    g = Guest("Данило", "BB222", "ddd@gmail.com", "+380501234567")

    g.add_loyalty_points(100)

    print(g.discount_percent)
    
    print(RoomStatus(RoomStatus.FREE).name)
    print(RoomStatus(RoomStatus.FREE).value)
