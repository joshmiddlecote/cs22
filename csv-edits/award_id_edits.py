import csv

# Read the input file and add the awardId column
with open("data/ml-latest-small/award_id.csv", "r", newline="", encoding="utf-8") as infile, \
     open("data/ml-latest-small/award_id_updated.csv", "w", newline="", encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read the header and add the new column
    header = next(reader)
    writer.writerow(["awardId"] + header)  # Add 'awardId' as the first column

    # Write rows with sequential awardId
    for i, row in enumerate(reader, start=1):
        writer.writerow([i] + row)

print("Updated CSV saved as award_id_updated.csv")
