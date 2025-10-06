#!/usr/bin/env python3
"""
Alternative Player Ranking Systems

This script implements several different ranking approaches to evaluate
players more effectively for fantasy hockey.
"""

import pandas as pd
import numpy as np

def load_data():
    """Load the corrected 2025 skater data."""
    return pd.read_csv('skater_data_2025_corrected.csv')

def weighted_ranking_system(df):
    """
    System 1: Weighted Categories
    - Goals and assists weighted higher (offensive categories)
    - Face-off wins weighted by position (centers get more weight)
    - Hits and blocked shots weighted lower
    """
    print("SYSTEM 1: WEIGHTED CATEGORIES")
    print("="*50)
    
    # Define weights for each category
    weights = {
        'goals': 3.0,           # High weight - primary scoring
        'assists': 2.5,         # High weight - primary scoring  
        'power_play_points': 2.0, # Medium-high - special teams
        'shots': 1.5,           # Medium - volume stat
        'face_off_wins': 1.0,   # Variable by position
        'hits': 0.8,            # Lower weight - peripheral
        'blocked_shots': 0.8    # Lower weight - peripheral
    }
    
    # Create weighted scores
    df_weighted = df.copy()
    
    for category, weight in weights.items():
        if category == 'face_off_wins':
            # Weight face-off wins by position (centers get full weight)
            position_multiplier = df['position'].map({'C': 1.0, 'F': 0.3, 'LW': 0.3, 'RW': 0.3, 'D': 0.1})
            df_weighted[f'{category}_weighted'] = df[category] * weight * position_multiplier
        else:
            df_weighted[f'{category}_weighted'] = df[category] * weight
    
    # Calculate total weighted score
    weighted_cols = [f'{cat}_weighted' for cat in weights.keys()]
    df_weighted['weighted_total'] = df_weighted[weighted_cols].sum(axis=1)
    
    # Rank by weighted total
    df_weighted['weighted_rank'] = df_weighted['weighted_total'].rank(method='dense', ascending=False)
    
    # Show top 10
    top_weighted = df_weighted.nsmallest(10, 'weighted_rank')[['name', 'position', 'weighted_rank', 'weighted_total'] + weighted_cols]
    print("Top 10 by Weighted System:")
    for i, row in top_weighted.iterrows():
        print(f"{row['weighted_rank']:2.0f}. {row['name']:<20} Score: {row['weighted_total']:6.1f}")
    
    return df_weighted

def percentile_ranking_system(df):
    """
    System 2: Percentile-Based Ranking
    - Convert raw stats to percentiles (0-100)
    - Sum percentiles for overall score
    - More balanced than raw ranks
    """
    print("\nSYSTEM 2: PERCENTILE-BASED RANKING")
    print("="*50)
    
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
    
    # Show top 10
    top_percentile = df_percentile.nsmallest(10, 'percentile_rank')[['name', 'position', 'percentile_rank', 'percentile_total'] + percentile_cols]
    print("Top 10 by Percentile System:")
    for i, row in top_percentile.iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<20} Score: {row['percentile_total']:6.1f}")
    
    return df_percentile

def z_score_ranking_system(df):
    """
    System 3: Z-Score Based Ranking
    - Convert stats to z-scores (standard deviations from mean)
    - Sum z-scores for overall score
    - Accounts for distribution differences between categories
    """
    print("\nSYSTEM 3: Z-SCORE BASED RANKING")
    print("="*50)
    
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
    
    # Show top 10
    top_zscore = df_zscore.nsmallest(10, 'zscore_rank')[['name', 'position', 'zscore_rank', 'zscore_total'] + zscore_cols]
    print("Top 10 by Z-Score System:")
    for i, row in top_zscore.iterrows():
        print(f"{row['zscore_rank']:2.0f}. {row['name']:<20} Score: {row['zscore_total']:6.2f}")
    
    return df_zscore

def position_adjusted_ranking_system(df):
    """
    System 4: Position-Adjusted Ranking
    - Rank players within their position first
    - Then combine position rankings
    - Accounts for position scarcity and different stat expectations
    """
    print("\nSYSTEM 4: POSITION-ADJUSTED RANKING")
    print("="*50)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_pos = df.copy()
    
    # Rank within each position
    position_ranks = []
    for position in df['position'].unique():
        pos_data = df[df['position'] == position].copy()
        
        for category in categories:
            pos_data[f'{category}_pos_rank'] = pos_data[category].rank(method='dense', ascending=False)
        
        # Calculate position-adjusted total
        pos_rank_cols = [f'{cat}_pos_rank' for cat in categories]
        pos_data['pos_total_rank'] = pos_data[pos_rank_cols].sum(axis=1)
        
        position_ranks.append(pos_data)
    
    # Combine all positions
    df_pos_combined = pd.concat(position_ranks, ignore_index=True)
    
    # Final ranking across all positions
    df_pos_combined['position_adjusted_rank'] = df_pos_combined['pos_total_rank'].rank(method='dense', ascending=True)
    
    # Show top 10
    top_pos = df_pos_combined.nsmallest(10, 'position_adjusted_rank')[['name', 'position', 'position_adjusted_rank', 'pos_total_rank']]
    print("Top 10 by Position-Adjusted System:")
    for i, row in top_pos.iterrows():
        print(f"{row['position_adjusted_rank']:2.0f}. {row['name']:<20} ({row['position']}) Total: {row['pos_total_rank']:4.0f}")
    
    return df_pos_combined

def efficiency_ranking_system(df):
    """
    System 5: Per-Game Efficiency Ranking
    - Calculate stats per game played
    - Rank based on efficiency rather than raw totals
    - Better for players who missed games due to injury
    """
    print("\nSYSTEM 5: PER-GAME EFFICIENCY RANKING")
    print("="*50)
    
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    df_efficiency = df.copy()
    
    # Calculate per-game stats
    for category in categories:
        df_efficiency[f'{category}_per_game'] = df[category] / df['games_played']
    
    # Rank per-game stats
    for category in categories:
        df_efficiency[f'{category}_efficiency_rank'] = df_efficiency[f'{category}_per_game'].rank(method='dense', ascending=False)
    
    # Calculate total efficiency rank
    efficiency_rank_cols = [f'{cat}_efficiency_rank' for cat in categories]
    df_efficiency['efficiency_total_rank'] = df_efficiency[efficiency_rank_cols].sum(axis=1)
    
    # Final ranking
    df_efficiency['efficiency_rank'] = df_efficiency['efficiency_total_rank'].rank(method='dense', ascending=True)
    
    # Show top 10
    top_efficiency = df_efficiency.nsmallest(10, 'efficiency_rank')[['name', 'position', 'efficiency_rank', 'games_played'] + [f'{cat}_per_game' for cat in categories[:3]]]
    print("Top 10 by Efficiency System:")
    for i, row in top_efficiency.iterrows():
        print(f"{row['efficiency_rank']:2.0f}. {row['name']:<20} GP: {row['games_played']:2.0f} G/GP: {row['goals_per_game']:.2f} A/GP: {row['assists_per_game']:.2f}")
    
    return df_efficiency

def compare_systems(df):
    """Compare the top 10 players across all ranking systems."""
    print("\n" + "="*80)
    print("COMPARISON OF RANKING SYSTEMS")
    print("="*80)
    
    # Get results from all systems
    df_weighted = weighted_ranking_system(df)
    df_percentile = percentile_ranking_system(df)
    df_zscore = z_score_ranking_system(df)
    df_pos = position_adjusted_ranking_system(df)
    df_efficiency = efficiency_ranking_system(df)
    
    # Create comparison table
    comparison_data = []
    
    # Get top 10 from each system
    systems = [
        ('Weighted', df_weighted, 'weighted_rank'),
        ('Percentile', df_percentile, 'percentile_rank'),
        ('Z-Score', df_zscore, 'zscore_rank'),
        ('Position-Adj', df_pos, 'position_adjusted_rank'),
        ('Efficiency', df_efficiency, 'efficiency_rank')
    ]
    
    # Find players who appear in top 10 of any system
    top_players = set()
    for system_name, df_system, rank_col in systems:
        top_10 = df_system.nsmallest(10, rank_col)
        top_players.update(top_10['name'].tolist())
    
    # Create comparison for each top player
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
    print("\nTop Players Across All Systems:")
    print(comparison_df.head(15).to_string(index=False))
    
    return comparison_df

def main():
    """Main function to run all ranking systems."""
    print("ALTERNATIVE FANTASY HOCKEY RANKING SYSTEMS")
    print("="*80)
    print("Comparing different approaches to evaluate player value")
    print("="*80)
    
    # Load data
    df = load_data()
    print(f"Loaded {len(df)} players for analysis")
    
    # Run all systems and compare
    comparison = compare_systems(df)
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("1. WEIGHTED SYSTEM: Best for standard fantasy leagues")
    print("   - Emphasizes scoring categories appropriately")
    print("   - Adjusts face-off value by position")
    print("   - Easy to customize weights for your league")
    print()
    print("2. PERCENTILE SYSTEM: Best for balanced evaluation")
    print("   - Treats all categories equally")
    print("   - Good for leagues with unusual scoring")
    print("   - Less sensitive to outliers")
    print()
    print("3. Z-SCORE SYSTEM: Best for statistical accuracy")
    print("   - Accounts for distribution differences")
    print("   - Most mathematically sound")
    print("   - Good for advanced analytics")
    print()
    print("4. POSITION-ADJUSTED: Best for position scarcity")
    print("   - Accounts for different position expectations")
    print("   - Good for leagues with position limits")
    print("   - Helps identify position-specific value")
    print()
    print("5. EFFICIENCY SYSTEM: Best for injury-prone players")
    print("   - Per-game basis accounts for missed games")
    print("   - Good for identifying breakout candidates")
    print("   - Useful for dynasty/keeper leagues")

if __name__ == "__main__":
    main()
