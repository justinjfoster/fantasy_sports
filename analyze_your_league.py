#!/usr/bin/env python3
"""
Fantasy Hockey Analysis for Your League

This script analyzes NHL player data specifically for your league's scoring system:
- Head-to-head weekly matchups
- Skater categories: Goals, Assists, Powerplay Points, Shots on Goal, Faceoffs Won, Hits, Blocks
- Goalie categories: Wins, GAA, Saves, Save Percentage
- Roster: 2C, 2RW, 2LW, 3D, 2Utility, 2G + 4 bench
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

from src.database import FantasyHockeyDB

def analyze_skater_categories(db, season="2023"):
    """Analyze skaters by your league's specific categories."""
    print(f"\n{'='*70}")
    print(f"SKATER CATEGORY ANALYSIS - SEASON {season}")
    print(f"{'='*70}")
    
    # Get all skater seasons for the specified season
    skaters = db.get_player_seasons(season=season)
    
    if not skaters:
        print(f"No skater data found for season {season}")
        return
    
    print(f"Analyzing {len(skaters)} skaters for your league categories...")
    
    # 1. GOALS
    print(f"\n🥅 TOP 20 GOAL SCORERS:")
    goal_leaders = sorted(skaters, key=lambda x: x['goals'], reverse=True)[:20]
    for i, player in enumerate(goal_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['goals']:2d} goals ({player['primary_position']})")
    
    # 2. ASSISTS
    print(f"\n🎯 TOP 20 ASSIST LEADERS:")
    assist_leaders = sorted(skaters, key=lambda x: x['assists'], reverse=True)[:20]
    for i, player in enumerate(assist_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['assists']:2d} assists ({player['primary_position']})")
    
    # 3. POWER PLAY POINTS
    print(f"\n⚡ TOP 20 POWER PLAY POINTS:")
    pp_leaders = sorted(skaters, key=lambda x: x['power_play_points'], reverse=True)[:20]
    for i, player in enumerate(pp_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['power_play_points']:2d} PPP ({player['primary_position']})")
    
    # 4. SHOTS ON GOAL
    print(f"\n🎯 TOP 20 SHOTS ON GOAL:")
    shot_leaders = sorted(skaters, key=lambda x: x['shots'], reverse=True)[:20]
    for i, player in enumerate(shot_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['shots']:3d} shots ({player['primary_position']})")
    
    # 5. FACEOFFS WON (only for centers)
    print(f"\n🔄 TOP 15 FACEOFF LEADERS (Centers only):")
    centers = [p for p in skaters if p['primary_position'] == 'Center']
    faceoff_leaders = sorted(centers, key=lambda x: x['face_off_percentage'], reverse=True)[:15]
    for i, player in enumerate(faceoff_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['face_off_percentage']:5.1f}% FO% ({player['goals']:2d}G, {player['assists']:2d}A)")
    
    # 6. HITS
    print(f"\n💥 TOP 20 HIT LEADERS:")
    hit_leaders = sorted(skaters, key=lambda x: x['hits'], reverse=True)[:20]
    for i, player in enumerate(hit_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['hits']:3d} hits ({player['primary_position']})")
    
    # 7. BLOCKED SHOTS
    print(f"\n🛡️ TOP 20 BLOCKED SHOTS:")
    block_leaders = sorted(skaters, key=lambda x: x['blocked_shots'], reverse=True)[:20]
    for i, player in enumerate(block_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<20} - {player['blocked_shots']:3d} blocks ({player['primary_position']})")

def analyze_goalie_categories(db, season="2023"):
    """Analyze goalies by your league's specific categories."""
    print(f"\n{'='*70}")
    print(f"GOALIE CATEGORY ANALYSIS - SEASON {season}")
    print(f"{'='*70}")
    
    # Get all goalie seasons for the specified season
    goalies = db.get_goalie_seasons(season=season)
    
    if not goalies:
        print(f"No goalie data found for season {season}")
        return
    
    print(f"Analyzing {len(goalies)} goalies for your league categories...")
    
    # 1. WINS
    print(f"\n🏆 TOP 10 GOALIES BY WINS:")
    win_leaders = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:10]
    for i, goalie in enumerate(win_leaders, 1):
        win_pct = (goalie['wins'] / goalie['games_played'] * 100) if goalie['games_played'] > 0 else 0
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['wins']:2d} wins ({win_pct:4.1f}% win rate)")
    
    # 2. GOALS AGAINST AVERAGE (GAA) - Lower is better
    print(f"\n🚫 TOP 10 GOALIES BY GAA (Lower is Better):")
    active_goalies = [g for g in goalies if g['games_played'] >= 20]
    gaa_leaders = sorted(active_goalies, key=lambda x: x['goals_against_average'])[:10]
    for i, goalie in enumerate(gaa_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['goals_against_average']:.2f} GAA ({goalie['wins']:2d} wins)")
    
    # 3. SAVES
    print(f"\n🛡️ TOP 10 GOALIES BY SAVES:")
    save_leaders = sorted(goalies, key=lambda x: x['saves'], reverse=True)[:10]
    for i, goalie in enumerate(save_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['saves']:4d} saves ({goalie['wins']:2d} wins)")
    
    # 4. SAVE PERCENTAGE
    print(f"\n🎯 TOP 10 GOALIES BY SAVE PERCENTAGE:")
    sv_pct_leaders = sorted(active_goalies, key=lambda x: x['save_percentage'], reverse=True)[:10]
    for i, goalie in enumerate(sv_pct_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['save_percentage']:.3f} SV% ({goalie['wins']:2d} wins)")

def analyze_by_position(db, season="2023"):
    """Analyze players by position for your roster needs."""
    print(f"\n{'='*70}")
    print(f"POSITION-SPECIFIC ANALYSIS - SEASON {season}")
    print(f"{'='*70}")
    print("Your roster needs: 2C, 2RW, 2LW, 3D, 2Utility, 2G")
    
    skaters = db.get_player_seasons(season=season)
    goalies = db.get_goalie_seasons(season=season)
    
    # Centers (need 2 starters)
    print(f"\n🏒 TOP 15 CENTERS:")
    centers = [p for p in skaters if p['primary_position'] == 'Center']
    top_centers = sorted(centers, key=lambda x: x['goals'] + x['assists'], reverse=True)[:15]
    for i, player in enumerate(top_centers, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Right Wings (need 2 starters)
    print(f"\n🏒 TOP 15 RIGHT WINGS:")
    rw = [p for p in skaters if p['primary_position'] == 'Right Wing']
    top_rw = sorted(rw, key=lambda x: x['goals'] + x['assists'], reverse=True)[:15]
    for i, player in enumerate(top_rw, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Left Wings (need 2 starters)
    print(f"\n🏒 TOP 15 LEFT WINGS:")
    lw = [p for p in skaters if p['primary_position'] == 'Left Wing']
    top_lw = sorted(lw, key=lambda x: x['goals'] + x['assists'], reverse=True)[:15]
    for i, player in enumerate(top_lw, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Defensemen (need 3 starters)
    print(f"\n🏒 TOP 20 DEFENSEMEN:")
    defensemen = [p for p in skaters if p['primary_position'] == 'Defenseman']
    top_d = sorted(defensemen, key=lambda x: x['goals'] + x['assists'], reverse=True)[:20]
    for i, player in enumerate(top_d, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['blocked_shots']:3d} blocks)")
    
    # Utility players (any skater position - top overall)
    print(f"\n🏒 TOP 20 UTILITY PLAYERS (Any Skater Position):")
    all_skaters = sorted(skaters, key=lambda x: x['goals'] + x['assists'], reverse=True)[:20]
    for i, player in enumerate(all_skaters, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['primary_position']})")
    
    # Goalies (need 2 starters)
    print(f"\n🏒 TOP 10 GOALIES:")
    top_goalies = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:10]
    for i, goalie in enumerate(top_goalies, 1):
        print(f"{i:2d}. {goalie['full_name']:<20} - {goalie['wins']:2d} wins, {goalie['save_percentage']:.3f} SV%, {goalie['goals_against_average']:.2f} GAA")

def create_draft_recommendations(db, season="2023"):
    """Create specific draft recommendations based on your league settings."""
    print(f"\n{'='*70}")
    print(f"DRAFT RECOMMENDATIONS - SEASON {season}")
    print(f"{'='*70}")
    
    skaters = db.get_player_seasons(season=season)
    goalies = db.get_goalie_seasons(season=season)
    
    print("🎯 RECOMMENDED DRAFT STRATEGY:")
    print("1. Focus on players who excel in multiple categories")
    print("2. Prioritize goalies early (only 2 starting spots)")
    print("3. Target defensemen who contribute offensively")
    print("4. Look for centers with high faceoff percentages")
    print("5. Consider utility players who can fill multiple positions")
    
    # Multi-category studs (players who rank high in multiple categories)
    print(f"\n🌟 MULTI-CATEGORY STUDS (High in 3+ categories):")
    multi_category_players = []
    
    for player in skaters:
        categories_high = 0
        if player['goals'] >= 15: categories_high += 1
        if player['assists'] >= 20: categories_high += 1
        if player['power_play_points'] >= 10: categories_high += 1
        if player['shots'] >= 100: categories_high += 1
        if player['hits'] >= 80: categories_high += 1
        if player['blocked_shots'] >= 50: categories_high += 1
        
        if categories_high >= 3:
            multi_category_players.append((player, categories_high))
    
    multi_category_players.sort(key=lambda x: x[1], reverse=True)
    for i, (player, count) in enumerate(multi_category_players[:10], 1):
        print(f"{i:2d}. {player['full_name']:<20} - {count} categories ({player['primary_position']})")
        print(f"    Goals: {player['goals']:2d}, Assists: {player['assists']:2d}, PPP: {player['power_play_points']:2d}, Shots: {player['shots']:3d}, Hits: {player['hits']:3d}, Blocks: {player['blocked_shots']:3d}")
    
    # Sleepers (players who might be undervalued)
    print(f"\n💤 POTENTIAL SLEEPERS:")
    sleepers = []
    for player in skaters:
        # Look for players with good peripheral stats but lower point totals
        if (player['goals'] + player['assists'] < 30 and 
            (player['shots'] >= 80 or player['hits'] >= 60 or player['blocked_shots'] >= 40)):
            sleepers.append(player)
    
    sleepers.sort(key=lambda x: x['shots'] + x['hits'] + x['blocked_shots'], reverse=True)
    for i, player in enumerate(sleepers[:8], 1):
        total_points = player['goals'] + player['assists']
        peripheral = player['shots'] + player['hits'] + player['blocked_shots']
        print(f"{i:2d}. {player['full_name']:<20} - {total_points:2d} points, {peripheral:3d} peripheral stats ({player['primary_position']})")

def main():
    """Main analysis function for your league."""
    print("=" * 70)
    print("FANTASY HOCKEY ANALYSIS - YOUR LEAGUE SETTINGS")
    print("=" * 70)
    print("League Format: Head-to-Head Weekly Matchups")
    print("Roster: 2C, 2RW, 2LW, 3D, 2Utility, 2G + 4 bench")
    print("Skater Categories: Goals, Assists, PPP, Shots, Faceoffs, Hits, Blocks")
    print("Goalie Categories: Wins, GAA, Saves, Save %")
    print("=" * 70)
    
    # Check if sample database exists
    if not os.path.exists("sample_fantasy_hockey.db"):
        print("Sample database not found!")
        print("Please run: python3 sample_data.py")
        sys.exit(1)
    
    # Initialize database
    db = FantasyHockeyDB("sample_fantasy_hockey.db")
    
    # Run analyses
    analyze_skater_categories(db, "2023")
    analyze_goalie_categories(db, "2023")
    analyze_by_position(db, "2023")
    create_draft_recommendations(db, "2023")
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    print("\nDraft Tips for Your League:")
    print("1. Goalies are scarce - draft 2 solid starters early")
    print("2. Look for defensemen who contribute offensively")
    print("3. Centers with high faceoff % are valuable")
    print("4. Target players who contribute in multiple categories")
    print("5. Don't ignore peripheral stats (hits, blocks, shots)")
    print("\nGood luck with your draft! 🏒")

if __name__ == "__main__":
    main()
