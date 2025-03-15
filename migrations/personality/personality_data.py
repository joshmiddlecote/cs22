import psycopg2
import csv
import os
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


# Step 2: Create the personality data table (if it doesn't exist already)
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
        movie_1 INT NOT NULL,
        rating_1 FLOAT NOT NULL,
        movie_2 INT NOT NULL,
        rating_2 FLOAT NOT NULL,
        movie_3 INT NOT NULL,
        rating_3 FLOAT NOT NULL,
        movie_4 INT NOT NULL,
        rating_4 FLOAT NOT NULL,
        movie_5 INT NOT NULL,
        rating_5 FLOAT NOT NULL,
        movie_6 INT NOT NULL,
        rating_6 FLOAT NOT NULL,
        movie_7 INT NOT NULL,
        rating_7 FLOAT NOT NULL,
        movie_8 INT NOT NULL,
        rating_8 FLOAT NOT NULL,
        movie_9 INT NOT NULL,
        rating_9 FLOAT NOT NULL,
        movie_10 INT NOT NULL,
        rating_10 FLOAT NOT NULL,
        movie_11 INT NOT NULL,
        rating_11 FLOAT NOT NULL,
        movie_12 INT NOT NULL,
        rating_12 FLOAT NOT NULL,
        is_personalised INT NOT NULL,
        enjoy_watching INT NOT NULL
    );
""")


# Step 3: Open the CSV file and load data into the table
with open('../data/personality-isf2018/personality-data.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        userid, openness, agreeableness, emotional_stability, conscentiousness, extraversion, assigned_metric, assigned_condition, movie_1, rating_1, movie_2, rating_2, movie_3, rating_3, movie_4, rating_4, movie_5, rating_5, movie_6, rating_6, movie_7, rating_7, movie_8, rating_8, movie_9, rating_9, movie_10, rating_10, movie_11, rating_11, movie_12, rating_12, is_personalised, enjoy_watching = row
        cursor.execute("""
            INSERT INTO personality_data (userid, openness, agreeableness, emotional_stability, conscientiousness, extraversion, assigned_metric, assigned_condition, movie_1, rating_1, movie_2, rating_2, movie_3, rating_3, movie_4, rating_4, movie_5, rating_5, movie_6, rating_6, movie_7, rating_7, movie_8, rating_8, movie_9, rating_9, movie_10, rating_10, movie_11, rating_11, movie_12, rating_12, is_personalised, enjoy_watching)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (userid) DO NOTHING;
        """, (userid, openness, agreeableness, emotional_stability, conscentiousness, extraversion, assigned_metric, assigned_condition, movie_1, rating_1, movie_2, rating_2, movie_3, rating_3, movie_4, rating_4, movie_5, rating_5, movie_6, rating_6, movie_7, rating_7, movie_8, rating_8, movie_9, rating_9, movie_10, rating_10, movie_11, rating_11, movie_12, rating_12, is_personalised, enjoy_watching))


# Step 4: Commit the changes
conn.commit()

# Step 5: Close the connection and cursor
cursor.close()
conn.close()

print("Personality data loaded successfully!")
