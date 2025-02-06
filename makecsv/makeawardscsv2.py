# import kagglehub

# Download latest version
# path = kagglehub.dataset_download("unanimad/golden-globe-awards")

# print("Path to dataset files:", path)

import csv

# File paths
movies_file = 'data/ml-latest-small/movies_cleaned.csv'
awards_file = 'data/ml-latest-small/golden_globe_awards.csv'
output_file = 'data/ml-latest-small/movies_with_awards2.csv'

# Load awards data into a dictionary (film title -> release year and full row)
awards_data = {}
with open(awards_file, 'r', encoding='utf-8') as infile:
    csvreader = csv.DictReader(infile)
    for row in csvreader:
        film = row['film'].strip()  # Clean up the film title
        year = row['year_film'].strip()  # Ensure the year is clean
        if (film, year) not in awards_data:
            awards_data[(film, year)] = []
        awards_data[(film, year)].append(row)  # Append the entire award row

# Process movies and match with awards
with open(movies_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    csvreader = csv.DictReader(infile)
    fieldnames = csvreader.fieldnames + list(next(iter(awards_data.values()))[0].keys())  # Combine movie and award columns
    csvwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    csvwriter.writeheader()  # Write the header row
    
    for row in csvreader:
        # Clean up title and get year from the row
        title = row['title'].strip()
        year = row['year'].strip()
        
        # Match movies with awards based on title and year
        if (title, year) in awards_data:
            for award_row in awards_data[(title, year)]:
                # Merge movie row with the matching award row
                # merged_row = {**row, **award_row}
                csvwriter.writerow(award_row)

print(f"Matched data written to {output_file}")