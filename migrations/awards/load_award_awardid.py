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
    CREATE TABLE IF NOT EXISTS awards (
        id INT PRIMARY KEY, 
        name VARCHAR(255) NOT NULL
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/award_id_final.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        award_id, award_name = row
        cursor.execute("""
            INSERT INTO awards (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (award_id, award_name))


# Step 4: Commit the changes
conn.commit()

# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Awards data loaded successfully!")
