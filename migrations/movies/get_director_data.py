import csv
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# TMDb API details
TMDB_API_URL = "https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Input and output file paths
MAPPING_FILE = "data/ml-latest-small/links.csv"  # File with movieID and tmdbID
OUTPUT_FILE = "data/ml-latest-small/movies_directors.csv"    # Output file for movies with director details

# Step 1: Fetch director using TMDb API
def get_director(tmdb_id):
    """Fetch the director for a given movie using the TMDb API."""
    try:
        response = requests.get(TMDB_API_URL.format(tmdb_id=tmdb_id), params={"api_key": TMDB_API_KEY})
        response.raise_for_status()
        data = response.json()
        # Extract director(s) from the "crew" section
        directors = [crew['name'] for crew in data.get('crew', []) if crew['job'] == "Director"]
        return directors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for tmdbID {tmdb_id}: {e}")
        return []

# Step 2: Read the mapping file and fetch director data
with open(MAPPING_FILE, newline='', encoding='utf-8') as mapping_file, open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as output_file:
    reader = csv.DictReader(mapping_file)  # Assuming columns are `movieID`, `imdbID`, and `tmdbID`
    writer = csv.writer(output_file)
    
    # Write header for the output CSV
    writer.writerow(["movieId", "director"])

    for row in reader:
        movie_id = row["movieId"]
        tmdb_id = row["tmdbId"]

        # Skip rows with missing tmdbID
        if not tmdb_id:
            print(f"Skipping movieID {movie_id} due to missing tmdbID.")
            continue

        # Fetch director for the movie
        directors = get_director(tmdb_id)

        # Skip movies with no director data
        if not directors:
            print(f"No director data found for movieID {movie_id} (tmdbID {tmdb_id}).")
            continue

        # If there's more than one director, format them inside quotes
        director = directors[0] if len(directors) == 1 else f'"{", ".join(directors)}"'

        # Write director to the output CSV
        writer.writerow([movie_id, director])
        
        # Avoid hitting the TMDb rate limit
        time.sleep(0.25)  # 250ms delay between requests

print(f"Director data written to {OUTPUT_FILE}")