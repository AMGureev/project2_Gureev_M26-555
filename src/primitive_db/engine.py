"""Консольный цикл и координация команд базы данных."""

import prompt
from prettytable import PrettyTable

from primitive_db import constants as const
from primitive_db import core, utils
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import parse_command


def print_help():
    """Напечатать синтаксис команд и поддерживаемые типы данных."""
    print(const.HELP_TEXT)


def welcome():
    """Показать приветствие и доступные команды перед первым запросом."""
    print(const.WELCOME_MESSAGE)
    print_help()


def _load_table(metadata, table_name):
    """Получить проверенную схему и текущие записи существующей таблицы."""
    schema = core.get_schema(metadata, table_name)
    if schema is None:
        return None
    return schema, utils.load_table_data(table_name)


def _create_table(metadata, table_name, columns):
    """Создать таблицу и сохранить метаданные вместе с пустым файлом данных."""
    updated = core.create_table(metadata, table_name, columns)
    if updated is not None:
        utils.save_table_data(table_name, [])
        utils.save_metadata(const.META_FILE, updated)
        print(
            const.TABLE_CREATED.format(
                table=table_name, columns=", ".join(updated[table_name])
            )
        )


def _drop_table(metadata, table_name):
    """После проверки и подтверждения удалить схему и файл таблицы."""
    if core.get_schema(metadata, table_name) is None:
        return
    updated = core.drop_table(metadata, table_name)
    if updated is not None:
        utils.save_metadata(const.META_FILE, updated)
        utils.remove_table_data(table_name)
        print(const.TABLE_DROPPED.format(table=table_name))


def _insert_row(metadata, table_name, values):
    """Загрузить записи, выполнить вставку и сохранить успешный результат."""
    loaded = _load_table(metadata, table_name)
    if loaded is None:
        return
    _, data = loaded
    updated = core.insert(metadata, table_name, values, data)
    if updated is not None:
        utils.save_table_data(table_name, updated)
        print(
            const.ROW_INSERTED.format(
                record_id=updated[-1][const.ID_COLUMN], table=table_name
            )
        )


def _select_rows(metadata, table_name, where_clause):
    """Вывести выбранные записи таблицей PrettyTable."""
    loaded = _load_table(metadata, table_name)
    if loaded is None:
        return
    schema, data = loaded
    if core.validate_fields(metadata, table_name, where_clause or {}) is None:
        return
    records = core.select(data, where_clause)
    if records is None:
        return
    table = PrettyTable()
    table.field_names = list(schema)
    table.add_rows([[record[column] for column in schema] for record in records])
    print(table)


def _change_rows(metadata, table_name, where_clause, set_clause=None):
    """Проверить условия, изменить либо удалить записи и сохранить данные."""
    loaded = _load_table(metadata, table_name)
    if loaded is None:
        return
    _, data = loaded
    if core.validate_fields(metadata, table_name, where_clause) is None:
        return
    if set_clause is not None:
        if core.validate_fields(metadata, table_name, set_clause) is None:
            return
        updated = core.update(data, set_clause, where_clause)
        message = const.ROW_UPDATED
    else:
        updated = core.delete(data, where_clause)
        message = const.ROW_DELETED
    if updated is None:
        return
    affected_ids = core.matching_ids(data, where_clause)
    if affected_ids is None:
        return
    utils.save_table_data(table_name, updated)
    for record_id in affected_ids:
        print(message.format(record_id=record_id, table=table_name))
    if not affected_ids:
        print(const.NO_MATCHES)


def _show_info(metadata, table_name):
    """Напечатать схему таблицы и текущее количество записей."""
    loaded = _load_table(metadata, table_name)
    if loaded is not None:
        _, data = loaded
        print(
            const.TABLE_INFO.format(
                table=table_name,
                columns=", ".join(metadata[table_name]),
                count=len(data),
            )
        )


@handle_db_errors
def execute_command(user_input):
    """Разобрать и выполнить одну команду; вернуть False для выхода."""
    command, arguments = parse_command(user_input)
    if command == const.EXIT:
        print(const.EXIT_MESSAGE)
        return False
    if command == const.HELP:
        print_help()
        return True
    metadata = utils.load_metadata(const.META_FILE)
    if command == const.CREATE_TABLE:
        _create_table(metadata, *arguments)
    elif command == const.DROP_TABLE:
        _drop_table(metadata, *arguments)
    elif command == const.LIST_TABLES:
        tables = core.list_tables(metadata)
        for table_name in tables:
            print(const.TABLE_LIST_ITEM.format(table=table_name))
        if not tables:
            print(const.NO_TABLES)
    elif command == const.INSERT:
        _insert_row(metadata, *arguments)
    elif command == const.SELECT:
        _select_rows(metadata, *arguments)
    elif command == const.UPDATE:
        table_name, set_clause, where_clause = arguments
        _change_rows(metadata, table_name, where_clause, set_clause)
    elif command == const.DELETE:
        _change_rows(metadata, *arguments)
    elif command == const.INFO:
        _show_info(metadata, *arguments)
    else:
        print(const.UNKNOWN_COMMAND.format(command=command))
    return True


def run():
    """Запрашивать команды до exit, EOF или прерывания пользователем."""
    welcome()
    while True:
        try:
            user_input = prompt.string(const.INPUT_PROMPT)
            if not user_input.strip():
                continue
            if execute_command(user_input) is False:
                break
        except (EOFError, KeyboardInterrupt):
            print(const.EXIT_MESSAGE)
            break
