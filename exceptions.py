class AnswerIsNot200(Exception):
    """Ответ сервера не равен 200."""


class EmptyValueError(Exception):
    """Ответ содержит пустое значение."""


class RequestExceptionError(Exception):
    """Ошибка запроса."""


class UnknownStatusError(Exception):
    """Ответ содержит недокументированный статус."""


class TokenError(Exception):
    """Отсутствует один из обязательных токенов."""
