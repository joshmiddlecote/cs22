import pandas as pd

# Load movie extra details
extra_details_file = "data/ml-latest-small/movie_extra_details.csv"
directors_file = "data/ml-latest-small/movie_directors.csv"

# Read both CSVs into pandas DataFrames
extra_details_df = pd.read_csv(extra_details_file)
directors_df = pd.read_csv(directors_file)

# print("Extra Details Columns:", extra_details_df.columns.tolist())
# print("Directors Columns:", directors_df.columns.tolist())


# Merge on 'movie_id' (assuming both files have this column)
merged_df = extra_details_df.merge(directors_df, on="movie_id", how="left")

# Save the updated CSV
merged_df.to_csv("data/ml-latest-small/movie_extra_details_updated.csv", index=False)

print("Updated CSV saved as 'movie_extra_details_updated.csv'")
