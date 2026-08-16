#!/usr/bin/env python3
"""
Pull the Fantrax player pool, with ADP and Fantrax's own projections.

    python scripts/fantrax_player_pool.py            # top 500
    python scripts/fantrax_player_pool.py --all      # all ~7,500
    python scripts/fantrax_player_pool.py --limit 200

Writes data/fantrax_player_pool.csv.

Fantrax returns this table already tailored to your league, so the projected
stat columns are exactly your scoring categories. Two draft-relevant columns
you cannot get from Hockey-Reference:

    adp        average draft position across all Fantrax leagues
    pct_drafted  share of leagues where the player was drafted
    score      Fantrax's own value formula for your league settings
"""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

from src.fantrax import FantraxAuthError, default_league_id, load_session

ENDPOINT = "https://www.fantrax.com/fxpa/req"
PAGE_SIZE = 100
RATE_LIMIT_SECONDS = 1.5

# Fixed leading columns; the rest are the league's scoring categories and are
# read from the response header, so this adapts if the league settings change.
LEADING = ['rank', 'status', 'age', 'opponent', 'score', 'pct_drafted', 'adp',
           'pct_rostered', 'pct_rostered_change']


def as_number(value, default=float('inf')):
    """
    Parse a Fantrax table cell as a number.

    Undrafted players carry '-' in the ADP column, and percentage columns
    arrive as strings like '99%'.
    """
    try:
        return float(str(value).rstrip('%'))
    except (ValueError, AttributeError):
        return default


def fetch_page(session, league_id, page):
    body = {"msgs": [{"method": "getPlayerStats", "data": {
        "leagueId": league_id,
        "pageNumber": str(page),
        "maxResultsPerPage": str(PAGE_SIZE),
    }}]}
    response = session.post(
        ENDPOINT, params={"leagueId": league_id}, json=body, timeout=30
    )
    payload = response.json()

    error = (payload.get("pageError") or {}).get("code")
    if error:
        raise RuntimeError(
            f"Fantrax returned {error}. "
            f"If it is WARNING_NOT_LOGGED_IN, re-run scripts/fantrax_login.py"
        )
    return payload["responses"][0]["data"]


def stat_columns(data):
    """Scoring-category column names, taken from the response header."""
    cells = data["tableHeader"]["cells"]
    return [c.get("shortName", f"col{i}").lower() for i, c in enumerate(cells)][len(LEADING):]


def parse_rows(data, stat_cols):
    for row in data["statsTable"]:
        scorer = row.get("scorer", {})
        values = [c.get("content", "") for c in row.get("cells", [])]

        record = {
            'name': scorer.get('name', ''),
            'team': scorer.get('teamShortName', ''),
            'position': scorer.get('posShortNames', ''),
            'rookie': scorer.get('rookie', False),
            'scorer_id': scorer.get('scorerId', ''),
        }
        for i, key in enumerate(LEADING + stat_cols):
            record[key] = values[i] if i < len(values) else ''
        yield record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=500,
                        help='how many players to pull (default 500)')
    parser.add_argument('--all', action='store_true', help='pull every player')
    parser.add_argument('--league', help='league id (else FANTRAX_LEAGUE_ID or .fantrax_league)')
    args = parser.parse_args()

    league_id = args.league or default_league_id()
    if not league_id:
        print("No league id. Set FANTRAX_LEAGUE_ID or create .fantrax_league")
        sys.exit(1)

    try:
        session = load_session()
    except FantraxAuthError as e:
        print(e)
        sys.exit(1)

    try:
        first = fetch_page(session, league_id, 1)
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    total = first["paginatedResultSet"]["totalNumResults"]
    wanted = total if args.all else min(args.limit, total)
    pages = (wanted + PAGE_SIZE - 1) // PAGE_SIZE

    stat_cols = stat_columns(first)
    print(f"League {league_id}: {total:,} players available, fetching {wanted:,}")
    print(f"Scoring categories: {', '.join(stat_cols)}")

    records = list(parse_rows(first, stat_cols))
    for page in range(2, pages + 1):
        time.sleep(RATE_LIMIT_SECONDS)
        print(f"  page {page}/{pages}...")
        records.extend(parse_rows(fetch_page(session, league_id, page), stat_cols))

    records = records[:wanted]

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fantrax_player_pool.csv')

    fieldnames = ['name', 'team', 'position', 'rookie', 'scorer_id'] + LEADING + stat_cols
    with open(out_path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\nSaved {len(records):,} players to {out_path}")
    print(f"\nTop 10 by ADP:")
    print(f"  {'ADP':>6}  {'Rk':>4}  {'name':<24} {'pos':<6} {'team'}")
    for r in sorted(records, key=lambda r: as_number(r['adp']))[:10]:
        print(f"  {r['adp']:>6}  {r['rank']:>4}  {r['name']:<24} {r['position']:<6} {r['team']}")


if __name__ == "__main__":
    main()
