import csv
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection details
host = "localhost"
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Set your TMDB API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/{tmdb_id}/images"


def get_movie_poster(tmdb_id):
    # print(tmdb_id)
    # Fetch movie poster URL from TMDB.
    response = requests.get(TMDB_BASE_URL.format(tmdb_id=tmdb_id), params={"api_key": TMDB_API_KEY})

    if response.status_code == 404:
        print(f"Movie ID {tmdb_id} not found!")
        return ""
    
    response.raise_for_status()
    data = response.json()
    
    # Check if any poster images exist
    if "posters" in data and data["posters"]:
        poster_path = data["posters"][0]["file_path"]  # Get the first poster
        image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"  # Construct full URL
        return(image_url)
    else:
        print(f"No poster available for movieID {tmdb_id}.")
        return ""


# Load tmdbId mapping from links.csv
tmdb_mapping = {}
with open("data/ml-latest-small/links.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tmdb_mapping[row["movieId"]] = row["tmdbId"]

# Read movies.csv and add poster column
movies = []
with open("data/ml-latest-small/movies.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames + ["poster"]  # Add new column
    for row in reader:
        tmdb_id = tmdb_mapping.get(row["movieId"])
        if tmdb_id:
            row["poster"] = get_movie_poster(tmdb_id)
        else:
            row["poster"] = ""
        movies.append(row)

print("Finished reading")

# Write updated movies.csv
with open("data/ml-latest-small/movies_with_posters.csv", "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(movies)

print("Updated CSV with posters saved as movies_with_posters.csv")
