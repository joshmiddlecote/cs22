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
def get_audience_ratings_by_genre(genre_name):
    with get_db() as conn: 
        with conn.cursor() as cursor:  
            cursor.execute("SELECT id FROM genres WHERE genre_name = %s;", (genre_name,))
            genre_id_result = cursor.fetchone()

            if not genre_id_result:
                return []  # Return an empty list if the genre name is not found

            genre_id = genre_id_result[0]  # Extract the genre_id

            cursor.execute("""
                SELECT user_id, genre_id, avg_rating, variance, total_ratings
                FROM user_ratings_by_genre
                WHERE genre_id = %s AND avg_rating > 4;
            """, (genre_id,))
            
            # Fetch all rows returned by the query
            audience_ratings = cursor.fetchall()

            # Format the results as a list of dictionaries
            audience_ratings_formatted = [
                {
                    'id': row[0],
                    'genre_id': row[1],
                    'avg_rating': round(row[2], 2), 
                    'variance': round(row[3], 2), 
                    'total_ratings': row[4]
                }
                for row in audience_ratings
            ] 
            
            return audience_ratings_formatted
        


