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

def get_all_languages():
     with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, name from languages where id != 16;" # we dont want to get id 16 as that is "(no genres listed)"
            cursor.execute(sql)
            languages = cursor.fetchall()
            languages = [{'id': language[0], "name": language[1]} for language in languages]
            return languages