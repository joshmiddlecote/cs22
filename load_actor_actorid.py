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


# Step 2: Create the actor_mapping table (if it doesn't exist already)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS actor_mapping (
        actorId INT PRIMARY KEY, 
        actorName VARCHAR(255) NOT NULL
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/actor_mapping.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        actor_id, actor_name = row
        cursor.execute("""
            INSERT INTO actor_mapping (actorId, actorName)
            VALUES (%s, %s)
            ON CONFLICT (actorId) DO NOTHING;  -- Avoid duplicate entries
        """, (actor_id, actor_name))

# Step 4: Commit the changes
conn.commit()

# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Actor to actor id mapping data loaded successfully!")
