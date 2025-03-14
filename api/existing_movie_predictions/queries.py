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

def get_preview_panel():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                WITH UserGenreCounts AS (
                    SELECT 
                        r.userId, 
                        COUNT(DISTINCT mg.genre_id) AS genre_count, -- Unique genres rated
                        COUNT(r.movieId) AS total_ratings -- Total movies rated
                    FROM ratings r
                    JOIN movie_genres mg ON r.movieId = mg.movie_id
                    GROUP BY r.userId
                )
                SELECT userId
                FROM UserGenreCounts
                ORDER BY genre_count DESC, total_ratings DESC
                LIMIT 50; -- Select top 50 diverse + active users
            """)
            
            preview_panel = [row[0] for row in cursor.fetchall()]
            return preview_panel  # List of user_ids

def get_predicted_ratings(movie_id):
    preview_panel = get_preview_panel()  # Get the selected panel

    if not preview_panel:
        return {"error": "No preview panel found"}

    with get_db() as conn:
        with conn.cursor() as cursor:
            # Get ratings from preview panel for the given movie
            cursor.execute("""
                SELECT rating
                FROM ratings
                WHERE movieId = %s AND userId = ANY(%s);
            """, (movie_id, preview_panel))
            
            panel_ratings = [row[0] for row in cursor.fetchall()]

            # Compute predicted rating
            predicted_rating = sum(panel_ratings) / len(panel_ratings) if panel_ratings else None

            cursor.execute("""
                SELECT title, average_rating, poster
                FROM movies
                WHERE id = %s;
            """, (movie_id,))
            
            movie_data = cursor.fetchone()

            if not movie_data:
                return {"error": "Movie not found"}

            return {
                "movie_id": movie_id,
                "movie_title": movie_data[0],
                "predicted_rating": round(predicted_rating, 2) if predicted_rating else None,
                "actual_rating": round(movie_data[1], 2) if movie_data[1] else None,
                "poster_url": movie_data[2]
            }
