"""Константы хранения, типов данных, команд и сообщений приложения."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
FILE_ENCODING = "utf-8"
JSON_INDENT = 4
ID_COLUMN = "ID"
TYPE_INT = "int"
TYPE_STR = "str"
TYPE_BOOL = "bool"
VALID_TYPES = {TYPE_INT: int, TYPE_STR: str, TYPE_BOOL: bool}
BOOL_VALUES = {"true": True, "false": False}

CREATE_TABLE = "create_table"
DROP_TABLE = "drop_table"
LIST_TABLES = "list_tables"
INSERT = "insert"
SELECT = "select"
UPDATE = "update"
DELETE = "delete"
INFO = "info"
HELP = "help"
EXIT = "exit"
INTO = "into"
FROM = "from"
VALUES = "values"
WHERE = "where"
SET = "set"
COLUMN_SEPARATOR = ":"
EQUALS = "="
COMMA = ","
OPEN_PAREN = "("
CLOSE_PAREN = ")"
PUNCTUATION = "(),="
QUOTE_CHARACTERS = "\"'"
ESCAPE_CHARACTER = "\\"
STRING_MARKER = "\x00string_"

WELCOME_MESSAGE = "***База данных***"
INPUT_PROMPT = ">>> Введите команду: "
EXIT_MESSAGE = "Работа завершена."
CONFIRM_PROMPT = 'Вы уверены, что хотите выполнить "{action}"? [y/n]: '
CONFIRM_YES = "y"
DROP_ACTION = "удаление таблицы"
DELETE_ACTION = "удаление записей"
CANCEL_MESSAGE = "Операция отменена."
TIME_MESSAGE = "Функция {name} выполнилась за {elapsed:.3f} секунд"
ERROR_MESSAGE = "Ошибка: {message}"
VALIDATION_MESSAGE = "Ошибка валидации: {message}"
FILE_ERROR_MESSAGE = (
    "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
)
STORAGE_ERROR_MESSAGE = "Ошибка работы с файлами: {message}"
UNKNOWN_COMMAND = "Функции {command} нет. Попробуйте снова."
INVALID_COMMAND = "Некорректный синтаксис команды. Введите help для справки."
INVALID_VALUE = (
    "Некорректное значение: {value}. Попробуйте снова. "
    "Строковые значения заключайте в кавычки."
)
INVALID_IDENTIFIER = "Некорректное имя: {name}. Используйте буквы, цифры и _."
UNCLOSED_STRING = "Не закрыты кавычки строкового значения."
TABLE_EXISTS = 'Таблица "{table}" уже существует.'
TABLE_MISSING = 'Таблица "{table}" не существует.'
COLUMN_MISSING = 'Столбец "{column}" не существует.'
INVALID_COLUMN = "Некорректное определение столбца: {column}."
DUPLICATE_COLUMN = 'Столбец "{column}" указан несколько раз.'
INVALID_TYPE = "Неподдерживаемый тип: {type_name}. Допустимы int, str, bool."
ID_TYPE_ERROR = "Столбец ID должен иметь тип int."
COLUMNS_REQUIRED = "Укажите хотя бы один столбец таблицы."
VALUES_COUNT_ERROR = (
    "Ожидалось значений: {expected}; передано: {actual}. ID задаётся автоматически."
)
VALUE_TYPE_ERROR = 'Столбец "{column}" ожидает тип {type_name}.'
INVALID_IDS = "ID должны быть уникальными положительными целыми числами."
INVALID_METADATA = "Файл метаданных должен содержать JSON-объект."
INVALID_TABLE_DATA = "Файл таблицы должен содержать JSON-массив записей."
TABLE_CREATED = 'Таблица "{table}" успешно создана со столбцами: {columns}'
TABLE_DROPPED = 'Таблица "{table}" успешно удалена.'
TABLE_LIST_ITEM = "- {table}"
NO_TABLES = "Таблиц пока нет."
ROW_INSERTED = 'Запись с ID={record_id} успешно добавлена в таблицу "{table}".'
ROW_UPDATED = 'Запись с ID={record_id} в таблице "{table}" успешно обновлена.'
ROW_DELETED = 'Запись с ID={record_id} успешно удалена из таблицы "{table}".'
NO_MATCHES = "Подходящие записи не найдены."
TABLE_INFO = "Таблица: {table}\nСтолбцы: {columns}\nКоличество записей: {count}"
HELP_TEXT = (
    "\nФункции:\n"
    "create_table <таблица> <столбец:тип> ... — создать таблицу\n"
    "list_tables — показать список таблиц\n"
    "drop_table <таблица> — удалить таблицу с подтверждением\n"
    "insert into <таблица> values (<значение>, ...) — добавить запись без ID\n"
    "select from <таблица> [where <столбец> = <значение>] — прочитать записи\n"
    "update <таблица> set <столбец> = <значение> "
    "where <столбец> = <значение> — обновить записи\n"
    "delete from <таблица> where <столбец> = <значение> — удалить записи\n"
    "info <таблица> — показать структуру и количество записей\n"
    "help — справка\n"
    "exit — выход\n"
    "Типы: int, str, bool. Строки — в кавычках, bool — true или false.\n"
)
