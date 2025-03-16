from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_password}@postgres_db/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def filter_movies_dataset(new_movie):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH genre_filter AS (
                SELECT m.id AS movie_id, COUNT(g.id) AS genre_match_count
                FROM movies m
                JOIN movie_genres mg ON m.id = mg.movie_id
                JOIN genres g ON mg.genre_id = g.id
                WHERE g.name IN %s
                GROUP BY m.id
            ),
            genre_count AS (
                SELECT COUNT(*) AS total FROM genre_filter
            ),
            director_match AS (
                SELECT m.id AS movie_id, COUNT(*) AS director_match_count
                FROM movies m
                JOIN unnest(string_to_array(m.director, ',')) AS dir ON dir IN %s
                GROUP BY m.id
            ),
            actor_match AS (
                SELECT fc.movie_id, COUNT(*) AS actor_match_count
                FROM film_cast fc
                JOIN actors a ON fc.actor_id = a.id
                WHERE a.name IN %s
                GROUP BY fc.movie_id
            ),
            ranked_movies AS (
                SELECT gf.movie_id,
                    COALESCE(dm.director_match_count, 0) AS director_matches,
                    COALESCE(am.actor_match_count, 0) AS actor_matches,
                    COALESCE(gf.genre_match_count, 0) AS genre_matches,
                    ROW_NUMBER() OVER (
                        ORDER BY COALESCE(dm.director_match_count, 0) DESC,
                                    COALESCE(am.actor_match_count, 0) DESC,
                                    COALESCE(gf.genre_match_count, 0) DESC,
                                    gf.movie_id
                    ) AS row_num
                FROM genre_filter gf
                LEFT JOIN director_match dm ON gf.movie_id = dm.movie_id
                LEFT JOIN actor_match am ON gf.movie_id = am.movie_id
            ),
            filtered_movies AS (
                SELECT movie_id
                FROM ranked_movies
                WHERE row_num <= 100
            )
            SELECT movie_id 
            FROM genre_filter 
            WHERE (SELECT total FROM genre_count) <= 100
            UNION 
            SELECT movie_id 
            FROM filtered_movies 
            WHERE (SELECT total FROM genre_count) > 100;
            """, (tuple(new_movie["genre"]), tuple(new_movie["director"]), tuple(new_movie["actor"])))

            filtered_movies = cursor.fetchall()

            if filtered_movies == []:
                return None

            filtered_movies = [movie[0] for movie in filtered_movies]

            return filtered_movies

def get_genre_weight(new_movie, movie_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH new_movie_genres AS (
                SELECT id FROM genres WHERE name IN %s
            ),
            existing_movie_genres AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            ),
            intersection_count AS (
                SELECT COUNT(*) AS intersection_size
                FROM movie_genres mg
                JOIN new_movie_genres nmg ON mg.genre_id = nmg.id
                WHERE mg.movie_id = %s
            ),
            union_count AS (
                SELECT COUNT(DISTINCT genre_id) AS union_size
                FROM (
                    SELECT genre_id FROM movie_genres WHERE movie_id = %s
                    UNION
                    SELECT id FROM new_movie_genres
                )
            )
            SELECT 
                (SELECT intersection_size FROM intersection_count) * 1.0 /
                NULLIF((SELECT union_size FROM union_count), 0) AS genre_weight;
            """, (tuple(new_movie["genre"]), str(movie_id), str(movie_id), str(movie_id),))

            genre_weight = cursor.fetchone()

            if genre_weight:
                return float(genre_weight[0])
            else:
                return None

def get_director_weight(new_movie, movie_id):
    director_values = ','.join(new_movie["director"])
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH new_movie_directors AS (
                SELECT unnest(string_to_array(%s, ',')) AS director_name
            ),
            existing_movie_directors AS (
                SELECT unnest(string_to_array(director, ',')) AS director_name
                FROM movies
                WHERE id = %s
            ),
            intersection_count AS (
                SELECT COUNT(*) AS intersecting_directors
                FROM new_movie_directors nmd
                JOIN existing_movie_directors emd ON nmd.director_name = emd.director_name
            )
            SELECT 
                COALESCE(
                    NULLIF((SELECT intersecting_directors FROM intersection_count) * 1.0 /
                        (SELECT COUNT(*) FROM new_movie_directors), 0),
                    0.1
                ) AS director_weight;
            """, (str(director_values), str(movie_id),))

            director_weight = cursor.fetchone()

            if director_weight:
                return float(director_weight[0])
            else:
                return None

def get_actor_weight(new_movie, movie_id):
    actor_values = ','.join(new_movie["actor"])
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH new_movie_actors AS (
                SELECT unnest(string_to_array(%s, ',')) AS actor_name
            ),
            existing_movie_actors AS (
                SELECT a.name AS actor_name
                FROM film_cast fc
                JOIN actors a ON fc.actor_id = a.id
                WHERE fc.movie_id = %s
            ),
            intersection_count AS (
                SELECT COUNT(*) AS intersecting_actors
                FROM new_movie_actors nma
                JOIN existing_movie_actors ema ON nma.actor_name = ema.actor_name
            )
            SELECT 
                COALESCE(
                    NULLIF((SELECT intersecting_actors FROM intersection_count) * 1.0 /
                        (SELECT COUNT(*) FROM new_movie_actors), 0),
                    0.1
                ) AS actor_weight;
            """, (str(actor_values), str(movie_id),))

            actor_weight = cursor.fetchone()

            if actor_weight:
                return float(actor_weight[0])
            else:
                return None

def get_budget_weight(new_movie, movie_id):
    budget = new_movie["budget"]
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT 
                LEAST(%s, m.budget) * 1.0 / 
                GREATEST(%s, m.budget) AS budget_ratio
            FROM movies m
            WHERE m.id = %s;
            """, (str(budget), str(budget), str(movie_id),))

            budget_weight = cursor.fetchone()

            if budget_weight:
                return float(budget_weight[0])
            else:
                return None

def get_movie_weight(new_movie, movie_id):
    genre_weight = get_genre_weight(new_movie, movie_id)
    director_weight = get_director_weight(new_movie, movie_id)
    actor_weight = get_actor_weight(new_movie, movie_id)
    budget_weight = get_budget_weight(new_movie, movie_id)

    if genre_weight and director_weight and actor_weight and budget_weight:
        movie_weight = (genre_weight + director_weight + actor_weight + budget_weight) / 4.0
        return movie_weight
    else: 
        return None

def get_movie_rating(movie_id):
    if movie_id:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT average_rating FROM movies WHERE movies.id = %s;", (str(movie_id),))

                average_rating = cursor.fetchone()

                if average_rating:
                    return float(average_rating[0])
                else:
                    return None
    else:
        return None

def calculate_rating(new_movie):
    movie_ids = filter_movies_dataset(new_movie)

    if not movie_ids:
        return None
    
    weighted_rating_sum = 0
    total_weight = 0

    for movie_id in movie_ids:
        rating = get_movie_rating(movie_id)
        weight = get_movie_weight(new_movie, movie_id)

        if rating and weight:
            weighted_rating_sum += (rating * weight)
            total_weight += weight

    predicted_rating = weighted_rating_sum / total_weight

    return predicted_rating

def movie_exists(movie_name):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM movies WHERE movies.title = %s;", (str(movie_name),))

            movie_id = cursor.fetchone()

            if movie_id:
                return int(movie_id[0])
            else:
                return None
