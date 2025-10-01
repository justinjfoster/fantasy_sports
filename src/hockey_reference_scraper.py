"""
Hockey-Reference Scraper Module

This module provides an alternative data source when the NHL API is not accessible.
It scrapes player statistics from Hockey-Reference.com.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional, Any
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HockeyReferenceScraper:
    """Class to scrape player statistics from Hockey-Reference.com."""
    
    BASE_URL = "https://www.hockey-reference.com"
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a request to Hockey-Reference with error handling.
        
        Args:
            url: URL to scrape
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def get_skater_stats(self, season: str) -> List[Dict[str, Any]]:
        """
        Get skater statistics for a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            List of skater statistics dictionaries
        """
        logger.info(f"Scraping skater stats for season {season}...")
        
        # Hockey-Reference uses season format like "2024" for 2023-24 season
        # The season parameter represents the year the season ended
        url = f"{self.BASE_URL}/leagues/NHL_{season}_skaters.html"
        
        soup = self._make_request(url)
        if not soup:
            return []
        
        # Find the stats table
        stats_table = soup.find('table', {'id': 'player_stats'})
        if not stats_table:
            logger.error(f"Could not find player_stats table for season {season}")
            return []
        
        players = []
        rows = stats_table.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                # Skip header rows
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                
                cells = row.find_all(['td', 'th'])
                if len(cells) < 10:  # Ensure we have enough columns
                    continue
                
                # Extract player data (columns: Rank, Name, Age, Team, Position, Games, Goals, Assists, Points, Plus/Minus, etc.)
                player_data = {
                    'name': cells[1].get_text(strip=True),  # Column 1: Name
                    'age': self._safe_int(cells[2].get_text(strip=True)),  # Column 2: Age
                    'team': cells[3].get_text(strip=True),  # Column 3: Team
                    'position': cells[4].get_text(strip=True),  # Column 4: Position
                    'games_played': self._safe_int(cells[5].get_text(strip=True)),  # Column 5: Games
                    'goals': self._safe_int(cells[6].get_text(strip=True)),  # Column 6: Goals
                    'assists': self._safe_int(cells[7].get_text(strip=True)),  # Column 7: Assists
                    'points': self._safe_int(cells[8].get_text(strip=True)),  # Column 8: Points
                    'plus_minus': self._safe_int(cells[9].get_text(strip=True)),  # Column 9: Plus/Minus
                    'penalty_minutes': self._safe_int(cells[10].get_text(strip=True)) if len(cells) > 10 else 0,
                    'power_play_goals': self._safe_int(cells[11].get_text(strip=True)) if len(cells) > 11 else 0,
                    'power_play_points': self._safe_int(cells[12].get_text(strip=True)) if len(cells) > 12 else 0,
                    'short_handed_goals': self._safe_int(cells[13].get_text(strip=True)) if len(cells) > 13 else 0,
                    'short_handed_points': self._safe_int(cells[14].get_text(strip=True)) if len(cells) > 14 else 0,
                    'game_winning_goals': self._safe_int(cells[15].get_text(strip=True)) if len(cells) > 15 else 0,
                    'shots': self._safe_int(cells[16].get_text(strip=True)) if len(cells) > 16 else 0,
                    'shooting_percentage': self._safe_float(cells[17].get_text(strip=True)) if len(cells) > 17 else 0.0,
                    'time_on_ice': cells[18].get_text(strip=True) if len(cells) > 18 else '0:00',
                    'hits': self._safe_int(cells[19].get_text(strip=True)) if len(cells) > 19 else 0,
                    'blocked_shots': self._safe_int(cells[20].get_text(strip=True)) if len(cells) > 20 else 0,
                    'face_off_percentage': self._safe_float(cells[21].get_text(strip=True)) if len(cells) > 21 else 0.0,
                    'season': season
                }
                
                # Only include players with meaningful stats
                if player_data['games_played'] > 0:
                    players.append(player_data)
                    
            except Exception as e:
                logger.warning(f"Error parsing player row: {e}")
                continue
        
        logger.info(f"Scraped {len(players)} skater records for season {season}")
        return players
    
    def get_goalie_stats(self, season: str) -> List[Dict[str, Any]]:
        """
        Get goalie statistics for a specific season.
        
        Args:
            season: Season in format YYYY (e.g., "2023")
            
        Returns:
            List of goalie statistics dictionaries
        """
        logger.info(f"Scraping goalie stats for season {season}...")
        
        # Hockey-Reference uses season format like "2024" for 2023-24 season
        url = f"{self.BASE_URL}/leagues/NHL_{season}_goalies.html"
        
        soup = self._make_request(url)
        if not soup:
            return []
        
        # Find the stats table
        stats_table = soup.find('table', {'id': 'goalie_stats'})
        if not stats_table:
            logger.error(f"Could not find goalie_stats table for season {season}")
            return []
        
        goalies = []
        rows = stats_table.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                # Skip header rows
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                
                cells = row.find_all(['td', 'th'])
                if len(cells) < 10:  # Ensure we have enough columns
                    continue
                
                # Extract goalie data (columns: Rank, Name, Age, Team, Position, Games, GS, Wins, Losses, Ties, etc.)
                goalie_data = {
                    'name': cells[1].get_text(strip=True),  # Column 1: Name
                    'age': self._safe_int(cells[2].get_text(strip=True)),  # Column 2: Age
                    'team': cells[3].get_text(strip=True),  # Column 3: Team
                    'games_played': self._safe_int(cells[5].get_text(strip=True)),  # Column 5: Games
                    'games_started': self._safe_int(cells[6].get_text(strip=True)),  # Column 6: Games Started
                    'wins': self._safe_int(cells[7].get_text(strip=True)),  # Column 7: Wins
                    'losses': self._safe_int(cells[8].get_text(strip=True)),  # Column 8: Losses
                    'ties': self._safe_int(cells[9].get_text(strip=True)),  # Column 9: Ties
                    'overtime_losses': self._safe_int(cells[10].get_text(strip=True)) if len(cells) > 10 else 0,
                    'saves': self._safe_int(cells[11].get_text(strip=True)) if len(cells) > 11 else 0,
                    'shots_against': self._safe_int(cells[12].get_text(strip=True)) if len(cells) > 12 else 0,
                    'save_percentage': self._safe_float(cells[13].get_text(strip=True)) if len(cells) > 13 else 0.0,
                    'goals_against_average': self._safe_float(cells[14].get_text(strip=True)) if len(cells) > 14 else 0.0,
                    'goals_against': self._safe_int(cells[12].get_text(strip=True)) - self._safe_int(cells[11].get_text(strip=True)) if len(cells) > 12 else 0,
                    'shutouts': self._safe_int(cells[15].get_text(strip=True)) if len(cells) > 15 else 0,
                    'season': season
                }
                
                # Only include goalies with meaningful stats
                if goalie_data['games_played'] > 0:
                    goalies.append(goalie_data)
                    
            except Exception as e:
                logger.warning(f"Error parsing goalie row: {e}")
                continue
        
        logger.info(f"Scraped {len(goalies)} goalie records for season {season}")
        return goalies
    
    def _safe_int(self, value: str) -> int:
        """Safely convert string to integer."""
        try:
            return int(value) if value and value != '' else 0
        except ValueError:
            return 0
    
    def _safe_float(self, value: str) -> float:
        """Safely convert string to float."""
        try:
            return float(value) if value and value != '' else 0.0
        except ValueError:
            return 0.0


def main():
    """Example usage of the Hockey-Reference scraper."""
    scraper = HockeyReferenceScraper()
    
    # Test scraping for 2023 season
    print("Testing Hockey-Reference scraper...")
    
    skaters = scraper.get_skater_stats("2023")
    print(f"Found {len(skaters)} skaters")
    
    if skaters:
        # Show top 5 scorers
        top_scorers = sorted(skaters, key=lambda x: x['points'], reverse=True)[:5]
        print("\nTop 5 scorers in 2023:")
        for i, player in enumerate(top_scorers, 1):
            print(f"{i}. {player['name']} - {player['points']} points ({player['goals']}G, {player['assists']}A)")
    
    goalies = scraper.get_goalie_stats("2023")
    print(f"\nFound {len(goalies)} goalies")
    
    if goalies:
        # Show top 5 goalies by wins
        top_goalies = sorted(goalies, key=lambda x: x['wins'], reverse=True)[:5]
        print("\nTop 5 goalies by wins in 2023:")
        for i, goalie in enumerate(top_goalies, 1):
            print(f"{i}. {goalie['name']} - {goalie['wins']} wins, {goalie['save_percentage']:.3f} SV%")


if __name__ == "__main__":
    main()
