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
    
    # Hockey-Reference tags every cell with a data-stat attribute. Keying off
    # those instead of column positions keeps the parser correct when the site
    # adds or reorders columns, which is what silently corrupted earlier scrapes.
    SKATER_REQUIRED_STATS = {
        'goals', 'assists', 'points', 'goals_pp', 'assists_pp',
        'shots', 'hits', 'blocks', 'faceoff_wins',
    }
    GOALIE_REQUIRED_STATS = {
        'goalie_wins', 'goalie_saves', 'shots_against_goalie',
        'save_pct_goalie', 'goals_against_avg',
    }

    def _cells_by_stat(self, row) -> Dict[str, str]:
        """Map each cell's data-stat attribute to its text for one table row."""
        return {
            cell.get('data-stat'): cell.get_text(strip=True)
            for cell in row.find_all(['td', 'th'])
            if cell.get('data-stat')
        }

    def _check_schema(self, cells: Dict[str, str], required: set, season: str) -> bool:
        """Fail loudly if the page no longer exposes the columns we depend on."""
        missing = required - cells.keys()
        if missing:
            logger.error(
                f"Season {season}: expected data-stat columns missing from "
                f"Hockey-Reference: {sorted(missing)}. Refusing to emit bad data."
            )
            return False
        return True

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
        schema_checked = False
        rows = stats_table.find('tbody').find_all('tr')

        for row in rows:
            try:
                # Skip the header rows repeated inside the table body
                if row.get('class') and 'thead' in row.get('class'):
                    continue

                cells = self._cells_by_stat(row)
                if len(cells) < 10:
                    continue

                # Validate the schema once per season before trusting any rows
                if not schema_checked:
                    if not self._check_schema(cells, self.SKATER_REQUIRED_STATS, season):
                        return []
                    schema_checked = True

                # Hockey-Reference has no power-play or short-handed *points*
                # column; both are the sum of the goals and assists columns.
                power_play_points = (
                    self._safe_int(cells.get('goals_pp'))
                    + self._safe_int(cells.get('assists_pp'))
                )
                short_handed_points = (
                    self._safe_int(cells.get('goals_sh'))
                    + self._safe_int(cells.get('assists_sh'))
                )

                player_data = {
                    'name': cells.get('name_display') or cells.get('player', ''),
                    'age': self._safe_int(cells.get('age')),
                    'team': cells.get('team_name_abbr') or cells.get('team_id', ''),
                    'position': cells.get('pos', ''),
                    'games_played': self._safe_int(cells.get('games')),
                    'goals': self._safe_int(cells.get('goals')),
                    'assists': self._safe_int(cells.get('assists')),
                    'points': self._safe_int(cells.get('points')),
                    'plus_minus': self._safe_int(cells.get('plus_minus')),
                    'penalty_minutes': self._safe_int(cells.get('pen_min')),
                    'even_strength_goals': self._safe_int(cells.get('goals_ev')),
                    'power_play_goals': self._safe_int(cells.get('goals_pp')),
                    'power_play_points': power_play_points,
                    'short_handed_goals': self._safe_int(cells.get('goals_sh')),
                    'short_handed_points': short_handed_points,
                    'game_winning_goals': self._safe_int(cells.get('goals_gw')),
                    'shots': self._safe_int(cells.get('shots')),
                    'shooting_percentage': self._safe_float(cells.get('shot_pct')),
                    'time_on_ice': self._toi_to_minutes(cells.get('time_on_ice')),
                    'hits': self._safe_int(cells.get('hits')),
                    'blocked_shots': self._safe_int(cells.get('blocks')),
                    'face_off_percentage': self._safe_float(cells.get('faceoff_percentage')),
                    'face_off_wins': self._safe_int(cells.get('faceoff_wins')),
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
        schema_checked = False
        rows = stats_table.find('tbody').find_all('tr')

        for row in rows:
            try:
                # Skip the header rows repeated inside the table body
                if row.get('class') and 'thead' in row.get('class'):
                    continue

                cells = self._cells_by_stat(row)
                if len(cells) < 10:
                    continue

                # Validate the schema once per season before trusting any rows
                if not schema_checked:
                    if not self._check_schema(cells, self.GOALIE_REQUIRED_STATS, season):
                        return []
                    schema_checked = True

                goalie_data = {
                    'name': cells.get('name_display') or cells.get('player', ''),
                    'age': self._safe_int(cells.get('age')),
                    'team': cells.get('team_name_abbr') or cells.get('team_id', ''),
                    'games_played': self._safe_int(cells.get('goalie_games')),
                    'games_started': self._safe_int(cells.get('goalie_starts')),
                    'wins': self._safe_int(cells.get('goalie_wins')),
                    'losses': self._safe_int(cells.get('goalie_losses')),
                    # Hockey-Reference's "T" column carries overtime/shootout
                    # losses in the modern NHL; there is no separate OTL column.
                    'ties': self._safe_int(cells.get('goalie_ties')),
                    'overtime_losses': self._safe_int(cells.get('goalie_ties')),
                    'saves': self._safe_int(cells.get('goalie_saves')),
                    'shots_against': self._safe_int(cells.get('shots_against_goalie')),
                    'save_percentage': self._safe_float(cells.get('save_pct_goalie')),
                    'goals_against_average': self._safe_float(cells.get('goals_against_avg')),
                    'goals_against': self._safe_int(cells.get('goalie_goals_against')),
                    'shutouts': self._safe_int(cells.get('goalie_shutouts')),
                    'minutes': self._toi_to_minutes(cells.get('goalie_min')),
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
    
    def _safe_int(self, value: Optional[str]) -> int:
        """Safely convert string to integer."""
        try:
            return int(value.replace(',', '')) if value else 0
        except (ValueError, AttributeError):
            return 0

    def _safe_float(self, value: Optional[str]) -> float:
        """Safely convert string to float."""
        try:
            return float(value.replace(',', '')) if value else 0.0
        except (ValueError, AttributeError):
            return 0.0

    def _toi_to_minutes(self, value: Optional[str]) -> float:
        """
        Convert Hockey-Reference's "MMMM:SS" time-on-ice string to minutes.

        Stored as a number rather than the raw string so it can be ranked and
        aggregated directly.
        """
        if not value:
            return 0.0
        try:
            minutes, seconds = value.split(':')
            return round(int(minutes) + int(seconds) / 60, 2)
        except (ValueError, AttributeError):
            return self._safe_float(value)


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
