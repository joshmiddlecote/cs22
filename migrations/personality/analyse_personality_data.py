import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Read the personality dataset
def load_and_prepare_data():
    personality_df = pd.read_csv('data/personality-isf2018/personality-data.csv')
    movies_df = pd.read_csv('data/ml-latest-small/genre_links.csv')
    
    # Convert column names to lowercase and strip whitespace
    personality_df.columns = personality_df.columns.str.lower().str.strip()
    movies_df.columns = movies_df.columns.str.lower().str.strip()
    
    # Print first few rows of each dataframe for debugging
    print("First few rows of personality_df:")
    print(personality_df.head())
    print("\nFirst few rows of movies_df:")
    print(movies_df.head())
    
    return personality_df, movies_df

def analyze_personality_traits(df):
    """Analyze basic statistics of personality traits"""
    personality_traits = ['openness', 'agreeableness', 'emotional_stability', 
                         'conscientiousness', 'extraversion']
    
    df.columns = df.columns.str.strip()
    
    # Calculate basic statistics
    trait_stats = df[personality_traits].describe()
    
    # Create correlation matrix for personality traits
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[personality_traits].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation between Personality Traits')
    plt.tight_layout()
    plt.savefig('personality_correlations.png')
    plt.close()
    
    return trait_stats

def analyze_movie_preferences(personality_df, movies_df):
    """Analyze correlation between personality traits and movie preferences"""
    # Merge movie information with ratings
    movie_columns = [col for col in personality_df.columns if col.startswith('Movie_')]
    
    # Create a long-format dataframe for analysis
    movie_ratings = pd.melt(personality_df, 
                           id_vars=['userid', 'openness', 'agreeableness', 
                                  'emotional_stability', 'conscientiousness', 'extraversion'],
                           value_vars=[col for col in personality_df.columns if col.startswith('Predicted_rating_')],
                           var_name='Movie_Number',
                           value_name='Rating')
    
    # Calculate average ratings per user
    user_avg_ratings = movie_ratings.groupby('userid')['Rating'].mean()
    
    # Analyze correlation between personality traits and average ratings
    personality_traits = ['openness', 'agreeableness', 'emotional_stability', 'conscientiousness', 'extraversion']
    
    correlations = {}
    for trait in personality_traits:
        correlation, p_value = stats.pearsonr(personality_df[trait], 
                                            personality_df['enjoy_watching'])
        correlations[trait] = {'correlation': correlation, 'p_value': p_value}
    
    return correlations

def visualize_results(personality_df):
    """Create visualizations for the analysis"""
    personality_traits = ['openness', 'agreeableness', 'emotional_stability', 'conscientiousness', 'extraversion']
    
    # Create scatter plots for each personality trait vs enjoyment
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.ravel()
    
    for idx, trait in enumerate(personality_traits):
        sns.scatterplot(data=personality_df, x=trait, y='enjoy_watching', ax=axes[idx])
        axes[idx].set_title(f'{trait} vs Enjoyment')
    
    plt.tight_layout()
    plt.savefig('personality_enjoyment_correlation.png')
    plt.close()

def analyze_genre_personality_correlation(personality_df, movies_df):
    """Analyze and visualize correlation between personality traits and genre preferences"""
    personality_traits = ['openness', 'agreeableness', 'emotional_stability', 
                         'conscientiousness', 'extraversion']
    
    # Get movie columns and their corresponding ratings
    movie_cols = [col for col in personality_df.columns if col.startswith('movie_')]
    rating_cols = [col for col in personality_df.columns if col.startswith('predicted_rating_')]
    
    # Create a long format dataframe
    all_ratings = []
    for movie_col, rating_col in zip(movie_cols, rating_cols):
        temp_df = personality_df[personality_traits + [movie_col, rating_col]].copy()
        temp_df['movie_id'] = temp_df[movie_col].astype(int)  # Convert to int
        temp_df['rating'] = pd.to_numeric(temp_df[rating_col], errors='coerce')
        all_ratings.append(temp_df[personality_traits + ['movie_id', 'rating']])
    
    ratings_df = pd.concat(all_ratings, ignore_index=True)
    
    # Ensure movie_id is same type in both dataframes
    movies_df['movie_id'] = movies_df['movie_id'].astype(int)
    ratings_df['movie_id'] = ratings_df['movie_id'].astype(int)
    
    # Print data types for debugging
    print("ratings_df movie_id dtype:", ratings_df['movie_id'].dtype)
    print("movies_df movie_id dtype:", movies_df['movie_id'].dtype)
    
    # Merge with genre information
    merged_df = pd.merge(ratings_df, movies_df, on='movie_id', how='left')
    
    # Get genre columns
    genre_cols = [col for col in movies_df.columns if col.startswith('genre_')]
    
    # Initialize correlation and p-value matrices with zeros
    correlation_matrix = np.zeros((len(personality_traits), len(genre_cols)))
    p_value_matrix = np.zeros((len(personality_traits), len(genre_cols)))
    
    # Calculate correlations
    for i, trait in enumerate(personality_traits):
        for j, genre in enumerate(genre_cols):
            # Calculate average rating per user per genre
            genre_ratings = merged_df[merged_df[genre] == 1]
            if not genre_ratings.empty:
                try:
                    corr, p_val = stats.pearsonr(
                        pd.to_numeric(genre_ratings[trait], errors='coerce'),
                        pd.to_numeric(genre_ratings['rating'], errors='coerce')
                    )
                    correlation_matrix[i, j] = corr if not np.isnan(corr) else 0
                    p_value_matrix[i, j] = p_val if not np.isnan(p_val) else 1
                except:
                    correlation_matrix[i, j] = 0
                    p_value_matrix[i, j] = 1
    
    # Create DataFrames from the matrices
    correlations = pd.DataFrame(
        correlation_matrix,
        index=personality_traits,
        columns=[g.replace('genre_', '') for g in genre_cols]
    )
    
    p_values = pd.DataFrame(
        p_value_matrix,
        index=personality_traits,
        columns=[g.replace('genre_', '') for g in genre_cols]
    )
    
    # Create heatmap
    plt.figure(figsize=(15, 8))
    mask = p_values > 0.05  # Create mask for non-significant correlations
    
    sns.heatmap(correlations, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                fmt='.2f',
                mask=mask,
                vmin=-1,
                vmax=1)
    
    plt.title('Correlation between Personality Traits and Genre Preferences\n(Only significant correlations shown, p < 0.05)')
    plt.xlabel('Movie Genres')
    plt.ylabel('Personality Traits')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('genre_personality_correlation.png')
    plt.close()
    
    # Create a summary of strongest correlations
    significant_correlations = []
    for trait in personality_traits:
        for genre in correlations.columns:
            corr = correlations.loc[trait, genre]
            p_val = p_values.loc[trait, genre]
            if abs(corr) > 0.1 and p_val < 0.05:  # Adjust threshold as needed
                significant_correlations.append({
                    'trait': trait,
                    'genre': genre,
                    'correlation': corr,
                    'p_value': p_val
                })
    
    # Sort by absolute correlation strength
    significant_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return significant_correlations

def main():
    # Load data
    personality_df, movies_df = load_and_prepare_data()
    
    # Analyze personality traits
    trait_stats = analyze_personality_traits(personality_df)
    print("Personality Trait Statistics:")
    print(trait_stats)
    
    # Analyze movie preferences
    correlations = analyze_movie_preferences(personality_df, movies_df)
    print("\nCorrelations between personality traits and movie enjoyment:")
    for trait, values in correlations.items():
        print(f"{trait}: correlation = {values['correlation']:.3f}, p-value = {values['p_value']:.3f}")
    
    # Analyze genre-personality correlations
    significant_correlations = analyze_genre_personality_correlation(personality_df, movies_df)
    
    # Print significant findings
    print("\nMost significant personality-genre correlations:")
    for corr in significant_correlations:
        direction = "positively" if corr['correlation'] > 0 else "negatively"
        print(f"{corr['trait'].title()} is {direction} correlated with {corr['genre']} movies "
              f"(r={corr['correlation']:.3f}, p={corr['p_value']:.3f})")
    
    # Create visualizations
    visualize_results(personality_df)

if __name__ == "__main__":
    main()
