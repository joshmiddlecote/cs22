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
OUTPUT_FILE = "data/ml-latest-small/movie_actors.csv"    # Output file for movieID and actor names

# Step 1: Fetch lead actors using TMDb API
def get_lead_actors(tmdb_id):
    """Fetch the lead actors for a given movie using the TMDb API."""
    try:
        response = requests.get(TMDB_API_URL.format(tmdb_id=tmdb_id), params={"api_key": TMDB_API_KEY})
        response.raise_for_status()
        data = response.json()
        actors = [cast['name'] for cast in data.get('cast', [])[:3]]  # Get top 3 actors
        return actors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for tmdbID {tmdb_id}: {e}")
        return []

# Step 2: Read the mapping file and fetch actor data
with open(MAPPING_FILE, newline='', encoding='utf-8') as mapping_file, open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as output_file:
    reader = csv.DictReader(mapping_file)  # Assuming columns are `movieID`, `imdbID`, and `tmdbID`
    writer = csv.writer(output_file)
    
    # Write header for the output CSV
    writer.writerow(["movieId", "actor"])

    for row in reader:
        movie_id = row["movieId"]
        tmdb_id = row["tmdbId"]

        # Skip rows with missing tmdbID
        if not tmdb_id:
            print(f"Skipping movieID {movie_id} due to missing tmdbID.")
            continue

        # Fetch lead actors for the movie
        actors = get_lead_actors(tmdb_id)

        # Skip movies with no actor data
        if not actors:
            print(f"No actor data found for movieID {movie_id} (tmdbID {tmdb_id}).")
            continue

        # Write each actor to the output CSV
        for actor in actors:
            writer.writerow([movie_id, actor])
        
        # Avoid hitting the TMDb rate limit
        time.sleep(0.25)  # 250ms delay between requests

print(f"Actor data written to {OUTPUT_FILE}")
