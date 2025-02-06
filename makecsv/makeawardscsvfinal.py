import csv

# Input files
oscars_file = "data/ml-latest-small/movies_with_awards_updated.csv"
golden_globes_file = "data/ml-latest-small/movies_with_awards_updated2.csv"
output_file = "data/ml-latest-small/awards.csv"

# Read and modify Oscars data
oscars_data = []
with open(oscars_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row["award_id"] = f"o{row['award_id']}"  # Prefix with 'o'
        oscars_data.append(row)

# Read and modify Golden Globes data
golden_globes_data = []
with open(golden_globes_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row["award_id"] = f"g{row['award_id']}"  # Prefix with 'g'
        golden_globes_data.append(row)

# Combine both datasets
combined_data = oscars_data + golden_globes_data

# Write to output file
with open(output_file, "w", newline='', encoding='utf-8') as f:
    fieldnames = ["year_film", "year_ceremony", "ceremony", "award_id", "nominee", "film", "winner"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(combined_data)

print(f"Combined awards data saved to {output_file}!")
