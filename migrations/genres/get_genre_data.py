import csv
from collections import defaultdict
import statistics


def get_unique_genres():
  unique_genres = set()
  with open('../data/ml-latest-small/movies.csv', 'r') as file:
      reader = csv.DictReader(file)
        
      for row in reader:
          genres = row['genres'].split('|')  # splits genres by '|'
          unique_genres.update(genres)      # add genres to set, ignoring duplicates
  
  return list(unique_genres)


def get_genre_links(genre_ids):
  genre_links = []
  with open('../data/ml-latest-small/movies.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movieId'])
            genres = row['genres'].split('|')

            for genre in genres:
              genre_id = genre_ids.index(genre) + 1
              genre_links.append({'movie_id': movie_id, 'genre_id': genre_id})

  return genre_links


def write_genre_links(genre_links):
   with open('../data/ml-latest-small/genre_links.csv', 'w', newline='') as file:
      writer = csv.DictWriter(file, fieldnames=['movie_id', 'genre_id'])
      writer.writeheader()
      writer.writerows(genre_links)


def get_genre_ratings(genre_ids, genre_links):
   rating_data = defaultdict(list)
   with open('../data/ml-latest-small/ratings.csv', 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
            movie_id = int(row['movieId'])
            rating = float(row['rating'])

            # check which genre(s) the movie is associated with
            genres = [item["genre_id"] for item in genre_links if item["movie_id"] == movie_id]
            for genre in genres:
               rating_data[genre].append(rating)

   # get statistics by genre from all rating data 
   rating_stats = {}
   for genre, ratings in rating_data.items():
      total_ratings = len(ratings)
      avg_rating = sum(ratings) / total_ratings 
      variance = statistics.variance(ratings)

      rating_stats[genre_ids[genre-1]] = [avg_rating, variance, total_ratings]
   return rating_stats


def write_genres(unique_genres, rating_stats):
   with open('../data/ml-latest-small/genres.csv', 'w', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(['id', 'genre_name', 'avg_rating', 'variance', 'total_ratings'])
      for i, genre in enumerate(unique_genres):
         stats = rating_stats.get(genre)
         avg_rating, variance, total_ratings = stats[0], stats[1], stats[2]
         writer.writerow([i+1, genre, avg_rating, variance, total_ratings])


def main():
   unique_genres = get_unique_genres()
   genre_links = get_genre_links(unique_genres)
   write_genre_links(genre_links)
   print('writing genre_links')
   rating_stats = get_genre_ratings(unique_genres, genre_links)
   print('got statistics for ratings by genre')
   write_genres(unique_genres, rating_stats)


if __name__ == "__main__":
    main()


