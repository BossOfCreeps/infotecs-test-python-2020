from datetime import datetime
import pytz
from flask import Flask, request
import json

app = Flask(__name__)
FILE = list()

NAMES = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class", "feature code",
         "country code", "cc2", "admin1 code", "admin2 code", "admin3 code", "admin4 code", "population", "elevation",
         "dem", "timezone", "modification date"]


#  Метод принимает идентификатор geonameid и возвращает информацию о городе.
@app.route('/city_info')
def city_info():
    # получаем значение geonameid
    geonameid = request.args["geonameid"]  # получаем geonameid

    # ищем бинарным поиском строку, так как массив отсортирован
    mid = len(FILE) // 2
    low = 0
    high = len(FILE) - 1
    while FILE[mid][0] != geonameid and low <= high:
        if int(geonameid) > int(FILE[mid][0]):
            low = mid + 1
        else:
            high = mid - 1
        mid = (low + high) // 2

    # сочетаем зачения масисва и названия в словарь, преобразуем его в json и выводим
    result = dict()
    for i, name in enumerate(NAMES):
        if i == 18:
            result[name] = FILE[mid][i][:-1]
        else:
            result[name] = FILE[mid][i]
    return json.dumps(result, ensure_ascii=False)


# Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией.
@app.route('/city_list_info')
def city_list_info():
    page = int(request.args["page"])-1  # получаем значение страницы и вычитаем 1
    city_on_page = int(request.args["city_on_page"])
    result = list()
    for city in FILE[page*city_on_page:(page+1)*city_on_page]:  # проходим по всем городам в срезе
        # формируем для них словарь и доьбавлем его в список
        temp = dict()
        for i, name in enumerate(NAMES):
            if i == 18:
                temp[name] = city[i][:-1]
            else:
                temp[name] = city[i]
        result.append(temp)

    return json.dumps(result, ensure_ascii=False)


# Метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах, а также
# какой из них расположен севернее и одинаковая ли у них временная зона (когда несколько городов имеют одно и то же
# название, разрешать неоднозначность выбирая город с большим населением; если население совпадает, брать первый)
@app.route('/two_city')
def two_city():
    # получаем значения городов
    first = request.args["first"].capitalize()
    second = request.args["second"].capitalize()
    first_data = list()
    second_data = list()

    for record in FILE:  # проходим по всему массиву
        if first in record[3].split(","):  # если название среди вариантов
            if first_data:  # если уже что-то занесено
                if int(first_data[14]) < int(record[14]):  # если в новом варианте население больше
                    first_data = record  # обновляем значение
            else:  # если знаений не было
                first_data = record  # заносим значение
        if second in record[3].split(","):
            if second_data:
                if int(second_data[14]) < int(record[14]):
                    second_data = record
            else:
                second_data = record

    # сочетаем зачения масисва и названия в словарь, преобразуем его в json и выводим
    result = {first: dict(), second: dict(), "to_the_north": None, "timezone": None}
    for i, name in enumerate(NAMES):
        if i == 18:
            result[first][name] = first_data[i][:-1]
            result[second][name] = second_data[i][:-1]
        else:
            result[first][name] = first_data[i]
            result[second][name] = second_data[i]

    # смотрим кто севернее и заносим в данные на выдачу
    if result[first]["latitude"] > result[second]["latitude"]:
        result["to_the_north"] = first
    else:
        result["to_the_north"] = second

    # вычисляем +UTC
    first_tz = float(datetime.now(pytz.timezone(result[first]["timezone"])).utcoffset().total_seconds() / 3600)
    second_tz = float(datetime.now(pytz.timezone(result[second]["timezone"])).utcoffset().total_seconds() / 3600)
    # смотрим у кого больше и заносим в выдачу
    if first_tz > second_tz:
        result["timezone"] = "time in the first place is more than {} hours".format(first_tz - second_tz)
    elif second_tz > first_tz:
        result["timezone"] = "time in the second place is more than {} hours".format(second_tz - first_tz)
    else:
        result["timezone"] = "the time is the same"

    # выводим всё
    return json.dumps(result, ensure_ascii=False)


# Реализовать метод, в котором пользователь вводит часть названия города и возвращает ему подсказку с возможными
# вариантами продолжений.
@app.route('/helper')
def helper():
    name = request.args["name"].capitalize()  # получаем начало названия города
    data = list()
    for record in FILE:  # провходим по всему массиву
        for var in record[3].split(","):  # рассматриваем все варианты для записи
            if var.find(name) == 0:  # если вариант начинается с полученного значения
                data.append(var)  # добавляем в выдачу
    return ", ".join(data)  # выводим через запятую


if __name__ == '__main__':
    # считываем данные в переменную
    with open('RU.txt', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        FILE.append(line.split("\t"))
    # запускаем Flask
    app.run("127.0.0.1", 8000)
