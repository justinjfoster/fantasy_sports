#!/usr/bin/env python3
"""
Skater rankings, second generation: percentile with a magnitude boost.

Plain percentile is purely ordinal. Finishing first in assists scores 100
whether you won by one assist or by thirty, so a player who genuinely
dominates a category is paid the same as one who edges it. That is why
McDavid falls outside the top 20 of the first-generation rankings on a
138-point season while well-rounded players top the list.

Switching to z-score over-corrects. Hits and faceoff wins are heavily
right-skewed, and a handful of specialists then distort the whole scale.

So each category is scored twice - ordinal percentile, and a winsorized
z-score (clipped at +/-3 so no single freak season dominates) mapped back
onto 0-100 through the normal CDF - and blended:

    score = (1 - boost) * percentile + boost * magnitude

    python scripts/skater_rankings_v2.py                # boost 0.5
    python scripts/skater_rankings_v2.py --boost 0      # first-gen behaviour
    python scripts/skater_rankings_v2.py --boost 1      # fully magnitude-aware
    python scripts/skater_rankings_v2.py --min-games 20

A games-played floor matters here for the same reason it does for goalies:
a skater with four games and one lucky power-play point should not occupy a
percentile that a full-season player is measured against.
"""

import argparse
import math
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rankings_data import LATEST_SEASON, load_skaters, rankings_path

# The league's seven skater categories. Every one is higher-is-better.
CATEGORIES = ['goals', 'assists', 'power_play_points', 'shots',
              'face_off_wins', 'hits', 'blocked_shots']
WINSOR = 3.0

SHORT = {'goals': 'G', 'assists': 'A', 'power_play_points': 'PPP',
         'shots': 'SOG', 'face_off_wins': 'FOW', 'hits': 'HIT',
         'blocked_shots': 'BLK'}


def _phi(z):
    """Standard normal CDF, to put a z-score back on a 0-100 scale."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def score(df, boost=0.5):
    out = df.copy()
    parts = []
    for cat in CATEGORIES:
        col = out[cat]
        pct = col.rank(pct=True) * 100

        mean, std = col.mean(), col.std()
        z = ((col - mean) / std if std else col * 0).clip(-WINSOR, WINSOR)
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
                    help='0 = ordinal percentile, 1 = fully magnitude-aware')
    ap.add_argument('--min-games', type=int, default=20)
    ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--highlight', nargs='*', default=[])
    args = ap.parse_args()

    df = load_skaters()
    before = len(df)
    df = df[df['games_played'] >= args.min_games].reset_index(drop=True)
    print(f"{LATEST_SEASON} skaters: {before} scraped, {len(df)} at "
          f">={args.min_games} GP ({before - len(df)} dropped)")
    print(f"boost = {args.boost}\n")

    ranked = score(df, boost=args.boost)

    hdr = "".join(f"{SHORT[c]:>5}" for c in CATEGORIES)
    print(f"{'#':>4}  {'skater':<22}{'pos':<5}{hdr}{'score':>8}")
    print('-' * (4 + 2 + 22 + 5 + 5 * len(CATEGORIES) + 8))
    for _, r in ranked.head(args.top).iterrows():
        cats = "".join(f"{r[c]:>5.0f}" for c in CATEGORIES)
        print(f"{r['rank']:>4.0f}  {r['name']:<22}{r.position:<5}{cats}{r.total:>8.1f}")

    for name in args.highlight:
        hit = ranked[ranked['name'].str.contains(name, case=False, na=False)]
        for _, r in hit.iterrows():
            per = "  ".join(f"{SHORT[c]} {r[f'{c}_score']:.0f}" for c in CATEGORIES)
            print(f"\n>> {r['name']}: rank {r['rank']:.0f} of {len(ranked)}   [{per}]")

    out = rankings_path(f'skater_rankings_v2_{LATEST_SEASON}.csv')
    keep = (['name', 'position', 'team', 'rank', 'total', 'games_played']
            + CATEGORIES + [f'{c}_score' for c in CATEGORIES])
    ranked[keep].to_csv(out, index=False)
    print(f"\nsaved {out}")


if __name__ == '__main__':
    main()
