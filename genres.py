import psycopg2
import csv
import os 
import re
from dotenv import load_dotenv


def drop_tables(cursor, conn):
    cursor.execute("""
        DROP TABLE IF EXISTS genre_links, movies, genres CASCADE;
    """)
    conn.commit()


def create_genres_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres(
            id INT PRIMARY KEY,
            genre_name VARCHAR(255) NOT NULL, 
            avg_rating FLOAT DEFAULT 0, 
            variance FLOAT DEFAULT 0, 
            total_ratings INT DEFAULT 0
        );
    """)
    conn.commit()


def create_genre_links_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genre_links(
            movie_id INT REFERENCES movies(id),
            genre_id INT REFERENCES genres(id),
            PRIMARY KEY (movie_id, genre_id)
        );
    """)
    conn.commit()



def insert_genres(cursor, conn):
    with open('data/ml-latest-small/genres.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            id = row['id']
            genre_name = row['genre_name']
            avg_rating = row['avg_rating']
            variance = row['variance']
            total_ratings = row['total_ratings']

            cursor.execute("""
                INSERT INTO genres (id, genre_name, avg_rating, variance, total_ratings)
                VALUES (%s, %s, %s, %s, %s);
            """, (id, genre_name, avg_rating, variance, total_ratings)) 

    conn.commit()


def insert_genre_links(cursor, conn):
    with open('data/ml-latest-small/genre_links.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movie_id'])
            genre_id = int(row['genre_id'])

            cursor.execute("""
                INSERT INTO genre_links(movie_id, genre_id)
                VALUES (%s, %s)
            """, (movie_id, genre_id))

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
        # create_movies_table(cursor, conn)
        create_genres_table(cursor, conn)
        create_genre_links_table(cursor, conn)
        print('Finished creating all tables')

        # insert data
        # insert_movies(cursor, conn)
        # print('Finished inserting movies data.')
        insert_genres(cursor, conn)
        print('Finished inserting genres data')
        insert_genre_links(cursor, conn)
        print('Finished inserting genre_links data.')

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    print("Genre data loaded successfully!")

if __name__ == "__main__":
    main()