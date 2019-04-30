# Developers: Shlapakova 90%, Bateneva 60%, Zikova 40%.

from dateutil.relativedelta import relativedelta
import datetime
import random


class Room:
    def __init__(self, text):
        self.text = text
        i = text.rstrip('\n')
        i = i.split(' ')
        self.number = int(i[0])
        self.type_ = i[1]
        self.person = int(i[2])
        self.comfort = i[3]

        self.date_year = None
        self.date_month = None
        self.date_day = None

    def __str__(self):
        return '%s.%s.%s' % (str(self.date_year), str(self.date_month), str(self.date_day))

    def __price(self, budget, discount):
        food = {'без питания': 0.00, 'завтрак': 280.00, 'полупансион': 1000.00}
        price_ = {'одноместный': 2900.00, 'двухместный': 2300.00, 'люкс': 4100.00, 'полулюкс': 3200.00}
        grow_price = {'стандарт': 1.0, 'стандарт_улучшенный': 1.2, 'апартамент': 1.5}

        pay = price_[self.type_] * grow_price[self.comfort] * discount

        if pay > budget:
            return -1

        expenses = budget - pay
        self.food_price = 0
        self.food_type = list(food.keys())[list(food.values()).index(0.)]

        for i in food:
            if expenses >= food[i]:
                self.food_price = food[i]
                self.food_type = i
        pay += self.food_price

        return pay

    @property
    def price(self):
        return self.__price

    def reserve(self, date, days):
        date = date.split('.')

        self.date_year = int(date[2])
        self.date_month = int(date[1])
        self.date_day = int(date[0])

        entry = datetime.date(self.date_year, self.date_month, self.date_day) + relativedelta(days=+(days-1))

        a = str(entry).split('-')

        self.date_year = int(a[0])
        self.date_month = int(a[1])
        self.date_day = int(a[2])

    def check_reserve(self, date):
        arrival = date.split('.')
        date_year = int(arrival[2])
        date_month = int(arrival[1])
        date_day = int(arrival[0])

        if self.date_year is None:
            self.reserve(date, 0)

        reservation = datetime.date(date_year, date_month, date_day)
        exit_ = datetime.date(self.date_year, self.date_month, self.date_day)

        if reservation >= exit_:
            return True
        return False

    def __repr__(self):
        return self.__str__()


class Hotel:
    def __init__(self, text):
        self.text = text
        self.room_with_price = []
        self.rooms = [Room(i.rstrip('\n')) for i in text]
        self.max_people = max([x.person for x in self.rooms])
        self.profit = 0
        self.lose = 0

        self.ones = len([x for x in self.rooms if x.type_ == 'одноместный'])
        self.twos = len([x for x in self.rooms if x.type_ == 'двухместный'])
        self.lux = len([x for x in self.rooms if x.type_ == 'люкс'])
        self.half_lux = len([x for x in self.rooms if x.type_ == 'полулюкс'])

    def __str__(self):
        info = ''
        info += '\nНомера нашего отеля:\n'
        for i in self.text:
            info += i
        return info

    @staticmethod
    def agree():
        good = random.randint(1, 100)
        if good >= 25:
            return True
        else:
            return False

    def find_room(self, people, date, budget):
        for p in range(people, self.max_people + 1):
            rooms = []

            for i in self.rooms:
                if i.person != p:
                    continue

                if not i.check_reserve(date):
                    continue
                discount = 1.
                if p > people:
                    discount = .7
                mood = i.price(budget, discount)

                if mood == -1:
                    continue

                rooms.append((mood, i))
            rooms.sort(key=lambda tup: tup[0])
            if rooms:
                return rooms[-1]
        return None

    def bookings(self, file='booking.txt'):
        with open(file, encoding='utf8') as f:
            text = f.readlines()
            current_date = ''

            for i, k in enumerate(text):
                fio = k.split()
                date_reserve = fio[0]
                amount_people = int(fio[4])
                date_in = fio[5]
                days = int(fio[6])
                budget = int(fio[7])

                print('-'*105, '\nПоступила заявка на бронирование:\n', k)

                ret = self.find_room(amount_people, date_in, budget)
                if ret:
                    right = ret[1]
                    current_price = ret[0] * amount_people
                    print('Найден:\n')
                    print('номер', right.number, right.type_, right.comfort, 'рассчитан на',
                          right.person, 'чел. фактически', amount_people, 'чел.',
                          right.food_type, 'стоимость', float("{0:.1f}".format(current_price)), 'руб./сутки\n')
                    if self.agree():
                        right.reserve(date_in, days)
                        self.profit += current_price
                        print('Клиент согласен. Номер забронирован.\n')
                    else:
                        self.lose += current_price
                        print('Клиент отказался от варианта.\n')
                else:
                    self.lose += (budget * amount_people)
                    print('Предложений по данному запросу нет. В бронировании отказано.\n')

                if not current_date:
                    current_date = date_reserve

                if current_date != date_reserve or i == (len(text) - 1):
                    print('=' * 40, '\nИтог за', current_date, '\n')
                    self.print_status(current_date)
                    self.profit = 0
                    self.lose = 0
                    current_date = date_reserve

    def reserved_rooms(self, date):
        ring = []
        for i in self.rooms:
            if not i.check_reserve(date):
                ring.append(i)
        return ring

    def print_status(self, date):
        stockpile = self.reserved_rooms(date)
        one = len([x for x in stockpile if x.type_ == 'одноместный'])
        two = len([x for x in stockpile if x.type_ == 'двухместный'])
        plux = len([x for x in stockpile if x.type_ == 'полулюкс'])
        lux = len([x for x in stockpile if x.type_ == 'люкс'])
        percent = float("{0:.1f}".format(len(stockpile) * 100 / len(self.rooms)))

        print('Количество занятых номеров за всё время:', len(stockpile))
        print('Количество свободных номеров:', len(self.rooms) - len(stockpile), '\n')
        print('Занятость по категориям:\n')
        print('Одноместных:', one, 'из', self.ones)
        print('Двухместных:', two, 'из', self.twos)
        print('Полулюкс:', plux, 'из', self.half_lux)
        print('Люкс:', lux, 'из', self.lux)
        print('Процент загруженности гостиницы:', percent, '%')
        print('Доход за день:', self.profit, 'руб.')
        print('Упущенный доход: ', self.lose, 'руб.\n')
        print('=' * 40)

    def __repr__(self):
        return self.__str__()
