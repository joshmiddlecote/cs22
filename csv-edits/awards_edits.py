import csv

# Load movies.csv and create a mapping of film titles to movieId
movies_dict = {}
with open("data/ml-latest-small/movies.csv", newline='', encoding='utf-8') as movies_file:
    reader = csv.DictReader(movies_file)
    for row in reader:
        # Extract title without the year (e.g., "Toy Story (1995)" → "Toy Story")
        title = row["title"].rsplit(" (", 1)[0]
        movies_dict[title] = row["movieId"]

# Process awards.csv and replace film with movieId
updated_awards = []
with open("data/ml-latest-small/awards.csv", newline='', encoding='utf-8') as awards_file:
    lines = awards_file.readlines()

    # Extract the header
    header = lines[0].strip().split(",")

    for line in lines[1:]:
        parts = line.strip().split(",")

        # Always take at least one column for nominee
        nominee_parts = [parts[4]]  # Ensure nominee is captured
        i = 5  # Start checking after nominee field

        while i < len(parts) - 3:  # Avoid affecting last three fields
            if parts[i].startswith(" "):  # Merge if part belongs to nominee
                nominee_parts.append(parts[i].strip())
            else:
                break
            i += 1

        nominee = ", ".join(nominee_parts)  # Ensure nominee is correctly formed

        # Extract other fields
        year_film, year_ceremony, ceremony, award_id = parts[:4]
        film = parts[-2]
        winner = parts[-1]

        # Replace film title with movieId
        film = movies_dict.get(film, "N/A")

        # Store processed row
        updated_awards.append([year_film, year_ceremony, ceremony, award_id, nominee, film, winner])

# Write the updated awards.csv
with open("data/ml-latest-small/awards_updated.csv", "w", newline='', encoding='utf-8') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(header)  # Write header
    writer.writerows(updated_awards)  # Write processed rows

print("Updated awards.csv has been saved as awards_updated.csv")
