# Описание проекта
Данный бот обращается к API сервиса Практикум.Домашка и узнает статус домашней работы студенты: взята домашняя работа в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.
### Технологии
- [Telegram Bot API](https://core.telegram.org/bots/api) - is an HTTP-based interface created for developers keen on building bots for Telegram.
- [Python](https://www.python.org/) - is an interpreted high-level general-purpose programming language.
- [Heroku](https://www.heroku.com/) - is a cloud platform that lets companies build, deliver, monitor and scale apps.
- [API Практикум.Домашка](https://practicum.yandex.ru/api/user_api/homework_statuses/) - is an HTTP-based interface created for developers to check homework statuses on Yandex Practicum platform.
### Документация к API сервиса Практикум.Домашка
API возвращает изменение статуса домашнего задания за определённый интервал
времени.
Если статус домашнего задания изменился за этот интервал времени, то в ответ
придут данные в формате JSON.
Интервал задаётся от времени, указанного в параметре from_date, до
текущего момента. Время передаётся в формате Unix time (оно вернётся в
ключе current_date, его можно использовать как начало интервала в
следующем запросе).

API доступно по адресу:
https://practicum.yandex.ru/api/user_api/homework_statuses/

Для успешного запроса нужно:
- в заголовке запроса передать токен авторизации Authorization: OAuth TOKEN;
- передать GET-параметр from_date.

Токен можно получить по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a

### Пример запроса
```
import requests

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {<ваш токен>}'}
payload = {'from_date': <временная метка в формате Unix time>}.
homework_statuses = requests.get(url, headers=headers, params=payload)
print(homework_statuses.json())
```

### Пример ответа API
В ответ на правильно сформированный запрос API Практикум.Домашка
пришлёт вам список домашних работ, статус которых изменился за
запрошенный период:
```
{
 "homeworks":[
 {
 "id":123,
 "status":"rejected",
 "homework_name":"username__hw_python_oop.zip",
 "reviewer_comment":"Код не по PEP8, нужно исправить",
 "date_updated":"2020-02-11T16:42:47Z",
 "lesson_name":"Итоговый проект"
 },
 {
 "id":124,
 "status":"approved",
 "homework_name":"username__hw_python_oop.zip",
 "reviewer_comment":"Всё нравится",
 "date_updated":"2020-02-13T14:40:57Z",
 "lesson_name":"Итоговый проект"
 }
],
"current_date":1581604970
}
```
Статус домашки (ключ status) может быть трёх типов:
- reviewing: работа взята в ревью;
- approved: ревью успешно пройдено;
- rejected: в работе есть ошибки, нужно поправить.

Если домашнюю ещё не взяли в работу или не проверили — её не будет в
выдаче. Комментарии отображаются только у последней работы.
