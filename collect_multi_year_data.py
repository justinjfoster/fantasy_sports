#!/usr/bin/env python3
"""
Multi-Year Data Collection Script

This script collects NHL player statistics from multiple years (2023, 2024, 2025)
and saves the results as CSV files for easy analysis.
"""

import sys
import os
import csv
import logging
from datetime import datetime

# Add src directory to path
sys.path.append('src')

from src.hockey_reference_scraper import HockeyReferenceScraper

# Scraped CSVs live alongside the rest of the data, not in the repo root
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Hockey-Reference labels a season by the year it ends, so "2026" is 2025-26
DEFAULT_SEASONS = ["2023", "2024", "2025", "2026"]

def deduplicate_traded_players(records, label):
    """
    Keep one row per player per season.

    Hockey-Reference lists a traded player once per team plus a combined
    "2TM"/"3TM" row holding their full-season totals. Only the combined row is
    useful for fantasy ranking, so drop the per-team splits when one exists.
    """
    by_player = {}
    for record in records:
        by_player.setdefault((record['name'], record['season']), []).append(record)

    cleaned, removed = [], 0
    for rows in by_player.values():
        if len(rows) == 1:
            cleaned.append(rows[0])
            continue
        combined = [r for r in rows if 'TM' in str(r.get('team', ''))]
        if combined:
            cleaned.append(combined[0])
            removed += len(rows) - 1
        else:
            # No combined row published; keep them all rather than lose stats
            cleaned.extend(rows)

    if removed:
        print(f"  Removed {removed} duplicate {label} rows for traded players")
    return cleaned


def collect_and_save_skater_data(seasons):
    """Collect skater data for multiple seasons and save as CSV."""
    print("Collecting skater data for multiple seasons...")
    
    scraper = HockeyReferenceScraper(rate_limit_delay=1.0)  # Be respectful to the website
    
    all_skaters = []
    
    for season in seasons:
        print(f"\nCollecting skater data for {season}...")
        try:
            skaters = scraper.get_skater_stats(season)
            print(f"Found {len(skaters)} skaters for {season}")
            
            # Add season to each player record
            for skater in skaters:
                skater['season'] = season
                all_skaters.append(skater)
                
        except Exception as e:
            print(f"Error collecting data for {season}: {e}")
            continue
    
    all_skaters = deduplicate_traded_players(all_skaters, 'skater')

    # Save to CSV
    if all_skaters:
        os.makedirs(DATA_DIR, exist_ok=True)
        filename = os.path.join(
            DATA_DIR, f"skater_data_{seasons[0]}_{seasons[-1]}.csv"
        )
        print(f"\nSaving {len(all_skaters)} skater records to {filename}...")

        # Define CSV columns
        fieldnames = [
            'season', 'name', 'age', 'team', 'position', 'games_played',
            'goals', 'assists', 'points', 'plus_minus', 'penalty_minutes',
            'even_strength_goals', 'power_play_goals', 'power_play_points',
            'short_handed_goals', 'short_handed_points', 'game_winning_goals',
            'shots', 'shooting_percentage', 'time_on_ice', 'hits',
            'blocked_shots', 'face_off_percentage', 'face_off_wins'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for skater in all_skaters:
                # Ensure all fields are present
                row = {}
                for field in fieldnames:
                    row[field] = skater.get(field, 0)
                writer.writerow(row)
        
        print(f"✓ Skater data saved to {filename}")
        return filename
    else:
        print("No skater data collected")
        return None

def collect_and_save_goalie_data(seasons):
    """Collect goalie data for multiple seasons and save as CSV."""
    print("\nCollecting goalie data for multiple seasons...")
    
    scraper = HockeyReferenceScraper(rate_limit_delay=1.0)  # Be respectful to the website
    
    all_goalies = []
    
    for season in seasons:
        print(f"\nCollecting goalie data for {season}...")
        try:
            goalies = scraper.get_goalie_stats(season)
            print(f"Found {len(goalies)} goalies for {season}")
            
            # Add season to each goalie record
            for goalie in goalies:
                goalie['season'] = season
                all_goalies.append(goalie)
                
        except Exception as e:
            print(f"Error collecting data for {season}: {e}")
            continue
    
    all_goalies = deduplicate_traded_players(all_goalies, 'goalie')

    # Save to CSV
    if all_goalies:
        os.makedirs(DATA_DIR, exist_ok=True)
        filename = os.path.join(
            DATA_DIR, f"goalie_data_{seasons[0]}_{seasons[-1]}.csv"
        )
        print(f"\nSaving {len(all_goalies)} goalie records to {filename}...")

        # Define CSV columns
        fieldnames = [
            'season', 'name', 'age', 'team', 'games_played', 'games_started',
            'wins', 'losses', 'ties', 'overtime_losses', 'saves',
            'shots_against', 'save_percentage', 'goals_against_average',
            'goals_against', 'shutouts', 'minutes'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for goalie in all_goalies:
                # Ensure all fields are present
                row = {}
                for field in fieldnames:
                    row[field] = goalie.get(field, 0)
                writer.writerow(row)
        
        print(f"✓ Goalie data saved to {filename}")
        return filename
    else:
        print("No goalie data collected")
        return None

def create_summary_report(skater_file, goalie_file, seasons):
    """Create a summary report of the collected data."""
    print(f"\n{'='*60}")
    print("DATA COLLECTION SUMMARY")
    print(f"{'='*60}")
    
    print(f"Seasons collected: {', '.join(seasons)}")
    print(f"Collection date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if skater_file and os.path.exists(skater_file):
        # Count records by season
        import pandas as pd
        try:
            df = pd.read_csv(skater_file)
            print(f"\nSkater data: {len(df)} total records")
            print("Records by season:")
            season_counts = df['season'].value_counts().sort_index()
            for season, count in season_counts.items():
                print(f"  {season}: {count} skaters")
        except ImportError:
            print(f"\nSkater data: {skater_file}")
    
    if goalie_file and os.path.exists(goalie_file):
        try:
            df = pd.read_csv(goalie_file)
            print(f"\nGoalie data: {len(df)} total records")
            print("Records by season:")
            season_counts = df['season'].value_counts().sort_index()
            for season, count in season_counts.items():
                print(f"  {season}: {count} goalies")
        except ImportError:
            print(f"\nGoalie data: {goalie_file}")
    
    print(f"\n{'='*60}")
    print("FILES CREATED:")
    print(f"{'='*60}")
    if skater_file:
        print(f"📊 Skater data: {skater_file}")
    if goalie_file:
        print(f"🥅 Goalie data: {goalie_file}")
    
    print(f"\nYou can now:")
    print("1. Import these CSV files into Excel or Google Sheets")
    print("2. Use pandas in Python: df = pd.read_csv('filename.csv')")
    print("3. Create custom analysis scripts")
    print("4. Build visualizations and dashboards")

def main():
    """Main function to collect multi-year data."""
    # Windows consoles default to cp1252, which cannot encode the checkmarks
    # and emoji used below; force UTF-8 so output is identical on macOS.
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

    print("=" * 60)
    print("MULTI-YEAR NHL DATA COLLECTION")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    # Seasons may be passed on the command line, e.g.:
    #   python collect_multi_year_data.py 2026
    #   python collect_multi_year_data.py 2023 2024 2025 2026
    seasons = sys.argv[1:] or DEFAULT_SEASONS

    print(f"Collecting data for seasons: {', '.join(seasons)}")
    print("This may take several minutes due to rate limiting...")
    
    try:
        # Collect skater data
        skater_file = collect_and_save_skater_data(seasons)
        
        # Collect goalie data
        goalie_file = collect_and_save_goalie_data(seasons)
        
        # Create summary report
        create_summary_report(skater_file, goalie_file, seasons)
        
        print(f"\n{'='*60}")
        print("DATA COLLECTION COMPLETE!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error during data collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
