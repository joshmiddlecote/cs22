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

def get_all_movies(limit=10, offset=0, year=None, rating=None, genre_id=None, award_id=None, winner=None, actor_id=None, language_id=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT m.id, m.title, m.runtime, m.average_rating, m.tagline, m.poster FROM movies m "
            (sql, params) = maybe_filter_by_params(sql, year, rating, genre_id, award_id, winner, actor_id, language_id, limit, offset)

            cursor.execute(sql, tuple(params))
            movies = cursor.fetchall()
            
            movies =  [{'id': movie[0], 'title': movie[1], 'runtime': movie[2], 'rating': round(movie[3], 2), 'tagline': movie[4], "poster": movie[5]} for movie in movies]

            return movies
        
def get_movie_by_movie_id(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.id, m.title, m.year_released, m.runtime, m.director, l.name, m.average_rating, m.num_ratings, 
                    m.budget, m.revenue, m.overview, m.tagline, m.poster 
                FROM movies m INNER JOIN languages l ON l.id = m.language_id 
                WHERE m.id = %s;
            """, (str(id),))

            movie = cursor.fetchone()
            return {'id': movie[0], 'title': movie[1], 'year_released': movie[2], 
                    'runtime': movie[3], 'director': movie[4], 'language_name': movie[5], 
                    'average_rating': movie[6], 'num_ratings': movie[7],
                    'budget': movie[8], 'revenue': movie[9],
                    'overview': movie[10], 'tagline': movie[11], 'poster': movie[12]}
        
def get_movie_by_movie_name(name):
    with get_db() as conn:
        with conn.cursor() as cursor:
            lower_case_name = str(name).lower()
            cursor.execute("""
            SELECT m.id, m.title, m.year_released, m.runtime, m.director, l.name, m.average_rating, m.num_ratings, 
                    m.budget, m.revenue, m.overview, m.tagline, m.poster 
            FROM movies m INNER JOIN languages l ON l.id = m.language_id 
            WHERE LOWER(m.title) = %s ;
            """, (lower_case_name, ))

            movie = cursor.fetchone()

            if movie is None:
                return None
            else:
                return {'id': movie[0], 'title': movie[1], 'year_released': movie[2], 
                    'runtime': movie[3], 'director': movie[4], 'language_name': movie[5], 
                    'average_rating': movie[6], 'num_ratings': movie[7],
                    'budget': movie[8], 'revenue': movie[9],
                    'overview': movie[10], 'tagline': movie[11], 'poster': movie[12]}
            
def get_movie_for_movie_planner(movie_id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, title, runtime, average_rating, tagline, poster FROM movies WHERE id = %s;"

            cursor.execute(sql, (int(movie_id), ))
            movie = cursor.fetchone()
            
            return {'id': movie[0], 'title': movie[1], 'runtime': movie[2], 'rating': round(movie[3], 2), 'tagline': movie[4], "poster": movie[5]}
        
def maybe_filter_by_params(sql, year, rating, genre_id, award_id, winner, actor_id, language_id, limit, offset):
    params = []

    # need to process filters than need table joins first

    if genre_id != None and genre_id != "":
        sql += "INNER JOIN movie_genres mg ON mg.movie_id = m.id "

    if award_id != None and award_id != "":
        sql += "INNER JOIN award_wins a ON a.movie_id = m.id "

    if actor_id != None and actor_id != "":
        sql += "INNER JOIN film_cast fc ON fc.movie_id = m.id "

    if language_id != None and language_id != "":
        sql += "INNER JOIN languages l ON l.id = m.language_id "

    # we can then add our where clauses based on the filters 

    sql += " WHERE 1=1 "

    if year != None and year != "":
        sql += "AND m.year_released >= %s " # might change this to be IN() so we can have a range rather than >=
        params.append(int(year))
    
    if rating != None and rating != "":
        sql += "AND m.average_rating >= %s " # same as above for this
        params.append(float(rating))

    if genre_id != None and genre_id != "":
        sql += "AND mg.genre_id = %s "
        params.append(int(genre_id))
    
    if award_id != None and award_id != "":
        sql += "AND a.award_id = %s "
        params.append(int(award_id))
        if winner == "true":
            sql += "AND a.winner = true "

    if actor_id != None and actor_id != "":
        sql += "AND fc.actor_id = %s "
        params.append(int(actor_id))

    if language_id != None and language_id != "":
        sql += "AND l.id = %s "
        params.append(int(language_id))
    
    sql += "LIMIT %s OFFSET %s ;"
    params += [limit, offset]

    return sql, params

        
