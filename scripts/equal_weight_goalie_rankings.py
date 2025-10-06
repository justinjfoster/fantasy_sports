#!/usr/bin/env python3
"""
Equal Weight Fantasy Hockey Goalie Ranking System

This script implements percentile-based ranking for goalies optimized for leagues where
all categories (wins, saves, save percentage, goals against average) are equally weighted.
"""

import pandas as pd
import numpy as np

def load_goalie_data():
    """Load the 2025 goalie data."""
    return pd.read_csv('data/goalie_data_2022_2025.csv')

def percentile_goalie_ranking_system(df):
    """
    Percentile-Based Goalie Ranking (BEST FOR EQUAL WEIGHT LEAGUES)
    - Convert raw stats to percentiles (0-100)
    - Sum percentiles for overall score
    - Treats all categories equally
    - Note: GAA is inverted (lower is better)
    """
    print("PERCENTILE-BASED GOALIE RANKING (RECOMMENDED FOR EQUAL WEIGHT)")
    print("="*70)
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    print(f"Found {len(goalies_2025)} goalies for 2025 season")
    
    # Define the 4 categories for ranking
    categories = ['wins', 'saves', 'save_percentage']
    inverted_categories = ['goals_against_average']  # Lower GAA is better
    
    df_percentile = goalies_2025.copy()
    
    # Convert normal categories to percentiles (higher is better)
    for category in categories:
        df_percentile[f'{category}_percentile'] = df_percentile[category].rank(pct=True) * 100
    
    # Convert inverted categories to percentiles (lower is better)
    for category in inverted_categories:
        # For GAA, we want lower values to have higher percentiles
        df_percentile[f'{category}_percentile'] = df_percentile[category].rank(pct=True, ascending=False) * 100
    
    # Calculate total percentile score
    percentile_cols = [f'{cat}_percentile' for cat in categories + inverted_categories]
    df_percentile['percentile_total'] = df_percentile[percentile_cols].sum(axis=1)
    
    # Rank by percentile total
    df_percentile['percentile_rank'] = df_percentile['percentile_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_percentile = df_percentile.nsmallest(20, 'percentile_rank')[['name', 'percentile_rank', 'percentile_total', 'wins', 'saves', 'save_percentage', 'goals_against_average'] + percentile_cols]
    print("Top 20 Goalies by Percentile System:")
    for i, row in top_percentile.iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<25} Score: {row['percentile_total']:6.1f} | W:{row['wins']:2.0f} S:{row['saves']:4.0f} SV%:{row['save_percentage']:5.3f} GAA:{row['goals_against_average']:4.2f}")
    
    return df_percentile

def z_score_goalie_ranking_system(df):
    """
    Z-Score Based Goalie Ranking
    - Convert stats to z-scores (standard deviations from mean)
    - Sum z-scores for overall score
    - Accounts for distribution differences between categories
    """
    print("\nZ-SCORE BASED GOALIE RANKING")
    print("="*70)
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    
    categories = ['wins', 'saves', 'save_percentage']
    inverted_categories = ['goals_against_average']  # Lower GAA is better
    
    df_zscore = goalies_2025.copy()
    
    # Convert normal categories to z-scores
    for category in categories:
        mean_val = goalies_2025[category].mean()
        std_val = goalies_2025[category].std()
        df_zscore[f'{category}_zscore'] = (goalies_2025[category] - mean_val) / std_val
    
    # Convert inverted categories to z-scores (lower is better)
    for category in inverted_categories:
        mean_val = goalies_2025[category].mean()
        std_val = goalies_2025[category].std()
        # For GAA, we want lower values to have higher z-scores
        df_zscore[f'{category}_zscore'] = (mean_val - goalies_2025[category]) / std_val
    
    # Calculate total z-score
    zscore_cols = [f'{cat}_zscore' for cat in categories + inverted_categories]
    df_zscore['zscore_total'] = df_zscore[zscore_cols].sum(axis=1)
    
    # Rank by z-score total
    df_zscore['zscore_rank'] = df_zscore['zscore_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_zscore = df_zscore.nsmallest(20, 'zscore_rank')[['name', 'zscore_rank', 'zscore_total', 'wins', 'saves', 'save_percentage', 'goals_against_average']]
    print("Top 20 Goalies by Z-Score System:")
    for i, row in top_zscore.iterrows():
        print(f"{row['zscore_rank']:2.0f}. {row['name']:<25} Score: {row['zscore_total']:6.2f} | W:{row['wins']:2.0f} S:{row['saves']:4.0f} SV%:{row['save_percentage']:5.3f} GAA:{row['goals_against_average']:4.2f}")
    
    return df_zscore

def normalized_goalie_ranking_system(df):
    """
    Normalized Goalie Ranking
    - Normalize each category to 0-1 scale
    - Sum normalized values for overall score
    - Treats all categories equally
    """
    print("\nNORMALIZED GOALIE RANKING")
    print("="*70)
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    
    categories = ['wins', 'saves', 'save_percentage']
    inverted_categories = ['goals_against_average']  # Lower GAA is better
    
    df_normalized = goalies_2025.copy()
    
    # Normalize normal categories to 0-1 scale
    for category in categories:
        min_val = goalies_2025[category].min()
        max_val = goalies_2025[category].max()
        if max_val > min_val:  # Avoid division by zero
            df_normalized[f'{category}_normalized'] = (goalies_2025[category] - min_val) / (max_val - min_val)
        else:
            df_normalized[f'{category}_normalized'] = 0
    
    # Normalize inverted categories (lower is better)
    for category in inverted_categories:
        min_val = goalies_2025[category].min()
        max_val = goalies_2025[category].max()
        if max_val > min_val:  # Avoid division by zero
            # For GAA, we want lower values to have higher normalized scores
            df_normalized[f'{category}_normalized'] = (max_val - goalies_2025[category]) / (max_val - min_val)
        else:
            df_normalized[f'{category}_normalized'] = 0
    
    # Calculate total normalized score
    normalized_cols = [f'{cat}_normalized' for cat in categories + inverted_categories]
    df_normalized['normalized_total'] = df_normalized[normalized_cols].sum(axis=1)
    
    # Rank by normalized total
    df_normalized['normalized_rank'] = df_normalized['normalized_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_normalized = df_normalized.nsmallest(20, 'normalized_rank')[['name', 'normalized_rank', 'normalized_total', 'wins', 'saves', 'save_percentage', 'goals_against_average']]
    print("Top 20 Goalies by Normalized System:")
    for i, row in top_normalized.iterrows():
        print(f"{row['normalized_rank']:2.0f}. {row['name']:<25} Score: {row['normalized_total']:6.3f} | W:{row['wins']:2.0f} S:{row['saves']:4.0f} SV%:{row['save_percentage']:5.3f} GAA:{row['goals_against_average']:4.2f}")
    
    return df_normalized

def compare_goalie_systems(df):
    """Compare the top goalies across equal weight ranking systems."""
    print("\n" + "="*80)
    print("COMPARISON OF EQUAL WEIGHT GOALIE RANKING SYSTEMS")
    print("="*80)
    
    # Get results from all systems
    df_percentile = percentile_goalie_ranking_system(df)
    df_zscore = z_score_goalie_ranking_system(df)
    df_normalized = normalized_goalie_ranking_system(df)
    
    # Find goalies who appear in top 15 of any system
    top_goalies = set()
    systems = [
        ('Percentile', df_percentile, 'percentile_rank'),
        ('Z-Score', df_zscore, 'zscore_rank'),
        ('Normalized', df_normalized, 'normalized_rank')
    ]
    
    for system_name, df_system, rank_col in systems:
        top_15 = df_system.nsmallest(15, rank_col)
        top_goalies.update(top_15['name'].tolist())
    
    # Create comparison for each top goalie
    comparison_data = []
    for goalie in sorted(top_goalies):
        row = {'Goalie': goalie}
        for system_name, df_system, rank_col in systems:
            goalie_data = df_system[df_system['name'] == goalie]
            if not goalie_data.empty:
                row[system_name] = goalie_data[rank_col].iloc[0]
            else:
                row[system_name] = 'N/A'
        comparison_data.append(row)
    
    # Show comparison
    comparison_df = pd.DataFrame(comparison_data)
    print("\nTop Goalies Across All Equal Weight Systems:")
    print(comparison_df.head(20).to_string(index=False))
    
    return comparison_df

def save_recommended_goalie_rankings(df):
    """Save the recommended percentile-based goalie rankings to CSV."""
    print("\n" + "="*70)
    print("SAVING RECOMMENDED GOALIE RANKINGS")
    print("="*70)
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    
    # Use percentile system as the recommended one
    categories = ['wins', 'saves', 'save_percentage']
    inverted_categories = ['goals_against_average']
    
    df_percentile = goalies_2025.copy()
    
    # Convert each category to percentiles
    for category in categories:
        df_percentile[f'{category}_percentile'] = df_percentile[category].rank(pct=True) * 100
    
    for category in inverted_categories:
        df_percentile[f'{category}_percentile'] = df_percentile[category].rank(pct=True, ascending=False) * 100
    
    # Calculate total percentile score
    percentile_cols = [f'{cat}_percentile' for cat in categories + inverted_categories]
    df_percentile['percentile_total'] = df_percentile[percentile_cols].sum(axis=1)
    
    # Rank by percentile total
    df_percentile['percentile_rank'] = df_percentile['percentile_total'].rank(method='dense', ascending=False)
    
    # Create output with all relevant columns
    output_columns = ['name', 'percentile_rank', 'percentile_total'] + percentile_cols + categories + inverted_categories
    output_df = df_percentile[output_columns].sort_values('percentile_rank')
    
    # Save to CSV
    output_file = 'equal_weight_goalie_rankings_2025.csv'
    output_df.to_csv(output_file, index=False)
    print(f"✓ Recommended equal weight goalie rankings saved to: {output_file}")
    
    # Show top 10
    print("\nTop 10 Equal Weight Goalie Rankings:")
    for i, row in output_df.head(10).iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<25} Score: {row['percentile_total']:6.1f} | W:{row['wins']:2.0f} S:{row['saves']:4.0f} SV%:{row['save_percentage']:5.3f} GAA:{row['goals_against_average']:4.2f}")
    
    return output_df

def show_goalie_insights(df):
    """Show insights about goalie performance across categories."""
    print("\n" + "="*70)
    print("GOALIE PERFORMANCE INSIGHTS")
    print("="*70)
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    
    print(f"Total goalies analyzed: {len(goalies_2025)}")
    print(f"Minimum games played: {goalies_2025['games_played'].min()}")
    print(f"Maximum games played: {goalies_2025['games_played'].max()}")
    print(f"Average games played: {goalies_2025['games_played'].mean():.1f}")
    
    print("\nCategory Statistics:")
    categories = ['wins', 'saves', 'save_percentage', 'goals_against_average']
    for category in categories:
        print(f"  {category.replace('_', ' ').title()}:")
        print(f"    Min: {goalies_2025[category].min():.3f}")
        print(f"    Max: {goalies_2025[category].max():.3f}")
        print(f"    Mean: {goalies_2025[category].mean():.3f}")
        print(f"    Std: {goalies_2025[category].std():.3f}")
    
    print("\nTop Performers by Category:")
    for category in categories:
        if category == 'goals_against_average':
            # Lower is better for GAA
            top_performer = goalies_2025.loc[goalies_2025[category].idxmin()]
            print(f"  Best {category.replace('_', ' ').title()}: {top_performer['name']} ({top_performer[category]:.3f})")
        else:
            # Higher is better for other categories
            top_performer = goalies_2025.loc[goalies_2025[category].idxmax()]
            print(f"  Best {category.replace('_', ' ').title()}: {top_performer['name']} ({top_performer[category]:.3f})")

def main():
    """Main function to run equal weight goalie ranking systems."""
    print("EQUAL WEIGHT FANTASY HOCKEY GOALIE RANKING SYSTEMS")
    print("="*80)
    print("Optimized for leagues where all goalie categories are equally weighted")
    print("Categories: Wins, Saves, Save Percentage, Goals Against Average")
    print("="*80)
    
    # Load data
    df = load_goalie_data()
    print(f"Loaded goalie data for seasons: {sorted(df['season'].unique())}")
    
    # Show insights
    show_goalie_insights(df)
    
    # Run all systems and compare
    comparison = compare_goalie_systems(df)
    
    # Save recommended rankings
    recommended = save_recommended_goalie_rankings(df)
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR EQUAL WEIGHT GOALIE LEAGUES:")
    print("="*80)
    print("🥇 PERCENTILE SYSTEM (BEST FOR EQUAL WEIGHT):")
    print("   ✅ Treats all categories equally (perfect for your league)")
    print("   ✅ Converts raw stats to 0-100 percentiles")
    print("   ✅ Properly handles GAA (lower is better)")
    print("   ✅ Less sensitive to outliers")
    print("   ✅ Easy to understand and explain")
    print("   ✅ Most balanced approach")
    print()
    print("🥈 Z-SCORE SYSTEM (BEST FOR STATISTICAL ACCURACY):")
    print("   ✅ Accounts for distribution differences")
    print("   ✅ Most mathematically sound")
    print("   ✅ Good for identifying true outliers")
    print("   ✅ Properly handles GAA (lower is better)")
    print("   ✅ Treats all categories equally")
    print()
    print("🥉 NORMALIZED SYSTEM (BEST FOR BALANCE):")
    print("   ✅ Normalizes all categories to 0-1 scale")
    print("   ✅ Treats all categories equally")
    print("   ✅ Properly handles GAA (lower is better)")
    print("   ✅ Good for comparing across different stat types")
    print()
    print("💡 FINAL RECOMMENDATION:")
    print("   Use the PERCENTILE SYSTEM as your primary goalie ranking")
    print("   - Perfect for equal weight leagues")
    print("   - Most intuitive and balanced")
    print("   - Properly handles GAA inversion")
    print("   - Saved as 'equal_weight_goalie_rankings_2025.csv'")

if __name__ == "__main__":
    main()
