from fastapi import FastAPI, Query, Request, Form, Depends, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import movies.queries as movie_queries
import genres.queries as genre_queries
import awards.queries as award_queries
import actors.queries as actor_queries
import languages.queries as language_queries
import users.queries as user_queries
import movie_planners.queries as planner_queries
import audience.queries as audience_queries
import predictions.queries as predictions_queries
import personality.queries as personality_queries
import genre_report.queries as genre_report_queries

from argon2 import PasswordHasher
ph = PasswordHasher()

def check_password(stored_hash, password):
    try:
        return ph.verify(stored_hash, password) 
    except Exception:
        return False 

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")

@app.get("/movies")
def movies(
        request: Request, page: int = Query(1, ge=1), size: int = Query(10, le=100), 
        year_released: str | None = Query(default=None), rating: str | None = Query(default=None),
        genre_id: str | None = Query(default=None), award_id: str | None = Query(default=None),
        winner: str | None = Query(default=None), actor_id: str | None = Query(default=None), 
        language_id: str | None = Query(default=None), user_id: str | None = Query(default=None)):
    
    offset = (page - 1) * size
    movies = movie_queries.get_all_movies(size, offset, year_released, rating, genre_id, award_id, winner, actor_id, language_id)
    genres = genre_queries.get_all_genres()
    awards = award_queries.get_all_awards()
    actors = actor_queries.get_all_actors()
    languages = language_queries.get_all_languages()

    if user_id:
        username = user_queries.get_user_details(user_id)
        user = {"username": username, "id": user_id}
        planners = planner_queries.get_user_movie_planners(user_id)
    else:
        user = None
        planners = None

    return templates.TemplateResponse("index.html", 
        {"request": request, "movies": movies, "page": page, 
         "size": size, "rating": rating, "year_released": year_released, 
         "genre_id": genre_id, "genres": genres,
         "award_id": award_id, "awards": awards,
         "actor_id": actor_id, "actors": actors,
         "language_id": language_id, "languages": languages, "user": user, "planners": planners})

@app.get("/movies/{movie_id}")
def read_movie(request: Request, movie_id: int):
    movie = movie_queries.get_movie_by_movie_id(movie_id)
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})

@app.get("/movies/name/{movie_name}")
def read_movie_name(request: Request, movie_name: str):
    movie = movie_queries.get_movie_by_movie_name(movie_name)

    if movie is None:
        return templates.TemplateResponse("no_movie_found.html", {"request": request})
    
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})

@app.get("/movies/{movie_id}/audience-analysis")
def analyse_ratings(request: Request, movie_id: int):
    movie_rating_data = audience_queries.get_audience_ratings(movie_id)
    ratings_count = audience_queries.get_ratings_distribution(movie_id)
    movie_genre = audience_queries.get_movie_genre(movie_id)
    highly_rated_genres = audience_queries.get_other_highly_rated_genres(movie_id, movie_rating_data['average_rating'])
    lowly_rated_genres = audience_queries.get_other_lowly_rated_genres(movie_id, movie_rating_data['average_rating'], highly_rated_genres)
    highly_rated_movies_same_genre = audience_queries.get_similar_highly_rated_movies_same_genre(movie_id, movie_rating_data['average_rating'])
    highly_rated_movies_diff_genre = audience_queries.get_similar_highly_rated_movies_different_genre(movie_id, movie_rating_data['average_rating'])
    lowly_rated_movies_same_genre = audience_queries.get_similar_lowly_rated_movies_same_genre(movie_id, movie_rating_data['average_rating'])
    lowly_rated_movies_diff_genre = audience_queries.get_similar_lowly_rated_movies_different_genre(movie_id, movie_rating_data['average_rating'])
    personality = personality_queries.get_personality_correlation_movies(movie_id)

    return templates.TemplateResponse("audience_analysis.html", {"request": request, "movie": movie_rating_data, "ratings_count": ratings_count,
        "movie_genre": movie_genre, "highly_rated_genres": highly_rated_genres, "lowly_rated_genres": lowly_rated_genres,
        "highly_rated_movies_same_genre": highly_rated_movies_same_genre, "highly_rated_movies_diff_genre": highly_rated_movies_diff_genre,
        "lowly_rated_movies_same_genre": lowly_rated_movies_same_genre, "lowly_rated_movies_diff_genre": lowly_rated_movies_diff_genre,
        "personality": personality})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = user_queries.get_user_password(username)
    if user is None or not check_password(user["password"], password):
        return templates.TemplateResponse("invalid_login.html", {"request": request})
    
    movies = movie_queries.get_all_movies()
    genres = genre_queries.get_all_genres()
    awards = award_queries.get_all_awards()
    actors = actor_queries.get_all_actors()
    languages = language_queries.get_all_languages()
    planners = planner_queries.get_user_movie_planners(user["id"])

    return templates.TemplateResponse("index.html", {"request": request, "page": 1, "size": 10, "movies": movies, "genres": genres, 
        "awards": awards, "actors": actors, "languages": languages, "user": user, "planners": planners})

@app.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...)):
    user_id = user_queries.insert_user_details(username, password)
    if not user_id:
        return movies(user_id=user_id)
    else:
        return RedirectResponse(url=f"/movies?user_id={user_id}", status_code=303)
    
@app.get("/register-user")
def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/add-movie-to-planner")
def add_movie_to_planner(request: Request, planner_id: str | None = Query(default=None), movie_id: str | None = Query(default=None), user_id: str | None = Query(default=None)):
    planner_queries.insert_new_movie_planner_item(int(planner_id), int(movie_id))
    return RedirectResponse(url=f"/movies?user_id={user_id}", status_code=303)

@app.get("/add-planner")
def add_planner(request: Request, user_id: str | None = Query(default=None), name: str | None = Query(default=None), description: str | None = Query(default=None)):
    planner_queries.insert_new_movie_planner(int(user_id), name, description)
    return RedirectResponse(url=f"/show-movie-planners/{user_id}", status_code=303)

@app.get("/show-movie-planners/{user_id}")
def show_movie_planners(request: Request, user_id: int):
    planners = planner_queries.get_movies_from_user_id(user_id)
    return templates.TemplateResponse("movie_planner.html", {"request": request, "planners": planners, "user_id": user_id})

@app.get("/delete-movie-from-planner")
def delete_movie_from_planner(request: Request, planner_id: str | None = Query(default=None), movie_id: str | None = Query(default=None), user_id: str | None = Query(default=None)):
    planner_queries.delete_movie_from_planner(int(movie_id), int(planner_id))
    planners = planner_queries.get_movies_from_user_id(user_id)
    return templates.TemplateResponse("movie_planner.html", {"request": request, "planners": planners, "user_id": user_id})

@app.get("/delete-planner")
def delete_planner(request: Request, planner_id: str | None = Query(default=None), user_id: str | None = Query(default=None)):
    planner_queries.delete_movie_planner(planner_id)
    planners = planner_queries.get_movies_from_user_id(user_id)
    return templates.TemplateResponse("movie_planner.html", {"request": request, "planners": planners, "user_id": user_id})

@app.get("/movies/get-prediction-parameters/{movie_name}")
def predict_ratings(request: Request, movie_name: str):
    movie = movie_queries.get_movie_by_movie_name(movie_name)
    if movie:
        movie_id = movie_queries.get_movie_by_movie_name(movie_name)["id"]
    else:
        movie_id = None
    return templates.TemplateResponse("prediction_parameters.html", {"request": request, "movie_name": movie_name, "movie_id": movie_id})

@app.post("/movies/predict-ratings")
def predict_ratings(request: Request, formData: dict = Body(...)):
    predicted_rating = predictions_queries.calculate_rating(formData)
    movie_id = formData["movie_id"]
    if movie_id == "None":
        movie_id = None

    if movie_id is not None:
        actual_rating = predictions_queries.get_movie_rating(formData["movie_id"])
        movie_poster = movie_queries.get_movie_by_movie_id(movie_id)["poster"]
    else:
        actual_rating = None
        movie_poster = "https://www.shutterstock.com/image-illustration/movie-poster-mockup-light-bulb-600nw-2383346723.jpg"
    return templates.TemplateResponse("rating_prediction.html", {"request": request, "movie_name": formData["movie_name"], "movie_poster": movie_poster, "predicted_rating": predicted_rating, "actual_rating": actual_rating})

@app.get("/genre-report")
def read_genres(request: Request):
    # Fetch all genres, default to displaying genres in order of descending average rating
    genres = genre_report_queries.get_genres()
    genres = sorted(genres, key=lambda x: x['avg_rating'], reverse=True) # sorted by avg rating
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})

@app.get("/genre-report/polarizing")
def get_most_polarizing_genres(request: Request):
    genres = genre_report_queries.get_genres()  
    genres_sorted = sorted(genres, key=lambda x: x['variance'], reverse=True) # sorted by variance
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres_sorted})

@app.get("/genre-report/most-watched")
def get_most_polarizing_genres(request: Request):
    genres = genre_report_queries.get_genres()  # Query sorted by variance
    genres_sorted = sorted(genres, key=lambda x: x['total_ratings'], reverse=True) # sorted by total no. of ratings
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres_sorted})

@app.get("/genre-report/most-liked")
def get_most_polarizing_genres(request: Request):
    genres = genre_report_queries.get_genres()  # Query sorted by variance
    genres_sorted = sorted(genres, key=lambda x: x['avg_rating'], reverse=True) # sorted by avg rating
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres_sorted})

@app.get("/genre-report/cult-classics")
def get_cult_classic_genres(request: Request):
    genres = genre_report_queries.get_cult_classic_genres()  # Query sorted by popularity score
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})

@app.get("/genre-report/niche-interests")
def get_niche_interest_genres(request: Request):
    genres = genre_report_queries.get_niche_interest_genres() 
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})

@app.get("/genre-report/{genre_id}")
def read_movie(request: Request, genre_id: int):
    genre_data = genre_report_queries.get_genre_data_by_id(genre_id)
    top_movies = genre_report_queries.get_top_movies_by_genre_id(genre_id)
    personality = personality_queries.get_genre_personality_correlation(genre_id)
    print(personality)
    return templates.TemplateResponse("genre_details.html", {"request": request, "genre_data": genre_data, "top_movies": top_movies, "personality": personality})