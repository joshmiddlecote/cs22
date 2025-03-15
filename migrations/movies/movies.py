import psycopg2 # type: ignore
import csv
import os 
import re
from dotenv import load_dotenv

def drop_tables(cursor, conn):
    cursor.execute("""
        DROP TABLE IF EXISTS movies CASCADE;
    """)

    conn.commit()

def create_movies_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            year_released INT NOT NULL,
            runtime INT DEFAULT 0,
            director VARCHAR(255),
            language_id INT REFERENCES languages(id),
            average_rating REAL,
            num_ratings BIGINT,
            variance REAL,
            rating_1 INT,
            rating_2 INT,
            rating_3 INT,
            rating_4 INT,
            rating_5 INT,
            budget BIGINT DEFAULT 0,
            revenue BIGINT DEFAULT 0,
            overview VARCHAR(2000) DEFAULT NULL,
            tagline VARCHAR(255) DEFAULT NULL,
            poster VARCHAR(500) DEFAULT NULL
        );
    """)
    conn.commit()

def handle_missing_data(row3):
    _, budget, revenue, _, overview, runtime, tagline, language_id = row3
    if budget == "":
        budget = 0
    if revenue == "":
        revenue = 0
    if runtime == "":
        runtime =  0

    return (budget, revenue, language_id, overview, runtime, tagline)

def insert_movie_data(cursor, conn):
    with open('../data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile, \
        open('../data/ml-latest-small/movie_average_ratings.csv', newline='', encoding='utf-8') as ratings_csvfile, \
        open('../data/ml-latest-small/movie_extra_details.csv', newline='', encoding='utf-8') as extra_details_csvfile, \
        open('../data/ml-latest-small/movies_with_posters.csv', newline='', encoding='utf-8') as posters_csvfile, \
        open('../data/ml-latest-small/movie_directors.csv', newline='', encoding='utf-8') as directors_csvfile, \
        open('../data/ml-latest-small/movie_ratings_count.csv', newline='', encoding='utf-8') as ratings_count_csvfile:

        movie_csvreader = csv.reader(csvfile)
        ratings_csvreader = csv.reader(ratings_csvfile)
        extra_details_csvreader = csv.reader(extra_details_csvfile)
        posters_csvreader = csv.reader(posters_csvfile)
        directors_csvreader = csv.reader(directors_csvfile)
        ratings_count_csvreader = csv.reader(ratings_count_csvfile)
        next(movie_csvreader)
        next(ratings_csvreader)
        next(extra_details_csvreader)
        next(posters_csvreader)
        next(directors_csvreader)
        next(ratings_count_csvreader)
        
        for row1, row2, row3, row4, row5, row6 in zip(movie_csvreader, ratings_csvreader, extra_details_csvreader, posters_csvreader, directors_csvreader, ratings_count_csvreader):
            movie_id, title, _ = row1
            _, average_rating, num_ratings, variance = row2
            (budget, revenue, language_id, overview, runtime, tagline) = handle_missing_data(row3)
            _,_,_, poster_url = row4
            _, director = row5
            _, rating_1, rating_2, rating_3, rating_4, rating_5 = row6

            year = re.search(r'\((\d{4})\)', title).group(1)
            title = re.sub(r'\s*\(\d{4}\)', '', title)

            cursor.execute("""
                INSERT INTO movies (id, title, year_released, runtime, director, language_id, average_rating, num_ratings, variance, rating_1, rating_2, rating_3, rating_4, rating_5, budget, revenue, overview, tagline, poster)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (movie_id, title, year, runtime, director, language_id, average_rating, num_ratings, variance, rating_1, rating_2, rating_3, rating_4, rating_5, budget, revenue, overview, tagline, poster_url))

    conn.commit()

def main():
    load_dotenv()
    host = "postgres_db"
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

    drop_tables(cursor, conn)
    create_movies_table(cursor, conn)
    insert_movie_data(cursor, conn)

    cursor.close()
    conn.close()

    print("Movie data loaded successfully!")

if __name__ == "__main__":
    main()