#!/usr/bin/env python3
"""
Sample Data Analysis Script

This script demonstrates how to analyze the collected NHL player data
for fantasy hockey draft preparation.
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

from src.database import FantasyHockeyDB

def analyze_skater_performance(db, season="2023"):
    """Analyze skater performance for fantasy hockey."""
    print(f"\n{'='*60}")
    print(f"SKATER ANALYSIS - SEASON {season}")
    print(f"{'='*60}")
    
    # Get all skater seasons for the specified season
    skaters = db.get_player_seasons(season=season)
    
    if not skaters:
        print(f"No skater data found for season {season}")
        return
    
    print(f"Analyzing {len(skaters)} skaters...")
    
    # Top scorers
    print(f"\n🏆 TOP 10 SCORERS:")
    top_scorers = sorted(skaters, key=lambda x: x['points'], reverse=True)[:10]
    for i, player in enumerate(top_scorers, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['points']:2d} points ({player['goals']:2d}G, {player['assists']:2d}A)")
    
    # Top goal scorers
    print(f"\n🥅 TOP 10 GOAL SCORERS:")
    top_goal_scorers = sorted(skaters, key=lambda x: x['goals'], reverse=True)[:10]
    for i, player in enumerate(top_goal_scorers, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['goals']:2d} goals ({player['points']:2d} points)")
    
    # Top assist leaders
    print(f"\n🎯 TOP 10 ASSIST LEADERS:")
    top_assist_leaders = sorted(skaters, key=lambda x: x['assists'], reverse=True)[:10]
    for i, player in enumerate(top_assist_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['assists']:2d} assists ({player['points']:2d} points)")
    
    # Power play specialists
    print(f"\n⚡ TOP 10 POWER PLAY POINTS:")
    pp_specialists = sorted(skaters, key=lambda x: x['power_play_points'], reverse=True)[:10]
    for i, player in enumerate(pp_specialists, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['power_play_points']:2d} PPP ({player['power_play_goals']:2d} PPG)")
    
    # Physical players (hits + blocked shots)
    print(f"\n💪 TOP 10 PHYSICAL PLAYERS (Hits + Blocked Shots):")
    physical_players = sorted(skaters, key=lambda x: x['hits'] + x['blocked_shots'], reverse=True)[:10]
    for i, player in enumerate(physical_players, 1):
        total_physical = player['hits'] + player['blocked_shots']
        print(f"{i:2d}. {player['full_name']:<20} - {total_physical:3d} total ({player['hits']:3d} hits, {player['blocked_shots']:2d} blocks)")
    
    # Shooting percentage leaders (minimum 50 shots)
    print(f"\n🎯 TOP 10 SHOOTING PERCENTAGE (min 50 shots):")
    shooters = [p for p in skaters if p['shots'] >= 50]
    shooting_leaders = sorted(shooters, key=lambda x: x['shooting_percentage'], reverse=True)[:10]
    for i, player in enumerate(shooting_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['shooting_percentage']:5.1f}% ({player['goals']:2d}G/{player['shots']:3d}S)")

def analyze_goalie_performance(db, season="2023"):
    """Analyze goalie performance for fantasy hockey."""
    print(f"\n{'='*60}")
    print(f"GOALIE ANALYSIS - SEASON {season}")
    print(f"{'='*60}")
    
    # Get all goalie seasons for the specified season
    goalies = db.get_goalie_seasons(season=season)
    
    if not goalies:
        print(f"No goalie data found for season {season}")
        return
    
    print(f"Analyzing {len(goalies)} goalies...")
    
    # Top goalies by wins
    print(f"\n🏆 TOP 10 GOALIES BY WINS:")
    top_winners = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:10]
    for i, goalie in enumerate(top_winners, 1):
        win_pct = (goalie['wins'] / goalie['games_played'] * 100) if goalie['games_played'] > 0 else 0
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['wins']:2d}W-{goalie['losses']:2d}L ({win_pct:4.1f}% win rate)")
    
    # Best save percentage (minimum 20 games)
    print(f"\n🛡️ TOP 10 SAVE PERCENTAGE (min 20 games):")
    active_goalies = [g for g in goalies if g['games_played'] >= 20]
    sv_pct_leaders = sorted(active_goalies, key=lambda x: x['save_percentage'], reverse=True)[:10]
    for i, goalie in enumerate(sv_pct_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['save_percentage']:.3f} SV% ({goalie['goals_against_average']:.2f} GAA)")
    
    # Most shutouts
    print(f"\n🚫 TOP 10 SHUTOUT LEADERS:")
    shutout_leaders = sorted(goalies, key=lambda x: x['shutouts'], reverse=True)[:10]
    for i, goalie in enumerate(shutout_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['shutouts']:2d} shutouts ({goalie['wins']:2d} wins)")

def analyze_fantasy_value(db, season="2023"):
    """Analyze fantasy value based on common scoring categories."""
    print(f"\n{'='*60}")
    print(f"FANTASY VALUE ANALYSIS - SEASON {season}")
    print(f"{'='*60}")
    
    # Common fantasy hockey scoring categories
    # This is just an example - you would customize based on your league settings
    
    skaters = db.get_player_seasons(season=season)
    goalies = db.get_goalie_seasons(season=season)
    
    print("Example fantasy scoring system:")
    print("Skaters: Goals (3), Assists (2), Plus/Minus (1), PIM (0.5), PPP (1), SHP (2), GWG (2), SOG (0.5), Hits (0.5), Blocks (0.5)")
    print("Goalies: Wins (5), GAA (-1 per goal), SV% (0.1 per save), Shutouts (3)")
    
    # Calculate fantasy points for skaters
    skater_fantasy_scores = []
    for player in skaters:
        fantasy_points = (
            player['goals'] * 3 +
            player['assists'] * 2 +
            player['plus_minus'] * 1 +
            player['penalty_minutes'] * 0.5 +
            player['power_play_points'] * 1 +
            player['short_handed_points'] * 2 +
            player['game_winning_goals'] * 2 +
            player['shots'] * 0.5 +
            player['hits'] * 0.5 +
            player['blocked_shots'] * 0.5
        )
        skater_fantasy_scores.append({
            'player': player,
            'fantasy_points': fantasy_points
        })
    
    # Calculate fantasy points for goalies
    goalie_fantasy_scores = []
    for goalie in goalies:
        if goalie['games_played'] >= 20:  # Minimum games threshold
            fantasy_points = (
                goalie['wins'] * 5 +
                goalie['saves'] * 0.1 +
                goalie['shutouts'] * 3 -
                goalie['goals_against'] * 1
            )
            goalie_fantasy_scores.append({
                'goalie': goalie,
                'fantasy_points': fantasy_points
            })
    
    # Top fantasy skaters
    print(f"\n🌟 TOP 15 FANTASY SKATERS:")
    top_fantasy_skaters = sorted(skater_fantasy_scores, key=lambda x: x['fantasy_points'], reverse=True)[:15]
    for i, item in enumerate(top_fantasy_skaters, 1):
        player = item['player']
        points = item['fantasy_points']
        print(f"{i:2d}. {player['full_name']:<20} - {points:6.1f} fantasy points ({player['points']:2d} actual points)")
    
    # Top fantasy goalies
    print(f"\n🌟 TOP 10 FANTASY GOALIES:")
    top_fantasy_goalies = sorted(goalie_fantasy_scores, key=lambda x: x['fantasy_points'], reverse=True)[:10]
    for i, item in enumerate(top_fantasy_goalies, 1):
        goalie = item['goalie']
        points = item['fantasy_points']
        print(f"{i:2d}. {goalie['full_name']:<20} - {points:6.1f} fantasy points ({goalie['wins']:2d} wins)")

def compare_seasons(db):
    """Compare player performance across seasons."""
    print(f"\n{'='*60}")
    print("SEASON-TO-SEASON COMPARISON")
    print(f"{'='*60}")
    
    seasons = ["2021", "2022", "2023"]
    
    # Get top scorers from each season
    for season in seasons:
        skaters = db.get_player_seasons(season=season)
        if skaters:
            top_scorer = max(skaters, key=lambda x: x['points'])
            print(f"{season}: {top_scorer['full_name']} - {top_scorer['points']} points")
    
    # Find players who improved significantly
    print(f"\n📈 PLAYERS WITH BIGGEST IMPROVEMENT (2022 → 2023):")
    improvements = []
    
    for season in ["2022", "2023"]:
        skaters = db.get_player_seasons(season=season)
        for player in skaters:
            player_id = player['player_id']
            points = player['points']
            
            # Find the same player in the other season
            other_season = "2023" if season == "2022" else "2022"
            other_skaters = db.get_player_seasons(season=other_season)
            other_player = next((p for p in other_skaters if p['player_id'] == player_id), None)
            
            if other_player:
                improvement = points - other_player['points']
                improvements.append({
                    'name': player['full_name'],
                    'improvement': improvement,
                    'points_2022': other_player['points'],
                    'points_2023': points
                })
    
    # Sort by improvement
    improvements.sort(key=lambda x: x['improvement'], reverse=True)
    for i, imp in enumerate(improvements[:10], 1):
        print(f"{i:2d}. {imp['name']:<20} - {imp['improvement']:+3d} points ({imp['points_2022']} → {imp['points_2023']})")

def main():
    """Main analysis function."""
    print("=" * 60)
    print("FANTASY HOCKEY DATA ANALYSIS")
    print("=" * 60)
    
    # Check if sample database exists
    if not os.path.exists("sample_fantasy_hockey.db"):
        print("Sample database not found!")
        print("Please run: python sample_data.py")
        sys.exit(1)
    
    # Initialize database
    db = FantasyHockeyDB("sample_fantasy_hockey.db")
    
    # Run analyses
    analyze_skater_performance(db, "2023")
    analyze_goalie_performance(db, "2023")
    analyze_fantasy_value(db, "2023")
    compare_seasons(db)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*60}")
    print("\nThis analysis demonstrates how you can:")
    print("1. Rank players by different statistical categories")
    print("2. Calculate fantasy points based on your league's scoring system")
    print("3. Identify trends and improvements across seasons")
    print("4. Make informed draft decisions based on historical data")
    print("\nNext steps:")
    print("- Customize the fantasy scoring system for your league")
    print("- Add more advanced metrics (Corsi, Fenwick, etc.)")
    print("- Create projections based on recent trends")
    print("- Build a web interface for easier analysis")

if __name__ == "__main__":
    main()
