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
    CREATE TABLE IF NOT EXISTS personality_user_ratings (
        userid VARCHAR(255) NOT NULL, 
        movie_id INT NOT NULL,
        rating FLOAT NOT NULL,
        time_stamp VARCHAR(255) NOT NULL,
        PRIMARY KEY (userid, movie_id)
    );
""")

with open('../data/personality-isf2018/ratings.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        userid, movie_id, rating, time_stamp = row
        cursor.execute("""
            INSERT INTO personality_user_ratings (userid, movie_id, rating, time_stamp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (userid, movie_id)
            DO UPDATE SET 
                rating = EXCLUDED.rating,
                time_stamp = EXCLUDED.time_stamp
            WHERE personality_user_ratings.time_stamp < EXCLUDED.time_stamp;
        """, (userid, movie_id, rating, time_stamp)) # update only if there is a newer rating

conn.commit()

cursor.close()
conn.close()

print("User ratings loaded successfully!")
