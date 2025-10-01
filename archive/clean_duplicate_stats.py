#!/usr/bin/env python3
"""
Clean Duplicate Stats Script

This script removes duplicate player entries from the CSV files, keeping only
the combined stats for players who were traded during the season.
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def clean_skater_data():
    """Clean skater data by removing duplicates and keeping combined stats."""
    print("Cleaning skater data...")
    
    # Load the data
    df = pd.read_csv('data/skater_data_2023_2025.csv')
    print(f"Original skater records: {len(df)}")
    
    # Create a copy for backup
    backup_file = f"data/skater_data_2023_2025_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    shutil.copy('data/skater_data_2023_2025.csv', backup_file)
    print(f"Backup created: {backup_file}")
    
    # Function to determine if a row should be kept
    def should_keep_row(group):
        """
        For each player-season combination, keep the row with the most games played.
        This will typically be the combined stats (2TM, 3TM, etc.) since they include
        games from all teams the player played for.
        """
        if len(group) == 1:
            return group.index[0]  # Only one entry, keep it
        
        # Find the row with the most games played (combined stats)
        max_games_idx = group['games_played'].idxmax()
        return max_games_idx
    
    # Group by name and season, then apply the cleaning logic
    cleaned_indices = []
    for (name, season), group in df.groupby(['name', 'season']):
        keep_idx = should_keep_row(group)
        cleaned_indices.append(keep_idx)
    
    # Create cleaned dataframe
    cleaned_df = df.loc[cleaned_indices].copy()
    
    # Sort by season, then by points descending
    cleaned_df = cleaned_df.sort_values(['season', 'points'], ascending=[True, False])
    
    # Reset index
    cleaned_df = cleaned_df.reset_index(drop=True)
    
    print(f"Cleaned skater records: {len(cleaned_df)}")
    print(f"Removed {len(df) - len(cleaned_df)} duplicate entries")
    
    # Save cleaned data
    cleaned_df.to_csv('data/skater_data_2023_2025_cleaned.csv', index=False)
    print("✓ Cleaned skater data saved to: data/skater_data_2023_2025_cleaned.csv")
    
    return cleaned_df

def clean_goalie_data():
    """Clean goalie data by removing duplicates and keeping combined stats."""
    print("\nCleaning goalie data...")
    
    # Load the data
    df = pd.read_csv('data/goalie_data_2023_2025.csv')
    print(f"Original goalie records: {len(df)}")
    
    # Create a copy for backup
    backup_file = f"data/goalie_data_2023_2025_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    shutil.copy('data/goalie_data_2023_2025.csv', backup_file)
    print(f"Backup created: {backup_file}")
    
    # Function to determine if a row should be kept
    def should_keep_row(group):
        """
        For each goalie-season combination, keep the row with the most games played.
        This will typically be the combined stats (2TM, 3TM, etc.) since they include
        games from all teams the goalie played for.
        """
        if len(group) == 1:
            return group.index[0]  # Only one entry, keep it
        
        # Find the row with the most games played (combined stats)
        max_games_idx = group['games_played'].idxmax()
        return max_games_idx
    
    # Group by name and season, then apply the cleaning logic
    cleaned_indices = []
    for (name, season), group in df.groupby(['name', 'season']):
        keep_idx = should_keep_row(group)
        cleaned_indices.append(keep_idx)
    
    # Create cleaned dataframe
    cleaned_df = df.loc[cleaned_indices].copy()
    
    # Sort by season, then by wins descending
    cleaned_df = cleaned_df.sort_values(['season', 'wins'], ascending=[True, False])
    
    # Reset index
    cleaned_df = cleaned_df.reset_index(drop=True)
    
    print(f"Cleaned goalie records: {len(cleaned_df)}")
    print(f"Removed {len(df) - len(cleaned_df)} duplicate entries")
    
    # Save cleaned data
    cleaned_df.to_csv('data/goalie_data_2023_2025_cleaned.csv', index=False)
    print("✓ Cleaned goalie data saved to: data/goalie_data_2023_2025_cleaned.csv")
    
    return cleaned_df

def show_cleaning_examples(cleaned_skaters, original_skaters):
    """Show examples of the cleaning process."""
    print("\n" + "="*60)
    print("CLEANING EXAMPLES")
    print("="*60)
    
    # Find players who had duplicates
    original_counts = original_skaters.groupby(['name', 'season']).size()
    duplicated_players = original_counts[original_counts > 1].index
    
    print(f"Found {len(duplicated_players)} players with duplicate entries")
    
    # Show a few examples
    for i, (name, season) in enumerate(duplicated_players[:5]):
        print(f"\nExample {i+1}: {name} ({season})")
        
        # Show original entries
        original_entries = original_skaters[(original_skaters['name'] == name) & 
                                          (original_skaters['season'] == season)]
        print("  Original entries:")
        for _, row in original_entries.iterrows():
            print(f"    Team: {row['team']:<4} Games: {row['games_played']:2d} Points: {row['points']:3d}")
        
        # Show cleaned entry
        cleaned_entry = cleaned_skaters[(cleaned_skaters['name'] == name) & 
                                       (cleaned_skaters['season'] == season)]
        if not cleaned_entry.empty:
            row = cleaned_entry.iloc[0]
            print(f"  Kept: Team: {row['team']:<4} Games: {row['games_played']:2d} Points: {row['points']:3d}")

def replace_original_files():
    """Replace original files with cleaned versions."""
    print("\n" + "="*60)
    print("REPLACING ORIGINAL FILES")
    print("="*60)
    
    # Replace skater file
    if os.path.exists('data/skater_data_2023_2025_cleaned.csv'):
        shutil.move('data/skater_data_2023_2025_cleaned.csv', 'data/skater_data_2023_2025.csv')
        print("✓ Replaced skater_data_2023_2025.csv with cleaned version")
    
    # Replace goalie file
    if os.path.exists('data/goalie_data_2023_2025_cleaned.csv'):
        shutil.move('data/goalie_data_2023_2025_cleaned.csv', 'data/goalie_data_2023_2025.csv')
        print("✓ Replaced goalie_data_2023_2025.csv with cleaned version")

def main():
    """Main function to clean duplicate stats."""
    print("=" * 60)
    print("CLEANING DUPLICATE NHL STATS")
    print("=" * 60)
    print("This script removes duplicate player entries and keeps only combined stats.")
    print("Backups of original files will be created automatically.")
    print("=" * 60)
    
    try:
        # Load original data for comparison
        original_skaters = pd.read_csv('data/skater_data_2023_2025.csv')
        original_goalies = pd.read_csv('data/goalie_data_2023_2025.csv')
        
        # Clean the data
        cleaned_skaters = clean_skater_data()
        cleaned_goalies = clean_goalie_data()
        
        # Show examples
        show_cleaning_examples(cleaned_skaters, original_skaters)
        
        # Ask user if they want to replace original files
        print(f"\n{'='*60}")
        print("CLEANING COMPLETE!")
        print(f"{'='*60}")
        print("Summary:")
        print(f"  Skaters: {len(original_skaters)} → {len(cleaned_skaters)} (removed {len(original_skaters) - len(cleaned_skaters)} duplicates)")
        print(f"  Goalies: {len(original_goalies)} → {len(cleaned_goalies)} (removed {len(original_goalies) - len(cleaned_goalies)} duplicates)")
        print(f"\nBackup files created with timestamps.")
        print(f"Cleaned files saved as *_cleaned.csv")
        
        # Replace original files
        replace_original_files()
        
        print(f"\n{'='*60}")
        print("FILES UPDATED!")
        print(f"{'='*60}")
        print("The original CSV files have been replaced with cleaned versions.")
        print("You can now run your analysis scripts with the cleaned data.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the CSV files exist in the data/ folder.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during cleaning: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
