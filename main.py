from hotel import *
with open('fund.txt', encoding='utf8') as f:
    text = f.readlines()
    hotel = Hotel(text)
    model = hotel.bookings()
    print(model)
