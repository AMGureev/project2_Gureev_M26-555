"""Разбор команд и типизированных значений с сохранением строк в кавычках."""

import shlex

from primitive_db import constants as const
from primitive_db.utils import validate_identifier


def tokenize(command):
    """Разбить команду через shlex, сохранив тип строковых литералов."""
    literals = {}
    protected = []
    position = 0
    while position < len(command):
        character = command[position]
        if character not in const.QUOTE_CHARACTERS:
            protected.append(character)
            position += 1
            continue
        quote = character
        end = position + 1
        while end < len(command) and command[end] != quote:
            if command[end] == const.ESCAPE_CHARACTER and quote == '"':
                end += 1
            end += 1
        if end >= len(command):
            raise ValueError(const.UNCLOSED_STRING)
        literal = command[position : end + 1]
        marker = f"{const.STRING_MARKER}{len(literals)}"
        literals[marker] = shlex.split(literal)[0]
        protected.extend((" ", marker, " "))
        position = end + 1

    lexer = shlex.shlex(
        "".join(protected), posix=True, punctuation_chars=const.PUNCTUATION
    )
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = []
    for token in lexer:
        if token in literals:
            tokens.append((const.TYPE_STR, literals[token]))
        elif all(character in const.PUNCTUATION for character in token):
            tokens.extend(token)
        else:
            tokens.append(token)
    return tokens


def parse_value(token):
    """Преобразовать строковый литерал, целое число или true/false."""
    if isinstance(token, tuple):
        return token[1]
    if token.lower() in const.BOOL_VALUES:
        return const.BOOL_VALUES[token.lower()]
    try:
        return int(token)
    except ValueError as error:
        raise ValueError(const.INVALID_VALUE.format(value=token)) from error


def _expect(condition):
    """Выдать единую ошибку для нарушения грамматики команды."""
    if not condition:
        raise ValueError(const.INVALID_COMMAND)


def _keyword(token, keyword):
    """Проверить служебное слово без изменения регистра строковых значений."""
    return isinstance(token, str) and token.lower() == keyword


def _assignments(tokens):
    """Прочитать пары столбец = значение, разделённые запятыми."""
    _expect(bool(tokens))
    assignments = {}
    position = 0
    while position < len(tokens):
        _expect(position + 2 < len(tokens))
        column, equals, value = tokens[position : position + 3]
        validate_identifier(column)
        _expect(equals == const.EQUALS)
        if column in assignments:
            raise ValueError(const.DUPLICATE_COLUMN.format(column=column))
        assignments[column] = parse_value(value)
        position += 3
        if position < len(tokens):
            _expect(tokens[position] == const.COMMA)
            position += 1
            _expect(position < len(tokens))
    return assignments


def parse_where(expression):
    """Преобразовать одно условие where в словарь столбец → значение."""
    tokens = tokenize(expression) if isinstance(expression, str) else expression
    _expect(len(tokens) == 3)
    return _assignments(tokens)


def parse_set(expression):
    """Преобразовать присваивания set в словарь изменяемых полей."""
    tokens = tokenize(expression) if isinstance(expression, str) else expression
    return _assignments(tokens)


def parse_values(expression):
    """Прочитать значения в скобках с учётом кавычек и запятых в строках."""
    tokens = tokenize(expression) if isinstance(expression, str) else expression
    _expect(len(tokens) >= 2)
    _expect(tokens[0] == const.OPEN_PAREN and tokens[-1] == const.CLOSE_PAREN)
    values = []
    body = tokens[1:-1]
    for position, token in enumerate(body):
        if position % 2:
            _expect(token == const.COMMA)
        else:
            values.append(parse_value(token))
    _expect(not body or len(body) % 2 == 1)
    return values


def parse_command(user_input):
    """Вернуть имя команды и её аргументы, проверив обязательный синтаксис."""
    tokens = tokenize(user_input)
    _expect(bool(tokens) and isinstance(tokens[0], str))
    command = tokens[0].lower()
    if command in (const.HELP, const.EXIT, const.LIST_TABLES):
        _expect(len(tokens) == 1)
        return command, ()
    if command == const.CREATE_TABLE:
        _expect(len(tokens) >= 3)
        return command, (tokens[1], tokens[2:])
    if command in (const.DROP_TABLE, const.INFO):
        _expect(len(tokens) == 2)
        return command, (tokens[1],)
    if command == const.INSERT:
        _expect(len(tokens) >= 6 and _keyword(tokens[1], const.INTO))
        _expect(_keyword(tokens[3], const.VALUES))
        return command, (tokens[2], parse_values(tokens[4:]))
    if command == const.SELECT:
        _expect(len(tokens) >= 3 and _keyword(tokens[1], const.FROM))
        if len(tokens) == 3:
            return command, (tokens[2], None)
        _expect(_keyword(tokens[3], const.WHERE))
        return command, (tokens[2], parse_where(tokens[4:]))
    if command == const.UPDATE:
        _expect(len(tokens) >= 4 and _keyword(tokens[2], const.SET))
        positions = [
            index for index, token in enumerate(tokens) if _keyword(token, const.WHERE)
        ]
        _expect(len(positions) == 1)
        where_position = positions[0]
        return command, (
            tokens[1],
            parse_set(tokens[3:where_position]),
            parse_where(tokens[where_position + 1 :]),
        )
    if command == const.DELETE:
        _expect(len(tokens) >= 4 and _keyword(tokens[1], const.FROM))
        _expect(_keyword(tokens[3], const.WHERE))
        return command, (tokens[2], parse_where(tokens[4:]))
    return command, ()
