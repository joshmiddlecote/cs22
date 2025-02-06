import csv

# File paths
input_file = 'data/ml-latest-small/movies_cleaned.csv'

# Open the input file for reading and the output file for writing
with open(input_file, 'r', encoding='utf-8') as infile:
    
    csvreader = csv.reader(infile)
    
    # Read and write the header row
    header = next(csvreader)
    
    # Process each row
    for row in csvreader:
        # Strip trailing and leading whitespace from the title column (index 1)
        print(row)
