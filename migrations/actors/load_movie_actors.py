import psycopg2
import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Database connection details
host = "postgres_db"
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


# Step 1: Connect to PostgreSQL database
conn = psycopg2.connect(
    host=host, 
    database=dbname, 
    user=user, 
    password=password
)
cursor = conn.cursor()


# Step 2: Create the movies_actors table (if it doesn't exist already)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS film_cast (
        movie_id INT NOT NULL, 
        actor_id INT NOT NULL,
        PRIMARY KEY (movie_id, actor_id),
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        FOREIGN KEY (actor_id) REFERENCES actors(id)
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('../data/ml-latest-small/movie_actors_with_id.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        movie_id, actor_id = row
        cursor.execute("""
            INSERT INTO film_cast (movie_id, actor_id)
            VALUES (%s, %s)
            ON CONFLICT (movie_id, actor_id) DO NOTHING;
        """, (movie_id, actor_id))


# Step 4: Commit the changes
conn.commit()


# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Movie ID to Actor ID mapping data loaded successfully!")
