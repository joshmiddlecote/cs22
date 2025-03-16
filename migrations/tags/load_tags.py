import psycopg2
import csv
import os
import requests
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
    CREATE TABLE IF NOT EXISTS tags (
        movie_id INT NOT NULL, 
        tag VARCHAR(255) NOT NULL,
        PRIMARY KEY (movie_id, tag),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    );
""")

with open('../data/ml-latest-small/tags.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        userId, movie_id, tag, timestamp = row
        cursor.execute("""
            INSERT INTO tags (movie_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (movie_id, tag) DO NOTHING;
        """, (movie_id, tag))

conn.commit()

cursor.close()
conn.close()

print("Tags loaded successfully!")
