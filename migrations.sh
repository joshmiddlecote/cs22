echo "Migrations running..."

python3 migrations/languages/languages.py
python3 migrations/movies/movies.py
python3 migrations/tags/load_tags.py
python3 migrations/genres/genres.py
python3 migrations/awards/load_award_awardid.py
python3 migrations/awards/load_movie_awards.py
python3 migrations/actors/load_actor_actorid.py
python3 migrations/actors/load_movie_actors.py
python3 migrations/audience/users_ratings.py
python3 migrations/users/users.py

echo "Migrations finished"