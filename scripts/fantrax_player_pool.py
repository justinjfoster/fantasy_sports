#!/usr/bin/env python3
"""
Pull the Fantrax player pool, with ADP and Fantrax's own projections.

    python scripts/fantrax_player_pool.py            # top 500 overall
    python scripts/fantrax_player_pool.py --all      # all ~8,700
    python scripts/fantrax_player_pool.py --limit 800

Writes data/fantrax_player_pool.csv.

Fantrax returns this table already tailored to your league, so the projected
stat columns are exactly your scoring categories. Two draft-relevant columns
you cannot get from Hockey-Reference:

    adp        average draft position across all Fantrax leagues
    pct_drafted  share of leagues where the player was drafted
    score      Fantrax's own value formula for your league settings

Getting both the full pool AND the projections takes three calls; see GROUPS.
Players already kept or rostered ARE included - filtering them is the caller's
job, so that a keeper can still be looked up and priced.
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

# `positionOrGroup` takes an id from the response's own `posOrGroupList`, and
# which id you send decides BOTH who is in the table and which columns it has.
# There is no single call that returns everybody with their projections.
#
#   (unrecognised, e.g. "ALL")  everybody, but only the 9 leading columns -
#                               no projected stats at all, for anyone
#   HOCKEY_SKATING (or omitted) skaters only + GP G A SOG PPP Hit Blk FOW
#   POS_201                     goalies only + GP W GAA SV SV%
#
# So we make all three calls: the pool view for the authoritative ranking, and
# the two group views for the categories. They are joined on `scorer_id`.
#
# Why rank has to come from the pool view: `rank` is relative to whichever
# table you asked for. In the skater view it is the overall rank (2, 3, 4, 13,
# ... with gaps where goalies sit); in the goalie view it restarts at 1 and
# counts goalies only. Taking them at face value and concatenating makes every
# goalie look like a top-25 overall pick. `score` is the one column that is
# identical in all three views.
POOL_GROUP = 'ALL'
GROUPS = {
    'skater': 'HOCKEY_SKATING',
    'goalie': 'POS_201',
}

# Fixed leading columns; the rest are the league's scoring categories and are
# read from the response header, so this adapts if the league settings change.
LEADING = ['rank', 'status', 'age', 'opponent', 'score', 'pct_drafted', 'adp',
           'pct_rostered', 'pct_rostered_change']

# The group views are ordered consistently with the pool view, so the top N of
# a group covers the members of that group in the pool's top N. A little slack
# absorbs ties at the boundary.
COVERAGE_MARGIN = 1.1


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


def fetch_page(session, league_id, page, group):
    body = {"msgs": [{"method": "getPlayerStats", "data": {
        "leagueId": league_id,
        "pageNumber": str(page),
        "maxResultsPerPage": str(PAGE_SIZE),
        "positionOrGroup": group,
        # Include players already on a roster. The endpoint defaults to
        # ALL_AVAILABLE, which silently drops every keeper - 32 of them this
        # season - so Nick Suzuki could not be priced from the file at all.
        # The pool is the full picture and its consumers decide who is
        # draftable; relying on the server-side filter hides players we need
        # to look up. Note the key is statusOrTeamFilter: statusOrTeam is
        # accepted and ignored.
        "statusOrTeamFilter": "ALL",
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
    names = [c.get("shortName", f"col{i}").lower() for i, c in enumerate(cells)]
    # 'sv%' would be awkward downstream; everything else is already plain.
    return [n.replace('%', '_pct') for n in names][len(LEADING):]


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


def collect(session, league_id, group, wanted, label):
    """Pull `wanted` players from one view. wanted=None means everything."""
    first = fetch_page(session, league_id, 1, group)
    total = first["paginatedResultSet"]["totalNumResults"]
    wanted = total if wanted is None else min(wanted, total)
    pages = (wanted + PAGE_SIZE - 1) // PAGE_SIZE

    stat_cols = stat_columns(first)
    shown = ', '.join(stat_cols) if stat_cols else '(none - pool view)'
    print(f"{label}: {total:,} available, fetching {wanted:,}")
    print(f"  categories: {shown}")

    records = list(parse_rows(first, stat_cols))
    for page in range(2, pages + 1):
        time.sleep(RATE_LIMIT_SECONDS)
        print(f"  page {page}/{pages}...")
        records.extend(parse_rows(fetch_page(session, league_id, page, group), stat_cols))

    return records[:wanted], stat_cols


def is_goalie(record):
    return 'G' in {p.strip().upper() for p in str(record.get('position', '')).split(',')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=500,
                        help='how many players to pull, by overall rank (default 500)')
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

    limit = None if args.all else args.limit

    try:
        # The pool view decides who is in the file and carries the only
        # ranking that spans skaters and goalies on one scale.
        records, _ = collect(session, league_id, POOL_GROUP, limit, "Pool")

        def covering(predicate):
            if limit is None:
                return None
            return int(sum(1 for r in records if predicate(r)) * COVERAGE_MARGIN) + PAGE_SIZE

        time.sleep(RATE_LIMIT_SECONDS)
        skaters, skater_cols = collect(
            session, league_id, GROUPS['skater'],
            covering(lambda r: not is_goalie(r)), "Skaters")
        time.sleep(RATE_LIMIT_SECONDS)
        goalies, goalie_cols = collect(
            session, league_id, GROUPS['goalie'],
            covering(is_goalie), "Goalies")
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    # Union of both groups' categories. A skater row simply has no 'w' or
    # 'gaa', and a goalie row has no 'fow' - DictWriter fills those blank.
    stat_cols = skater_cols + [c for c in goalie_cols if c not in skater_cols]

    stats = {}
    for source, cols in ((skaters, skater_cols), (goalies, goalie_cols)):
        for row in source:
            stats[row['scorer_id']] = {c: row.get(c, '') for c in cols}

    missing = 0
    for record in records:
        found = stats.get(record['scorer_id'])
        if found is None:
            missing += 1
        record.update(found or {})

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fantrax_player_pool.csv')

    fieldnames = ['name', 'team', 'position', 'rookie', 'scorer_id'] + LEADING + stat_cols
    with open(out_path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, restval='')
        writer.writeheader()
        writer.writerows(records)

    n_goalies = sum(1 for r in records if is_goalie(r))
    print(f"\nSaved {len(records):,} players "
          f"({len(records) - n_goalies:,} skaters + {n_goalies:,} goalies) to {out_path}")
    if missing:
        print(f"WARNING: {missing} players got no projections; raise COVERAGE_MARGIN")

    print(f"\nTop 10 by ADP:")
    print(f"  {'ADP':>6}  {'Rk':>4}  {'name':<24} {'pos':<6} {'team'}")
    for r in sorted(records, key=lambda r: as_number(r['adp']))[:10]:
        print(f"  {r['adp']:>6}  {r['rank']:>4}  {r['name']:<24} {r['position']:<6} {r['team']}")


if __name__ == "__main__":
    main()
