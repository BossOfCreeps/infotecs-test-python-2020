Реализованный сервер должен предоставлять REST API сервис со следующими методами:
1.	Метод принимает идентификатор geonameid и возвращает информацию о городе.
http://127.0.0.1:8000/city_info?geonameid=10232663
2.	Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией. http://127.0.0.1:8000/city_list_info?page=2
3.	Метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах, а также дополнительно: какой из них расположен севернее и одинаковая ли у них временная зона (когда несколько городов имеют одно и то же название, разрешать неоднозначность выбирая город с большим населением; если население совпадает, брать первый попавшийся)
http://127.0.0.1:8000/two_city?first=Томск&second=Москва
4. Реализовать метод, в котором пользователь вводит часть названия города и возвращает ему подсказку с возможными вариантами продолжений.
http://127.0.0.1:8000/helper?name=Том