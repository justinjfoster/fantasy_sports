"""
Data Collector Module

This module orchestrates the collection of NHL data by combining the data fetcher
and database modules. It provides high-level functions to collect and store
historical player statistics.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm

from .data_fetcher import NHLDataFetcher
from .database import FantasyHockeyDB

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Class to orchestrate data collection from NHL API and storage in database."""
    
    def __init__(self, db_path: str = "fantasy_hockey.db", rate_limit_delay: float = 0.1):
        """
        Initialize the data collector.
        
        Args:
            db_path: Path to the SQLite database file
            rate_limit_delay: Delay between API calls in seconds
        """
        self.fetcher = NHLDataFetcher(rate_limit_delay=rate_limit_delay)
        self.db = FantasyHockeyDB(db_path)
        self.collected_teams = set()
        self.collected_players = set()
    
    def collect_all_teams(self) -> bool:
        """
        Collect and store all NHL teams.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Collecting all NHL teams...")
        
        teams = self.fetcher.get_all_teams()
        if not teams:
            logger.error("Failed to fetch teams from NHL API")
            return False
        
        success_count = 0
        for team in tqdm(teams, desc="Storing teams"):
            if self.db.insert_team(team):
                success_count += 1
                self.collected_teams.add(team['id'])
        
        logger.info(f"Successfully stored {success_count}/{len(teams)} teams")
        return success_count == len(teams)
    
    def collect_players_for_season(self, season: str) -> bool:
        """
        Collect and store all players who played in a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Collecting players for season {season}...")
        
        players = self.fetcher.get_all_players_for_season(season)
        if not players:
            logger.error(f"Failed to fetch players for season {season}")
            return False
        
        success_count = 0
        for player in tqdm(players, desc=f"Storing players for {season}"):
            if self.db.insert_player(player):
                success_count += 1
                self.collected_players.add(player['id'])
        
        logger.info(f"Successfully stored {success_count}/{len(players)} players for season {season}")
        return success_count == len(players)
    
    def collect_player_stats_for_season(self, season: str, 
                                      player_ids: List[int] = None) -> bool:
        """
        Collect and store player statistics for a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            player_ids: List of specific player IDs to collect (optional, collects all if None)
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Collecting player stats for season {season}...")
        
        if player_ids is None:
            # Get all players from the database for this season
            player_seasons = self.db.get_player_seasons(season=season)
            player_ids = list(set([ps['player_id'] for ps in player_seasons]))
        
        if not player_ids:
            logger.warning(f"No players found for season {season}")
            return False
        
        success_count = 0
        error_count = 0
        
        for player_id in tqdm(player_ids, desc=f"Collecting stats for {season}"):
            try:
                # Get player season stats
                player_data = self.fetcher.get_player_season_stats(player_id, season)
                
                if not player_data:
                    error_count += 1
                    continue
                
                player_info = player_data.get('player_info', {})
                stats_data = player_data.get('season_stats', {})
                
                # Determine if this is a goalie or skater
                position = player_info.get('primaryPosition', {}).get('name', '')
                is_goalie = position == 'Goalie'
                
                # Get team info (we'll need to get this from the roster data)
                # For now, we'll use a placeholder - in a real implementation,
                # you'd want to track which team each player was on for each season
                team_id = None
                team_name = "Unknown"
                
                if is_goalie:
                    if self.db.insert_goalie_season(player_id, season, team_id, team_name, stats_data):
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    if self.db.insert_player_season(player_id, season, team_id, team_name, stats_data):
                        success_count += 1
                    else:
                        error_count += 1
                        
            except Exception as e:
                logger.error(f"Error collecting stats for player {player_id}: {e}")
                error_count += 1
        
        logger.info(f"Successfully collected stats for {success_count} players, {error_count} errors")
        return success_count > 0
    
    def collect_season_data(self, season: str) -> bool:
        """
        Collect complete data for a season (teams, players, and stats).
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting complete data collection for season {season}...")
        
        # Step 1: Collect teams (if not already collected)
        if not self.collected_teams:
            if not self.collect_all_teams():
                logger.error("Failed to collect teams")
                return False
        
        # Step 2: Collect players for the season
        if not self.collect_players_for_season(season):
            logger.error(f"Failed to collect players for season {season}")
            return False
        
        # Step 3: Collect player statistics
        if not self.collect_player_stats_for_season(season):
            logger.error(f"Failed to collect player stats for season {season}")
            return False
        
        logger.info(f"Successfully completed data collection for season {season}")
        return True
    
    def collect_multiple_seasons(self, seasons: List[str]) -> Dict[str, bool]:
        """
        Collect data for multiple seasons.
        
        Args:
            seasons: List of seasons in format YYYY (e.g., ["2021", "2022", "2023"])
            
        Returns:
            Dictionary mapping season to success status
        """
        results = {}
        
        for season in seasons:
            logger.info(f"Collecting data for season {season}...")
            results[season] = self.collect_season_data(season)
        
        successful_seasons = [s for s, success in results.items() if success]
        failed_seasons = [s for s, success in results.items() if not success]
        
        logger.info(f"Data collection completed. Successful: {successful_seasons}, Failed: {failed_seasons}")
        return results
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected data.
        
        Returns:
            Dictionary containing summary statistics
        """
        # Get counts from database
        player_seasons = self.db.get_player_seasons()
        goalie_seasons = self.db.get_goalie_seasons()
        
        seasons = list(set([ps['season'] for ps in player_seasons + goalie_seasons]))
        seasons.sort()
        
        summary = {
            'total_teams': len(self.collected_teams),
            'total_players': len(self.collected_players),
            'total_player_seasons': len(player_seasons),
            'total_goalie_seasons': len(goalie_seasons),
            'seasons_collected': seasons,
            'latest_season': max(seasons) if seasons else None,
            'earliest_season': min(seasons) if seasons else None
        }
        
        return summary


def main():
    """Example usage of the DataCollector."""
    collector = DataCollector()
    
    # Test data collection for recent seasons
    recent_seasons = ["2023", "2022", "2021"]
    
    print("Starting data collection...")
    results = collector.collect_multiple_seasons(recent_seasons)
    
    print("\nCollection Results:")
    for season, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} Season {season}")
    
    # Get summary
    summary = collector.get_collection_summary()
    print(f"\nCollection Summary:")
    print(f"Teams: {summary['total_teams']}")
    print(f"Players: {summary['total_players']}")
    print(f"Player Seasons: {summary['total_player_seasons']}")
    print(f"Goalie Seasons: {summary['total_goalie_seasons']}")
    print(f"Seasons: {summary['seasons_collected']}")


if __name__ == "__main__":
    main()
