#!/usr/bin/env python3
"""
CSV Data Analysis Script

This script demonstrates how to analyze the collected CSV data
for your fantasy hockey league.
"""

import pandas as pd
import sys

# Windows consoles default to cp1252 and cannot encode the emoji used below
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

def analyze_skater_csv():
    """Analyze the skater CSV data."""
    print("=" * 60)
    print("SKATER DATA ANALYSIS")
    print("=" * 60)
    
    # Load the data
    df = pd.read_csv('data/skater_data_2023_2026.csv')
    print(f"Loaded {len(df)} skater records")
    
    # Show data structure
    print(f"\nColumns: {list(df.columns)}")
    print(f"Seasons: {sorted(df['season'].unique())}")
    
    # Top scorers by season
    for season in sorted(df['season'].unique()):
        season_data = df[df['season'] == season]
        top_scorers = season_data.nlargest(5, 'points')
        
        print(f"\n🏆 TOP 5 SCORERS - {season}:")
        for i, (_, player) in enumerate(top_scorers.iterrows(), 1):
            print(f"{i}. {player['name']:<25} - {player['points']:3d} points ({player['goals']:2d}G, {player['assists']:2d}A)")
    
    # Top goal scorers across all seasons
    print(f"\n🥅 TOP 10 GOAL SCORERS (2023-2026):")
    top_goal_scorers = df.nlargest(10, 'goals')
    for i, (_, player) in enumerate(top_goal_scorers.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['goals']:2d} goals ({player['season']})")
    
    # Top assist leaders across all seasons
    print(f"\n🎯 TOP 10 ASSIST LEADERS (2023-2026):")
    top_assist_leaders = df.nlargest(10, 'assists')
    for i, (_, player) in enumerate(top_assist_leaders.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['assists']:2d} assists ({player['season']})")
    
    # Top power play point leaders
    print(f"\n⚡ TOP 10 POWER PLAY POINTS (2023-2026):")
    top_pp = df.nlargest(10, 'power_play_points')
    for i, (_, player) in enumerate(top_pp.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['power_play_points']:2d} PPP ({player['season']})")
    
    # Top shot leaders
    print(f"\n🎯 TOP 10 SHOTS ON GOAL (2023-2026):")
    top_shots = df.nlargest(10, 'shots')
    for i, (_, player) in enumerate(top_shots.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['shots']:3d} shots ({player['season']})")
    
    # Top hit leaders
    print(f"\n💥 TOP 10 HIT LEADERS (2023-2026):")
    top_hits = df.nlargest(10, 'hits')
    for i, (_, player) in enumerate(top_hits.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['hits']:3d} hits ({player['season']})")
    
    # Top blocked shot leaders
    print(f"\n🛡️ TOP 10 BLOCKED SHOTS (2023-2026):")
    top_blocks = df.nlargest(10, 'blocked_shots')
    for i, (_, player) in enumerate(top_blocks.iterrows(), 1):
        print(f"{i:2d}. {player['name']:<25} - {player['blocked_shots']:3d} blocks ({player['season']})")

def analyze_goalie_csv():
    """Analyze the goalie CSV data."""
    print("\n" + "=" * 60)
    print("GOALIE DATA ANALYSIS")
    print("=" * 60)
    
    # Load the data
    df = pd.read_csv('data/goalie_data_2023_2026.csv')
    print(f"Loaded {len(df)} goalie records from the scraped seasons")
    
    # Show data structure
    print(f"\nColumns: {list(df.columns)}")
    print(f"Seasons: {sorted(df['season'].unique())}")
    
    # Top goalies by wins across all seasons
    print(f"\n🏆 TOP 10 GOALIES BY WINS (2023-2026):")
    top_wins = df.nlargest(10, 'wins')
    for i, (_, goalie) in enumerate(top_wins.iterrows(), 1):
        print(f"{i:2d}. {goalie['name']:<25} - {goalie['wins']:2d} wins ({goalie['season']})")
    
    # Top goalies by save percentage (minimum 20 games)
    print(f"\n🎯 TOP 10 SAVE PERCENTAGE (2023-2026, min 20 games):")
    active_goalies = df[df['games_played'] >= 20]
    top_sv_pct = active_goalies.nlargest(10, 'save_percentage')
    for i, (_, goalie) in enumerate(top_sv_pct.iterrows(), 1):
        print(f"{i:2d}. {goalie['name']:<25} - {goalie['save_percentage']:.3f} SV% ({goalie['season']})")
    
    # Top goalies by saves
    print(f"\n🛡️ TOP 10 GOALIES BY SAVES (2023-2026):")
    top_saves = df.nlargest(10, 'saves')
    for i, (_, goalie) in enumerate(top_saves.iterrows(), 1):
        print(f"{i:2d}. {goalie['name']:<25} - {goalie['saves']:4d} saves ({goalie['season']})")
    
    # Best GAA (lowest is best)
    print(f"\n🚫 TOP 10 GOALIES BY GAA - LOWER IS BETTER (2023-2026, min 20 games):")
    top_gaa = active_goalies.nsmallest(10, 'goals_against_average')
    for i, (_, goalie) in enumerate(top_gaa.iterrows(), 1):
        print(f"{i:2d}. {goalie['name']:<25} - {goalie['goals_against_average']:.2f} GAA ({goalie['season']})")

def analyze_by_position():
    """Analyze players by position for your roster needs."""
    print("\n" + "=" * 60)
    print("POSITION-SPECIFIC ANALYSIS")
    print("=" * 60)
    print("Your roster needs: 2C, 2RW, 2LW, 3D, 2Utility, 2G")
    
    # Load skater data
    skaters_df = pd.read_csv('data/skater_data_2023_2026.csv')

    # Get the most recent season present in the file
    season = skaters_df['season'].max()
    latest_skaters = skaters_df[skaters_df['season'] == season]

    # Hockey-Reference uses position codes, not full names. 'F' covers
    # forwards it does not break out into C/LW/RW.
    groups = [
        ('CENTERS', ['C'], 15),
        ('RIGHT WINGS', ['RW'], 15),
        ('LEFT WINGS', ['LW'], 15),
        ('DEFENSEMEN', ['D'], 20),
    ]
    for label, codes, count in groups:
        print(f"\n🏒 TOP {count} {label} ({season}):")
        subset = latest_skaters[latest_skaters['position'].isin(codes)]
        for i, (_, player) in enumerate(subset.nlargest(count, 'points').iterrows(), 1):
            print(f"{i:2d}. {player['name']:<25} - {player['points']:3d} points ({player['goals']:2d}G, {player['assists']:2d}A)")

def main():
    """Main analysis function."""
    print("=" * 60)
    print("CSV DATA ANALYSIS FOR YOUR FANTASY HOCKEY LEAGUE")
    print("=" * 60)
    
    try:
        # Analyze skater data
        analyze_skater_csv()
        
        # Analyze goalie data
        analyze_goalie_csv()
        
        # Analyze by position
        analyze_by_position()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print("\nFiles available:")
        print(f"📊 data/skater_data_2023_2026.csv - {len(pd.read_csv('data/skater_data_2023_2026.csv')):,} skater records")
        print(f"🥅 data/goalie_data_2023_2026.csv - {len(pd.read_csv('data/goalie_data_2023_2026.csv')):,} goalie records")
        print("\nYou can now:")
        print("1. Import these files into Excel/Google Sheets")
        print("2. Create custom analysis with pandas")
        print("3. Build visualizations")
        print("4. Use for your draft preparation")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run: python3 collect_multi_year_data.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
