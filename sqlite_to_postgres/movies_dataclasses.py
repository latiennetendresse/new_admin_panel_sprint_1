import datetime
import uuid
from dataclasses import dataclass, field


@dataclass
class Genre:
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Person:
    id: uuid.UUID
    full_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class Filmwork:
    id: uuid.UUID
    title: str
    description: str
    creation_date: datetime.datetime
    file_path: str
    rating: float
    type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class GenreFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime.datetime


@dataclass
class PersonFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime.datetime
