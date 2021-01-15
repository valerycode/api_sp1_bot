import os
import time

import logging
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
                 ' запроса со следующими параметрами: URL: {URL_API},'
                 ' TOKEN: {token}, параметры: {params}')
RESPONSE_ERROR = ('Ошибка в ответе сервера при выполнени запроса'
                  ' со следующими параметрами:'
                  ' URL: {URL_API}, введенный токен: {token},'
                  ' параметры: {params}, значение {key}: {item}')
STATUS_ERROR = 'Неизвестный статус работы "{homework_name}"'
STATUS_MESSAGE = 'У вас проверили работу "{homework_name}"!\n\n{verdict}'
ERROR_MESSAGE = 'Бот столкнулся с ошибкой: {error}'
SEND_MESSAGE = 'Бот успешно отправил сообщение в Телеграм-чат {message}'
BOT_LAUNCH = 'Бот успешно запушен'
HOMEWORK_STATUSES_DICT = {
    'reviewing': 'Работа взята в ревью',
    'approved': 'Ревьюеру всё понравилось,'
                ' можно приступать к следующему уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.'}
logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s; %(levelname)s; %(name)s; %(message)s')
logger = logging.getLogger('__name__')


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_STATUSES_DICT:
        message = STATUS_ERROR.format(homework_name=homework_name)
        logging.info(message)
        return message
    verdict = HOMEWORK_STATUSES_DICT.get(status)
    return STATUS_MESSAGE.format(homework_name=homework_name, verdict=verdict)


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(URL_PRAKTIKUM, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        raise ConnectionError(REQUEST_ERROR.format(
            URL_API=URL_PRAKTIKUM,
            token=PRAKTIKUM_TOKEN,
            params=params,
            error=error)
        )
    homeworks = response.json()
    error_keys = ['error', 'code']
    for key in error_keys:
        if key in homeworks:
            raise ValueError(RESPONSE_ERROR.format(
                URL_API=URL_PRAKTIKUM,
                token=PRAKTIKUM_TOKEN,
                params=params,
                key=key,
                item=homeworks[key])
            )
    return homeworks


def send_message(message, bot_client):
    try:
        sent_message = bot_client.send_message(CHAT_ID, message)
    except Exception as error:
        raise ValueError(ERROR_MESSAGE.format(error=error))
    logging.info(SEND_MESSAGE.format(message=message))
    return sent_message


def main():

    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            logging.debug(BOT_LAUNCH)
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            time.sleep(300)

        except Exception as error:
            print(ERROR_MESSAGE.format(error=error))
            logging.error(error, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
