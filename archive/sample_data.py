#!/usr/bin/env python3
"""
Sample Data Generator

This script creates sample NHL player data for testing the fantasy hockey analysis
functionality when the NHL API is not accessible.
"""

import sys
import random
from datetime import datetime

# Add src directory to path
sys.path.append('src')

from src.database import FantasyHockeyDB

def generate_sample_data():
    """Generate sample player data for testing."""
    
    # Sample teams
    teams = [
        {'id': 1, 'name': 'Edmonton Oilers', 'abbreviation': 'EDM'},
        {'id': 2, 'name': 'Toronto Maple Leafs', 'abbreviation': 'TOR'},
        {'id': 3, 'name': 'Boston Bruins', 'abbreviation': 'BOS'},
        {'id': 4, 'name': 'New York Rangers', 'abbreviation': 'NYR'},
        {'id': 5, 'name': 'Colorado Avalanche', 'abbreviation': 'COL'},
        {'id': 6, 'name': 'Tampa Bay Lightning', 'abbreviation': 'TBL'},
        {'id': 7, 'name': 'Vegas Golden Knights', 'abbreviation': 'VGK'},
        {'id': 8, 'name': 'Carolina Hurricanes', 'abbreviation': 'CAR'},
    ]
    
    # Sample players (mix of real and fictional names)
    players = [
        {'id': 1, 'fullName': 'Connor McDavid', 'firstName': 'Connor', 'lastName': 'McDavid', 'primaryPosition': {'name': 'Center'}},
        {'id': 2, 'fullName': 'Leon Draisaitl', 'firstName': 'Leon', 'lastName': 'Draisaitl', 'primaryPosition': {'name': 'Center'}},
        {'id': 3, 'fullName': 'Auston Matthews', 'firstName': 'Auston', 'lastName': 'Matthews', 'primaryPosition': {'name': 'Center'}},
        {'id': 4, 'fullName': 'Mitch Marner', 'firstName': 'Mitch', 'lastName': 'Marner', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 5, 'fullName': 'Brad Marchand', 'firstName': 'Brad', 'lastName': 'Marchand', 'primaryPosition': {'name': 'Left Wing'}},
        {'id': 6, 'fullName': 'David Pastrnak', 'firstName': 'David', 'lastName': 'Pastrnak', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 7, 'fullName': 'Artemi Panarin', 'firstName': 'Artemi', 'lastName': 'Panarin', 'primaryPosition': {'name': 'Left Wing'}},
        {'id': 8, 'fullName': 'Mika Zibanejad', 'firstName': 'Mika', 'lastName': 'Zibanejad', 'primaryPosition': {'name': 'Center'}},
        {'id': 9, 'fullName': 'Nathan MacKinnon', 'firstName': 'Nathan', 'lastName': 'MacKinnon', 'primaryPosition': {'name': 'Center'}},
        {'id': 10, 'fullName': 'Mikko Rantanen', 'firstName': 'Mikko', 'lastName': 'Rantanen', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 11, 'fullName': 'Nikita Kucherov', 'firstName': 'Nikita', 'lastName': 'Kucherov', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 12, 'fullName': 'Steven Stamkos', 'firstName': 'Steven', 'lastName': 'Stamkos', 'primaryPosition': {'name': 'Center'}},
        {'id': 13, 'fullName': 'Mark Stone', 'firstName': 'Mark', 'lastName': 'Stone', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 14, 'fullName': 'Jack Eichel', 'firstName': 'Jack', 'lastName': 'Eichel', 'primaryPosition': {'name': 'Center'}},
        {'id': 15, 'fullName': 'Sebastian Aho', 'firstName': 'Sebastian', 'lastName': 'Aho', 'primaryPosition': {'name': 'Center'}},
        {'id': 16, 'fullName': 'Andrei Svechnikov', 'firstName': 'Andrei', 'lastName': 'Svechnikov', 'primaryPosition': {'name': 'Right Wing'}},
        {'id': 17, 'fullName': 'Cale Makar', 'firstName': 'Cale', 'lastName': 'Makar', 'primaryPosition': {'name': 'Defenseman'}},
        {'id': 18, 'fullName': 'Victor Hedman', 'firstName': 'Victor', 'lastName': 'Hedman', 'primaryPosition': {'name': 'Defenseman'}},
        {'id': 19, 'fullName': 'Adam Fox', 'firstName': 'Adam', 'lastName': 'Fox', 'primaryPosition': {'name': 'Defenseman'}},
        {'id': 20, 'fullName': 'Charlie McAvoy', 'firstName': 'Charlie', 'lastName': 'McAvoy', 'primaryPosition': {'name': 'Defenseman'}},
        {'id': 21, 'fullName': 'Igor Shesterkin', 'firstName': 'Igor', 'lastName': 'Shesterkin', 'primaryPosition': {'name': 'Goalie'}},
        {'id': 22, 'fullName': 'Andrei Vasilevskiy', 'firstName': 'Andrei', 'lastName': 'Vasilevskiy', 'primaryPosition': {'name': 'Goalie'}},
        {'id': 23, 'fullName': 'Connor Hellebuyck', 'firstName': 'Connor', 'lastName': 'Hellebuyck', 'primaryPosition': {'name': 'Goalie'}},
        {'id': 24, 'fullName': 'Linus Ullmark', 'firstName': 'Linus', 'lastName': 'Ullmark', 'primaryPosition': {'name': 'Goalie'}},
    ]
    
    return teams, players

def generate_realistic_stats(player, season, is_goalie=False):
    """Generate realistic statistics for a player based on their position and skill level."""
    
    # Base skill levels (higher = better player)
    skill_levels = {
        'Connor McDavid': 95,
        'Leon Draisaitl': 92,
        'Auston Matthews': 90,
        'Mitch Marner': 88,
        'Brad Marchand': 87,
        'David Pastrnak': 89,
        'Artemi Panarin': 88,
        'Mika Zibanejad': 85,
        'Nathan MacKinnon': 91,
        'Mikko Rantanen': 87,
        'Nikita Kucherov': 90,
        'Steven Stamkos': 86,
        'Mark Stone': 84,
        'Jack Eichel': 85,
        'Sebastian Aho': 83,
        'Andrei Svechnikov': 82,
        'Cale Makar': 89,
        'Victor Hedman': 87,
        'Adam Fox': 85,
        'Charlie McAvoy': 83,
        'Igor Shesterkin': 92,
        'Andrei Vasilevskiy': 90,
        'Connor Hellebuyck': 88,
        'Linus Ullmark': 86,
    }
    
    skill = skill_levels.get(player['fullName'], 75)
    
    if is_goalie:
        # Goalie stats
        games_played = random.randint(45, 65)
        games_started = games_played - random.randint(0, 5)
        wins = int(games_started * (0.4 + (skill - 70) / 100 * 0.3))
        losses = games_started - wins - random.randint(0, 3)
        ties = random.randint(0, 2)
        overtime_losses = random.randint(0, 5)
        
        # GAA and SV% based on skill
        gaa = 3.5 - (skill - 70) / 100 * 1.5
        sv_pct = 0.88 + (skill - 70) / 100 * 0.08
        
        shots_against = int(games_started * 30 + random.randint(-5, 5))
        saves = int(shots_against * sv_pct)
        goals_against = shots_against - saves
        shutouts = random.randint(2, 8) if skill > 85 else random.randint(0, 4)
        
        return {
            'games_played': games_played,
            'games_started': games_started,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'overtime_losses': overtime_losses,
            'goals_against_average': round(gaa, 2),
            'save_percentage': round(sv_pct, 3),
            'shutouts': shutouts,
            'saves': saves,
            'shots_against': shots_against,
            'goals_against': goals_against,
            'time_on_ice': f"{games_started * 60}:00"
        }
    else:
        # Skater stats
        games_played = random.randint(70, 82)
        
        # Points based on skill and position
        if player['primaryPosition'] == 'Defenseman':
            base_points = (skill - 60) * 0.8
        else:
            base_points = (skill - 60) * 1.2
        
        points = max(0, int(base_points + random.randint(-10, 10)))
        goals = int(points * (0.4 + random.random() * 0.2))
        assists = points - goals
        
        # Other stats
        plus_minus = random.randint(-20, 30) if skill > 80 else random.randint(-30, 10)
        penalty_minutes = random.randint(20, 80)
        power_play_goals = int(goals * (0.2 + random.random() * 0.3))
        power_play_points = int(points * (0.3 + random.random() * 0.2))
        short_handed_goals = random.randint(0, 3) if skill > 85 else random.randint(0, 1)
        short_handed_points = short_handed_goals + random.randint(0, 2)
        game_winning_goals = random.randint(2, 8) if skill > 80 else random.randint(0, 4)
        overtime_goals = random.randint(0, 3)
        shots = int(goals * (3 + random.random() * 2))
        shooting_percentage = round((goals / shots * 100) if shots > 0 else 0, 1)
        
        # Time on ice (minutes:seconds format)
        toi_minutes = 15 + (skill - 70) / 100 * 10
        toi_seconds = random.randint(0, 59)
        time_on_ice = f"{int(toi_minutes)}:{toi_seconds:02d}"
        
        face_off_percentage = random.randint(45, 60) if player['primaryPosition'] == 'Center' else 0
        hits = random.randint(50, 200) if player['primaryPosition'] in ['Defenseman', 'Left Wing', 'Right Wing'] else random.randint(20, 100)
        blocked_shots = random.randint(20, 150) if player['primaryPosition'] == 'Defenseman' else random.randint(5, 50)
        
        return {
            'games_played': games_played,
            'goals': goals,
            'assists': assists,
            'points': points,
            'plus_minus': plus_minus,
            'penalty_minutes': penalty_minutes,
            'power_play_goals': power_play_goals,
            'power_play_points': power_play_points,
            'short_handed_goals': short_handed_goals,
            'short_handed_points': short_handed_points,
            'game_winning_goals': game_winning_goals,
            'overtime_goals': overtime_goals,
            'shots': shots,
            'shooting_percentage': shooting_percentage,
            'time_on_ice': time_on_ice,
            'face_off_percentage': face_off_percentage,
            'hits': hits,
            'blocked_shots': blocked_shots
        }

def populate_sample_database():
    """Populate the database with sample data."""
    print("Creating sample database with realistic NHL player data...")
    
    db = FantasyHockeyDB("sample_fantasy_hockey.db")
    teams, players = generate_sample_data()
    
    # Insert teams
    print("Inserting teams...")
    for team in teams:
        db.insert_team(team)
    
    # Insert players
    print("Inserting players...")
    for player in players:
        db.insert_player(player)
    
    # Generate stats for multiple seasons
    seasons = ["2021", "2022", "2023"]
    
    for season in seasons:
        print(f"Generating stats for season {season}...")
        
        for player in players:
            # Assign random team for this season
            team = random.choice(teams)
            
            if player['primaryPosition'] == 'Goalie':
                stats = generate_realistic_stats(player, season, is_goalie=True)
                db.insert_goalie_season(
                    player['id'], season, team['id'], team['name'], 
                    {'stats': [{'splits': [{'stat': stats}]}]}
                )
            else:
                stats = generate_realistic_stats(player, season, is_goalie=False)
                db.insert_player_season(
                    player['id'], season, team['id'], team['name'],
                    {'stats': [{'splits': [{'stat': stats}]}]}
                )
    
    print("Sample database created successfully!")
    
    # Show some sample data
    print("\nSample data preview:")
    
    # Top scorers from 2023
    top_scorers = db.get_top_players_by_category("2023", "points", 10)
    print(f"\nTop 10 scorers in 2023:")
    for i, player in enumerate(top_scorers, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['points']:2d} points ({player['goals']:2d}G, {player['assists']:2d}A)")
    
    # Top goalies by wins
    top_goalies = db.get_goalie_seasons(season="2023")
    top_goalies = sorted(top_goalies, key=lambda x: x['wins'], reverse=True)[:5]
    print(f"\nTop 5 goalies by wins in 2023:")
    for i, goalie in enumerate(top_goalies, 1):
        print(f"{i}. {goalie['full_name']:<20} - {goalie['wins']:2d} wins, {goalie['save_percentage']:.3f} SV%")
    
    return db

def main():
    """Main function to create sample database."""
    print("=" * 60)
    print("SAMPLE NHL DATA GENERATOR")
    print("=" * 60)
    
    try:
        db = populate_sample_database()
        
        print("\n" + "=" * 60)
        print("SAMPLE DATABASE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now test the analysis functionality with:")
        print("python analyze_sample_data.py")
        print("\nThe sample database contains:")
        print("- 8 NHL teams")
        print("- 24 players (including 4 goalies)")
        print("- 3 seasons of data (2021, 2022, 2023)")
        print("- Realistic statistics based on player skill levels")
        
    except Exception as e:
        print(f"Error creating sample database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
