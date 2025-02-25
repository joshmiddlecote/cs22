import psycopg2
import csv
import os
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


# Step 2: Create the actor_mapping table (if it doesn't exist already)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_ratings (
        userid VARCHAR(255) NOT NULL, 
        movie_id INT NOT NULL,
        rating FLOAT NOT NULL,
        time_stamp VARCHAR(255) NOT NULL,
        PRIMARY KEY (userid, movie_id)
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/personality-isf2018/ratings.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        userid, movie_id, rating, time_stamp = row
        cursor.execute("""
            INSERT INTO user_ratings (userid, movie_id, rating, time_stamp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (userid, movie_id)
            DO UPDATE SET 
                rating = EXCLUDED.rating,
                time_stamp = EXCLUDED.time_stamp
            WHERE user_ratings.time_stamp < EXCLUDED.time_stamp;
        """, (userid, movie_id, rating, time_stamp)) # update only if there is a newer rating


# Step 4: Commit the changes
conn.commit()

# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("User ratings loaded successfully!")
