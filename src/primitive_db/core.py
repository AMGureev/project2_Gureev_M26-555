"""Бизнес-логика таблиц, проверки схем и CRUD-операции."""

import json

from primitive_db import constants as const
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data, validate_identifier

_select_cache = create_cacher()


def _schema(metadata, table_name):
    """Получить схему существующей таблицы."""
    validate_identifier(table_name)
    if table_name not in metadata:
        raise KeyError(const.TABLE_MISSING.format(table=table_name))
    return dict(column.split(const.COLUMN_SEPARATOR) for column in metadata[table_name])


def _matches(record, where_clause):
    """Проверить равенство значений и их типов для всех условий."""
    return all(
        type(record[column]) is type(value) and record[column] == value
        for column, value in (where_clause or {}).items()
    )


def _validate_row_clause(table_data, clause):
    """Проверить существование полей и типы значений на имеющихся записях."""
    for record in table_data:
        for column, value in clause.items():
            if column not in record:
                raise KeyError(const.COLUMN_MISSING.format(column=column))
            if type(record[column]) is not type(value):
                raise ValueError(
                    const.VALUE_TYPE_ERROR.format(
                        column=column, type_name=type(record[column]).__name__
                    )
                )


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Добавить таблицу с проверенной схемой и первым столбцом ID:int."""
    validate_identifier(table_name)
    if table_name in metadata:
        raise KeyError(const.TABLE_EXISTS.format(table=table_name))
    if not columns:
        raise ValueError(const.COLUMNS_REQUIRED)
    schema = [f"{const.ID_COLUMN}{const.COLUMN_SEPARATOR}{const.TYPE_INT}"]
    seen = set()
    for definition in columns:
        if not isinstance(definition, str):
            raise ValueError(const.INVALID_COLUMN.format(column=definition))
        column, separator, type_name = definition.partition(const.COLUMN_SEPARATOR)
        validate_identifier(column)
        if not separator or type_name not in const.VALID_TYPES:
            raise ValueError(const.INVALID_TYPE.format(type_name=type_name))
        if column in seen:
            raise ValueError(const.DUPLICATE_COLUMN.format(column=column))
        seen.add(column)
        if column == const.ID_COLUMN:
            if type_name != const.TYPE_INT:
                raise ValueError(const.ID_TYPE_ERROR)
            continue
        schema.append(definition)
    metadata[table_name] = schema
    return metadata


@handle_db_errors
@confirm_action(const.DROP_ACTION)
def drop_table(metadata, table_name):
    """Удалить существующую таблицу из метаданных после подтверждения."""
    _schema(metadata, table_name)
    del metadata[table_name]
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Вернуть имена таблиц по алфавиту."""
    return sorted(metadata)


@handle_db_errors
def get_schema(metadata, table_name):
    """Вернуть схему таблицы для проверки и отображения в интерфейсе."""
    return _schema(metadata, table_name)


@handle_db_errors
def validate_fields(metadata, table_name, clause):
    """Проверить поля и точные типы значений по схеме, включая пустую таблицу."""
    schema = _schema(metadata, table_name)
    for column, value in clause.items():
        if column not in schema:
            raise KeyError(const.COLUMN_MISSING.format(column=column))
        type_name = schema[column]
        if type(value) is not const.VALID_TYPES[type_name]:
            raise ValueError(
                const.VALUE_TYPE_ERROR.format(column=column, type_name=type_name)
            )
    return clause


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data=None):
    """Проверить значения, назначить следующий ID и вернуть записи с новой."""
    schema = _schema(metadata, table_name)
    columns = [column for column in schema if column != const.ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(
            const.VALUES_COUNT_ERROR.format(expected=len(columns), actual=len(values))
        )
    for column, value in zip(columns, values):
        type_name = schema[column]
        if type(value) is not const.VALID_TYPES[type_name]:
            raise ValueError(
                const.VALUE_TYPE_ERROR.format(column=column, type_name=type_name)
            )
    data = load_table_data(table_name) if table_data is None else table_data
    record_id = max((row[const.ID_COLUMN] for row in data), default=0) + 1
    record = {const.ID_COLUMN: record_id}
    record.update(zip(columns, values))
    return [*data, record]


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Вернуть копии выбранных записей, кэшируя одинаковые запросы и данные."""
    _validate_row_clause(table_data, where_clause or {})
    key = (
        json.dumps(table_data, sort_keys=True),
        json.dumps(where_clause, sort_keys=True),
    )
    cached = _select_cache(
        key,
        lambda: [
            record.copy() for record in table_data if _matches(record, where_clause)
        ],
    )
    return [record.copy() for record in cached]


@handle_db_errors
def matching_ids(table_data, where_clause):
    """Вернуть ID записей, затрагиваемых обновлением или удалением."""
    _validate_row_clause(table_data, where_clause)
    return [
        record[const.ID_COLUMN]
        for record in table_data
        if _matches(record, where_clause)
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Изменить подходящие записи, сохранив типы и уникальность ID."""
    _validate_row_clause(table_data, set_clause)
    _validate_row_clause(table_data, where_clause)
    updated = []
    for record in table_data:
        replacement = record.copy()
        if _matches(record, where_clause):
            replacement.update(set_clause)
        updated.append(replacement)
    ids = [record[const.ID_COLUMN] for record in updated]
    if len(ids) != len(set(ids)) or any(record_id <= 0 for record_id in ids):
        raise ValueError(const.INVALID_IDS)
    return updated


@handle_db_errors
@confirm_action(const.DELETE_ACTION)
def delete(table_data, where_clause):
    """Удалить подходящие записи только после явного подтверждения."""
    _validate_row_clause(table_data, where_clause)
    return [
        record.copy() for record in table_data if not _matches(record, where_clause)
    ]
