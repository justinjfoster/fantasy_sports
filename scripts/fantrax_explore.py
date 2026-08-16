#!/usr/bin/env python3
"""
Poke around a Fantrax league.

    python scripts/fantrax_explore.py <league_id>

Prints what the API exposes for your league: teams, standings, rosters and
recent transactions. Run scripts/fantrax_login.py first.

Also usable as a starting point for your own queries - see raw_call() at the
bottom for hitting the endpoint directly with any method name.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

from src.fantrax import FantraxAuthError, connect, load_session

ENDPOINT = "https://www.fantrax.com/fxpa/req"


def show_league(league):
    print("=" * 66)
    print("LEAGUE")
    print("=" * 66)
    for attr in ("name", "year", "sport", "start_date", "end_date"):
        value = getattr(league, attr, None)
        if value:
            print(f"  {attr:12} {value}")

    teams = getattr(league, "teams", None) or []
    print(f"\n  {len(teams)} teams:")
    for team in teams:
        print(f"    - {team}")
    return teams


def show_standings(league):
    print("\n" + "=" * 66)
    print("STANDINGS")
    print("=" * 66)
    try:
        standings = league.standings()
    except Exception as e:
        print(f"  unavailable: {type(e).__name__}: {e}")
        return
    for rank in getattr(standings, "ranks", {}).values():
        print(f"  {rank}")


def show_roster(league, teams):
    if not teams:
        return
    print("\n" + "=" * 66)
    print(f"ROSTER - {teams[0]}")
    print("=" * 66)
    try:
        roster = league.roster_info(teams[0].team_id)
    except Exception as e:
        print(f"  unavailable: {type(e).__name__}: {e}")
        return
    for row in getattr(roster, "rows", []):
        if getattr(row, "player", None):
            print(f"  {row.pos_id:<6} {row.player.name:<28} {row.player.team_name}")


def show_transactions(league):
    print("\n" + "=" * 66)
    print("RECENT TRANSACTIONS")
    print("=" * 66)
    try:
        transactions = league.transactions(count=10)
    except Exception as e:
        print(f"  unavailable: {type(e).__name__}: {e}")
        return
    for transaction in transactions:
        print(f"  {transaction}")


def raw_call(league_id, method, **data):
    """
    Call any Fantrax method directly and return the parsed JSON.

    The website uses this one endpoint for everything, so the fastest way to
    discover new methods is to open Fantrax in your browser with DevTools on
    the Network tab, click around, and copy the "method" name out of the
    request payload to /fxpa/req.

        raw_call(league_id, "getStandings")
        raw_call(league_id, "getTeamRosterInfo", teamId="abc123")
    """
    session = load_session()
    payload = {"msgs": [{"method": method, "data": {"leagueId": league_id, **data}}]}
    response = session.post(ENDPOINT, params={"leagueId": league_id}, json=payload, timeout=30)
    return response.json()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Your league id is in the league URL:")
        print("  https://www.fantrax.com/fantasy/league/<league_id>/home")
        sys.exit(1)

    league_id = sys.argv[1]

    try:
        league = connect(league_id)
    except FantraxAuthError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        name = type(e).__name__
        print(f"Could not open league {league_id}: {name}: {e}")
        if name == "NotMemberOfLeague":
            print("\nEither the league id is wrong, or the saved cookies belong to")
            print("an account that is not in this league.")
        elif name == "NotLoggedIn":
            print("\nCookies have expired. Re-run: python scripts/fantrax_login.py")
        sys.exit(1)

    teams = show_league(league)
    show_standings(league)
    show_roster(league, teams)
    show_transactions(league)

    print("\n" + "=" * 66)
    print("Explore further with raw_call() - see the docstring in this file")
    print("and the method list in FANTRAX.md")
    print("=" * 66)


if __name__ == "__main__":
    main()
