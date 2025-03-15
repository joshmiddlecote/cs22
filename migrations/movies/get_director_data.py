import csv
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

TMDB_API_URL = "https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

LINKS_FILE = "../data/ml-latest-small/links.csv"
OUTPUT_FILE = "../data/ml-latest-small/movies_directors.csv"

def get_director(tmdb_id):
    try:
        response = requests.get(TMDB_API_URL.format(tmdb_id=tmdb_id), params={"api_key": TMDB_API_KEY})
        response.raise_for_status()
        data = response.json()
        directors = [crew['name'] for crew in data.get('crew', []) if crew['job'] == "Director"]
        return directors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for tmdbID {tmdb_id}: {e}")
        return []

with open(LINKS_FILE, newline='', encoding='utf-8') as LINKS_file, open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as output_file:
    reader = csv.DictReader(LINKS_file)
    writer = csv.writer(output_file)
    
    writer.writerow(["movieId", "director"])

    for row in reader:
        movie_id = row["movieId"]
        tmdb_id = row["tmdbId"]

        if not tmdb_id:
            print(f"MovieID {movie_id} has missing tmdbID.")
            writer.writerow([movie_id, "N/A"])
            continue

        directors = get_director(tmdb_id)

        if not directors:
            print(f"No director data found for movieID {movie_id} (tmdbID {tmdb_id}).")
            writer.writerow([movie_id, "N/A"])
            continue

        director = directors[0] if len(directors) == 1 else f'"{", ".join(directors[:10])}"'

        writer.writerow([movie_id, director])
        
        time.sleep(0.25)

print(f"Director data written to {OUTPUT_FILE}")