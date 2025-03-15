import csv
import time
import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_base_url = "https://api.themoviedb.org/3/movie/"
tmdb_api_key = os.getenv("TMDB_API_KEY")
headers = {
    "Authorization": f"Bearer {tmdb_api_key}", 
    "Content-Type": "application/json",
}

data = []
file_path = '../data/ml-latest-small/movie_extra_details.csv'

max_retries = 5
backoff_factor = 1.5


def get_tmdb_api_response(api_url):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed with status code {response.status_code}: {response.text}")
                print(api_url)

        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

        if attempt < max_retries:
            wait_time = backoff_factor ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    print("All retry attempts failed.")
    return "error"


with open('../data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile, open('../data/ml-latest-small/links.csv', newline='', encoding='utf-8') as links_csvfile:
    movie_csvreader = csv.reader(csvfile)
    links_csvreader = csv.reader(links_csvfile)
    next(movie_csvreader)
    next(links_csvreader)
    row_no = 1

    for row1, row2 in zip(movie_csvreader, links_csvreader):
        movie_id, title, genres = row1
        _, _, tmdb_id = row2

        if tmdb_id == "":
            data.append({'movie_id': None, 'budget': None, 'revenue': None, 'language': None, 'overview': None, 'runtime': None, 'tagline': None})
            print(f"no tmdb id for movie id: {movie_id}")
            continue

        api_url = api_base_url + f"{tmdb_id}?language=en-US"
        api_response = get_tmdb_api_response(api_url)

        if api_response == "error":
            data.append({'movie_id': None, 'budget': None, 'revenue': None, 'language': None, 'overview': None, 'runtime': None, 'tagline': None})
            print(f"no tmdb info for movie id: {movie_id}")
            continue

        budget = api_response.get("budget")
        revenue = api_response.get("revenue")
        language = api_response.get("original_language")
        overview = api_response.get("overview")
        runtime = api_response.get("runtime")
        tagline = api_response.get("tagline")

        data.append({'movie_id': movie_id, 'budget': budget, 'revenue': revenue, 'language': language, 'overview': overview, 'runtime': runtime, 'tagline': tagline})
        row_no += 1
        print(row_no)
  
with open(file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['movie_id', 'budget', 'revenue', 'language', 'overview', 'runtime', 'tagline'])
    writer.writeheader()
    writer.writerows(data)