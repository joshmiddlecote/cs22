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

def get_all_movies(limit=10, offset=0, year=None, rating=None):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM movies WHERE 1=1 "
            (sql_for_filters, params, sql_with_offset, params_with_offset) = maybe_filter_by_params(sql, year, rating, limit, offset)
            cursor.execute(sql_with_offset, tuple(params_with_offset))
            movies = cursor.fetchall()


            count_movies_sql = "SELECT COUNT(*) FROM movies WHERE 1=1 " + sql_for_filters
            cursor.execute(count_movies_sql, tuple(params))
            total_movies = cursor.fetchone()[0]
            
            total_pages = (total_movies + limit - 1) // limit if limit > 0 else 0
            movies =  [{'id': movie[0], 'title': movie[1], 'runtime': movie[3], 'rating': round(movie[6], 2), 'tagline': movie[12]} for movie in movies]

            return (movies, total_pages)
        
def get_movie_by_movie_id(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movies WHERE id = %s;;
            """, (str(id),))

            movie = cursor.fetchone()
            return {'id': movie[0], 'title': movie[1], 'year_released': movie[2], 
                    'runtime': movie[3], 'director': movie[4], 'language_id': movie[5], 
                    'average_rating': movie[6], 'num_ratings': movie[7],
                    'budget': movie[9], 'revenue': movie[10],
                    'overview': movie[11], 'tagline': movie[12]}
        
def maybe_filter_by_params(sql, year, rating, limit, offset):
    filters = []
    params = []

    if year != None and year != "":
        filters.append("year_released >= %s ")
        params.append(int(year))
    
    if rating != None and rating != "":
        filters.append("average_rating >= %s ")
        params.append(float(rating))

    sql_for_filters = f"AND {' AND '.join(filters)} " if filters else ""
    sql_with_offset = f"{sql} {sql_for_filters}LIMIT %s OFFSET %s"
    
    params_with_offset = params + [limit, offset]

    return sql_for_filters, params, sql_with_offset, params_with_offset

        
