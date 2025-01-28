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
            runtime INT DEFAULT 0,
            director VARCHAR(255),
            language VARCHAR(255),
            average_rating REAL,
            num_ratings BIGINT,
            budget BIGINT DEFAULT 0,
            revenue BIGINT DEFAULT 0,
            overview VARCHAR(2000) DEFAULT NULL,
            tagline VARCHAR(255) DEFAULT NULL
        );
    """)
    conn.commit()

def handle_missing_data(row3):
    _, budget, revenue, language, overview, runtime, tagline = row3
    if budget == "":
        budget = 0
    if revenue == "":
        revenue = 0
    if runtime == "":
        runtime =  0

    return (budget, revenue, language, overview, runtime, tagline)

def insert_movie_data(cursor, conn):
    with open('data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile, open('data/ml-latest-small/movie_average_ratings.csv', newline='', encoding='utf-8') as ratings_csvfile, open('data/ml-latest-small/movie_extra_details.csv', newline='', encoding='utf-8') as extra_details_csvfile:
        movie_csvreader = csv.reader(csvfile)
        ratings_csvreader = csv.reader(ratings_csvfile)
        extra_details_csvreader = csv.reader(extra_details_csvfile)
        next(movie_csvreader)
        next(ratings_csvreader)
        next(extra_details_csvreader)
        
        for row1, row2, row3 in zip(movie_csvreader, ratings_csvreader, extra_details_csvreader):
            movie_id, title, genres = row1
            _, average_rating, num_ratings = row2
            (budget, revenue, language, overview, runtime, tagline) = handle_missing_data(row3)
            year = re.search(r'\((\d{4})\)', title).group(1)
            title = re.sub(r'\s*\(\d{4}\)', '', title)

            cursor.execute("""
                INSERT INTO movies (id, title, year_released, runtime, language, average_rating, num_ratings, budget, revenue, overview, tagline)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (movie_id, title, year, runtime, language, average_rating, num_ratings, budget, revenue, overview, tagline))

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