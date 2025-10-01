"""
NHL Data Fetcher Module

This module handles fetching historical player statistics from the NHL API.
It provides functions to retrieve player data, team data, and season statistics.
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NHLDataFetcher:
    """Class to handle fetching data from the NHL API."""
    
    BASE_URL = "https://statsapi.web.nhl.com/api/v1"
    
    def __init__(self, rate_limit_delay: float = 0.1):
        """
        Initialize the NHL Data Fetcher.
        
        Args:
            rate_limit_delay: Delay between API calls in seconds to respect rate limits
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Fantasy Hockey Draft Tool/1.0'
        })
    
    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Make a request to the NHL API with error handling and rate limiting.
        
        Args:
            endpoint: API endpoint to call
            
        Returns:
            JSON response data or None if request failed
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from {url}: {e}")
            return None
    
    def get_all_teams(self) -> List[Dict[str, Any]]:
        """
        Get all NHL teams.
        
        Returns:
            List of team data dictionaries
        """
        data = self._make_request("/teams")
        if data and 'teams' in data:
            return data['teams']
        return []
    
    def get_team_roster(self, team_id: int, season: str = None) -> List[Dict[str, Any]]:
        """
        Get roster for a specific team.
        
        Args:
            team_id: NHL team ID
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            List of player data dictionaries
        """
        endpoint = f"/teams/{team_id}/roster"
        if season:
            endpoint += f"?season={season}"
            
        data = self._make_request(endpoint)
        if data and 'roster' in data:
            return data['roster']
        return []
    
    def get_player_stats(self, player_id: int, season: str = None, 
                        stats_type: str = "statsSingleSeason") -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific player.
        
        Args:
            player_id: NHL player ID
            season: Season in format YYYY (e.g., "2023")
            stats_type: Type of stats to retrieve
                       - "statsSingleSeason": Single season stats
                       - "yearByYear": Year by year stats
                       - "careerRegularSeason": Career regular season stats
                       - "careerPlayoffs": Career playoff stats
            
        Returns:
            Player statistics data or None if request failed
        """
        endpoint = f"/people/{player_id}/stats"
        params = {"stats": stats_type}
        
        if season:
            params["season"] = season
            
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint += f"?{query_string}"
        
        return self._make_request(endpoint)
    
    def get_player_info(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Get basic information for a specific player.
        
        Args:
            player_id: NHL player ID
            
        Returns:
            Player information data or None if request failed
        """
        return self._make_request(f"/people/{player_id}")
    
    def get_season_standings(self, season: str) -> List[Dict[str, Any]]:
        """
        Get standings for a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            List of team standings data
        """
        data = self._make_request(f"/standings?season={season}")
        if data and 'records' in data:
            return data['records']
        return []
    
    def get_all_players_for_season(self, season: str) -> List[Dict[str, Any]]:
        """
        Get all players who played in a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            List of player data dictionaries
        """
        all_players = []
        teams = self.get_all_teams()
        
        logger.info(f"Fetching players for season {season} from {len(teams)} teams...")
        
        for team in teams:
            team_id = team['id']
            roster = self.get_team_roster(team_id, season)
            
            for player in roster:
                player_data = player.get('person', {})
                player_data['team_id'] = team_id
                player_data['team_name'] = team['name']
                all_players.append(player_data)
        
        logger.info(f"Found {len(all_players)} players for season {season}")
        return all_players
    
    def get_player_season_stats(self, player_id: int, season: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive season statistics for a player.
        
        Args:
            player_id: NHL player ID
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            Combined player info and stats data
        """
        # Get player basic info
        player_info = self.get_player_info(player_id)
        if not player_info:
            return None
            
        # Get player stats
        player_stats = self.get_player_stats(player_id, season, "statsSingleSeason")
        
        # Combine the data
        result = {
            'player_info': player_info.get('people', [{}])[0] if player_info else {},
            'season_stats': player_stats,
            'season': season
        }
        
        return result


def main():
    """Example usage of the NHLDataFetcher."""
    fetcher = NHLDataFetcher()
    
    # Test basic functionality
    print("Testing NHL Data Fetcher...")
    
    # Get all teams
    teams = fetcher.get_all_teams()
    print(f"Found {len(teams)} teams")
    
    if teams:
        # Get roster for first team
        first_team = teams[0]
        roster = fetcher.get_team_roster(first_team['id'])
        print(f"Team {first_team['name']} has {len(roster)} players")
        
        if roster:
            # Get stats for first player
            first_player = roster[0]['person']
            player_id = first_player['id']
            stats = fetcher.get_player_season_stats(player_id, "2023")
            if stats:
                print(f"Retrieved stats for {first_player['fullName']}")


if __name__ == "__main__":
    main()
