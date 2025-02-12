from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_passsword = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_passsword}@localhost/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_all_genres():
     with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, name from genres where id != 16;" # we dont want to get id 16 as that is "(no genres listed)"
            cursor.execute(sql)
            genres = cursor.fetchall()
            genres = [{'id': genre[0], "name": genre[1]} for genre in genres]
            return genres