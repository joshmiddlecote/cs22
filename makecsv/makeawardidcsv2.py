import csv

# File paths
input_file = 'data/ml-latest-small/movies_with_awards2.csv'
award_id_file = 'data/ml-latest-small/award_id2.csv'
output_file = 'data/ml-latest-small/movies_with_awards_updated2.csv'

# Step 1: Extract unique categories and assign them an ID
awards_dict = {}
award_id = 1

# Read the input file and collect unique categories
with open(input_file, 'r', encoding='utf-8') as infile:
    csvreader = csv.DictReader(infile)
    
    for row in csvreader:
        category = row.get('category')  # Safely get the value
        if category not in awards_dict:
            awards_dict[category] = award_id
            award_id += 1  # Increment ID for the next category

# Step 2: Write the award_id.csv file
with open(award_id_file, 'w', newline='', encoding='utf-8') as award_file:
    csvwriter = csv.writer(award_file)
    csvwriter.writerow(['awardId', 'award_name'])  # Header
    for category, id_ in awards_dict.items():
        csvwriter.writerow([id_, category])

print(f"Award mapping saved to {award_id_file}")

