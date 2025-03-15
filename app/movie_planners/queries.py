from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv
from movies import queries as movie_queries

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

def get_user_movie_planners(user_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM movie_planners WHERE user_id = %s ;"
            cursor.execute(sql, (int(user_id),))
            movie_planners = cursor.fetchall()
            return [{"id": planner[0], "name": planner[2]} for planner in movie_planners]
        
def get_movies_from_planners(planner_id, name):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * from movie_planner_items WHERE movie_list_id = %s ;"
            cursor.execute(sql, (int(planner_id),))
            movies = cursor.fetchall()
            return {"planner_id": planner_id, "name": name, "movies": [movie_queries.get_movie_for_movie_planner(movie_id=movie[2]) for movie in movies]}

def get_movies_from_user_id(user_id):
    movie_planners = get_user_movie_planners(user_id)
    return [get_movies_from_planners(planner["id"], planner["name"]) for planner in movie_planners]

def insert_new_movie_planner(user_id, name):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT INTO movie_planners(user_id, name) VALUES(%s, %s) RETURNING id;"
            cursor.execute(sql, tuple([user_id, name]))
            conn.commit()
            return cursor.fetchone()[0]
        
def insert_new_movie_planner_item(movie_planner_id, movie_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT INTO movie_planner_items(movie_list_id, movie_id) VALUES(%s, %s);"
            cursor.execute(sql, tuple([movie_planner_id, movie_id]))
            conn.commit()

def delete_movie_from_planner(movie_id, movie_planner_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM movie_planner_items WHERE movie_list_id = %s AND movie_id = %s ;"
            cursor.execute(sql, tuple([movie_planner_id, movie_id]))
            conn.commit()

def delete_movie_planner(movie_planner_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM movie_planner_items WHERE movie_list_id = %s"
            cursor.execute(sql, tuple([movie_planner_id]))
            conn.commit()
            sql = "DELETE FROM movie_planners WHERE id = %s"
            cursor.execute(sql, tuple([movie_planner_id]))
            conn.commit()