from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import queries

app = FastAPI()
templates = Jinja2Templates(directory="../../templates")

@app.get("/movies")
def read_root(request: Request):
    movies = queries.get_all_movies()
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movies})

@app.get("/movies/{movie_id}")
def read_movie(request: Request, movie_id: int):
    movie = queries.get_movie_by_movie_id(movie_id)
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movie})
