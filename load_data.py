import psycopg2
import csv

# Database connection details
host = "db"
dbname = " "
user = " "
password = " "

# Step 1: Connect to PostgreSQL database
conn = psycopg2.connect(
    host=host, 
    database=dbname, 
    user=user, 
    password=password
)
cursor = conn.cursor()

# Step 2: Create the movies table (if it doesn't exist already)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        movieId INT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        genres VARCHAR(255)
    );
""")
conn.commit()

# Step 3: Open the CSV file and load data into the table
with open('data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # Skip the header row
    
    for row in csvreader:
        movie_id, title, genres = row
        cursor.execute("""
            INSERT INTO movies (movieId, title, genres)
            VALUES (%s, %s, %s)
            ON CONFLICT (movieId) DO NOTHING;  -- Avoid duplicate entries if the movie already exists
        """, (movie_id, title, genres))

# Commit the changes
conn.commit()

# Step 4: Close the connection and cursor
cursor.close()
conn.close()

print("Data loaded successfully!")
