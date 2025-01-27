echo "Migrations running..."

python3 migrations/movies/movies.py
python3 migrations/users/users.py

echo "Migrations finished"