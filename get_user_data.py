import csv
from collections import defaultdict
import statistics

def get_movie_genre_links():
   movie_genre_links = {}
   with open('data/ml-latest-small/genre_links.csv', 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
        movie_id = row['movie_id']
        genre_id = row['genre_id']
        movie_genre_links[movie_id] = genre_id

   return movie_genre_links


def get_user_data(movie_genre_links):
   with open('data/ml-latest-small/ratings.csv', 'r') as file:
      reader = csv.DictReader(file)
      user_data = defaultdict(dict)

      for row in reader:
        user_id = int(row['userId'])
        movie_id = row['movieId']
        rating = float(row['rating'])

        genre = movie_genre_links[movie_id]

        if genre in user_data[user_id]:
           user_data[user_id][genre].append(rating)
        else:
           user_data[user_id][genre] = [rating]
      
      return user_data
   

def write_user_data_by_genre(user_data):
  user_data_all_movies = defaultdict(list)
  with open('data/ml-latest-small/user_ratings_by_genre.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'genre_id', 'avg_rating', 'variance', 'total_ratings'])
    for user_id, all_ratings in user_data.items():
       for genre_id, ratings in all_ratings.items():
          for rating in ratings:
             user_data_all_movies[user_id].append(rating)
          # get stats
          total_ratings = len(ratings)
          avg_rating = sum(ratings) / total_ratings
          if total_ratings > 1:
            variance = statistics.variance(ratings)
          else:
            variance = 0.0
          writer.writerow([user_id, int(genre_id), avg_rating, variance, total_ratings])

  return user_data_all_movies


def write_user_data_all_movies(user_data):
   with open('data/ml-latest-small/user_ratings_all_movies.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'avg_rating', 'variance', 'total_ratings'])
    for user_id, ratings in user_data.items():
       total_ratings = len(ratings)
       avg_rating = sum(ratings) / total_ratings
       if total_ratings > 1:
          variance = statistics.variance(ratings)
       else:
          variance = 0.0
       writer.writerow([user_id, avg_rating, variance, total_ratings])
   

def main():
   movie_genre_links = get_movie_genre_links()
   user_data = get_user_data(movie_genre_links)
   print("Finished getting user rating data.")
   user_data_all_movies = write_user_data_by_genre(user_data)
   print("Finished writing user rating data by genre.")
   write_user_data_all_movies(user_data_all_movies)
   print("Finished writing user rating data for all movies.")

if __name__ == "__main__":
    main()

           


