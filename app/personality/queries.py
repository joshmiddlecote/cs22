from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv
import numpy as np

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
            WHERE mg.movie_id = %s
            GROUP BY
                pg.genre_id, pg.name;"""
            
            cursor.execute(sql, (movie_id,))
            corr = cursor.fetchall()

            numeric_data = np.array([row[2:] for row in corr])

            column_averages = np.mean(numeric_data, axis=0)
            min_avg_index = np.argmin(column_averages)
            max_avg_index = np.argmax(column_averages)

            min_text = get_personality_index_min(min_avg_index)
            max_text = get_personality_index_max(max_avg_index)

            return {"max": max_text, "min": min_text}
        
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
            numeric_data = np.array([row[2:] for row in corr])

            column_averages = np.mean(numeric_data, axis=0)
            min_avg_index = np.argmin(column_averages)
            max_avg_index = np.argmax(column_averages)

            min_text = get_personality_index_min(min_avg_index)
            max_text = get_personality_index_max(max_avg_index)

            return {"max": max_text, "min": min_text}

def get_personality_index_max(index):
    match index:
        case 0:
            return "are more likely to be open people."
        case 1:
            return "are more likely to be agreeable."
        case 2:
            return "are more likely to be extraverted."
        case 3:
            return "are more likely to be emotionally stable."
        case 4:
            return "are more likely to be conscientious."
        
def get_personality_index_min(index):
    match index:
        case 0:
            return "are less likely to be open people."
        case 1:
            return "are less likely to be agreeable."
        case 2:
            return "are less likely to be extraverted."
        case 3:
            return "are less likely to be emotionally stable."
        case 4:
            return "are less likely to be conscientious."
