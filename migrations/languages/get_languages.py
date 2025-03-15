import csv

languages_file = '../data/ml-latest-small/languages.csv'
input_file = '../data/ml-latest-small/movie_extra_details.csv'
output_file = '../data/ml-latest-small/updated_movie_extra_details.csv'

language_to_id = {}
with open(languages_file, mode='r', newline='', encoding='utf-8') as lang_file:
    reader = csv.DictReader(lang_file)
    for row in reader:
        language_to_id[row['language']] = int(row['id'])

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['language_id'] 
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for row in reader:
        language_name = row.get('language')
        row['language_id'] = language_to_id.get(language_name, None)
        writer.writerow(row)

