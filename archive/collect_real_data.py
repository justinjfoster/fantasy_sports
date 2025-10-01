#!/usr/bin/env python3
"""
Real Data Collection Script

This script collects real NHL player statistics from Hockey-Reference
and stores them in the database for analysis.
"""

import sys
import os
import logging

# Add src directory to path
sys.path.append('src')

from src.hockey_reference_scraper import HockeyReferenceScraper
from src.database import FantasyHockeyDB

def collect_real_data(season="2024"):
    """Collect real NHL data for the specified season."""
    print(f"Collecting real NHL data for season {season}...")
    
    # Initialize scraper and database
    scraper = HockeyReferenceScraper(rate_limit_delay=1.0)  # Be respectful to the website
    db = FantasyHockeyDB(f"real_fantasy_hockey_{season}.db")
    
    # Collect skater data
    print("Collecting skater statistics...")
    skaters = scraper.get_skater_stats(season)
    print(f"Found {len(skaters)} skaters")
    
    # Collect goalie data
    print("Collecting goalie statistics...")
    goalies = scraper.get_goalie_stats(season)
    print(f"Found {len(goalies)} goalies")
    
    # Store skater data
    print("Storing skater data...")
    skater_count = 0
    for skater in skaters:
        # Create a player record
        player_data = {
            'id': skater_count + 1000,  # Use high numbers to avoid conflicts
            'fullName': skater['name'],
            'firstName': skater['name'].split()[0] if ' ' in skater['name'] else skater['name'],
            'lastName': skater['name'].split()[-1] if ' ' in skater['name'] else '',
            'primaryPosition': {'name': skater['position']}
        }
        
        if db.insert_player(player_data):
            # Create season stats
            stats_data = {
                'stats': [{
                    'splits': [{
                        'stat': {
                            'games': skater['games_played'],
                            'goals': skater['goals'],
                            'assists': skater['assists'],
                            'points': skater['points'],
                            'plusMinus': skater['plus_minus'],
                            'pim': skater['penalty_minutes'],
                            'powerPlayGoals': skater['power_play_goals'],
                            'powerPlayPoints': skater['power_play_points'],
                            'shortHandedGoals': skater['short_handed_goals'],
                            'shortHandedPoints': skater['short_handed_points'],
                            'gameWinningGoals': skater['game_winning_goals'],
                            'shots': skater['shots'],
                            'shotPct': skater['shooting_percentage'],
                            'timeOnIce': skater['time_on_ice'],
                            'faceOffPct': skater['face_off_percentage'],
                            'hits': skater['hits'],
                            'blocked': skater['blocked_shots']
                        }
                    }]
                }]
            }
            
            db.insert_player_season(
                player_data['id'], season, 0, skater['team'], stats_data
            )
            skater_count += 1
    
    # Store goalie data
    print("Storing goalie data...")
    goalie_count = 0
    for goalie in goalies:
        # Create a player record
        player_data = {
            'id': goalie_count + 2000,  # Use different range for goalies
            'fullName': goalie['name'],
            'firstName': goalie['name'].split()[0] if ' ' in goalie['name'] else goalie['name'],
            'lastName': goalie['name'].split()[-1] if ' ' in goalie['name'] else '',
            'primaryPosition': {'name': 'Goalie'}
        }
        
        if db.insert_player(player_data):
            # Create season stats
            stats_data = {
                'stats': [{
                    'splits': [{
                        'stat': {
                            'games': goalie['games_played'],
                            'gamesStarted': goalie['games_started'],
                            'wins': goalie['wins'],
                            'losses': goalie['losses'],
                            'ties': goalie['ties'],
                            'ot': goalie['overtime_losses'],
                            'goalAgainstAverage': goalie['goals_against_average'],
                            'savePercentage': goalie['save_percentage'],
                            'shutouts': goalie['shutouts'],
                            'saves': goalie['saves'],
                            'shotsAgainst': goalie['shots_against'],
                            'goalsAgainst': goalie['goals_against'],
                            'timeOnIce': f"{goalie['games_played'] * 60}:00"
                        }
                    }]
                }]
            }
            
            db.insert_goalie_season(
                player_data['id'], season, 0, goalie['team'], stats_data
            )
            goalie_count += 1
    
    print(f"Successfully stored {skater_count} skaters and {goalie_count} goalies")
    return db

def main():
    """Main function to collect real data."""
    print("=" * 60)
    print("REAL NHL DATA COLLECTION")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    try:
        # Collect 2024 data
        db = collect_real_data("2024")
        
        print("\n" + "=" * 60)
        print("DATA COLLECTION COMPLETE!")
        print("=" * 60)
        
        # Show some sample data
        print("\nTop 10 scorers from real 2024 data:")
        top_scorers = db.get_top_players_by_category("2024", "points", 10)
        for i, player in enumerate(top_scorers, 1):
            print(f"{i:2d}. {player['full_name']:<25} - {player['points']:3d} points ({player['goals']:2d}G, {player['assists']:2d}A)")
        
        print("\nTop 5 goalies by wins from real 2024 data:")
        top_goalies = db.get_goalie_seasons(season="2024")
        top_goalies = sorted(top_goalies, key=lambda x: x['wins'], reverse=True)[:5]
        for i, goalie in enumerate(top_goalies, 1):
            print(f"{i}. {goalie['full_name']:<25} - {goalie['wins']:2d} wins, {goalie['save_percentage']:.3f} SV%")
        
        print(f"\nDatabase saved as: real_fantasy_hockey_2024.db")
        print("You can now run: python3 analyze_real_data.py")
        
    except Exception as e:
        print(f"Error collecting data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
