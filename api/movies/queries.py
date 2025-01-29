from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_passsword = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_passsword}@localhost/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_all_movies(limit=10, offset=0):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movies LIMIT %s OFFSET %s;
            """, (limit, offset))

            movies = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM movies;")
            total_movies = cursor.fetchone()[0]
            
            total_pages = (total_movies + limit - 1) // limit if limit > 0 else 0
            movies =  [{'id': movie[0], 'title': movie[1], 'runtime': movie[3], 'overview': movie[11]} for movie in movies]

            return (movies, total_pages)
        
def get_movie_by_movie_id(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movies WHERE id = %s;;
            """, (str(id)))

            movie = cursor.fetchone()
            return {'id': movie[0], 'title': movie[1], 'year_released': movie[2], 
                    'runtime': movie[3], 'director': movie[4], 'language_id': movie[5], 
                    'average_rating': movie[6], 'num_ratings': movie[7],
                    'budget': movie[9], 'revenue': movie[10],
                    'overview': movie[11], 'tagline': movie[12]}
        