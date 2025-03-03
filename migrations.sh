echo "Migrations running..."

python migrations/languages/languages.py
python migrations/movies/movies.py
python migrations/tags/load_tags.py
python migrations/genres/genres.py
python migrations/awards/load_award_awardid.py
python migrations/awards/load_movie_awards.py
python migrations/actors/load_actor_actorid.py
python migrations/actors/load_movie_actors.py
python migrations/audience/users_ratings.py
python migrations/users/users.py
python migrations/personality/personality_data.py
python migrations/personality/ratings.py

echo "Migrations finished"