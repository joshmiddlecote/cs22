import csv

# Read the movie_actors.csv to get actor names and map to actor ids
actor_map = {}
actor_id = 1  # Start actor_id from 1

# Read the movie_actors.csv and create actor_id and actor_name mapping
with open('data/ml-latest-small/movie_actors.csv', 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header if present
    
    for row in reader:
        movie_id, actor_name = row
        if actor_name not in actor_map:
            actor_map[actor_name] = actor_id
            actor_id += 1  # Increment actor_id for each new actor

# Write the actor_id and actor_name mapping into a new CSV
with open('actor_mapping.csv', 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['actorId', 'actorName'])  # Write header
    for actor_name, id in actor_map.items():
        writer.writerow([id, actor_name])  # Write actor_id and actor_name

# Create a new movie_actors.csv with actor names replaced by actor_ids
with open('data/ml-latest-small/movie_actors.csv', 'r', encoding='utf-8') as infile, \
     open('movie_actors_with_id.csv', 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    header = next(reader)  # Skip header if present
    writer.writerow(['movie_id', 'actor_id'])  # New header with actor_id
    
    for row in reader:
        movie_id, actor_name = row
        actor_id = actor_map.get(actor_name)  # Get the actor_id from the map
        if actor_id:
            writer.writerow([movie_id, actor_id])  # Write the movie_id and actor_id

print("actor_mapping.csv and movie_actors_with_id.csv created successfully.")
