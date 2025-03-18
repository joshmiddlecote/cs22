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
    CREATE TABLE IF NOT EXISTS personality_data (
        userid VARCHAR(255) PRIMARY KEY, 
        openness FLOAT NOT NULL,
        agreeableness FLOAT NOT NULL,
        emotional_stability FLOAT NOT NULL,
        conscientiousness FLOAT NOT NULL,
        extraversion FLOAT NOT NULL,
        assigned_metric VARCHAR(255) NOT NULL,
        assigned_condition VARCHAR(255) NOT NULL,
        is_personalised INT NOT NULL,
        enjoy_watching INT NOT NULL
    );
""")

with open('../data/personality-isf2018/personality-data.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    for row in csvreader:
        userid, openness, agreeableness, emotional_stability, conscientiousness, extraversion, assigned_metric, assigned_condition, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, is_personalised, enjoy_watching = row
        cursor.execute("""
            INSERT INTO personality_data (userid, openness, agreeableness, emotional_stability, conscientiousness, extraversion, assigned_metric, assigned_condition, is_personalised, enjoy_watching)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (userid) DO NOTHING;
        """, (userid, openness, agreeableness, emotional_stability, conscientiousness, extraversion, assigned_metric, assigned_condition, is_personalised, enjoy_watching))

conn.commit()

cursor.close()
conn.close()

print("Personality data loaded successfully!")
