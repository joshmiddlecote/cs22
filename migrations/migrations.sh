#!/bin/sh
sleep 3
echo "Migrations running..."

python3 languages/languages.py
python3 movies/movies.py
python3 tags/load_tags.py
python3 genres/genres.py
python3 awards/load_award_awardid.py
python3 awards/load_movie_awards.py
python3 actors/load_actor_actorid.py
python3 actors/load_movie_actors.py
python3 audience/users_ratings.py
python3 users/users.py
python3 personality/personality_data.py
python3 personality/ratings.py

echo "Migrations finished"