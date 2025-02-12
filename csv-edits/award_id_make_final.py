import csv

input_file = "data/ml-latest-small/award_id_updated.csv"
output_file = "data/ml-latest-small/award_id_final.csv"

with open(input_file, "r", newline="", encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    
    # Define new field names excluding "award_id"
    new_fieldnames = [fn for fn in reader.fieldnames if fn != "award_id"]

    writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
    writer.writeheader()

    for row in reader:
        del row["award_id"]  # Remove the second column
        writer.writerow(row)

print(f"Updated CSV saved as {output_file}")
