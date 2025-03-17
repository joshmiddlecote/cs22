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
    CREATE TABLE IF NOT EXISTS film_cast (
        movie_id INT NOT NULL, 
        actor_id INT NOT NULL,
        PRIMARY KEY (movie_id, actor_id),
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        FOREIGN KEY (actor_id) REFERENCES actors(id)
    );
""")

with open('../data/ml-latest-small/movie_actors_with_id.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        movie_id, actor_id = row
        cursor.execute("""
            INSERT INTO film_cast (movie_id, actor_id)
            VALUES (%s, %s)
            ON CONFLICT (movie_id, actor_id) DO NOTHING;
        """, (movie_id, actor_id))

conn.commit()

cursor.close()
conn.close()

print("Movie ID to Actor ID mapping data loaded successfully!")
