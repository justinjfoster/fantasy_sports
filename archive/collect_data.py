#!/usr/bin/env python3
"""
Data Collection Script for Fantasy Hockey Draft Tool

This script collects historical NHL player statistics and stores them in a local database.
Run this script to populate your database with player data for analysis.

Usage:
    python collect_data.py --seasons 2021 2022 2023
    python collect_data.py --seasons 2023 --players-only
    python collect_data.py --help
"""

import argparse
import sys
import logging
from typing import List

# Add src directory to path
sys.path.append('src')

from src.data_collector import DataCollector

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main function to handle command line arguments and run data collection."""
    parser = argparse.ArgumentParser(
        description="Collect NHL player statistics for fantasy hockey analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data for multiple seasons
  python collect_data.py --seasons 2021 2022 2023
  
  # Collect data for just one season
  python collect_data.py --seasons 2023
  
  # Collect only player info (no stats) for faster initial setup
  python collect_data.py --seasons 2023 --players-only
  
  # Use custom database file
  python collect_data.py --seasons 2023 --db my_hockey_data.db
  
  # Verbose output
  python collect_data.py --seasons 2023 --verbose
        """
    )
    
    parser.add_argument(
        '--seasons',
        nargs='+',
        required=True,
        help='Seasons to collect data for (e.g., 2021 2022 2023)'
    )
    
    parser.add_argument(
        '--db',
        default='fantasy_hockey.db',
        help='Database file path (default: fantasy_hockey.db)'
    )
    
    parser.add_argument(
        '--players-only',
        action='store_true',
        help='Only collect player information, skip statistics (faster)'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=0.1,
        help='Delay between API calls in seconds (default: 0.1)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate seasons
    current_year = 2024
    valid_seasons = []
    
    for season in args.seasons:
        try:
            season_int = int(season)
            if 1917 <= season_int <= current_year:
                valid_seasons.append(season)
            else:
                logger.warning(f"Season {season} is outside valid range (1917-{current_year})")
        except ValueError:
            logger.error(f"Invalid season format: {season}")
    
    if not valid_seasons:
        logger.error("No valid seasons provided")
        sys.exit(1)
    
    logger.info(f"Starting data collection for seasons: {valid_seasons}")
    logger.info(f"Database: {args.db}")
    logger.info(f"Rate limit: {args.rate_limit}s between API calls")
    
    # Initialize data collector
    try:
        collector = DataCollector(db_path=args.db, rate_limit_delay=args.rate_limit)
    except Exception as e:
        logger.error(f"Failed to initialize data collector: {e}")
        sys.exit(1)
    
    # Collect data
    try:
        if args.players_only:
            logger.info("Collecting players only (no statistics)")
            
            # Collect teams first
            if not collector.collect_all_teams():
                logger.error("Failed to collect teams")
                sys.exit(1)
            
            # Collect players for each season
            for season in valid_seasons:
                if not collector.collect_players_for_season(season):
                    logger.error(f"Failed to collect players for season {season}")
                    sys.exit(1)
        else:
            # Collect complete data
            results = collector.collect_multiple_seasons(valid_seasons)
            
            # Check results
            failed_seasons = [s for s, success in results.items() if not success]
            if failed_seasons:
                logger.error(f"Failed to collect data for seasons: {failed_seasons}")
                sys.exit(1)
        
        # Print summary
        summary = collector.get_collection_summary()
        logger.info("Data collection completed successfully!")
        logger.info(f"Summary:")
        logger.info(f"  Teams: {summary['total_teams']}")
        logger.info(f"  Players: {summary['total_players']}")
        logger.info(f"  Player Seasons: {summary['total_player_seasons']}")
        logger.info(f"  Goalie Seasons: {summary['total_goalie_seasons']}")
        logger.info(f"  Seasons: {summary['seasons_collected']}")
        
    except KeyboardInterrupt:
        logger.info("Data collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during data collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
