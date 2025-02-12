import csv

# Load award_id mappings into a dictionary
award_id_map = {}

with open("data/ml-latest-small/award_id_updated.csv", "r", newline="", encoding="utf-8") as award_file:
    reader = csv.DictReader(award_file)
    for row in reader:
        award_id_map[row["award_id"]] = row["awardId"]  # Map old award_id to new awardId

# Process awards_updated.csv and replace award_id with awardId
with open("data/ml-latest-small/awards_updated.csv", "r", newline="", encoding="utf-8") as infile, \
     open("data/ml-latest-small/awards_final.csv", "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = ["year_film", "year_ceremony", "ceremony", "awardId", "nominee", "movieId", "winner"]  # Update header
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()  # Write new header

    for row in reader:
        row["awardId"] = award_id_map.get(row["award_id"], row["award_id"])  # Replace award_id with awardId
        del row["award_id"]  # Remove old award_id column
        writer.writerow(row)

print("Updated CSV saved as awards_final.csv")
