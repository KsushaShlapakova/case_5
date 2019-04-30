import datetime
from dateutil.relativedelta import relativedelta
import random


class Room:
    food = {'без питания': 0.00, 'завтрак': 280.00, 'полупансион': 1000.00}
    price_ = {'одноместный': 2900.00, 'двухместный': 2300.00, 'люкс': 4100.00, 'полулюкс': 3200.00}
    grow_price = {'стандарт': 1.0, 'стандарт_улучшенный': 1.2, 'апартамент': 1.5}

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

    def price(self, budget, discount):
        food = {'без питания': 0., 'завтрак': 280., 'полупансион': 1000.}
        price_ = {'одноместный': 2900., 'двухместный': 2300., 'люкс': 4100., 'полулюкс': 3200.}
        grow_price = {'стандарт': 1., 'стандарт_улучшенный': 1.2, 'апартамент': 1.5}

        p = price_[self.type_] * grow_price[self.comfort] * discount

        if p > budget:
            return -1

        n = budget - p
        self.food_price = 0
        self.food_type = list(food.keys())[list(food.values()).index(0.)]

        for i in food:
            if n >= food[i]:
                self.food_price = food[i]
                self.food_type = i
        p += self.food_price

        return p  # макс цена по бюджету клиента

    def reserve(self, date, days):
        date = date.split('.')

        self.date_year = int(date[2])
        self.date_month = int(date[1])
        self.date_day = int(date[0])

        d = datetime.date(self.date_year, self.date_month, self.date_day) + relativedelta(days=+(days-1))

        a = str(d).split('-')

        self.date_year = int(a[0])
        self.date_month = int(a[1])
        self.date_day = int(a[2])

    def check_reserve(self, date):

        d = date.split('.')
        date_year = int(d[2])
        date_month = int(d[1])
        date_day = int(d[0])

        if self.date_year == None:
            self.reserve(date, 0)

        d1 = datetime.date(date_year, date_month, date_day)  # дата бронирования
        d2 = datetime.date(self.date_year, self.date_month, self.date_day)  # дата освобождения

        if d1 >= d2:
            return True  # номер свободен
        return False


class Hotel:
    def __init__(self, text):
        self.text = text
        self.room_with_price = []
        self.rooms = [Room(i.rstrip('\n')) for i in text]  # список всех комнат
        self.max_people = max([x.person for x in self.rooms])  # спиок вмещаемости каждой комнаты
        self.profit = 0
        self.lose = 0

        self.ones = len([x for x in self.rooms if x.type_ == 'одноместный'])
        self.twos = len([x for x in self.rooms if x.type_ == 'двухместный'])
        self.lux = len([x for x in self.rooms if x.type_ == 'люкс'])
        self.half_lux = len([x for x in self.rooms if x.type_ == 'полулюкс'])

    @staticmethod
    def agree():
        a = random.randint(1, 100)
        if a >= 25:
            return True  # 'Клиент согласен. Номер забронирован.\n'
        else:
            return False  # 'Клиент отказался от варианта.\n'

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
                m = i.price(budget, discount)

                if m == -1:
                    continue

                rooms.append((m, i))
            rooms.sort(key=lambda tup: tup[0])
            if rooms:
                return rooms[-1]
        return None

    def bookings(self, file='booking.txt'):

        with open('booking.txt', encoding='utf8') as f:
            text = f.readlines()
            current_date = ''

            for i, k in enumerate(text):
                j = k.split()  # 01.03.2018 Аксёнов Лаврентий Семенович 3 03.03.2018 2 4600
                date_reserve = j[0]
                name = j[1] + ' ' + j[2] + ' ' + j[3]
                amount_people = int(j[4])
                date_in = j[5]
                days = int(j[6])
                budget = int(j[7])

                if not current_date:
                    current_date = date_reserve

                if current_date != date_reserve or i == (len(text) - 1):
                    print('='*50, '\nИтог за', current_date, '\n')
                    self.print_status(current_date)
                    self.profit = 0
                    self.lose = 0
                    current_date = date_reserve

                print('-'*50, '\nПоступила заявка на бронирование:\n', k)

                ret = self.find_room(amount_people, date_in, budget)
                if ret:
                    r = ret[1]
                    current_price = ret[0] * amount_people
                    print('Найден:\n')
                    print('номер', r.number, r.type_, r.comfort, 'рассчитан на',
                          r.person, 'чел. фактически', amount_people, 'чел.',
                          r.food_type, 'стоимость', current_price, 'руб./сутки\n')
                    if self.agree():
                        r.reserve(date_in, days)
                        self.profit += current_price
                        print('Клиент согласен. Номер забронирован.\n')
                    else:
                        self.lose += current_price
                        print('Клиент отказался от варианта.\n')
                else:
                    self.lose += (budget * amount_people)
                    print('Предложений по данному запросу нет. В бронировании отказано.\n')

    def reserved_rooms(self, date):
        r = []
        for i in self.rooms:
            if not i.check_reserve(date):
                r.append(i)
        return r

    def print_status(self, date):
        r = self.reserved_rooms(date)
        o = len([x for x in r if x.type_ == 'одноместный'])
        d = len([x for x in r if x.type_ == 'двухместный'])
        p = len([x for x in r if x.type_ == 'полулюкс'])
        l = len([x for x in r if x.type_ == 'люкс'])
        percent = len(r) * 100 / len(self.rooms)

        print('Количество занятых номеров:', len(r), '\n')
        print('Количество свободных номеров:', len(self.rooms) - len(r), '\n')
        print('Занятость по категориям:\n')
        print('Одноместных:', o, 'из', self.ones)
        print('Двухместных:', d, 'из', self.twos)
        print('Полулюкс:', p, 'из', self.half_lux)
        print('Люкс:', l, 'из', self.lux)
        print('Процент загруженности гостиницы:', percent, '%')
        print('Доход за день:', self.profit, 'руб.')
        print('Упущенный доход: ', self.lose, 'руб.\n')
