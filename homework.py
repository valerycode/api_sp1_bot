import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRAKTIKUM = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
REQUEST_ERROR = ('Сбой в работе сети. Произошла ошибка {error} при выполнении'
                 ' запроса со следующими параметрами: URL: {url},'
                 ' TOKEN: {headers}, параметры: {params}')
RESPONSE_ERROR = ('Ошибка в ответе сервера при выполнени запроса'
                  ' со следующими параметрами:'
                  ' URL: {url}, введенный токен: {headers},'
                  ' параметры: {params}, значение {key}: {item}')
STATUS_ERROR = 'Неизвестный статус работы "{name}: {status}"'
STATUS_MESSAGE = 'У вас проверили работу "{name}"!\n\n{verdict}'
ERROR_MESSAGE = 'Бот столкнулся с ошибкой: {error}'
SEND_MESSAGE = 'Бот успешно отправил сообщение в Телеграм-чат {message}'
BOT_LAUNCH = 'Бот успешно запушен'
VERDICTS = {
    'reviewing': 'Работа взята в ревью',
    'approved': 'Ревьюеру всё понравилось,'
                ' можно приступать к следующему уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.'}
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    name = homework['homework_name']
    status = homework['status']
    if status not in VERDICTS:
        raise ValueError(STATUS_ERROR.format(name=name, status=status))
    return STATUS_MESSAGE.format(name=name, verdict=VERDICTS[status])


def get_homework_statuses(current_timestamp):
    args = dict(url=URL_PRAKTIKUM, headers=HEADERS,
                params={'from_date': current_timestamp})
    try:
        response = requests.get(**args)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(REQUEST_ERROR.format(**args, error=error))
    homeworks = response.json()
    for key in ['error', 'code']:
        if key in homeworks:
            raise RuntimeError(RESPONSE_ERROR.format(
                **args,
                key=key,
                item=homeworks[key])
            )
    return homeworks


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.debug(BOT_LAUNCH)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                message = parse_homework_status(
                    new_homework.get('homeworks')[0])
                send_message(message, bot_client)
                logging.info(SEND_MESSAGE.format(message=message))
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            time.sleep(300)

        except Exception as error:
            logging.error(ERROR_MESSAGE.format(error=error), exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename=__file__ + '.log',
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')
    main()
