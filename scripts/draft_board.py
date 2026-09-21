#!/usr/bin/env python3
"""
Combined draft board: our rankings, Fantrax's projections, and ADP in one table.

A command-line view of the same model the draft-night app uses
(`src/valuation.py`); see that module for how the blend and the per-position
replacement levels are built.

    python scripts/draft_board.py
    python scripts/draft_board.py --weight 0        # our rankings only
    python scripts/draft_board.py --weight 1        # Fantrax only
    python scripts/draft_board.py --pick 32         # who lasts to your pick
    python scripts/draft_board.py --pos C
    python scripts/draft_board.py --next            # only what fits an open slot

For draft night itself use the app, which can mark players off as they go:

    streamlit run scripts/draft_night.py
"""

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.fantrax import default_league_id
from src.valuation import (BENCH, MY_TEAM, REPO, SLOTS, ascii_name, build,
                           open_slots, wanted_positions)


def keepers():
    """Players already locked up, read live from the draft results."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from fantrax_explore import raw_call
    data = raw_call(default_league_id(), "getDraftResults")["responses"][0]["data"]
    by_id = {s["scorerId"]: s for s in data["scorers"]}
    teams = {t["id"]: t["name"] for t in data["fantasyTeamsOrdered"]}
    out = []
    for p in data["draftPicksOrdered"]:
        if p.get("scorerId"):
            s = by_id.get(p["scorerId"], {})
            out.append({"key": ascii_name(s.get("name", "")), "name": s.get("name"),
                        "team": teams.get(p["teamId"]),
                        "position": s.get("posShortNames", ""), "round": p["round"]})
    return pd.DataFrame(out)


def show(df, title, top):
    print(f"\n{title}")
    print(f"{'#':>4}{'value':>8}{'ADP':>7}{'edge':>6}  {'player':<24}{'pos':<8}{'slot':<5}{'team'}")
    print("-" * 78)
    for _, r in df.head(top).iterrows():
        a = f"{r.adp:.0f}" if pd.notna(r.adp) else "  -"
        e = f"{r.edge:+.0f}" if pd.notna(r.edge) else "   -"
        flag = "*" if r.projection_only else " "
        print(f"{r.board_rank:>4}{r.value:>8.2f}{a:>7}{e:>6}  {r['name']:<23}{flag}"
              f"{str(r.position):<8}{str(r.slot or '-'):<5}{str(r.team)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weight", type=float, default=0.5,
                    help="0 = our rankings only, 1 = Fantrax only (default 0.5)")
    ap.add_argument("--goalie-weight", type=float, default=1.0,
                    help="multiplier on goalie value, on top of replacement level")
    ap.add_argument("--pick", type=int, help="show who typically lasts to this pick")
    ap.add_argument("--pos", help="filter to a position, e.g. C or G")
    ap.add_argument("--next", action="store_true",
                    help="what to take, given the slots you still have open")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    df, levels = build(weight=args.weight, goalie_weight=args.goalie_weight)

    kept = keepers()
    df = df[~df.key.isin(set(kept.key))]

    mine = kept[kept.team == MY_TEAM]
    remaining = open_slots(mine)

    print(f"{len(kept)} keepers removed | blend weight {args.weight} "
          f"(0 = ours, 1 = Fantrax)")
    print("replacement level by position:")
    print(f"    {'':<5}" + "".join(f"{p:>9}" for p in SLOTS))
    for label, key in (("ours", "ours"), ("fntx", "fantrax")):
        print(f"    {label:<5}" + "".join(f"{levels[key][p]:>9.1f}" for p in SLOTS))
    print("\nyour open slots: "
          + ", ".join(f"{p} {n}" for p, n in remaining.items() if n))

    if args.pos:
        df = df[df["position"].fillna("").str.contains(args.pos.upper())]
    if args.pick:
        df = df[df["adp"] >= args.pick]

    if args.next:
        wanted = wanted_positions(remaining)
        fits = df[df.slot.isin(wanted)]
        show(fits, f"Best available that fits an open slot "
                   f"({', '.join(sorted(wanted))}):  * = Fantrax projection only",
             args.top)
        blocked = df[~df.slot.isin(wanted) & df.slot.notna()]
        if len(blocked):
            b = blocked.iloc[0]
            print(f"\nskipped: {b['name']} ({b.slot}) rates {b.value:+.2f} "
                  f"but you have no {b.slot} slot open")
    else:
        title = (f"Likely available at pick {args.pick}:" if args.pick
                 else "Best available:")
        show(df, title + "   * = Fantrax projection only", args.top)

    out = os.path.join(REPO, "data", "draft_board.csv")
    cols = ["board_rank", "name", "position", "team", "slot", "value", "adp",
            "edge", "rank", "score", "ours", "projection_only",
            "g", "a", "ppp", "sog", "fow", "hit", "blk", "w", "gaa", "sv", "sv_pct"]
    df[[c for c in cols if c in df.columns]].to_csv(out, index=False)
    print(f"\nsaved {out}  ({len(df)} players)")


if __name__ == "__main__":
    main()
