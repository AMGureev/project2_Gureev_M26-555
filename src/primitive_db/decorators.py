"""Обработка ошибок, подтверждение, замер времени и кэш в замыкании."""

import time

from primitive_db import constants as const


def _preserve_metadata(wrapper, function):
    """Сохранить имя и документацию функции без дополнительных импортов."""
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    wrapper.__wrapped__ = function
    return wrapper


def handle_db_errors(function):
    """Преобразовать ожидаемые ошибки базы данных в сообщения пользователю."""

    def wrapper(*args, **kwargs):
        """Выполнить операцию и централизованно обработать её ошибку."""
        try:
            return function(*args, **kwargs)
        except FileNotFoundError:
            print(const.FILE_ERROR_MESSAGE)
        except KeyError as error:
            print(const.ERROR_MESSAGE.format(message=error.args[0]))
        except ValueError as error:
            print(const.VALIDATION_MESSAGE.format(message=error))
        except OSError as error:
            print(const.STORAGE_ERROR_MESSAGE.format(message=error))
        return None

    return _preserve_metadata(wrapper, function)


def confirm_action(action_name):
    """Запросить подтверждение указанного опасного действия."""

    def decorate(function):
        """Добавить запрос подтверждения перед вызовом функции."""

        def wrapper(*args, **kwargs):
            """Вызвать операцию только после ответа y."""
            answer = input(const.CONFIRM_PROMPT.format(action=action_name))
            if answer.strip() != const.CONFIRM_YES:
                print(const.CANCEL_MESSAGE)
                return None
            return function(*args, **kwargs)

        return _preserve_metadata(wrapper, function)

    return decorate


def log_time(function):
    """Вывести длительность вызова по монотонным часам."""

    def wrapper(*args, **kwargs):
        """Измерить время операции, сохранив её возвращаемое значение."""
        started = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(const.TIME_MESSAGE.format(name=function.__name__, elapsed=elapsed))

    return _preserve_metadata(wrapper, function)


def create_cacher():
    """Создать независимый кэш, хранящийся в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть сохранённое значение или вычислить и сохранить новое."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
