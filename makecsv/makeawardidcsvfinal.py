import csv

# Input files
oscars_id_file = "data/ml-latest-small/award_id.csv"
golden_globes_id_file = "data/ml-latest-small/award_id2.csv"
output_id_file = "data/ml-latest-small/combined_award_id.csv"  # Avoid overwriting input

# Function to read and prefix award IDs
def read_and_prefix_awards(file_path, prefix):
    data = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row and "award_id" in row and row["award_id"]:  # Skip empty rows
                row["award_id"] = f"{prefix}{row['award_id']}"
                data.append(row)
            else:
                print(f"Skipping invalid row: {row}")  # Debugging
    return data

# Read Oscars and Golden Globes data
oscars_data = read_and_prefix_awards(oscars_id_file, "o")
golden_globes_data = read_and_prefix_awards(golden_globes_id_file, "g")

# Combine both datasets
combined_data = oscars_data + golden_globes_data

# Ensure correct fieldnames
if combined_data:
    fieldnames = combined_data[0].keys()  # Dynamically set fieldnames from valid data

    # Write to output file
    with open(output_id_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"Combined awards data saved to {output_id_file}!")
else:
    print("No valid data to write.")
