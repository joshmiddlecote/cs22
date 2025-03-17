import psycopg2
import csv
import os
from dotenv import load_dotenv

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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS award_wins (
        year_film INT,
        year_ceremony INT,
        ceremony INT,
        award_id INT REFERENCES awards(id),
        nominee VARCHAR(255),
        movie_id INT REFERENCES movies(id),
        winner BOOLEAN,
        PRIMARY KEY (award_id, nominee, movie_id)
    );
""")

with open('../data/ml-latest-small/awards_final.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        year_film = row['year_film']
        year_ceremony = row['year_ceremony']
        ceremony = row['ceremony']
        award_id = row['award_id']
        nominee = row['nominee']
        movie_id = row['movieId']
        winner = row['winner'] == 'True'

        if movie_id == 'N/A':
            continue

        if award_id == 'gUNKNOWN':
            continue

        cursor.execute("""
            INSERT INTO award_wins (year_film, year_ceremony, ceremony, award_id, nominee, movie_id, winner)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (award_id, nominee, movie_id) DO NOTHING;
        """, (year_film, year_ceremony, ceremony, award_id, nominee, movie_id, winner))

conn.commit()

cursor.close()
conn.close()

print("Awards data loaded successfully!")
