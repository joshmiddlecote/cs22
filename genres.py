import psycopg2
import csv
import os 
import re
from dotenv import load_dotenv
from collections import defaultdict
import statistics


def drop_tables(cursor, conn):
    cursor.execute("""
        DROP TABLE IF EXISTS genres_link, movies, genres CASCADE;
    """)
    conn.commit()


def create_genres_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres(
            id SERIAL PRIMARY KEY,
            genre_name VARCHAR(255) NOT NULL, 
            avg_rating FLOAT DEFAULT 0, 
            variance FLOAT DEFAULT 0, 
            total_ratings INT DEFAULT 0
        );
    """)
    conn.commit()


def create_genres_link_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres_link(
            movie_id INT REFERENCES movies(id),
            genre_id INT REFERENCES genres(id),
            PRIMARY KEY (movie_id, genre_id)
        );
    """)
    conn.commit()


def create_movies_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id INT PRIMARY KEY,
            title VARCHAR(255),
            genres VARCHAR(255)
        );
    """)
    conn.commit()


def insert_unique_genres(cursor, conn):
    unique_genres = set()
    with open('data/ml-latest-small/movies.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            genres = row['genres'].split('|')  # splits genres by '|'
            unique_genres.update(genres)      # add genres to set, ignoring duplicates

    for genre in unique_genres:
        cursor.execute("""
            INSERT INTO genres (genre_name)
            VALUES (%s);
        """, (genre,))  # ON CONFLICT to skip duplicates

    conn.commit()


def insert_movies(cursor, conn):
    with open('data/ml-latest-small/movies.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movieId'])
            title = row['title']
            genres = row['genres'].split('|')

            cursor.execute("""
                INSERT INTO movies(id, title, genres)
                VALUES (%s, %s, %s)
            """, (movie_id, title, genres))

        conn.commit()


def insert_genre_links(cursor, conn):
    with open('data/ml-latest-small/movies.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movieId'])
            genres = row['genres'].split('|')

            cursor.execute("""
                SELECT id FROM movies WHERE id = %s;
            """, (movie_id,))
            movie_id_primary = cursor.fetchone()  # Fetch one result

            for genre in genres:

              cursor.execute("""
                  SELECT id FROM genres WHERE genre_name = %s;
                """, (genre,))
              genre_id_primary = cursor.fetchone()

              cursor.execute("""
                  INSERT INTO genres_link(movie_id, genre_id)
                  VALUES (%s, %s)
              """, (movie_id_primary, genre_id_primary))

        conn.commit()


def get_genre_ratings_data(cursor, conn):
    ratings_by_genre = defaultdict(list)

    with open('data/ml-latest-small/ratings.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movieId'])
            rating = float(row['rating'])

            cursor.execute("""
                SELECT genre_id FROM genres_link
                WHERE movie_id = %s;
            """, (movie_id,))
            genre_ids = cursor.fetchall() # list of all genres the movie belongs to 
            genre_ids = [id[0] for id in genre_ids]

            for genre_id in genre_ids:
                ratings_by_genre[int(genre_id)].append(rating)
    # print('RATINGS BY GENRE: ', ratings_by_genre)
    insert_genre_ratings_data(cursor, conn, ratings_by_genre)


def insert_genre_ratings_data(cursor, conn, ratings_by_genre):
    for genre_id, ratings_list in ratings_by_genre.items():
        num_ratings = len(ratings_list)
        avg_rating = sum(ratings_list) / num_ratings 
        variance = statistics.variance(ratings_list)

        cursor.execute("""
            UPDATE genres
            SET avg_rating = %s, variance = %s, total_ratings = %s
            WHERE id = %s;
        """, (avg_rating, variance, num_ratings, genre_id))
    print('Finished inserting genre ratings data.')
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
        # drop_tables(cursor, conn)

        # create tables
        create_movies_table(cursor, conn)
        create_genres_table(cursor, conn)
        create_genres_link_table(cursor, conn)
        print('Finished creating all tables')

        # insert data
        # insert_unique_genres(cursor, conn)
        # print('Finished inserting genres id + name data.')
        # insert_movies(cursor, conn)
        # print('Finished inserting movies data.')
        # insert_genre_links(cursor, conn)
        # print('Finished inserting genre_links data.')

        get_genre_ratings_data(cursor, conn)

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
