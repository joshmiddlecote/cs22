import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv()

languages_file = '../data/ml-latest-small/languages.csv'

api_url = "https://api.themoviedb.org/3/configuration/languages"
tmdb_api_key = os.getenv("TMDB_API_KEY")
headers = {
    "Authorization": f"Bearer {tmdb_api_key}", 
    "Content-Type": "application/json",
}

data = []

tmdb_languages = requests.get(api_url, headers=headers).json()

with open(languages_file, newline='', encoding='utf-8') as csvfile:
    language_csvreader = csv.reader(csvfile)
    next(language_csvreader)

    for row in language_csvreader:
        code, id = row
        for language in tmdb_languages:
            if language['iso_639_1'] == code:
                data.append({'id': id, 'code': code, 'name': language['english_name']})

with open('../data/ml-latest-small/new_languages.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['id', 'code', 'name'])
    writer.writeheader()
    writer.writerows(data)