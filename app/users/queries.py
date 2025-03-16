from contextlib import contextmanager
import os
import psycopg2
from dotenv import load_dotenv
from argon2 import PasswordHasher

load_dotenv()
db_username = os.getenv("DB_USER")
db_passsword = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{db_username}:{db_passsword}@postgres_db/{db_name}"

# Initialize argon2 Password Hasher
# argon2 is a modern, robust password hashing function that provides strong resistance to brute force and side channel attacks
ph = PasswordHasher()

def hash_password(password):
    # Generate a hash using the Argon2 hashing algorithm
    return ph.hash(password)

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
            if user is None:
                return None
            return {"id": user[0], "password": user[1]}
        
def insert_user_details(username, password):
    with get_db() as conn:
        with conn.cursor() as cursor:
            hashed_password = hash_password(password) # store hash of the password instead of storing in plaintext for added security
            sql = "INSERT INTO users(username, password) VALUES (%s, %s) RETURNING id;"
            cursor.execute(sql, tuple([username, hashed_password]))
            conn.commit()
            return cursor.fetchone()[0]