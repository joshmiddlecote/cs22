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
    CREATE TABLE IF NOT EXISTS tags (
        movie_id INT NOT NULL, 
        tag VARCHAR(255) NOT NULL,
        PRIMARY KEY (movie_id, tag),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/tags.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        userId, movie_id, tag, timestamp = row
        cursor.execute("""
            INSERT INTO tags (movie_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (movie_id, tag) DO NOTHING;
        """, (movie_id, tag))


# Step 4: Commit the changes
conn.commit()


# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Tags loaded successfully!")
