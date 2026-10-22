"""Загрузка и сохранение метаданных и записей в JSON-файлах."""

import json
import os

from primitive_db import constants as const


def load_metadata(filepath):
    """Прочитать метаданные; для отсутствующего файла вернуть пустой словарь."""
    try:
        with open(filepath, encoding=const.FILE_ENCODING) as metadata_file:
            metadata = json.load(metadata_file)
    except FileNotFoundError:
        return {}
    if not isinstance(metadata, dict):
        raise ValueError(const.INVALID_METADATA)
    return metadata


def save_metadata(filepath, data):
    """Сохранить метаданные в указанный JSON-файл."""
    with open(filepath, "w", encoding=const.FILE_ENCODING) as metadata_file:
        json.dump(data, metadata_file, ensure_ascii=False, indent=const.JSON_INDENT)


def table_filepath(table_name):
    """Построить путь к файлу таблицы с допустимым именем."""
    validate_identifier(table_name)
    return os.path.join(const.DATA_DIR, f"{table_name}.json")


def validate_identifier(name):
    """Проверить имя таблицы или столбца без разрешения путей к файлам."""
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError(const.INVALID_IDENTIFIER.format(name=name))
    return name


def load_table_data(table_name):
    """Загрузить список записей; для отсутствующего файла вернуть пустой список."""
    filepath = table_filepath(table_name)
    try:
        with open(filepath, encoding=const.FILE_ENCODING) as table_file:
            data = json.load(table_file)
    except FileNotFoundError:
        return []
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError(const.INVALID_TABLE_DATA)
    return data


def save_table_data(table_name, data):
    """Создать каталог данных при необходимости и сохранить записи таблицы."""
    filepath = table_filepath(table_name)
    os.makedirs(const.DATA_DIR, exist_ok=True)
    with open(filepath, "w", encoding=const.FILE_ENCODING) as table_file:
        json.dump(data, table_file, ensure_ascii=False, indent=const.JSON_INDENT)


def remove_table_data(table_name):
    """Удалить файл данных удаляемой таблицы, если файл существует."""
    filepath = table_filepath(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)
