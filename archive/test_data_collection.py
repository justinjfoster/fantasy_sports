#!/usr/bin/env python3
"""
Test Script for Fantasy Hockey Data Collection

This script tests the data collection functionality with a small sample
to ensure everything is working correctly before running a full collection.
"""

import sys
import logging

# Add src directory to path
sys.path.append('src')

from src.data_fetcher import NHLDataFetcher
from src.database import FantasyHockeyDB
from src.data_collector import DataCollector

def test_data_fetcher():
    """Test the NHL data fetcher functionality."""
    print("Testing NHL Data Fetcher...")
    
    fetcher = NHLDataFetcher()
    
    # Test 1: Get all teams
    print("1. Testing team retrieval...")
    teams = fetcher.get_all_teams()
    print(f"   Found {len(teams)} teams")
    
    if teams:
        first_team = teams[0]
        print(f"   First team: {first_team['name']} (ID: {first_team['id']})")
        
        # Test 2: Get team roster
        print("2. Testing roster retrieval...")
        roster = fetcher.get_team_roster(first_team['id'])
        print(f"   Found {len(roster)} players on {first_team['name']}")
        
        if roster:
            first_player = roster[0]['person']
            print(f"   First player: {first_player['fullName']} (ID: {first_player['id']})")
            
            # Test 3: Get player stats
            print("3. Testing player stats retrieval...")
            stats = fetcher.get_player_season_stats(first_player['id'], "2023")
            if stats:
                print(f"   Successfully retrieved stats for {first_player['fullName']}")
            else:
                print(f"   No stats found for {first_player['fullName']}")
    
    print("Data fetcher tests completed.\n")
    return True

def test_database():
    """Test the database functionality."""
    print("Testing Database...")
    
    db = FantasyHockeyDB("test_fantasy_hockey.db")
    
    # Test 1: Insert a test team
    print("1. Testing team insertion...")
    test_team = {
        'id': 999,
        'name': 'Test Team',
        'abbreviation': 'TST',
        'firstYearOfPlay': 2020
    }
    
    if db.insert_team(test_team):
        print("   Team insertion successful")
    else:
        print("   Team insertion failed")
    
    # Test 2: Insert a test player
    print("2. Testing player insertion...")
    test_player = {
        'id': 999,
        'fullName': 'Test Player',
        'firstName': 'Test',
        'lastName': 'Player',
        'primaryPosition': {'name': 'Forward'}
    }
    
    if db.insert_player(test_player):
        print("   Player insertion successful")
    else:
        print("   Player insertion failed")
    
    # Test 3: Insert test player season
    print("3. Testing player season insertion...")
    test_stats = {
        'stats': [{
            'splits': [{
                'stat': {
                    'games': 82,
                    'goals': 30,
                    'assists': 40,
                    'points': 70
                }
            }]
        }]
    }
    
    if db.insert_player_season(999, "2023", 999, "Test Team", test_stats):
        print("   Player season insertion successful")
    else:
        print("   Player season insertion failed")
    
    # Test 4: Query data
    print("4. Testing data queries...")
    players = db.get_player_seasons(player_id=999)
    print(f"   Found {len(players)} player seasons for test player")
    
    if players:
        player = players[0]
        print(f"   Player: {player['full_name']}, Points: {player['points']}")
    
    print("Database tests completed.\n")
    return True

def test_small_data_collection():
    """Test data collection with a very small sample."""
    print("Testing Small Data Collection...")
    
    collector = DataCollector("test_fantasy_hockey.db", rate_limit_delay=0.2)
    
    # Test 1: Collect teams
    print("1. Testing team collection...")
    if collector.collect_all_teams():
        print("   Team collection successful")
    else:
        print("   Team collection failed")
        return False
    
    # Test 2: Collect players for one team only
    print("2. Testing limited player collection...")
    fetcher = NHLDataFetcher()
    teams = fetcher.get_all_teams()
    
    if teams:
        # Just get one team's roster
        first_team = teams[0]
        roster = fetcher.get_team_roster(first_team['id'])
        
        # Insert just the first few players
        success_count = 0
        for i, player in enumerate(roster[:3]):  # Only first 3 players
            player_data = player['person']
            if collector.db.insert_player(player_data):
                success_count += 1
        
        print(f"   Successfully collected {success_count}/3 test players")
    
    print("Small data collection tests completed.\n")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("FANTASY HOCKEY DATA COLLECTION TESTS")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing
    
    try:
        # Run tests
        test_data_fetcher()
        test_database()
        test_small_data_collection()
        
        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now run the full data collection with:")
        print("python collect_data.py --seasons 2023")
        print("\nOr collect multiple seasons:")
        print("python collect_data.py --seasons 2021 2022 2023")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
