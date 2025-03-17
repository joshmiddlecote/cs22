from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_password}@postgres_db/{db_name}"

# Database connection manager
@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Function to fetch most popular genres with their stats
def get_cult_classic_genres():
    with get_db() as conn:  # Open a database connection
        with conn.cursor() as cursor:  # Create a cursor to execute SQL queries
            # SQL query to fetch genre_name, avg_rating, variance, and total_ratings
            cursor.execute("""
                SELECT id, name, avg_rating, variance, total_ratings
                FROM genres
                WHERE name <> '(no genres listed)'
                ORDER BY name;
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()

            popularity_scores = []
            W = 1000  # Adjust to fine-tune weighting of avg rating vs. total number of ratings
            popularity_scores = []

            for genre in genres:
                avg_rating = float(genre[2])
                total_ratings = genre[4]

                popularity_score = (avg_rating * W) + (total_ratings / W)
                popularity_scores.append(popularity_score)

            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'id': genres[i][0],
                    'genre_name': genres[i][1],
                    'avg_rating': round(genres[i][2], 2), 
                    'variance': round(genres[i][3], 2), 
                    'total_ratings': genres[i][4],
                    'popularity_score': popularity_scores[i]
                }
                for i in range(len(genres))
            ]

            genres_formatted_sorted = sorted(genres_formatted, key=lambda x: x['popularity_score'], reverse=True)
            
            return genres_formatted_sorted
        

def get_genres():
    with get_db() as conn:  # Open a database connection
        with conn.cursor() as cursor:  # Create a cursor to execute SQL queries
            # SQL query to fetch genre_name, avg_rating, variance, and total_ratings
            cursor.execute("""
                SELECT id, name, avg_rating, variance, total_ratings
                FROM genres
                WHERE name <> '(no genres listed)';
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()
            
            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'id': genres[i][0],
                    'genre_name': genres[i][1],
                    'avg_rating': round(genres[i][2], 2), 
                    'variance': round(genres[i][3], 2), 
                    'total_ratings': genres[i][4],
                }
                for i in range(len(genres))
            ]

            genres_formatted_sorted = sorted(genres_formatted, key=lambda x: x['variance'], reverse=True)
            
            return genres_formatted_sorted
        


def get_niche_interest_genres():
    with get_db() as conn:  # Open a database connection
        with conn.cursor() as cursor:  # Create a cursor to execute SQL queries
            # SQL query to fetch genre_name, avg_rating, variance, and total_ratings
            cursor.execute("""
                SELECT id, name, avg_rating, variance, total_ratings
                FROM genres
                WHERE name <> '(no genres listed)';
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()
            
            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'id': genres[i][0],
                    'genre_name': genres[i][1],
                    'avg_rating': round(genres[i][2], 2), 
                    'variance': round(genres[i][3], 2), 
                    'total_ratings': genres[i][4],
                }
                for i in range(len(genres))
                if genres[i][4] < 8000 and genres[i][2] > 3.5  # Apply filtering conditions

            ]

            genres_formatted_sorted = sorted(genres_formatted, key=lambda x: x['avg_rating'], reverse=True)
            
            return genres_formatted_sorted
        

def get_genre_data_by_id(genre_id):
     with get_db() as conn:  # Open a database connection
        with conn.cursor() as cursor:  # Create a cursor to execute SQL queries    
          cursor.execute("""
              SELECT 
                    COALESCE(SUM(m.rating_1), 0) AS rating_1,
                    COALESCE(SUM(m.rating_2), 0) AS rating_2,
                    COALESCE(SUM(m.rating_3), 0) AS rating_3,
                    COALESCE(SUM(m.rating_4), 0) AS rating_4,
                    COALESCE(SUM(m.rating_5), 0) AS rating_5,
                    g.name AS genre_name,
                    COALESCE(SUM(m.num_ratings), 0) AS total_ratings
              FROM movies m
              JOIN movie_genres mg ON m.id = mg.movie_id
              JOIN genres g ON mg.genre_id = g.id
              WHERE g.id = %s
              GROUP BY g.name;
          """, (genre_id, ))

          genre_data = cursor.fetchall()

          genres_formatted = [
                {
                    "rating_1": row[0],
                    "rating_2": row[1],
                    "rating_3": row[2],
                    "rating_4": row[3],
                    "rating_5": row[4],
                    "genre_name": row[5],
                    "total_ratings": row[6],
                }
                for row in genre_data  # Iterate over the fetched data
            ]

          return genres_formatted

def get_top_movies_by_genre_id(genre_id):
     with get_db() as conn:  # Open a database connection
        with conn.cursor() as cursor:  # Create a cursor to execute SQL queries    
          cursor.execute("""
              SELECT m.title, m.average_rating, m.num_ratings, m.poster
              FROM movies m
              JOIN movie_genres mg ON m.id = mg.movie_id
              JOIN genres g ON mg.genre_id = g.id
              WHERE g.id = %s
              ORDER BY m.num_ratings DESC
              LIMIT 10;
          """, (genre_id, ))

          top_movies = cursor.fetchall()

          top_movies_formatted = [
              {
                  "title": movie[0],
                  "avg_rating": round(movie[1], 2),
                  "total_ratings": movie[2],
                  "poster": movie[3]
              }
              for movie in top_movies
          ]

          return top_movies_formatted