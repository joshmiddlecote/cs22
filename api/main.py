from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import movies.queries as movie_queries
import genres.queries as genre_queries
import awards.queries as award_queries
import actors.queries as actor_queries
import languages.queries as language_queries

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")

# year, genre, rating, actor, director, tags, awards, language, runtime

@app.get("/movies")
def read_root(
        request: Request, page: int = Query(1, ge=1), size: int = Query(10, le=100), 
        year_released: str | None = Query(default=None), rating: str | None = Query(default=None),
        genre_id: str | None = Query(default=None), award_id: str | None = Query(default=None),
        winner: str | None = Query(default=None), actor_id: str | None = Query(default=None), 
        language_id: str | None = Query(default=None)):
    
    offset = (page - 1) * size
    movies = movie_queries.get_all_movies(size, offset, year_released, rating, genre_id, award_id, winner, actor_id, language_id)
    genres = genre_queries.get_all_genres()
    awards = award_queries.get_all_awards()
    actors = actor_queries.get_all_actors()
    languages = language_queries.get_all_languages()

    return templates.TemplateResponse("index.html", 
        {"request": request, "movies": movies, "page": page, 
         "size": size, "rating": rating, "year_released": year_released, 
         "genre_id": genre_id, "genres": genres,
         "award_id": award_id, "awards": awards,
         "actor_id": actor_id, "actors": actors,
         "language_id": language_id, "languages": languages})

@app.get("/movies/{movie_id}")
def read_movie(request: Request, movie_id: int):
    movie = movie_queries.get_movie_by_movie_id(movie_id)
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})

@app.get("/movies/name/{movie_name}")
def read_movie_name(request: Request, movie_name: str):
    print(movie_name)
    movie = movie_queries.get_movie_by_movie_name(movie_name)

    if movie is None:
        return templates.TemplateResponse("no_movie_found.html", {"request": request})
    
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})
