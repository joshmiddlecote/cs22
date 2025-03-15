from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_username = os.getenv("DB_USER")
db_passsword = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_passsword}@postgres_db/{db_name}"

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def get_all_actors():
     with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * from actors LIMIT 50;" # limit to 50 as there is over 11000 actors
            cursor.execute(sql)
            actors = cursor.fetchall()
            actors = [{'id': actor[0], "name": actor[1]} for actor in actors]
            return actors