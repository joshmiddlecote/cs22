import csv
import math

ratings_count = {}

with open("data/ml-latest-small/ratings.csv", mode="r", newline="", encoding="utf-8") as csvfilereader, \
    open("data/ml-latest-small/movies.csv", mode="r", newline="", encoding="utf-8") as moviesfilereader:
    ratingreader = csv.reader(csvfilereader)
    moviereader = csv.reader(moviesfilereader)
    next(ratingreader)
    next(moviereader)

    for row in moviereader:
        movie_id = int(row[0])
        ratings_count[movie_id] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for row in ratingreader:
        movie_id = int(row[1])
        rating = math.ceil(float(row[2]))

        if rating not in [1, 2, 3, 4, 5]:
            print(f"Unexpected rating found: {rating} for movie {movie_id}")
            continue

        if movie_id in ratings_count:
            ratings_count[movie_id][rating] += 1
        else:
            print(f"'{movie_id}' not in ratings count")


with open("data/ml-latest-small/movie_ratings_count.csv", mode="w", newline="", encoding="utf-8") as csvfilewriter:
    writer = csv.writer(csvfilewriter)
    writer.writerow(["movieId", "count1", "count2", "count3", "count4", "count5"])

    for movie_id, counts in ratings_count.items():
        writer.writerow([movie_id, counts[1], counts[2], counts[3], counts[4], counts[5]])

print(f"Ratings counted for each movie")
