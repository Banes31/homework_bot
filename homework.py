import json
import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv
from exceptions import (
    AnswerIsNot200,
    EmptyValueError,
    RequestExceptionError,
    TokenError,
    UnknownStatusError
)
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)


def send_message(bot, message):
    """Отправить сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Сообщение отправлено в Telegram: {message}')
    except telegram.TelegramError as error:
        logger.error(
            f'Сообщение не отправлено в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        response = requests.get(ENDPOINT, headers=headers, params=params)
        if response.status_code != HTTPStatus.OK.value:
            code_api_msg = (
                f'Эндпоинт {ENDPOINT} недоступен.'
                f' Код ответа API: {response.status_code}'
            )
            logger.error(code_api_msg)
            raise AnswerIsNot200(code_api_msg)
        return response.json()
    except requests.exceptions.RequestException as error:
        code_api_msg = f'Код ответа API (RequestException): {error}'
        logger.error(code_api_msg)
        raise RequestExceptionError(code_api_msg)
    except json.JSONDecodeError as error:
        code_api_msg = f'Код ответа API (ValueError): {error}'
        logger.error(code_api_msg)
        raise json.JSONDecodeError(code_api_msg)


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        code_api_msg = 'Тип response отличен от dict'
        logger.error(code_api_msg)
        raise TypeError(code_api_msg)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        code_api_msg = 'Тип homeworks отличен от list'
        logger.error(code_api_msg)
        raise TypeError(code_api_msg)
    if homeworks is None:
        code_api_msg = (
            'Ключ homeworks или response'
            'имеет пустое значение.'
        )
        logger.error(code_api_msg)
        raise EmptyValueError(code_api_msg)
    if homeworks == []:
        return homeworks
    return homeworks


def parse_status(homework):
    """Имеет следующий алгоритм.
    Извлекает из информации о конкретной домашней работе статус этой работы.
    Возвращает наименование конкретной домашней работы и текущий статус ревью.
    """
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status is None:
        code_api_msg = (
            f'homework_status имеет пустое значение "{homework_status}".',
        )
        logger.error(code_api_msg)
        raise EmptyValueError(code_api_msg)
    if homework_name is None:
        code_api_msg = (
            f'homework_name имеет пустое значение "{homework_name}".',
        )
        logger.error(code_api_msg)
        raise EmptyValueError(code_api_msg)
    if homework_status not in HOMEWORK_STATUSES:
        code_api_msg = (
            f'Получен недокументированный статус домашней работы: '
            f'{homework_status}'
        )
        logger.error(code_api_msg)
        raise UnknownStatusError(code_api_msg)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения (токенов).
    Которые необходимы для работы программы.
    """
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Главная функция запуска бота."""
    if not check_tokens():
        no_tokens_msg = (
            'Программа принудительно остановлена. '
            'Отсутствует обязательная переменная окружения:'
        )
        if PRACTICUM_TOKEN is None:
            logger.critical(f'{no_tokens_msg} PRACTICUM_TOKEN')
            raise TokenError(f'{no_tokens_msg} PRACTICUM_TOKEN')
        if TELEGRAM_TOKEN is None:
            logger.critical(f'{no_tokens_msg} TELEGRAM_TOKEN')
            raise TokenError(f'{no_tokens_msg} TELEGRAM_TOKEN')
        if TELEGRAM_CHAT_ID is None:
            logger.critical(f'{no_tokens_msg} TELEGRAM_CHAT_ID')
            raise TokenError(f'{no_tokens_msg} TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    cache_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
                logger.info('Обновился статус проверки домашней работы.')
            else:
                logger.info(
                    'Статус домашней работы не изменился. '
                    'Ждем 10 минут и повторно проверяем API.'
                )
            current_timestamp = response.get('current_date')
            logger.debug('Запуск основной ветки прошел без ошибок.')
        except Exception as error:
            message = f'Ошибка: {error}'
            logger.error(message)
            if message != cache_message:
                send_message(bot, message)
                cache_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
