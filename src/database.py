"""
Database Module for Fantasy Hockey Draft Tool

This module handles data storage and retrieval using SQLite.
It provides functions to store and query player statistics and team data.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FantasyHockeyDB:
    """Class to handle database operations for fantasy hockey data."""
    
    def __init__(self, db_path: str = "fantasy_hockey.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create teams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    abbreviation TEXT,
                    first_year_of_play INTEGER,
                    division_id INTEGER,
                    conference_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    birth_date TEXT,
                    nationality TEXT,
                    height TEXT,
                    weight INTEGER,
                    shoots_catches TEXT,
                    primary_position TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create player_seasons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_seasons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    season TEXT NOT NULL,
                    team_id INTEGER,
                    team_name TEXT,
                    games_played INTEGER DEFAULT 0,
                    goals INTEGER DEFAULT 0,
                    assists INTEGER DEFAULT 0,
                    points INTEGER DEFAULT 0,
                    plus_minus INTEGER DEFAULT 0,
                    penalty_minutes INTEGER DEFAULT 0,
                    power_play_goals INTEGER DEFAULT 0,
                    power_play_points INTEGER DEFAULT 0,
                    short_handed_goals INTEGER DEFAULT 0,
                    short_handed_points INTEGER DEFAULT 0,
                    game_winning_goals INTEGER DEFAULT 0,
                    overtime_goals INTEGER DEFAULT 0,
                    shots INTEGER DEFAULT 0,
                    shooting_percentage REAL DEFAULT 0.0,
                    time_on_ice TEXT,
                    face_off_percentage REAL DEFAULT 0.0,
                    hits INTEGER DEFAULT 0,
                    blocked_shots INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    UNIQUE(player_id, season)
                )
            """)
            
            # Create goalie_seasons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goalie_seasons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    season TEXT NOT NULL,
                    team_id INTEGER,
                    team_name TEXT,
                    games_played INTEGER DEFAULT 0,
                    games_started INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    ties INTEGER DEFAULT 0,
                    overtime_losses INTEGER DEFAULT 0,
                    goals_against_average REAL DEFAULT 0.0,
                    save_percentage REAL DEFAULT 0.0,
                    shutouts INTEGER DEFAULT 0,
                    saves INTEGER DEFAULT 0,
                    shots_against INTEGER DEFAULT 0,
                    goals_against INTEGER DEFAULT 0,
                    time_on_ice TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    UNIQUE(player_id, season)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_seasons_player_id ON player_seasons(player_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_seasons_season ON player_seasons(season)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_goalie_seasons_player_id ON goalie_seasons(player_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_goalie_seasons_season ON goalie_seasons(season)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_team(self, team_data: Dict[str, Any]) -> bool:
        """
        Insert or update team data.
        
        Args:
            team_data: Dictionary containing team information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO teams 
                    (id, name, abbreviation, first_year_of_play, division_id, conference_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    team_data.get('id'),
                    team_data.get('name'),
                    team_data.get('abbreviation'),
                    team_data.get('firstYearOfPlay'),
                    team_data.get('division', {}).get('id'),
                    team_data.get('conference', {}).get('id')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting team {team_data.get('name', 'Unknown')}: {e}")
            return False
    
    def insert_player(self, player_data: Dict[str, Any]) -> bool:
        """
        Insert or update player data.
        
        Args:
            player_data: Dictionary containing player information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO players 
                    (id, full_name, first_name, last_name, birth_date, nationality, 
                     height, weight, shoots_catches, primary_position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_data.get('id'),
                    player_data.get('fullName'),
                    player_data.get('firstName'),
                    player_data.get('lastName'),
                    player_data.get('birthDate'),
                    player_data.get('nationality'),
                    player_data.get('height'),
                    player_data.get('weight'),
                    player_data.get('shootsCatches'),
                    player_data.get('primaryPosition', {}).get('name') if player_data.get('primaryPosition') else None
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting player {player_data.get('fullName', 'Unknown')}: {e}")
            return False
    
    def insert_player_season(self, player_id: int, season: str, 
                           team_id: int, team_name: str, stats_data: Dict[str, Any]) -> bool:
        """
        Insert or update player season statistics.
        
        Args:
            player_id: NHL player ID
            season: Season (e.g., "2023")
            team_id: Team ID
            team_name: Team name
            stats_data: Dictionary containing season statistics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract stats from the nested structure
                splits = stats_data.get('stats', [{}])[0].get('splits', [{}])
                if not splits:
                    logger.warning(f"No stats data found for player {player_id} in season {season}")
                    return False
                
                stat = splits[0].get('stat', {})
                
                cursor.execute("""
                    INSERT OR REPLACE INTO player_seasons 
                    (player_id, season, team_id, team_name, games_played, goals, assists, points,
                     plus_minus, penalty_minutes, power_play_goals, power_play_points,
                     short_handed_goals, short_handed_points, game_winning_goals, overtime_goals,
                     shots, shooting_percentage, time_on_ice, face_off_percentage, hits, blocked_shots)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_id, season, team_id, team_name,
                    stat.get('games', 0),
                    stat.get('goals', 0),
                    stat.get('assists', 0),
                    stat.get('points', 0),
                    stat.get('plusMinus', 0),
                    stat.get('pim', 0),
                    stat.get('powerPlayGoals', 0),
                    stat.get('powerPlayPoints', 0),
                    stat.get('shortHandedGoals', 0),
                    stat.get('shortHandedPoints', 0),
                    stat.get('gameWinningGoals', 0),
                    stat.get('overTimeGoals', 0),
                    stat.get('shots', 0),
                    stat.get('shotPct', 0.0),
                    stat.get('timeOnIce', '0:00'),
                    stat.get('faceOffPct', 0.0),
                    stat.get('hits', 0),
                    stat.get('blocked', 0)
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting player season stats for player {player_id}, season {season}: {e}")
            return False
    
    def insert_goalie_season(self, player_id: int, season: str, 
                           team_id: int, team_name: str, stats_data: Dict[str, Any]) -> bool:
        """
        Insert or update goalie season statistics.
        
        Args:
            player_id: NHL player ID
            season: Season (e.g., "2023")
            team_id: Team ID
            team_name: Team name
            stats_data: Dictionary containing season statistics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract stats from the nested structure
                splits = stats_data.get('stats', [{}])[0].get('splits', [{}])
                if not splits:
                    logger.warning(f"No goalie stats data found for player {player_id} in season {season}")
                    return False
                
                stat = splits[0].get('stat', {})
                
                cursor.execute("""
                    INSERT OR REPLACE INTO goalie_seasons 
                    (player_id, season, team_id, team_name, games_played, games_started, wins, losses,
                     ties, overtime_losses, goals_against_average, save_percentage, shutouts,
                     saves, shots_against, goals_against, time_on_ice)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player_id, season, team_id, team_name,
                    stat.get('games', 0),
                    stat.get('gamesStarted', 0),
                    stat.get('wins', 0),
                    stat.get('losses', 0),
                    stat.get('ties', 0),
                    stat.get('ot', 0),
                    stat.get('goalAgainstAverage', 0.0),
                    stat.get('savePercentage', 0.0),
                    stat.get('shutouts', 0),
                    stat.get('saves', 0),
                    stat.get('shotsAgainst', 0),
                    stat.get('goalsAgainst', 0),
                    stat.get('timeOnIce', '0:00')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error inserting goalie season stats for player {player_id}, season {season}: {e}")
            return False
    
    def get_player_seasons(self, player_id: int = None, season: str = None) -> List[Dict[str, Any]]:
        """
        Get player season statistics.
        
        Args:
            player_id: Filter by specific player ID (optional)
            season: Filter by specific season (optional)
            
        Returns:
            List of player season records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT ps.*, p.full_name, p.primary_position
                FROM player_seasons ps
                JOIN players p ON ps.player_id = p.id
            """
            params = []
            conditions = []
            
            if player_id:
                conditions.append("ps.player_id = ?")
                params.append(player_id)
            
            if season:
                conditions.append("ps.season = ?")
                params.append(season)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY ps.season DESC, ps.points DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_goalie_seasons(self, player_id: int = None, season: str = None) -> List[Dict[str, Any]]:
        """
        Get goalie season statistics.
        
        Args:
            player_id: Filter by specific player ID (optional)
            season: Filter by specific season (optional)
            
        Returns:
            List of goalie season records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT gs.*, p.full_name
                FROM goalie_seasons gs
                JOIN players p ON gs.player_id = p.id
            """
            params = []
            conditions = []
            
            if player_id:
                conditions.append("gs.player_id = ?")
                params.append(player_id)
            
            if season:
                conditions.append("gs.season = ?")
                params.append(season)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY gs.season DESC, gs.wins DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_players_by_category(self, season: str, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get top players by a specific statistical category.
        
        Args:
            season: Season to analyze
            category: Statistical category (e.g., 'points', 'goals', 'assists')
            limit: Number of players to return
            
        Returns:
            List of top players in the specified category
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Validate category
            valid_categories = [
                'points', 'goals', 'assists', 'plus_minus', 'power_play_points',
                'short_handed_points', 'game_winning_goals', 'shots', 'hits', 'blocked_shots'
            ]
            
            if category not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
            
            query = f"""
                SELECT ps.*, p.full_name, p.primary_position
                FROM player_seasons ps
                JOIN players p ON ps.player_id = p.id
                WHERE ps.season = ? AND ps.{category} > 0
                ORDER BY ps.{category} DESC
                LIMIT ?
            """
            
            cursor.execute(query, (season, limit))
            return [dict(row) for row in cursor.fetchall()]


def main():
    """Example usage of the FantasyHockeyDB."""
    db = FantasyHockeyDB()
    
    # Test database operations
    print("Testing Fantasy Hockey Database...")
    
    # Get some sample data
    players = db.get_player_seasons(season="2023")
    print(f"Found {len(players)} player seasons for 2023")
    
    if players:
        top_scorers = db.get_top_players_by_category("2023", "points", 10)
        print(f"Top 10 scorers in 2023:")
        for i, player in enumerate(top_scorers, 1):
            print(f"{i}. {player['full_name']} - {player['points']} points")


if __name__ == "__main__":
    main()
