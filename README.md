# Hammer Systems Test

Тестовое задание от компании Hammer Systems

## Описание API

* `/api/users/login/`  
[ POST ]  
{ 'phone': '+71234567890' }  
Считывание уже существующих кодов для генерации нового уникального кода на основе дерева префиксов. Добавление созданного кода в Redis с таймаутом, передача кода в RabbitMQ для отправки уведомления через сторонний сервис ([`services/phone_notification.py`](https://github.com/Vek123/hammer-s-test/blob/main/services/phone_notification.py)).

* `/api/users/login/confirm/`  
[ POST ]  
{ 'code': 1234 }  
Проверка на наличие кода в Redis, в случае успеха выполняется авторизация для пользователя с id, полученным в качестве значения из Redis.

* `/api/users/logout/`  
[ POST ]  
Выход из аккаунта.

* `/api/users/profile/`  
[ GET, PUT, PATCH ]  
{ 'claimed_invite_code': 123456 }  
Получение данных об авторизованном пользователе в формате:  
{  
    &emsp;'phone': '+71234567890',  
    &emsp;'invite_code': '123456',  
    &emsp;'claimed_invite_code': Null | '123456',  
    &emsp;invites: [] | ['+71234567891']  
}
