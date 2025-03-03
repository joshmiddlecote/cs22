from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import api.movies.queries as movie_queries
import api.genre_report.queries as genre_report_queries
import api.movies.queries as movie_queries
import api.genres.queries as genre_queries
import api.awards.queries as award_queries
import api.actors.queries as actor_queries
import api.languages.queries as language_queries
import api.users.queries as user_queries
import api.movie_planners.queries as planner_queries
import api.audience.queries as audience_queries

app = FastAPI()
# templates = Jinja2Templates(directory="../templates")
templates_dir = str(Path(__file__).parent.parent / "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")


@app.get("/genre-report")
def read_genres(request: Request):
    # Fetch all genres using the function from genre_report.queries
    genres = genre_report_queries.get_popular_genres()
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

# year, genre, rating, actor, director, tags, awards, language, runtime

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
    rating_data = audience_queries.get_audience_ratings(movie_id)

    return templates.TemplateResponse("audience_analysis.html", {"request": request, "movie": rating_data})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = user_queries.get_user_password(username)
    if user is None or user["password"] != password:
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
def add_planner(request: Request, user_id: str | None = Query(default=None), name: str | None = Query(default=None)):
    planner_queries.insert_new_movie_planner(int(user_id), name)
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