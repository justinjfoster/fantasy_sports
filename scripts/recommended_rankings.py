#!/usr/bin/env python3
"""
Recommended Fantasy Hockey Ranking Systems

This script implements the most practical alternative ranking approaches
for fantasy hockey evaluation.
"""

import pandas as pd
import numpy as np

def load_data():
    """Load the corrected 2025 skater data."""
    return pd.read_csv('skater_data_2025_corrected.csv')

def weighted_ranking_system(df):
    """
    System 1: Weighted Categories (RECOMMENDED)
    - Goals and assists weighted higher (offensive categories)
    - Face-off wins weighted by position (centers get more weight)
    - Hits and blocked shots weighted lower
    """
    print("SYSTEM 1: WEIGHTED CATEGORIES (RECOMMENDED)")
    print("="*60)
    
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
    
    # Show top 15
    top_weighted = df_weighted.nsmallest(15, 'weighted_rank')[['name', 'position', 'weighted_rank', 'weighted_total', 'goals', 'assists', 'power_play_points', 'face_off_wins']]
    print("Top 15 by Weighted System:")
    for i, row in top_weighted.iterrows():
        print(f"{row['weighted_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['weighted_total']:6.1f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} FOW:{row['face_off_wins']:3.0f}")
    
    return df_weighted

def percentile_ranking_system(df):
    """
    System 2: Percentile-Based Ranking
    - Convert raw stats to percentiles (0-100)
    - Sum percentiles for overall score
    - More balanced than raw ranks
    """
    print("\nSYSTEM 2: PERCENTILE-BASED RANKING")
    print("="*60)
    
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
    
    # Show top 15
    top_percentile = df_percentile.nsmallest(15, 'percentile_rank')[['name', 'position', 'percentile_rank', 'percentile_total', 'goals', 'assists', 'power_play_points', 'face_off_wins']]
    print("Top 15 by Percentile System:")
    for i, row in top_percentile.iterrows():
        print(f"{row['percentile_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['percentile_total']:6.1f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} FOW:{row['face_off_wins']:3.0f}")
    
    return df_percentile

def z_score_ranking_system(df):
    """
    System 3: Z-Score Based Ranking
    - Convert stats to z-scores (standard deviations from mean)
    - Sum z-scores for overall score
    - Accounts for distribution differences between categories
    """
    print("\nSYSTEM 3: Z-SCORE BASED RANKING")
    print("="*60)
    
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
    
    # Show top 15
    top_zscore = df_zscore.nsmallest(15, 'zscore_rank')[['name', 'position', 'zscore_rank', 'zscore_total', 'goals', 'assists', 'power_play_points', 'face_off_wins']]
    print("Top 15 by Z-Score System:")
    for i, row in top_zscore.iterrows():
        print(f"{row['zscore_rank']:2.0f}. {row['name']:<20} ({row['position']}) Score: {row['zscore_total']:6.2f} | G:{row['goals']:2.0f} A:{row['assists']:2.0f} PPP:{row['power_play_points']:2.0f} FOW:{row['face_off_wins']:3.0f}")
    
    return df_zscore

def efficiency_ranking_system(df):
    """
    System 4: Per-Game Efficiency Ranking
    - Calculate stats per game played
    - Rank based on efficiency rather than raw totals
    - Better for players who missed games due to injury
    """
    print("\nSYSTEM 4: PER-GAME EFFICIENCY RANKING")
    print("="*60)
    
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
    
    # Show top 15
    top_efficiency = df_efficiency.nsmallest(15, 'efficiency_rank')[['name', 'position', 'efficiency_rank', 'games_played', 'goals_per_game', 'assists_per_game', 'power_play_points_per_game']]
    print("Top 15 by Efficiency System:")
    for i, row in top_efficiency.iterrows():
        print(f"{row['efficiency_rank']:2.0f}. {row['name']:<20} ({row['position']}) GP: {row['games_played']:2.0f} | G/GP: {row['goals_per_game']:.2f} A/GP: {row['assists_per_game']:.2f} PPP/GP: {row['power_play_points_per_game']:.2f}")
    
    return df_efficiency

def compare_top_players(df):
    """Compare the top 10 players across the main ranking systems."""
    print("\n" + "="*80)
    print("TOP PLAYERS COMPARISON")
    print("="*80)
    
    # Get results from main systems
    df_weighted = weighted_ranking_system(df)
    df_percentile = percentile_ranking_system(df)
    df_zscore = z_score_ranking_system(df)
    df_efficiency = efficiency_ranking_system(df)
    
    # Find players who appear in top 10 of any system
    top_players = set()
    systems = [
        ('Weighted', df_weighted, 'weighted_rank'),
        ('Percentile', df_percentile, 'percentile_rank'),
        ('Z-Score', df_zscore, 'zscore_rank'),
        ('Efficiency', df_efficiency, 'efficiency_rank')
    ]
    
    for system_name, df_system, rank_col in systems:
        top_10 = df_system.nsmallest(10, rank_col)
        top_players.update(top_10['name'].tolist())
    
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
    print("\nTop Players Across All Systems:")
    print(comparison_df.head(20).to_string(index=False))
    
    return comparison_df

def main():
    """Main function to run recommended ranking systems."""
    print("RECOMMENDED FANTASY HOCKEY RANKING SYSTEMS")
    print("="*80)
    print("Comparing the most practical approaches for fantasy evaluation")
    print("="*80)
    
    # Load data
    df = load_data()
    print(f"Loaded {len(df)} players for analysis")
    
    # Run main systems and compare
    comparison = compare_top_players(df)
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("🥇 WEIGHTED SYSTEM (BEST OVERALL):")
    print("   ✅ Emphasizes scoring categories appropriately")
    print("   ✅ Adjusts face-off value by position")
    print("   ✅ Easy to customize weights for your league")
    print("   ✅ Most realistic for standard fantasy leagues")
    print()
    print("🥈 PERCENTILE SYSTEM (BEST FOR BALANCE):")
    print("   ✅ Treats all categories equally")
    print("   ✅ Good for leagues with unusual scoring")
    print("   ✅ Less sensitive to outliers")
    print("   ✅ Good for category-based leagues")
    print()
    print("🥉 Z-SCORE SYSTEM (BEST FOR ANALYTICS):")
    print("   ✅ Accounts for distribution differences")
    print("   ✅ Most mathematically sound")
    print("   ✅ Good for advanced analytics")
    print("   ✅ Best for identifying true outliers")
    print()
    print("🏅 EFFICIENCY SYSTEM (BEST FOR INJURY-PRONE):")
    print("   ✅ Per-game basis accounts for missed games")
    print("   ✅ Good for identifying breakout candidates")
    print("   ✅ Useful for dynasty/keeper leagues")
    print("   ✅ Best for players with injury concerns")
    print()
    print("💡 CUSTOMIZATION TIPS:")
    print("   • Adjust weights in weighted system for your league")
    print("   • Consider position scarcity in your league")
    print("   • Use efficiency system for injury-prone players")
    print("   • Combine multiple systems for best results")

if __name__ == "__main__":
    main()
