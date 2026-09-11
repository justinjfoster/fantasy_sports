#!/usr/bin/env python3
"""
Goalie rankings, second generation.

Two changes over scripts/equal_weight_goalie_rankings.py:

1. A minimum games-played filter. The unfiltered pool has 21 goalies with
   fewer than 5 appearances, and they hold the best save percentages and
   GAAs in the league on samples of one or two games. They cannot be
   drafted or started, but they occupy the top of two of the four
   categories and squash the scale every real starter is measured on.

2. A magnitude boost. Plain percentile is purely ordinal: finishing first
   in saves scores 100 whether you won by one save or by three hundred.
   Each category is also scored as a winsorized z-score mapped through the
   normal CDF, which keeps the 0-100 scale but rewards genuinely outlying
   production. --boost slides between the two.

    python scripts/goalie_rankings_v2.py                  # boost 0.5, 25 GP
    python scripts/goalie_rankings_v2.py --boost 0        # pure percentile
    python scripts/goalie_rankings_v2.py --boost 1        # pure magnitude
    python scripts/goalie_rankings_v2.py --min-games 15
"""

import argparse
import math
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rankings_data import LATEST_SEASON, load_goalies, rankings_path

# Your league's four goalie categories. GAA is the only one where lower wins.
CATEGORIES = ['wins', 'saves', 'save_percentage']
INVERTED = ['goals_against_average']
WINSOR = 3.0


def _phi(z):
    """Standard normal CDF, so a z-score lands back on a 0-100 scale."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def score(df, boost=0.5):
    out = df.copy()
    parts = []

    for cat in CATEGORIES + INVERTED:
        higher_is_better = cat not in INVERTED
        col = out[cat]

        pct = col.rank(pct=True, ascending=higher_is_better) * 100

        mean, std = col.mean(), col.std()
        z = (col - mean) / std if std else col * 0
        if not higher_is_better:
            z = -z
        z = z.clip(-WINSOR, WINSOR)
        mag = z.map(_phi) * 100

        out[f'{cat}_percentile'] = pct
        out[f'{cat}_magnitude'] = mag
        out[f'{cat}_score'] = (1 - boost) * pct + boost * mag
        parts.append(f'{cat}_score')

    out['total'] = out[parts].sum(axis=1)
    out['rank'] = out['total'].rank(method='min', ascending=False)
    return out.sort_values('rank')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--boost', type=float, default=0.5,
                    help='0 = pure percentile, 1 = pure magnitude (default 0.5)')
    ap.add_argument('--min-games', type=int, default=25,
                    help='drop goalies below this many appearances (default 25)')
    ap.add_argument('--highlight', nargs='*', default=[],
                    help='player names to call out wherever they land')
    ap.add_argument('--top', type=int, default=25)
    args = ap.parse_args()

    df = load_goalies()
    before = len(df)
    df = df[df['games_played'] >= args.min_games].reset_index(drop=True)
    print(f"{LATEST_SEASON} goalies: {before} scraped, {len(df)} at "
          f">={args.min_games} GP ({before - len(df)} dropped)")
    print(f"boost = {args.boost}  (0 = ordinal percentile, 1 = magnitude-aware)\n")

    ranked = score(df, boost=args.boost)

    print(f"{'#':>3}  {'goalie':<24}{'GP':>4}{'W':>4}{'SV':>6}{'SV%':>7}{'GAA':>6}{'score':>8}")
    print('-' * 63)
    for _, r in ranked.head(args.top).iterrows():
        print(f"{r['rank']:>3.0f}  {r['name']:<24}{r.games_played:>4.0f}{r.wins:>4.0f}"
              f"{r.saves:>6.0f}{r.save_percentage:>7.3f}{r.goals_against_average:>6.2f}"
              f"{r.total:>8.1f}")

    for name in args.highlight:
        hit = ranked[ranked['name'].str.contains(name, case=False, na=False)]
        for _, r in hit.iterrows():
            cats = "  ".join(
                f"{c.replace('goals_against_average','GAA').replace('save_percentage','SV%')
                    .replace('wins','W').replace('saves','SV')}"
                f" {r[f'{c}_score']:.0f}"
                for c in CATEGORIES + INVERTED)
            print(f"\n>> {r['name']}: rank {r['rank']:.0f} of {len(ranked)}   [{cats}]")

    out = rankings_path(f'goalie_rankings_v2_{LATEST_SEASON}.csv')
    keep = (['name', 'rank', 'total', 'games_played']
            + CATEGORIES + INVERTED
            + [f'{c}_score' for c in CATEGORIES + INVERTED])
    ranked[keep].to_csv(out, index=False)
    print(f"\nsaved {out}")


if __name__ == '__main__':
    main()
