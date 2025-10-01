#!/usr/bin/env python3
"""
Real Data Analysis Script

This script analyzes real NHL player data from 2024 for your fantasy hockey league.
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

from src.database import FantasyHockeyDB

def analyze_real_skater_categories(db, season="2024"):
    """Analyze real skater data by your league's specific categories."""
    print(f"\n{'='*70}")
    print(f"REAL 2024 SKATER CATEGORY ANALYSIS")
    print(f"{'='*70}")
    
    # Get all skater seasons for the specified season
    skaters = db.get_player_seasons(season=season)
    
    if not skaters:
        print(f"No skater data found for season {season}")
        return
    
    print(f"Analyzing {len(skaters)} real skaters for your league categories...")
    
    # 1. GOALS
    print(f"\n🥅 TOP 20 GOAL SCORERS (2024):")
    goal_leaders = sorted(skaters, key=lambda x: x['goals'], reverse=True)[:20]
    for i, player in enumerate(goal_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['goals']:2d} goals ({player['primary_position']})")
    
    # 2. ASSISTS
    print(f"\n🎯 TOP 20 ASSIST LEADERS (2024):")
    assist_leaders = sorted(skaters, key=lambda x: x['assists'], reverse=True)[:20]
    for i, player in enumerate(assist_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['assists']:2d} assists ({player['primary_position']})")
    
    # 3. POWER PLAY POINTS
    print(f"\n⚡ TOP 20 POWER PLAY POINTS (2024):")
    pp_leaders = sorted(skaters, key=lambda x: x['power_play_points'], reverse=True)[:20]
    for i, player in enumerate(pp_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['power_play_points']:2d} PPP ({player['primary_position']})")
    
    # 4. SHOTS ON GOAL
    print(f"\n🎯 TOP 20 SHOTS ON GOAL (2024):")
    shot_leaders = sorted(skaters, key=lambda x: x['shots'], reverse=True)[:20]
    for i, player in enumerate(shot_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['shots']:3d} shots ({player['primary_position']})")
    
    # 5. FACEOFFS WON (only for centers)
    print(f"\n🔄 TOP 15 FACEOFF LEADERS - CENTERS (2024):")
    centers = [p for p in skaters if p['primary_position'] == 'Center']
    faceoff_leaders = sorted(centers, key=lambda x: x['face_off_percentage'], reverse=True)[:15]
    for i, player in enumerate(faceoff_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['face_off_percentage']:5.1f}% FO% ({player['goals']:2d}G, {player['assists']:2d}A)")
    
    # 6. HITS
    print(f"\n💥 TOP 20 HIT LEADERS (2024):")
    hit_leaders = sorted(skaters, key=lambda x: x['hits'], reverse=True)[:20]
    for i, player in enumerate(hit_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['hits']:3d} hits ({player['primary_position']})")
    
    # 7. BLOCKED SHOTS
    print(f"\n🛡️ TOP 20 BLOCKED SHOTS (2024):")
    block_leaders = sorted(skaters, key=lambda x: x['blocked_shots'], reverse=True)[:20]
    for i, player in enumerate(block_leaders, 1):
        print(f"{i:2d}. {player['full_name']:<25} - {player['blocked_shots']:3d} blocks ({player['primary_position']})")

def analyze_real_goalie_categories(db, season="2024"):
    """Analyze real goalie data by your league's specific categories."""
    print(f"\n{'='*70}")
    print(f"REAL 2024 GOALIE CATEGORY ANALYSIS")
    print(f"{'='*70}")
    
    # Get all goalie seasons for the specified season
    goalies = db.get_goalie_seasons(season=season)
    
    if not goalies:
        print(f"No goalie data found for season {season}")
        return
    
    print(f"Analyzing {len(goalies)} real goalies for your league categories...")
    
    # 1. WINS
    print(f"\n🏆 TOP 15 GOALIES BY WINS (2024):")
    win_leaders = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:15]
    for i, goalie in enumerate(win_leaders, 1):
        win_pct = (goalie['wins'] / goalie['games_played'] * 100) if goalie['games_played'] > 0 else 0
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['wins']:2d} wins ({win_pct:4.1f}% win rate)")
    
    # 2. GOALS AGAINST AVERAGE (GAA) - Lower is better
    print(f"\n🚫 TOP 15 GOALIES BY GAA - LOWER IS BETTER (2024):")
    active_goalies = [g for g in goalies if g['games_played'] >= 20]
    gaa_leaders = sorted(active_goalies, key=lambda x: x['goals_against_average'])[:15]
    for i, goalie in enumerate(gaa_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['goals_against_average']:.2f} GAA ({goalie['wins']:2d} wins)")
    
    # 3. SAVES
    print(f"\n🛡️ TOP 15 GOALIES BY SAVES (2024):")
    save_leaders = sorted(goalies, key=lambda x: x['saves'], reverse=True)[:15]
    for i, goalie in enumerate(save_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['saves']:4d} saves ({goalie['wins']:2d} wins)")
    
    # 4. SAVE PERCENTAGE
    print(f"\n🎯 TOP 15 GOALIES BY SAVE PERCENTAGE (2024):")
    sv_pct_leaders = sorted(active_goalies, key=lambda x: x['save_percentage'], reverse=True)[:15]
    for i, goalie in enumerate(sv_pct_leaders, 1):
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['save_percentage']:.3f} SV% ({goalie['wins']:2d} wins)")

def analyze_real_by_position(db, season="2024"):
    """Analyze real players by position for your roster needs."""
    print(f"\n{'='*70}")
    print(f"REAL 2024 POSITION-SPECIFIC ANALYSIS")
    print(f"{'='*70}")
    print("Your roster needs: 2C, 2RW, 2LW, 3D, 2Utility, 2G")
    
    skaters = db.get_player_seasons(season=season)
    goalies = db.get_goalie_seasons(season=season)
    
    # Centers (need 2 starters)
    print(f"\n🏒 TOP 20 CENTERS (2024):")
    centers = [p for p in skaters if p['primary_position'] == 'Center']
    top_centers = sorted(centers, key=lambda x: x['goals'] + x['assists'], reverse=True)[:20]
    for i, player in enumerate(top_centers, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<25} - {total_points:3d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Right Wings (need 2 starters)
    print(f"\n🏒 TOP 20 RIGHT WINGS (2024):")
    rw = [p for p in skaters if p['primary_position'] == 'Right Wing']
    top_rw = sorted(rw, key=lambda x: x['goals'] + x['assists'], reverse=True)[:20]
    for i, player in enumerate(top_rw, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<25} - {total_points:3d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Left Wings (need 2 starters)
    print(f"\n🏒 TOP 20 LEFT WINGS (2024):")
    lw = [p for p in skaters if p['primary_position'] == 'Left Wing']
    top_lw = sorted(lw, key=lambda x: x['goals'] + x['assists'], reverse=True)[:20]
    for i, player in enumerate(top_lw, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<25} - {total_points:3d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['hits']:3d} hits)")
    
    # Defensemen (need 3 starters)
    print(f"\n🏒 TOP 25 DEFENSEMEN (2024):")
    defensemen = [p for p in skaters if p['primary_position'] == 'Defenseman']
    top_d = sorted(defensemen, key=lambda x: x['goals'] + x['assists'], reverse=True)[:25]
    for i, player in enumerate(top_d, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<25} - {total_points:3d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['blocked_shots']:3d} blocks)")
    
    # Utility players (any skater position - top overall)
    print(f"\n🏒 TOP 25 UTILITY PLAYERS - ANY SKATER POSITION (2024):")
    all_skaters = sorted(skaters, key=lambda x: x['goals'] + x['assists'], reverse=True)[:25]
    for i, player in enumerate(all_skaters, 1):
        total_points = player['goals'] + player['assists']
        print(f"{i:2d}. {player['full_name']:<25} - {total_points:3d} points ({player['goals']:2d}G, {player['assists']:2d}A, {player['primary_position']})")
    
    # Goalies (need 2 starters)
    print(f"\n🏒 TOP 15 GOALIES (2024):")
    top_goalies = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:15]
    for i, goalie in enumerate(top_goalies, 1):
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['wins']:2d} wins, {goalie['save_percentage']:.3f} SV%, {goalie['goals_against_average']:.2f} GAA")

def create_real_draft_recommendations(db, season="2024"):
    """Create specific draft recommendations based on real 2024 data."""
    print(f"\n{'='*70}")
    print(f"REAL 2024 DRAFT RECOMMENDATIONS")
    print(f"{'='*70}")
    
    skaters = db.get_player_seasons(season=season)
    goalies = db.get_goalie_seasons(season=season)
    
    print("🎯 RECOMMENDED DRAFT STRATEGY FOR 2024:")
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
        if player['goals'] >= 20: categories_high += 1
        if player['assists'] >= 30: categories_high += 1
        if player['power_play_points'] >= 15: categories_high += 1
        if player['shots'] >= 150: categories_high += 1
        if player['hits'] >= 100: categories_high += 1
        if player['blocked_shots'] >= 80: categories_high += 1
        
        if categories_high >= 3:
            multi_category_players.append((player, categories_high))
    
    multi_category_players.sort(key=lambda x: x[1], reverse=True)
    for i, (player, count) in enumerate(multi_category_players[:15], 1):
        print(f"{i:2d}. {player['full_name']:<25} - {count} categories ({player['primary_position']})")
        print(f"    Goals: {player['goals']:2d}, Assists: {player['assists']:2d}, PPP: {player['power_play_points']:2d}, Shots: {player['shots']:3d}, Hits: {player['hits']:3d}, Blocks: {player['blocked_shots']:3d}")
    
    # Elite goalies
    print(f"\n🥅 ELITE GOALIES (2024):")
    elite_goalies = [g for g in goalies if g['wins'] >= 25 and g['save_percentage'] >= 0.900]
    elite_goalies.sort(key=lambda x: x['wins'], reverse=True)
    for i, goalie in enumerate(elite_goalies[:10], 1):
        print(f"{i:2d}. {goalie['full_name']:<25} - {goalie['wins']:2d} wins, {goalie['save_percentage']:.3f} SV%, {goalie['goals_against_average']:.2f} GAA")

def main():
    """Main analysis function for real 2024 data."""
    print("=" * 70)
    print("REAL 2024 FANTASY HOCKEY ANALYSIS - YOUR LEAGUE SETTINGS")
    print("=" * 70)
    print("League Format: Head-to-Head Weekly Matchups")
    print("Roster: 2C, 2RW, 2LW, 3D, 2Utility, 2G + 4 bench")
    print("Skater Categories: Goals, Assists, PPP, Shots, Faceoffs, Hits, Blocks")
    print("Goalie Categories: Wins, GAA, Saves, Save %")
    print("=" * 70)
    
    # Check if real database exists
    if not os.path.exists("real_fantasy_hockey_2024.db"):
        print("Real 2024 database not found!")
        print("Please run: python3 collect_real_data.py")
        sys.exit(1)
    
    # Initialize database
    db = FantasyHockeyDB("real_fantasy_hockey_2024.db")
    
    # Run analyses
    analyze_real_skater_categories(db, "2024")
    analyze_real_goalie_categories(db, "2024")
    analyze_real_by_position(db, "2024")
    create_real_draft_recommendations(db, "2024")
    
    print(f"\n{'='*70}")
    print("REAL 2024 ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    print("\nDraft Tips for Your League (Based on Real 2024 Data):")
    print("1. Goalies are scarce - draft 2 solid starters early")
    print("2. Look for defensemen who contribute offensively")
    print("3. Centers with high faceoff % are valuable")
    print("4. Target players who contribute in multiple categories")
    print("5. Don't ignore peripheral stats (hits, blocks, shots)")
    print("\nGood luck with your draft! 🏒")

if __name__ == "__main__":
    main()
