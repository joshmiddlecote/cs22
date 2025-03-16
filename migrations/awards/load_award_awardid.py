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
    CREATE TABLE IF NOT EXISTS awards (
        id INT PRIMARY KEY, 
        name VARCHAR(255) NOT NULL
    );
""")

with open('../data/ml-latest-small/award_id_final.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        award_id, award_name = row
        cursor.execute("""
            INSERT INTO awards (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (award_id, award_name))

conn.commit()
cursor.close()
conn.close()

print("Awards data loaded successfully!")
