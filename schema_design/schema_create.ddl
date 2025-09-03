-- Создаем схему
CREATE SCHEMA IF NOT EXISTS content;

SET search_path TO content,public;

-- Таблица: genre - жанры фильмов
CREATE TABLE genre (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Запрещаем повторения в жанрах
CREATE UNIQUE INDEX ux_genre_name ON genre (lower(name));


-- Таблица: film_work
CREATE TABLE film_work (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date DATE,
    rating NUMERIC(3,1) CHECK (rating >= 0 AND rating <= 10),
    type VARCHAR(20) NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Для поиска по названию
CREATE INDEX idx_film_work_title ON film_work (lower(title));

-- Таблица: person
CREATE TABLE person (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT now(),
    modified TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Для поиска по имени
CREATE INDEX idx_person_full_name ON person (lower(full_name));

-- Таблица: genre_film_work (связь между genre и film_work)
-- ============================================
CREATE TABLE genre_film_work (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    genre_id UUID NOT NULL REFERENCES genre(id) ON DELETE CASCADE,
    film_work_id UUID NOT NULL REFERENCES film_work(id) ON DELETE CASCADE,
    created TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ux_genre_film UNIQUE (genre_id, film_work_id)
);

-- Для ускорения фильтрации
CREATE INDEX idx_genre_film_work_genre_id ON genre_film_work (genre_id);
CREATE INDEX idx_genre_film_work_film_work_id ON genre_film_work (film_work_id);

-- Таблица: person_film_work (связь между person и film_work)
CREATE TABLE person_film_work (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    film_work_id UUID NOT NULL REFERENCES film_work(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK,
    created TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ux_person_film UNIQUE (person_id, film_work_id, role)
);

-- Для ускорения фильтрации
CREATE INDEX idx_person_film_work_person_id ON person_film_work (person_id);
CREATE INDEX idx_person_film_work_film_work_id ON person_film_work (film_work_id);
CREATE INDEX idx_person_film_work_role ON person_film_work (role);
