import psycopg2
import csv
import os 
import re
from dotenv import load_dotenv

def create_users_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    """)
    conn.commit()

# CHANGED to add description column
def create_movie_lists(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie_planners(
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255)
        );
    """)
    conn.commit()

def create_movie_list_items(cursor, conn):
    cursor.execute("""
        CREATE TABLE movie_planner_items(
            id SERIAL PRIMARY KEY,
            movie_list_id INT REFERENCES movie_planners(id),
            movie_id INT REFERENCES movies(id)
        );
    """)
    conn.commit()

def main():
    load_dotenv()
    host = "localhost"
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
        DROP TABLE IF EXISTS movie_planners CASCADE;
    """)

    cursor.execute("""
        DROP TABLE IF EXISTS movie_planner_items CASCADE;
    """)

    create_users_table(cursor, conn)
    create_movie_lists(cursor, conn)
    create_movie_list_items(cursor, conn)

    cursor.close()
    conn.close()

    print("User data loaded successfully!")

if __name__ == "__main__":
    main()