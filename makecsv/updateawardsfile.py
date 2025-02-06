import csv

# Step 1: Read award_id.csv into a dictionary
award_dict = {}

with open("data/ml-latest-small/award_id.csv", "r", encoding="utf-8") as award_file:
    reader = csv.DictReader(award_file)
    for row in reader:
        award_dict[row["award_name"]] = row["award_id"]  # Map award_name to award_id

# Step 2: Process awards_with_movies.csv and replace category with award_id
input_file = 'data/ml-latest-small/movies_with_awards.csv'
output_file = 'data/ml-latest-small/movies_with_awards_updated.csv'

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8", newline="") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ["year_film", "year_ceremony", "ceremony", "award_id", "name", "film", "winner"]  # Replace 'category' with 'award_id'
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()  # Write new header

    for row in reader:
        category_name = row["category"].strip()  # Clean category name
        row["award_id"] = award_dict.get(category_name, "UNKNOWN")  # Replace with award_id or "UNKNOWN" if not found
        del row["category"]  # Remove the old 'category' column
        writer.writerow(row)  # Write updated row

print("Replacement completed! Check awards_with_movies_updated.csv")
