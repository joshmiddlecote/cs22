import psycopg2 # type: ignore
import csv
import os 
from dotenv import load_dotenv

def create_languages_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            id SERIAL PRIMARY KEY,
            code VARCHAR(10),
            name VARCHAR(100)
        );
    """)
    conn.commit()

def insert_languages_data(cursor, conn):
    with open('../data/ml-latest-small/languages.csv', newline='', encoding='utf-8') as csvfile:
        languages_csvreader = csv.reader(csvfile)
        next(languages_csvreader)

        for row in languages_csvreader:
            id, code, name = row
            sql = """
                INSERT INTO languages(id, code, name) VALUES(%s, %s, %s)
            """
            cursor.execute(sql, (id, code, name))
    
    conn.commit()

def main():
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

    create_languages_table(cursor, conn)
    insert_languages_data(cursor, conn)

    cursor.close()
    conn.close()

    print("Language data loaded successfully!")

if __name__ == "__main__":
    main()