import csv

data = []

file_path = 'movie_average_ratings.csv'

def get_ratings_by_movie_id(file_path, target_id):
    rating = 0
    number_ratings = 0
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["movieId"] == target_id:
                rating += float(row["rating"])
                number_ratings += 1
    if number_ratings == 0:
        average_rating = 0
    else:
        average_rating = rating/number_ratings
    return (average_rating, number_ratings)

with open('data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as movie_csvfile:
    movie_csvreader = csv.reader(movie_csvfile)
    next(movie_csvreader)
    row_number = 1
    
    for row in movie_csvreader:
        movie_id, title, genres = row
        (average_rating, num_ratings) = get_ratings_by_movie_id('data/ml-latest-small/ratings.csv', movie_id)
        data.append({'movie_id': movie_id, 'average_rating': average_rating, 'num_ratings': num_ratings})
        print(row_number)
        row_number +=1

with open(file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['movie_id', 'average_rating', 'num_ratings'])
    writer.writeheader()
    writer.writerows(data)


print(f"CSV file '{file_path}' written successfully!")
