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

def get_user_details(id):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT username from users where id = %s;"
            cursor.execute(sql, (int(id),))
            username = cursor.fetchone()
            return username[0]
        
def get_user_password(username):
    with get_db() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, password from users where username = %s;"
            cursor.execute(sql, (str(username),))
            user = cursor.fetchone()
            return {"id": user[0], "username": user[1]}