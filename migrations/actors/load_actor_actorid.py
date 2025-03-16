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
    CREATE TABLE IF NOT EXISTS actors (
        id INT PRIMARY KEY, 
        name VARCHAR(255) NOT NULL
    );
""")

with open('../data/ml-latest-small/actor_mapping.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        actor_id, actor_name = row
        cursor.execute("""
            INSERT INTO actors (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (actor_id, actor_name))

conn.commit()
cursor.close()
conn.close()

print("Actor to actor id mapping data loaded successfully!")
