#!/usr/bin/env python3
"""
Player Ranking Script for 2025 Season

This script ranks skaters and goalies across multiple categories and calculates
overall rankings based on cumulative rank scores.
"""

import pandas as pd
import numpy as np

def rank_skaters_2025():
    """Rank skaters across 7 categories for 2025 season."""
    print("Ranking skaters for 2025 season...")
    
    # Load the corrected 2025 data
    skaters_2025 = pd.read_csv('skater_data_2025_corrected.csv')
    print(f"Found {len(skaters_2025)} skaters for 2025 season")
    
    # Define the 7 categories for ranking
    categories = ['goals', 'assists', 'power_play_points', 'hits', 'blocked_shots', 'face_off_wins', 'shots']
    
    # Create ranking columns
    ranking_data = skaters_2025[['name', 'position']].copy()
    
    # Rank each category (higher values get better ranks)
    for category in categories:
        # Use dense ranking (ties get same rank, next rank doesn't skip)
        ranking_data[f'{category}_rank'] = skaters_2025[category].rank(method='dense', ascending=False)
    
    # Calculate overall rank (sum of all category ranks)
    rank_columns = [f'{cat}_rank' for cat in categories]
    ranking_data['overall_rank'] = ranking_data[rank_columns].sum(axis=1)
    
    # Sort by overall rank (lower total rank score is better)
    ranking_data = ranking_data.sort_values('overall_rank').reset_index(drop=True)
    
    # Re-rank the overall rank to get final 1st, 2nd, 3rd, etc.
    ranking_data['overall_rank'] = ranking_data['overall_rank'].rank(method='dense', ascending=True)
    
    # Reorder columns for output
    output_columns = ['name', 'position', 'overall_rank'] + rank_columns
    ranking_data = ranking_data[output_columns]
    
    # Save to CSV
    output_file = 'skater_rankings_2025.csv'
    ranking_data.to_csv(output_file, index=False)
    print(f"✓ Skater rankings saved to: {output_file}")
    
    # Show top 10 skaters
    print("\nTop 10 skaters by overall rank:")
    print(ranking_data.head(10).to_string(index=False))
    
    return ranking_data

def rank_goalies_2025():
    """Rank goalies across 4 categories for 2025 season."""
    print("\nRanking goalies for 2025 season...")
    
    # Load the data
    df = pd.read_csv('data/goalie_data_2022_2025.csv')
    
    # Filter for 2025 data only
    goalies_2025 = df[df['season'] == 2025].copy()
    print(f"Found {len(goalies_2025)} goalies for 2025 season")
    
    # Define the 4 categories for ranking
    # Note: GAA is inverted (lower is better), save_percentage is normal (higher is better)
    categories = ['wins', 'saves', 'save_percentage']
    inverted_categories = ['goals_against_average']  # Lower GAA is better
    
    # Create ranking columns (goalies don't have position column, so we'll add 'G' for all)
    ranking_data = goalies_2025[['name']].copy()
    ranking_data['position'] = 'G'  # All goalies are position 'G'
    
    # Rank normal categories (higher values get better ranks)
    for category in categories:
        ranking_data[f'{category}_rank'] = goalies_2025[category].rank(method='dense', ascending=False)
    
    # Rank inverted categories (lower values get better ranks)
    for category in inverted_categories:
        ranking_data[f'{category}_rank'] = goalies_2025[category].rank(method='dense', ascending=True)
    
    # Calculate overall rank (sum of all category ranks)
    rank_columns = [f'{cat}_rank' for cat in categories + inverted_categories]
    ranking_data['overall_rank'] = ranking_data[rank_columns].sum(axis=1)
    
    # Sort by overall rank (lower total rank score is better)
    ranking_data = ranking_data.sort_values('overall_rank').reset_index(drop=True)
    
    # Re-rank the overall rank to get final 1st, 2nd, 3rd, etc.
    ranking_data['overall_rank'] = ranking_data['overall_rank'].rank(method='dense', ascending=True)
    
    # Reorder columns for output
    output_columns = ['name', 'position', 'overall_rank'] + rank_columns
    ranking_data = ranking_data[output_columns]
    
    # Save to CSV
    output_file = 'goalie_rankings_2025.csv'
    ranking_data.to_csv(output_file, index=False)
    print(f"✓ Goalie rankings saved to: {output_file}")
    
    # Show top 10 goalies
    print("\nTop 10 goalies by overall rank:")
    print(ranking_data.head(10).to_string(index=False))
    
    return ranking_data

def show_ranking_summary(skaters_df, goalies_df):
    """Show summary statistics of the rankings."""
    print("\n" + "="*60)
    print("RANKING SUMMARY")
    print("="*60)
    
    print(f"Skaters ranked: {len(skaters_df)}")
    print(f"Goalies ranked: {len(goalies_df)}")
    
    # Show category breakdown for top skater
    if len(skaters_df) > 0:
        top_skater = skaters_df.iloc[0]
        print(f"\nTop skater: {top_skater['name']} (Overall Rank: {top_skater['overall_rank']})")
        print("Category ranks:")
        for col in skaters_df.columns:
            if col.endswith('_rank') and col != 'overall_rank':
                category = col.replace('_rank', '')
                print(f"  {category}: {top_skater[col]}")
    
    # Show category breakdown for top goalie
    if len(goalies_df) > 0:
        top_goalie = goalies_df.iloc[0]
        print(f"\nTop goalie: {top_goalie['name']} (Overall Rank: {top_goalie['overall_rank']})")
        print("Category ranks:")
        for col in goalies_df.columns:
            if col.endswith('_rank') and col != 'overall_rank':
                category = col.replace('_rank', '')
                print(f"  {category}: {top_goalie[col]}")

def main():
    """Main function to rank players for 2025 season."""
    print("=" * 60)
    print("PLAYER RANKING FOR 2025 SEASON")
    print("=" * 60)
    print("Ranking skaters across 7 categories and goalies across 4 categories")
    print("Using dense ranking method (ties get same rank)")
    print("=" * 60)
    
    try:
        # Rank skaters
        skaters_rankings = rank_skaters_2025()
        
        # Rank goalies
        goalies_rankings = rank_goalies_2025()
        
        # Show summary
        show_ranking_summary(skaters_rankings, goalies_rankings)
        
        print(f"\n{'='*60}")
        print("RANKING COMPLETE!")
        print(f"{'='*60}")
        print("Files created:")
        print("  - skater_rankings_2025.csv")
        print("  - goalie_rankings_2025.csv")
        print("\nYou can now analyze the rankings or import into Excel/Google Sheets.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the CSV files exist in the data/ folder.")
    except Exception as e:
        print(f"Error during ranking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
