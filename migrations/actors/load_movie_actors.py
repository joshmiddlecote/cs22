import psycopg2
import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Database connection details
host = "localhost"
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
    CREATE TABLE IF NOT EXISTS movie_actors (
        movieId INT NOT NULL, 
        actorId INT NOT NULL,
        PRIMARY KEY (movieId, actorId),
        FOREIGN KEY (movieId) REFERENCES movies(id) ON DELETE CASCADE,
        FOREIGN KEY (actorId) REFERENCES actor_mapping(actorId) ON DELETE CASCADE
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/movie_actors_with_id.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        movie_id, actor_id = row
        cursor.execute("""
            INSERT INTO movie_actors (movieId, actorId)
            VALUES (%s, %s)
            ON CONFLICT (movieId, actorId) DO NOTHING;  -- Avoid duplicate entries if the movie already exists
        """, (movie_id, actor_id))


# Step 4: Commit the changes
conn.commit()


# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Movie ID to Actor ID mapping data loaded successfully!")
