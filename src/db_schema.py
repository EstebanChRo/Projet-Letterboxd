from typing import List, Tuple

TABLE_DEFINITIONS: List[Tuple[str, str]] = [
    (
        "collection",
        """
        CREATE TABLE IF NOT EXISTS collection (
            id_collection SERIAL PRIMARY KEY,
            name TEXT,
            original_name TEXT,
            overview TEXT,
            poster_path TEXT,
            backdrop_path TEXT
        )
        """
    ),
    (
        "language",
        """
        CREATE TABLE IF NOT EXISTS language (
            iso_639_1 VARCHAR(8) PRIMARY KEY,
            english_name TEXT
        )
        """
    ),
    (
        "country",
        """
        CREATE TABLE IF NOT EXISTS country (
            iso_3166_1 VARCHAR(8) PRIMARY KEY,
            english_name TEXT
        )
        """
    ),
    (
        "production_company",
        """
        CREATE TABLE IF NOT EXISTS production_company (
            id SERIAL PRIMARY KEY,
            iso_3166_1 VARCHAR(8),
            name TEXT,
            logo_path TEXT,
            CONSTRAINT fk_production_company_country FOREIGN KEY (iso_3166_1) REFERENCES country (iso_3166_1)
        )
        """
    ),
    (
        "genre",
        """
        CREATE TABLE IF NOT EXISTS genre (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
        """
    ),
    (
        "person",
        """
        CREATE TABLE IF NOT EXISTS person (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
        """
    ),
    (
        "users",
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT,
            given_name TEXT,
            family_name TEXT,
            bio TEXT
        )
        """
    ),
    (
        "film",
        """
        CREATE TABLE IF NOT EXISTS film (
            tmdb_id INTEGER PRIMARY KEY,
            iso_639_1 VARCHAR(8),
            iso_3166_1 VARCHAR(8),
            id_collection INTEGER,
            title TEXT,
            original_title TEXT,
            release_date DATE,
            runtime INTEGER,
            budget BIGINT,
            homepage TEXT,
            letterboxd_uri TEXT,
            imdb_id TEXT,
            overview TEXT,
            tagline TEXT,
            poster_path TEXT,
            CONSTRAINT fk_film_language FOREIGN KEY (iso_639_1) REFERENCES language (iso_639_1),
            CONSTRAINT fk_film_country FOREIGN KEY (iso_3166_1) REFERENCES country (iso_3166_1),
            CONSTRAINT fk_film_collection FOREIGN KEY (id_collection) REFERENCES collection (id_collection)
        )
        """
    ),
    (
        "film_production_company",
        """
        CREATE TABLE IF NOT EXISTS film_production_company (
            tmdb_id INTEGER NOT NULL,
            id_production_company INTEGER NOT NULL,
            CONSTRAINT pk_film_production_company PRIMARY KEY (tmdb_id, id_production_company),
            CONSTRAINT fk_film_prod_company_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_film_prod_company_company FOREIGN KEY (id_production_company) REFERENCES production_company (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "film_genre",
        """
        CREATE TABLE IF NOT EXISTS film_genre (
            tmdb_id INTEGER NOT NULL,
            id_genre INTEGER NOT NULL,
            CONSTRAINT pk_film_genre PRIMARY KEY (tmdb_id, id_genre),
            CONSTRAINT fk_film_genre_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_film_genre_genre FOREIGN KEY (id_genre) REFERENCES genre (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "direct",
        """
        CREATE TABLE IF NOT EXISTS direct (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_direct PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_direct_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_direct_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "compose_the_music",
        """
        CREATE TABLE IF NOT EXISTS compose_the_music (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_compose_the_music PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_compose_the_music_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_compose_the_music_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "direct_the_photo",
        """
        CREATE TABLE IF NOT EXISTS direct_the_photo (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_direct_the_photo PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_direct_the_photo_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_direct_the_photo_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "product",
        """
        CREATE TABLE IF NOT EXISTS product (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_product PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_product_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_product_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "write",
        """
        CREATE TABLE IF NOT EXISTS write (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_write PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_write_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_write_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "act_in",
        """
        CREATE TABLE IF NOT EXISTS act_in (
            tmdb_id INTEGER NOT NULL,
            id_person INTEGER NOT NULL,
            CONSTRAINT pk_act_in PRIMARY KEY (tmdb_id, id_person),
            CONSTRAINT fk_act_in_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE,
            CONSTRAINT fk_act_in_person FOREIGN KEY (id_person) REFERENCES person (id) ON DELETE CASCADE
        )
        """
    ),
    (
        "user_watchlist",
        """
        CREATE TABLE IF NOT EXISTS user_watchlist (
            id_user INTEGER NOT NULL,
            tmdb_id INTEGER NOT NULL,
            CONSTRAINT pk_user_watchlist PRIMARY KEY (id_user, tmdb_id),
            CONSTRAINT fk_user_watchlist_user FOREIGN KEY (id_user) REFERENCES users (id) ON DELETE CASCADE,
            CONSTRAINT fk_user_watchlist_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE
        )
        """
    ),
    (
        "user_watch_film",
        """
        CREATE TABLE IF NOT EXISTS user_watch_film (
            id_user INTEGER NOT NULL,
            tmdb_id INTEGER NOT NULL,
            rating NUMERIC(3,1),
            rewatch BOOLEAN,
            tags TEXT,
            review TEXT,
            date DATE,
            liked BOOLEAN,
            CONSTRAINT pk_user_watch_film PRIMARY KEY (id_user, tmdb_id),
            CONSTRAINT fk_user_watch_film_user FOREIGN KEY (id_user) REFERENCES users (id) ON DELETE CASCADE,
            CONSTRAINT fk_user_watch_film_film FOREIGN KEY (tmdb_id) REFERENCES film (tmdb_id) ON DELETE CASCADE
        )
        """
    ),
]
