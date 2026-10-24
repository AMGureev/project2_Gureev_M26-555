# Примитивная база данных

Консольная база данных на Python 3.12 с хранением схем и записей в JSON.
Поддерживает создание таблиц, CRUD, типы `int`, `str`, `bool`, фильтрацию,
подтверждение удаления, обработку ошибок и кэширование выборки.

## Установка и запуск

Нужны Python 3.12 и [uv](https://docs.astral.sh/uv/getting-started/installation/).

```console
git clone https://github.com/AMGureev/project2_Gureev_M26-555.git
cd project2_Gureev_M26-555
uv sync --locked
uv run database
```

Команда `uv run project` запускает то же приложение.
Также можно выполнить `uv run python -m primitive_db.main`.
При установленном GNU Make доступны:

```console
make install
make run
make lint
```

Они выполняют соответственно `uv sync --locked`, `uv run database`
и `uv run ruff check .`. Версии зависимостей закреплены в `uv.lock`;
Ruff находится только в группе зависимостей разработки.

## Управление таблицами

```text
create_table users name:str age:int is_active:bool
list_tables
info users
drop_table users
```

При создании автоматически добавляется первый столбец `ID:int`.
Имена таблиц и столбцов состоят из букв, цифр и подчёркиваний,
начинаются с буквы или подчёркивания. Повторяющиеся столбцы,
неподдерживаемые типы и повторное создание таблицы отклоняются.
Команда `drop_table` запрашивает подтверждение и удаляет схему и данные.

## CRUD-операции

```text
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
```

Все пользовательские поля обязательны. Значение `ID` при вставке не передаётся:
оно вычисляется как максимальный существующий ID плюс один, начиная с 1.
Строки записываются в одинарных или двойных кавычках, включая строки
с пробелами и запятыми. Числа должны быть целыми, логические значения —
`true` или `false`. Например, `"28"` — строка, а `28` — число.

`where` задаёт одно равенство. `set` поддерживает одно или несколько
присваиваний через запятую:

```text
update users set name = "Sergei Petrov", age = 30 where ID = 1
```

`select` без `where` выводит все записи через PrettyTable. `info` показывает
схему и количество записей. `help` выводит справку, `exit` завершает работу.

## Ошибки, подтверждение и кэширование

`handle_db_errors` обрабатывает ошибки таблиц, столбцов, значений и файлов.
После сообщения об ошибке программа продолжает запрашивать команды.
`confirm_action` применяется к `drop_table` и `delete`: действие выполняется
только после ответа `y`, остальные ответы отменяют операцию.
`log_time` выводит время `insert` и `select` по `time.monotonic()`.

`create_cacher()` хранит результаты в замыкании. Повторный `select`
с теми же данными и условием использует кэш; изменение данных меняет ключ,
поэтому после вставки, обновления и удаления возвращаются актуальные записи.

## Хранение данных

В текущей рабочей папке создаются `db_meta.json` и каталог `data/`
с файлами вида `data/users.json`. Записи сохраняются между запусками.
Для работы с той же базой запускайте программу из той же папки.
Файлы базы, окружение и артефакты сборки исключены из Git.

## Сборка и установка пакета

```console
uv build
uvx twine check dist/*
uv tool install dist/primitive_db-0.1.0-py3-none-any.whl
database
```

`uv build` создаёт wheel и исходный архив. `twine check` проверяет
метаданные локально; публикация на PyPI не требуется.
`uv tool install` устанавливает CLI в отдельное окружение.
При необходимости добавьте каталог инструментов в PATH командой
`uv tool update-shell` и перезапустите терминал.

## Демонстрация

[![asciicast](https://asciinema.org/a/vfFZ03WOTGUkcz1x.svg)](https://asciinema.org/a/vfFZ03WOTGUkcz1x)
