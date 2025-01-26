import psycopg2 # type: ignore
import csv
import os 
import re
from dotenv import load_dotenv

def create_movies_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            year_released INT NOT NULL,
            director VARCHAR(255),
            language VARCHAR(255),
            average_rating REAL,
            num_ratings BIGINT
        );
    """)
    conn.commit()

def insert_movie_data(cursor, conn):
    with open('data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile, open('data/ml-latest-small/movie_average_ratings.csv', newline='', encoding='utf-8') as ratings_csvfile:
        movie_csvreader = csv.reader(csvfile)
        ratings_csvreader = csv.reader(ratings_csvfile)
        next(movie_csvreader)
        next(ratings_csvfile)
        
        for row1, row2 in zip(movie_csvreader, ratings_csvreader):
            movie_id, title, genres = row1
            _, average_rating, num_ratings = row2
            year = re.search(r'\((\d{4})\)', title).group(1)
            title = re.sub(r'\s*\(\d{4}\)', '', title)

            cursor.execute("""
                INSERT INTO movies (id, title, year_released, average_rating, num_ratings)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (movie_id, title, year, average_rating, num_ratings))

    conn.commit()

def main():
    load_dotenv()
    host = "localhost"
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        host=host, 
        database=dbname, 
        user=user, 
        password=password
    )
    cursor = conn.cursor()

    create_movies_table(cursor, conn)
    insert_movie_data(cursor, conn)

    cursor.close()
    conn.close()

    print("Movie data loaded successfully!")

if __name__ == "__main__":
    main()