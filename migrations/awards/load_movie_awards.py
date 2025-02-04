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


# Step 2: Create the awards table (if it doesn't exist already)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS awards (
        year_film INT,
        year_ceremony INT,
        ceremony INT,
        award_id VARCHAR(255),
        nominee VARCHAR(255),
        film VARCHAR(255),
        winner BOOLEAN,
        PRIMARY KEY (award_id, nominee, film)
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/awards.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)  # Read the file as a dictionary
    for row in csvreader:
        year_film = row['year_film']
        year_ceremony = row['year_ceremony']
        ceremony = row['ceremony']
        award_id = row['award_id']
        nominee = row['nominee']
        film = row['film']
        winner = row['winner'] == 'True'  # Convert winner to boolean (True/False)

        cursor.execute("""
            INSERT INTO awards (year_film, year_ceremony, ceremony, award_id, nominee, film, winner)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (award_id, nominee, film) DO NOTHING;  -- Avoid duplicate entries
        """, (year_film, year_ceremony, ceremony, award_id, nominee, film, winner))


# Step 4: Commit the changes
conn.commit()

# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Awards data loaded successfully!")
