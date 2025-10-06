#!/usr/bin/env python3
"""
Equal Weight Fantasy Hockey Ranking System

This script implements ranking systems optimized for leagues where
all categories are equally weighted.
"""

import pandas as pd
import numpy as np

def load_data():
    """Load the corrected 2025 skater data."""
    return pd.read_csv('skater_data_2025_corrected.csv')

def percentile_ranking_system(df):
    """
    System 1: Percentile-Based Ranking (BEST FOR EQUAL WEIGHT LEAGUES)
    - Convert raw stats to percentiles (0-100)
    - Sum percentiles for overall score
    - Treats all categories equally
    """
    print("SYSTEM 1: PERCENTILE-BASED RANKING (RECOMMENDED FOR EQUAL WEIGHT)")
    print("="*70)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_percentile = df.copy()
    
    # Convert each category to percentiles
    for category in categories:
        df_percentile[f'{category}_percentile'] = df[category].rank(pct=True) * 100
    
    # Calculate total percentile score
    percentile_cols = [f'{cat}_percentile' for cat in categories]
    df_percentile['percentile_total'] = df_percentile[percentile_cols].sum(axis=1)
    
    # Rank by percentile total
    df_percentile['percentile_rank'] = df_percentile['percentile_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_percentile = df_percentile.nsmallest(20, 'percentile_rank')[['name', 'position', 'percentile_rank', 'percentile_total', 'goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']]
    print("Top 20 by Percentile System:")
    for i, row in top_percentile.iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['percentile_total']:6.1f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} H:{row['hits']:3.0f} B:{row['blocked_shots']:3.0f} FOW:{row['face_off_wins']:3.0f} S:{row['shots']:3.0f}")
    
    return df_percentile

def z_score_ranking_system(df):
    """
    System 2: Z-Score Based Ranking (BEST FOR STATISTICAL ACCURACY)
    - Convert stats to z-scores (standard deviations from mean)
    - Sum z-scores for overall score
    - Accounts for distribution differences between categories
    """
    print("\nSYSTEM 2: Z-SCORE BASED RANKING")
    print("="*70)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_zscore = df.copy()
    
    # Convert each category to z-scores
    for category in categories:
        mean_val = df[category].mean()
        std_val = df[category].std()
        df_zscore[f'{category}_zscore'] = (df[category] - mean_val) / std_val
    
    # Calculate total z-score
    zscore_cols = [f'{cat}_zscore' for cat in categories]
    df_zscore['zscore_total'] = df_zscore[zscore_cols].sum(axis=1)
    
    # Rank by z-score total
    df_zscore['zscore_rank'] = df_zscore['zscore_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_zscore = df_zscore.nsmallest(20, 'zscore_rank')[['name', 'position', 'zscore_rank', 'zscore_total', 'goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']]
    print("Top 20 by Z-Score System:")
    for i, row in top_zscore.iterrows():
        print(f"{row['zscore_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['zscore_total']:6.2f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} H:{row['hits']:3.0f} B:{row['blocked_shots']:3.0f} FOW:{row['face_off_wins']:3.0f} S:{row['shots']:3.0f}")
    
    return df_zscore

def normalized_ranking_system(df):
    """
    System 3: Normalized Ranking (BEST FOR BALANCE)
    - Normalize each category to 0-1 scale
    - Sum normalized values for overall score
    - Treats all categories equally
    """
    print("\nSYSTEM 3: NORMALIZED RANKING")
    print("="*70)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_normalized = df.copy()
    
    # Normalize each category to 0-1 scale
    for category in categories:
        min_val = df[category].min()
        max_val = df[category].max()
        if max_val > min_val:  # Avoid division by zero
            df_normalized[f'{category}_normalized'] = (df[category] - min_val) / (max_val - min_val)
        else:
            df_normalized[f'{category}_normalized'] = 0
    
    # Calculate total normalized score
    normalized_cols = [f'{cat}_normalized' for cat in categories]
    df_normalized['normalized_total'] = df_normalized[normalized_cols].sum(axis=1)
    
    # Rank by normalized total
    df_normalized['normalized_rank'] = df_normalized['normalized_total'].rank(method='dense', ascending=False)
    
    # Show top 20
    top_normalized = df_normalized.nsmallest(20, 'normalized_rank')[['name', 'position', 'normalized_rank', 'normalized_total', 'goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']]
    print("Top 20 by Normalized System:")
    for i, row in top_normalized.iterrows():
        print(f"{row['normalized_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['normalized_total']:6.3f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} H:{row['hits']:3.0f} B:{row['blocked_shots']:3.0f} FOW:{row['face_off_wins']:3.0f} S:{row['shots']:3.0f}")
    
    return df_normalized

def position_adjusted_equal_weight(df):
    """
    System 4: Position-Adjusted Equal Weight
    - Rank players within their position first
    - Then combine position rankings
    - Accounts for position scarcity while maintaining equal weights
    """
    print("\nSYSTEM 4: POSITION-ADJUSTED EQUAL WEIGHT")
    print("="*70)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_pos = df.copy()
    
    # Rank within each position
    position_ranks = []
    for position in df['position'].unique():
        pos_data = df[df['position'] == position].copy()
        
        for category in categories:
            pos_data[f'{category}_pos_rank'] = pos_data[category].rank(method='dense', ascending=False)
        
        # Calculate position-adjusted total (sum of ranks within position)
        pos_rank_cols = [f'{cat}_pos_rank' for cat in categories]
        pos_data['pos_total_rank'] = pos_data[pos_rank_cols].sum(axis=1)
        
        position_ranks.append(pos_data)
    
    # Combine all positions
    df_pos_combined = pd.concat(position_ranks, ignore_index=True)
    
    # Final ranking across all positions
    df_pos_combined['position_adjusted_rank'] = df_pos_combined['pos_total_rank'].rank(method='dense', ascending=True)
    
    # Show top 20
    top_pos = df_pos_combined.nsmallest(20, 'position_adjusted_rank')[['name', 'position', 'position_adjusted_rank', 'pos_total_rank', 'goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']]
    print("Top 20 by Position-Adjusted System:")
    for i, row in top_pos.iterrows():
        print(f"{row['position_adjusted_rank']:2.0f}. {row['name']:<20} ({row['position']}) Total: {row['pos_total_rank']:4.0f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} H:{row['hits']:3.0f} B:{row['blocked_shots']:3.0f} FOW:{row['face_off_wins']:3.0f} S:{row['shots']:3.0f}")
    
    return df_pos_combined

def compare_equal_weight_systems(df):
    """Compare the top players across equal weight ranking systems."""
    print("\n" + "="*80)
    print("COMPARISON OF EQUAL WEIGHT RANKING SYSTEMS")
    print("="*80)
    
    # Get results from all systems
    df_percentile = percentile_ranking_system(df)
    df_zscore = z_score_ranking_system(df)
    df_normalized = normalized_ranking_system(df)
    df_pos = position_adjusted_equal_weight(df)
    
    # Find players who appear in top 15 of any system
    top_players = set()
    systems = [
        ('Percentile', df_percentile, 'percentile_rank'),
        ('Z-Score', df_zscore, 'zscore_rank'),
        ('Normalized', df_normalized, 'normalized_rank'),
        ('Position-Adj', df_pos, 'position_adjusted_rank')
    ]
    
    for system_name, df_system, rank_col in systems:
        top_15 = df_system.nsmallest(15, rank_col)
        top_players.update(top_15['name'].tolist())
    
    # Create comparison for each top player
    comparison_data = []
    for player in sorted(top_players):
        row = {'Player': player}
        for system_name, df_system, rank_col in systems:
            player_data = df_system[df_system['name'] == player]
            if not player_data.empty:
                row[system_name] = player_data[rank_col].iloc[0]
            else:
                row[system_name] = 'N/A'
        comparison_data.append(row)
    
    # Show comparison
    comparison_df = pd.DataFrame(comparison_data)
    print("\nTop Players Across All Equal Weight Systems:")
    print(comparison_df.head(25).to_string(index=False))
    
    return comparison_df

def save_recommended_rankings(df):
    """Save the recommended percentile-based rankings to CSV."""
    print("\n" + "="*70)
    print("SAVING RECOMMENDED RANKINGS")
    print("="*70)
    
    # Use percentile system as the recommended one
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_percentile = df.copy()
    
    # Convert each category to percentiles
    for category in categories:
        df_percentile[f'{category}_percentile'] = df[category].rank(pct=True) * 100
    
    # Calculate total percentile score
    percentile_cols = [f'{cat}_percentile' for cat in categories]
    df_percentile['percentile_total'] = df_percentile[percentile_cols].sum(axis=1)
    
    # Rank by percentile total
    df_percentile['percentile_rank'] = df_percentile['percentile_total'].rank(method='dense', ascending=False)
    
    # Create output with all relevant columns
    output_columns = ['name', 'position', 'percentile_rank', 'percentile_total'] + percentile_cols + categories
    output_df = df_percentile[output_columns].sort_values('percentile_rank')
    
    # Save to CSV
    output_file = 'equal_weight_skater_rankings_2025.csv'
    output_df.to_csv(output_file, index=False)
    print(f"✓ Recommended equal weight rankings saved to: {output_file}")
    
    # Show top 10
    print("\nTop 10 Equal Weight Rankings:")
    for i, row in output_df.head(10).iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['percentile_total']:6.1f}")
    
    return output_df

def main():
    """Main function to run equal weight ranking systems."""
    print("EQUAL WEIGHT FANTASY HOCKEY RANKING SYSTEMS")
    print("="*80)
    print("Optimized for leagues where all categories are equally weighted")
    print("="*80)
    
    # Load data
    df = load_data()
    print(f"Loaded {len(df)} players for analysis")
    
    # Run all systems and compare
    comparison = compare_equal_weight_systems(df)
    
    # Save recommended rankings
    recommended = save_recommended_rankings(df)
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR EQUAL WEIGHT LEAGUES:")
    print("="*80)
    print("🥇 PERCENTILE SYSTEM (BEST FOR EQUAL WEIGHT):")
    print("   ✅ Treats all categories equally (perfect for your league)")
    print("   ✅ Converts raw stats to 0-100 percentiles")
    print("   ✅ Less sensitive to outliers")
    print("   ✅ Easy to understand and explain")
    print("   ✅ Most balanced approach")
    print()
    print("🥈 Z-SCORE SYSTEM (BEST FOR STATISTICAL ACCURACY):")
    print("   ✅ Accounts for distribution differences")
    print("   ✅ Most mathematically sound")
    print("   ✅ Good for identifying true outliers")
    print("   ✅ Treats all categories equally")
    print()
    print("🥉 NORMALIZED SYSTEM (BEST FOR BALANCE):")
    print("   ✅ Normalizes all categories to 0-1 scale")
    print("   ✅ Treats all categories equally")
    print("   ✅ Good for comparing across different stat types")
    print()
    print("🏅 POSITION-ADJUSTED (BEST FOR POSITION SCARCITY):")
    print("   ✅ Ranks within position first")
    print("   ✅ Accounts for position scarcity")
    print("   ✅ Good for leagues with position limits")
    print()
    print("💡 FINAL RECOMMENDATION:")
    print("   Use the PERCENTILE SYSTEM as your primary ranking")
    print("   - Perfect for equal weight leagues")
    print("   - Most intuitive and balanced")
    print("   - Saved as 'equal_weight_skater_rankings_2025.csv'")

if __name__ == "__main__":
    main()
