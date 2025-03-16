from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_passsword = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_passsword}@postgres_db/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_personality_correlation_movies(movie_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = """
            WITH avg_rating_per_genre_per_person AS (
            SELECT
                ur.userid,
                mg.genre_id,
                AVG(ur.rating) AS avg_rating
            FROM
                personality_user_ratings ur
            INNER JOIN
                movie_genres mg ON ur.movie_id = mg.movie_id
            GROUP BY
                ur.userid, mg.genre_id
            ),
            personality_genre AS (
                SELECT
                    gr.genre_id,
                    g.name,
                    ps.openness,
                    ps.agreeableness,
                    ps.extraversion,
                    ps.emotional_stability,
                    ps.conscientiousness,
                    gr.avg_rating
                FROM
                    personality_data ps
                INNER JOIN
                    avg_rating_per_genre_per_person gr ON ps.userid = gr.userid
                INNER JOIN
                    genres g ON gr.genre_id = g.id
            )
            SELECT
                pg.genre_id,
                pg.name,
                corr(openness, avg_rating) AS openness_corr,
                corr(agreeableness, avg_rating) AS agreeableness_corr,
                corr(extraversion, avg_rating) AS extraversion_corr,
                corr(emotional_stability, avg_rating) AS emotional_stability_corr,
                corr(conscientiousness, avg_rating) AS conscientiousness_corr
            FROM
                personality_genre pg
            INNER JOIN movie_genres mg ON mg.genre_id = pg.genre_id
            WHERE mg.movie_id = 1
            GROUP BY
                pg.genre_id, pg.name;"""
            
            cursor.execute(sql, (movie_id,))
            corr = cursor.fetchall()

            openness = 0
            agree = 0
            extraversion = 0
            emotstab = 0
            cons = 0

            for row in corr:
                openness += row[2]
                agree += row[3]
                extraversion += row[4]
                emotstab += row[5]
                cons += row[6]

            num_rows = len(corr)
            average_openness = openness / num_rows
            average_agree = agree / num_rows
            average_extraversion = extraversion / num_rows
            average_emotstab = emotstab / num_rows
            average_cons = cons / num_rows

            max, min = max(average_openness, average_openness, average_agree, average_extraversion, average_emotstab, average_cons), min(average_openness, average_openness, average_agree, average_extraversion, average_emotstab, average_cons)

            return [{"id": row[0], "name": row[1], "max": max} for row in corr]
        
def get_genre_personality_correlation(genre_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = """
            WITH avg_rating_per_genre_per_person AS (
                SELECT
                    ur.userid,
                    mg.genre_id,
                    AVG(ur.rating) AS avg_rating
                FROM
                    personality_user_ratings ur
                INNER JOIN
                    movie_genres mg ON ur.movie_id = mg.movie_id
                GROUP BY
                    ur.userid, mg.genre_id
            ),
            personality_genre AS (
                SELECT
                    gr.genre_id,
                    g.name,
                    ps.openness,
                    ps.agreeableness,
                    ps.extraversion,
                    ps.emotional_stability,
                    ps.conscientiousness,
                    gr.avg_rating
                FROM
                    personality_data ps
                INNER JOIN
                    avg_rating_per_genre_per_person gr ON ps.userid = gr.userid
                INNER JOIN
                    genres g ON gr.genre_id = g.id
            )
            SELECT
                genre_id,
                name,
                corr(openness, avg_rating) AS openness_corr,
                corr(agreeableness, avg_rating) AS agreeableness_corr,
                corr(extraversion, avg_rating) AS extraversion_corr,
                corr(emotional_stability, avg_rating) AS emotional_stability_corr,
                corr(conscientiousness, avg_rating) AS conscientiousness_corr
            FROM
                personality_genre
            WHERE genre_id = %s
            GROUP BY
                genre_id, name; """
            
            cursor.execute(sql, (genre_id,))
            corr = cursor.fetchall()
            return [{"id": row[0], "name": row[1], "openness": row[2], "agreeableness": row[3], "extraversion": row[4], "emotional_stability": row[5], "conscientiousness": row[6]} for row in corr]

                    