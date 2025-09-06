import dataclasses
import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


def convert_sqlite_field(sqlite_field: str) -> datetime:
    """
    Converts an SQLite timestamp to datetime.

    Args:
        sqlite_field: The SQLite timestamp as a datetime object.

    Returns:
        A PostgreSQL timestamp as a datetime object, or None if the conversion fails.
    """
    if isinstance(sqlite_field, str):
        try:
            sqlite_field = str(uuid.UUID(sqlite_field))
        except ValueError:
            if sqlite_field.split("-")[0].isdigit():
                try:
                    sqlite_field = datetime.strptime(sqlite_field, '%Y-%m-%d %H:%M:%S.%f+00')
                except ValueError:
                    try:
                        sqlite_field = datetime.strptime(sqlite_field, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
            # else:
            #     sqlite_field = f"E'{sqlite_field}'"
    return sqlite_field


@dataclass
class SQLDataClass:
    """
    Базовый датакласс с идентификатором, временами создания/модификации и логикой формирования запросов
    """
    id: Optional[str]
    created: datetime
    modified: datetime

    def __init__(self, column_names: list, db_row: list):
        """
        Создаем датакласс из названия столбцов и строки таблицы
        Args:
        column_names: Список строк с именами.
        db_row: список с результатами select-запроса
        """
        field_names = [col.replace("_at", "").replace("updated", "modified") for col in column_names]
        for attr, value in zip(field_names, db_row):
            setattr(self, str(attr), convert_sqlite_field(value))

    def get_data(self) -> tuple:
        """
        Выдаем данные в виде tuple в порядке нахождения полей датакласса
        """
        return tuple([getattr(self, fn) for fn in self.get_field_names()])

    def get_table_name(self) -> str:
        """
        Имя таблицы в БД совпадает с именем класса в нижнем регистре
        """
        return self.__class__.__name__.lower()

    def get_select_query(self):
        """
        Запрос для забора данных из SQLite.
        """
        return f"SELECT * FROM {self.get_table_name()}"

    def get_insert_query(self) -> str:
        """
        Запрос для вставки данных в Postgres
        """
        field_names = self.get_field_names()
        return f"""INSERT INTO content.{self.get_table_name()} 
        ({", ".join(field_names)}) VALUES ({", ".join(["%s" for f in field_names])}) ON CONFLICT DO NOTHING;
                """

    def get_field_names(self) -> list:
        return [f.name for f in dataclasses.fields(self)]

@dataclass
class Genre(SQLDataClass):
    """
    Датакласс жанров
    """
    name: str
    description: Optional[str] = None

    def __init__(self, column_names: list, db_row: list):
        super().__init__(column_names, db_row)

@dataclass
class Person(SQLDataClass):
    """
    Датакласс персон
    """
    full_name: str

    def __init__(self, column_names: list, db_row: list):
        super().__init__(column_names, db_row)


@dataclass
class FilmWork(SQLDataClass):
    """
    Датакласс для основной таблицы с видео
    """
    title: str
    description: Optional[str]
    creation_date: Optional[datetime.date]
    rating: float
    type: str

    def __init__(self, column_names: list, db_row: list):
        super().__init__(column_names, db_row)
        if hasattr(self, 'type'):
            self.type = self.type.replace('movie','Film')

    def get_table_name(self) -> str:
        """
        В данном случае вставляем подчеркивание
        """
        return "film_work"

@dataclass
class GenreFilmWork(SQLDataClass):
    """
    Датакласс для таблицы связей genre_film_work.
    """
    genre_id: str
    film_work_id: str

    def __init__(self, column_names: list, db_row: list):
        super().__init__(column_names, db_row)

    def get_field_names(self) -> list:
        """
        Исключаем поле modified
        """
        return [fn for fn in super().get_field_names() if fn != 'modified']

    def get_table_name(self) -> str:
        """
        В данном случае вставляем подчеркивание
        """
        return "genre_film_work"


@dataclass
class PersonFilmWork(SQLDataClass):
    """
    Датакласс для таблицы связей person_film_work.
    """
    person_id: str
    film_work_id: str
    role: str

    def __init__(self, column_names: list, db_row: list):
        super().__init__(column_names, db_row)

    def get_field_names(self) -> list:
        """
        Исключаем поле modified
        """
        return [fn for fn in super().get_field_names() if fn != 'modified']

    def get_table_name(self) -> str:
        """
        В данном случае вставляем подчеркивание
        """
        return "person_film_work"


# Множество датаклассов для копирования данных
movies_dcs = [Genre, Person, FilmWork, GenreFilmWork, PersonFilmWork]
