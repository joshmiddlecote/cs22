from fastapi import FastAPI, Query, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import movies.queries as movie_queries
import genres.queries as genre_queries
import awards.queries as award_queries
import actors.queries as actor_queries
import languages.queries as language_queries
import users.queries as user_queries
import movie_planners.queries as planner_queries

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")

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
    else:
        user = None

    return templates.TemplateResponse("index.html", 
        {"request": request, "movies": movies, "page": page, 
         "size": size, "rating": rating, "year_released": year_released, 
         "genre_id": genre_id, "genres": genres,
         "award_id": award_id, "awards": awards,
         "actor_id": actor_id, "actors": actors,
         "language_id": language_id, "languages": languages, "user": user})

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

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = user_queries.get_user_password(username)
    if user is None:
        return templates.TemplateResponse("invalid_login.html", {"request": request})
    
    movies = movie_queries.get_all_movies()
    genres = genre_queries.get_all_genres()
    awards = award_queries.get_all_awards()
    actors = actor_queries.get_all_actors()
    languages = language_queries.get_all_languages()

    return templates.TemplateResponse("index.html", {"request": request, "page": 1, "size": 10, "movies": movies, "genres": genres, 
        "awards": awards, "actors": actors, "languages": languages, "user": user})

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

@app.get("/add-movie-to-planner/{planner_id}/{movie_id}")
def add_movie_to_planner(request: Request, planner_id: int, movie_id: int, user_id: str | None = Query(default=None)):
    planner_queries.insert_new_movie_planner_item(planner_id, movie_id)
    return RedirectResponse(url=f"/movies?user_id={user_id}", status_code=303)

@app.get("/add-planner/{user_id}/{name}")
def add_planner(request: Request, user_id: int, name: str):
    planner_queries.insert_new_movie_planner(user_id, name)
    return RedirectResponse(url=f"/movies?user_id={user_id}", status_code=303)

@app.get("/show-movie-planners/{user_id}")
def show_movie_planners(request: Request, user_id: int):
    planners = planner_queries.get_movies_from_user_id(user_id)
    return templates.TemplateResponse("movie_planner.html", {"request": request, "planners": planners})