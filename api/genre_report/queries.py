from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_password}@localhost/{db_name}"

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
                SELECT genre_name, avg_rating, variance, total_ratings
                FROM genres
                ORDER BY genre_name;
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()

            popularity_scores = []
            W = 1000  # Adjust to fine-tune weighting of avg rating vs. total number of ratings
            popularity_scores = []

            for genre in genres:
                avg_rating = float(genre[1])
                total_ratings = genre[3]

                popularity_score = (avg_rating * W) + (total_ratings / W)
                popularity_scores.append(popularity_score)

            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'genre_name': genres[i][0],
                    'avg_rating': round(genres[i][1], 2), 
                    'variance': round(genres[i][2], 2), 
                    'total_ratings': genres[i][3],
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
                SELECT genre_name, avg_rating, variance, total_ratings
                FROM genres;
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()
            
            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'genre_name': genres[i][0],
                    'avg_rating': round(genres[i][1], 2), 
                    'variance': round(genres[i][2], 2), 
                    'total_ratings': genres[i][3],
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
                SELECT genre_name, avg_rating, variance, total_ratings
                FROM genres;
            """)
            
            # Fetch all rows returned by the query
            genres = cursor.fetchall()
            
            # Format the results as a list of dictionaries
            genres_formatted = [
                {
                    'genre_name': genres[i][0],
                    'avg_rating': round(genres[i][1], 2), 
                    'variance': round(genres[i][2], 2), 
                    'total_ratings': genres[i][3],
                }
                for i in range(len(genres))
                if genres[i][3] < 8000 and genres[i][1] > 3.5  # Apply filtering conditions

            ]

            genres_formatted_sorted = sorted(genres_formatted, key=lambda x: x['avg_rating'], reverse=True)
            
            return genres_formatted_sorted
        
