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

def get_all_movies():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movies;
            """)

            movies = cursor.fetchall()
            return [{'id': movie[0], 'title': movie[1], 'runtime': movie[3], 'overview': movie[11]} for movie in movies]
        
def get_movie_by_movie_id(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movies WHERE id = %s;;
            """, (str(id)))

            movie = cursor.fetchone()
            return [{'id': movie[0], 'title': movie[1], 'runtime': movie[3], 'overview': movie[11]}]