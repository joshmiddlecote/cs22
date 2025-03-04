from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_password}@localhost/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_audience_ratings(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT title, average_rating, num_ratings, poster from movies where id = %s;", (str(id),))
            rating_data = cursor.fetchone()
            if rating_data:
                return {"id": id, "title": rating_data[0], "average_rating": round(rating_data[1], 1), "num_ratings": rating_data[2], "poster": rating_data[3]}
            return None
        
def get_ratings_distribution(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT rating_1, rating_2, rating_3, rating_4, rating_5 FROM movies WHERE id = %s;", (str(id),))
            rating_distribution = cursor.fetchone()
            if rating_distribution:
                return {"rating_1": rating_distribution[0], "rating_2": rating_distribution[1], "rating_3": rating_distribution[2], "rating_4": rating_distribution[3], "rating_5": rating_distribution[4]}
            return None
        
def get_movie_genre(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT g.name
            FROM movie_genres mg
            JOIN genres g ON mg.genre_id = g.id
            WHERE mg.movie_id = %s;
            """, (str(id),))
            
            genres = cursor.fetchall()
            if genres == []:
                return None
            
            genres_string = ", ".join(genre[0] for genre in genres)
    
            return {'genre_name': genres_string}
        
def get_similar_highly_rated_movies_same_genre(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH high_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating >= 4
            ),

            other_high_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN high_raters hr ON r.userId = hr.userId
                WHERE r.movieId != %s AND rating >= 4
                GROUP BY r.movieId
            ),
                           
            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            )

            SELECT DISTINCT m.id, m.title, m.poster, m.average_rating, m.num_ratings, ohrm.avg_rating, ohrm.rating_count
            FROM movies m
            JOIN other_high_rated_movies ohrm ON m.id = ohrm.movieId
            JOIN movie_genres mg ON mg.movie_id = m.id
            WHERE mg.genre_id IN (SELECT genre_id FROM input_movie_genre)
            ORDER BY ohrm.avg_rating DESC, ohrm.rating_count DESC
            LIMIT 5;
            """, (str(id), str(id), str(id),))

            similar_movies_same_genre_high = cursor.fetchall()

            if similar_movies_same_genre_high == []:
                return None

            similar_movies_same_genre_high = [{'id': movie[0], 'title': movie[1], 'poster': movie[2], 'average_rating': round(movie[3], 1), 'num_ratings': movie[4], 'genre': get_movie_genre(movie[0])['genre_name']} for movie in similar_movies_same_genre_high]

            return similar_movies_same_genre_high

def get_similar_lowly_rated_movies_same_genre(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH low_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating <= 3
            ),

            other_low_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN low_raters lr ON r.userId = lr.userId
                WHERE r.movieId != %s AND rating <= 3
                GROUP BY r.movieId
            ),
                           
            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            )

            SELECT DISTINCT m.id, m.title, m.poster, m.average_rating, m.num_ratings, olrm.avg_rating, olrm.rating_count
            FROM movies m
            JOIN other_low_rated_movies olrm ON m.id = olrm.movieId
            JOIN movie_genres mg ON mg.movie_id = m.id
            WHERE mg.genre_id IN (SELECT genre_id FROM input_movie_genre)
            ORDER BY olrm.avg_rating ASC, olrm.rating_count ASC
            LIMIT 5;
            """, (str(id), str(id), str(id),))

            similar_movies_same_genre_low = cursor.fetchall()

            if similar_movies_same_genre_low == []:
                return None

            similar_movies_same_genre_low = [{'id': movie[0], 'title': movie[1], 'poster': movie[2], 'average_rating': round(movie[3], 1), 'num_ratings': movie[4], 'genre': get_movie_genre(movie[0])['genre_name']} for movie in similar_movies_same_genre_low]

            return similar_movies_same_genre_low

def get_similar_highly_rated_movies_different_genre(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH high_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating >= 4
            ),

            other_high_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN high_raters hr ON r.userId = hr.userId
                WHERE r.movieId != %s AND rating >= 4
                GROUP BY r.movieId
            ),
                           
            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            )

            SELECT DISTINCT m.id, m.title, m.poster, m.average_rating, m.num_ratings, ohrm.avg_rating, ohrm.rating_count 
            FROM movies m
            JOIN other_high_rated_movies ohrm ON m.id = ohrm.movieId
            WHERE NOT EXISTS (
                SELECT 1
                FROM movie_genres mg 
                WHERE mg.movie_id = m.id
                AND mg.genre_id IN (SELECT genre_id FROM input_movie_genre)
            )
            ORDER BY ohrm.avg_rating DESC, ohrm.rating_count DESC
            LIMIT 5;
            """, (str(id), str(id), str(id),))

            similar_movies_diff_genre_high = cursor.fetchall()

            if similar_movies_diff_genre_high == []:
                return None

            similar_movies_diff_genre_high = [{'id': movie[0], 'title': movie[1], 'poster': movie[2], 'average_rating': round(movie[3], 1), 'num_ratings': movie[4], 'genre': get_movie_genre(movie[0])['genre_name']} for movie in similar_movies_diff_genre_high]

            return similar_movies_diff_genre_high

def get_similar_lowly_rated_movies_different_genre(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH low_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating <= 3
            ),

            other_low_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN low_raters lr ON r.userId = lr.userId
                WHERE r.movieId != %s AND rating <= 3
                GROUP BY r.movieId
            ),
                           
            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            )

            SELECT DISTINCT m.id, m.title, m.poster, m.average_rating, m.num_ratings, olrm.avg_rating, olrm.rating_count 
            FROM movies m
            JOIN other_low_rated_movies olrm ON m.id = olrm.movieId
            WHERE NOT EXISTS (
                SELECT 1
                FROM movie_genres mg 
                WHERE mg.movie_id = m.id
                AND mg.genre_id IN (SELECT genre_id FROM input_movie_genre)
            )
            ORDER BY olrm.avg_rating ASC, olrm.rating_count ASC
            LIMIT 5;
            """, (str(id), str(id), str(id),))

            similar_movies_diff_genre_low = cursor.fetchall()

            if similar_movies_diff_genre_low == []:
                return None

            similar_movies_diff_genre_low = [{'id': movie[0], 'title': movie[1], 'poster': movie[2], 'average_rating': round(movie[3], 1), 'num_ratings': movie[4], 'genre': get_movie_genre(movie[0])['genre_name']} for movie in similar_movies_diff_genre_low]

            return similar_movies_diff_genre_low
        

def get_other_highly_rated_genres(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH high_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating >= 4
            ),

            other_high_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN high_raters hr ON r.userId = hr.userId
                WHERE r.movieId != %s AND r.rating >= 4
                GROUP BY r.movieId
            ),

            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            ),

            genre_high_ratings AS (
                SELECT g.name, SUM(hrm.rating_count) AS high_rating_count
                FROM other_high_rated_movies hrm
                JOIN movie_genres mg ON hrm.movieId = mg.movie_id
                JOIN genres g ON mg.genre_id = g.id
                WHERE mg.genre_id NOT IN (SELECT genre_id FROM input_movie_genre)
                GROUP BY g.name
            )

            SELECT name
            FROM genre_high_ratings
            ORDER BY high_rating_count DESC
            LIMIT 1;
            """ , (str(id), str(id), str(id),))

            genre_high = cursor.fetchall()

            if genre_high == []:
                return None

            genre_high_string = ", ".join(genre[0] for genre in genre_high)
    
            return {'genre_name': genre_high_string}

def get_other_lowly_rated_genres(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            WITH low_raters AS (
                SELECT userId
                FROM ratings
                WHERE movieId = %s AND rating >= 5
            ),

            other_low_rated_movies AS (
                SELECT r.movieId, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
                FROM ratings r
                JOIN low_raters lr ON r.userId = lr.userId
                WHERE r.movieId != %s AND r.rating <= 1
                GROUP BY r.movieId
            ),

            input_movie_genre AS (
                SELECT genre_id FROM movie_genres WHERE movie_id = %s
            ),

            genre_low_ratings AS (
                SELECT g.name, SUM(lrm.rating_count) AS low_rating_count
                FROM other_low_rated_movies lrm
                JOIN movie_genres mg ON lrm.movieId = mg.movie_id
                JOIN genres g ON mg.genre_id = g.id
                WHERE mg.genre_id NOT IN (SELECT genre_id FROM input_movie_genre)
                GROUP BY g.name
            )

            SELECT name
            FROM genre_low_ratings
            ORDER BY low_rating_count DESC
            LIMIT 1;
            """ , (str(id), str(id), str(id),))

            genre_low = cursor.fetchall()

            if genre_low == []:
                return None

            genre_low_string = ", ".join(genre[0] for genre in genre_low)
    
            return {'genre_name': genre_low_string}