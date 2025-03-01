import psycopg2
import csv
import os 
import re
from dotenv import load_dotenv


def drop_tables(cursor, conn):
    cursor.execute("""
        DROP TABLE IF EXISTS ratings, user_ratings_all_movies, user_ratings_by_genre CASCADE;
    """)
    conn.commit()


def create_ratings_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings(
            userId INT NOT NULL,
            movieId INT NOT NULL,
            rating FLOAT NOT NULL,
            timestamp INT NOT NULL,
            PRIMARY KEY (userId, movieId),
            FOREIGN KEY (movieId) REFERENCES movies(id)
        );
    """)


def create_user_ratings_all_movies_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings_all_movies(
            id INT PRIMARY KEY,
            avg_rating FLOAT DEFAULT 0, 
            variance FLOAT DEFAULT 0, 
            total_ratings INT DEFAULT 0
        );
    """)
    conn.commit()


def create_user_ratings_by_genre_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings_by_genre(
            id SERIAL PRIMARY KEY,
            user_id INT, 
            genre_id INT REFERENCES genres(id),
            avg_rating FLOAT DEFAULT 0, 
            variance FLOAT DEFAULT 0, 
            total_ratings INT DEFAULT 0
        );
    """)
    conn.commit()


def insert_ratings_table(cursor, conn):
    with open('data/ml-latest-small/ratings.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            userId = int(row['userId'])
            movieId = int(row['movieId'])
            rating = float(row['rating'])
            timestamp = int(row['timestamp'])

            cursor.execute("""
                INSERT INTO ratings(userId, movieId, rating, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (userId, movieId)
                DO UPDATE SET 
                    rating = EXCLUDED.rating,
                    timestamp = EXCLUDED.timestamp
                WHERE ratings.timestamp < EXCLUDED.timestamp;
            """, (userId, movieId, rating, timestamp))

        conn.commit()


def insert_user_ratings_all_movies_table(cursor, conn):
    with open('data/ml-latest-small/user_ratings_all_movies.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            id = int(row['id'])
            avg_rating = float(row['avg_rating'])
            variance = float(row['variance'])
            total_ratings = int(row['total_ratings'])

            cursor.execute("""
                INSERT INTO user_ratings_all_movies(id, avg_rating, variance, total_ratings)
                VALUES (%s, %s, %s, %s)
            """, (id, avg_rating, variance, total_ratings))

        conn.commit()


def insert_user_ratings_by_genre_table(cursor, conn):
    with open('data/ml-latest-small/user_ratings_by_genre.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_id = int(row['id'])
            genre_id = int(row['genre_id'])
            avg_rating = float(row['avg_rating'])
            variance = float(row['variance'])
            total_ratings = int(row['total_ratings'])

            cursor.execute("""
                INSERT INTO user_ratings_by_genre(user_id, genre_id, avg_rating, variance, total_ratings)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, genre_id, avg_rating, variance, total_ratings))

        conn.commit()


def main():
    load_dotenv()
    host = "localhost"
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Make sure that all necessary environment variables are set
    if not dbname or not user or not password:
        raise ValueError("Environment variables DB_NAME, DB_USER, and DB_PASSWORD must be set.")

    try:
        conn = psycopg2.connect(
            host=host, 
            database=dbname, 
            user=user, 
            password=password
        )
        cursor = conn.cursor()

        # delete any existing tables
        drop_tables(cursor, conn)

        # create tables
        create_ratings_table(cursor, conn)
        create_user_ratings_all_movies_table(cursor, conn)
        create_user_ratings_by_genre_table(cursor, conn)
        print('Finished creating all tables')

        # insert data
        insert_ratings_table(cursor, conn)
        print('Finished inserting user ratings.')
        insert_user_ratings_all_movies_table(cursor, conn)
        print('Finished inserting user ratings for all movies data.')
        insert_user_ratings_by_genre_table(cursor, conn)
        print('Finished inserting user ratings by genre data')

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    print("User ratings data loaded successfully!")

if __name__ == "__main__":
    main()
