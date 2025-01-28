import csv

data = []

file_path = 'movie_average_ratings.csv'

def get_ratings_by_movie_id(file_path, target_id):
    rating = 0
    ratings = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["movieId"] == target_id:
                rating += float(row["rating"])
                ratings.append(float(row["rating"]))
    num_ratings = len(ratings)

    if num_ratings == 0:
        return(0,0,0)
    else:
        average_rating = rating/num_ratings

    total_x = 0

    for rating in ratings:
        x = (rating - average_rating)**2
        total_x += x
    
    variance = total_x / num_ratings
    return (average_rating, num_ratings, variance)

with open('data/ml-latest-small/movies.csv', newline='', encoding='utf-8') as movie_csvfile:
    movie_csvreader = csv.reader(movie_csvfile)
    next(movie_csvreader)
    row_number = 1
    
    for row in movie_csvreader:
        movie_id, title, genres = row
        (average_rating, num_ratings, variance) = get_ratings_by_movie_id('data/ml-latest-small/ratings.csv', movie_id)
        data.append({'movie_id': movie_id, 'average_rating': average_rating, 'num_ratings': num_ratings, 'variance': variance})
        print(row_number)
        row_number +=1

with open(file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['movie_id', 'average_rating', 'num_ratings', 'variance'])
    writer.writeheader()
    writer.writerows(data)


print(f"CSV file '{file_path}' written successfully!")
