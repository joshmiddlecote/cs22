from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import api.movies.queries as movie_queries
import api.genre_report.queries as genre_report_queries

app = FastAPI()
# templates = Jinja2Templates(directory="../templates")
templates_dir = str(Path(__file__).parent.parent / "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")

# year, genre, rating, actor, director, tags, awards, language, runtime
@app.get("/movies")
def read_root(
        request: Request, 
        page: int = Query(1, ge=1), 
        size: int = Query(10, le=100), 
        year_released: Optional[int] = Query(default=None),  # Use Optional[int] instead of int | None
        rating: Optional[float] = Query(default=None)        # Use Optional[float] instead of float | None
    ):
    
    print(year_released)
    print(rating)
    
    start_index = (page - 1) * size
    (movies, total_pages) = movie_queries.get_all_movies(size, start_index, year_released, rating)
    return templates.TemplateResponse("index.html", 
        {"request": request, "movies": movies, "page": page, 
         "size": size, "total_pages": total_pages})

@app.get("/movies/{movie_id}")
def read_movie(request: Request, movie_id: int):
    movie = movie_queries.get_movie_by_movie_id(movie_id)
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})

@app.get("/genre-report")
def read_genres(request: Request):
    # Fetch all genres using the function from genre_report.queries
    genres = genre_report_queries.get_popular_genres()
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})

@app.get("/genre-report/popular")
def get_most_popular_genres(request: Request):
    genres = genre_report_queries.get_popular_genres()  # Query sorted by popularity score
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})

@app.get("/genre-report/polarizing")
def get_most_polarizing_genres(request: Request):
    genres = genre_report_queries.get_polarizing_genres()  # Query sorted by variance
    return templates.TemplateResponse("genre_report.html", {"request": request, "genres": genres})