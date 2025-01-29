from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import movies.queries as movie_queries

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

@app.get("/")
async def root():
    return RedirectResponse(url="/movies")

@app.get("/movies")
def read_root(request: Request, page: int = Query(1, ge=1), size: int = Query(10, le=100)):
    start_index = (page - 1) * size
    (movies, total_pages) = movie_queries.get_all_movies(size, start_index)
    return templates.TemplateResponse("index.html", 
        {"request": request, "movies": movies, "page": page, 
         "size": size, "total_pages": total_pages})

@app.get("/movies/{movie_id}")
def read_movie(request: Request, movie_id: int):
    movie = movie_queries.get_movie_by_movie_id(movie_id)
    return templates.TemplateResponse("movie.html", {"request": request, "movie": movie})

