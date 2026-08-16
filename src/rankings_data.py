"""
Shared data loading for the ranking scripts.

Keeps every ranking script pointed at the same scraped files and applies the
two filters they all need: drop goalies from the skater table, and select a
single season. Paths resolve relative to the repo so the scripts work no
matter which directory they are run from.
"""

import os
import sys

import pandas as pd

# Every ranking script imports this module and prints checkmarks and emoji.
# Windows consoles default to cp1252 and would crash on them, so force UTF-8
# here once rather than in each script.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, 'data')
RANKINGS_DIR = os.path.join(REPO_ROOT, 'rankings')

SKATER_FILE = 'skater_data_2023_2026.csv'
GOALIE_FILE = 'goalie_data_2023_2026.csv'

# Hockey-Reference labels a season by the year it ends, so 2026 is 2025-26
LATEST_SEASON = 2026


def load_skaters(season=LATEST_SEASON):
    """Load skaters for one season, excluding goalies."""
    df = pd.read_csv(os.path.join(DATA_DIR, SKATER_FILE))

    # Hockey-Reference lists goalies on the skater page; they would otherwise
    # occupy ~400 rows of the skater rankings with all-zero stats.
    df = df[df['position'] != 'G']

    if season is not None:
        df = df[df['season'] == season]
        if df.empty:
            raise ValueError(
                f"No skater rows for season {season} in {SKATER_FILE}. "
                f"Run: python collect_multi_year_data.py {season}"
            )
    return df.reset_index(drop=True)


def load_goalies(season=LATEST_SEASON):
    """Load goalies for one season."""
    df = pd.read_csv(os.path.join(DATA_DIR, GOALIE_FILE))

    if season is not None:
        df = df[df['season'] == season]
        if df.empty:
            raise ValueError(
                f"No goalie rows for season {season} in {GOALIE_FILE}. "
                f"Run: python collect_multi_year_data.py {season}"
            )
    return df.reset_index(drop=True)


def rankings_path(filename):
    """Absolute path for a generated rankings file, creating the folder."""
    os.makedirs(RANKINGS_DIR, exist_ok=True)
    return os.path.join(RANKINGS_DIR, filename)
