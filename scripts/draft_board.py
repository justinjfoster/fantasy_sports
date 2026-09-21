#!/usr/bin/env python3
"""
Combined draft board: our rankings, Fantrax's projections, and ADP in one table.

Three independent signals, and the disagreements are the point:

    ours    what the player actually did last season, scored in this league's
            exact categories (scripts/skater_rankings_v2.py / goalie_rankings_v2.py)
    fantrax Fantrax's own projection for the coming season, already tailored
            to the league's scoring
    adp     when he is typically drafted - across all Fantrax leagues, most of
            which do not count faceoffs, which is where the edge comes from

Players kept by other teams are removed: they are not draftable.

    python scripts/draft_board.py
    python scripts/draft_board.py --pick 17     # who is likely there at pick 17
    python scripts/draft_board.py --pos C
"""

import argparse
import os
import sys
import unicodedata

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.fantrax import default_league_id
from src.rankings_data import LATEST_SEASON, rankings_path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAMS, ROUNDS = 12, 17
ROSTERED = TEAMS * ROUNDS


def ascii_name(s):
    """Hockey-Reference writes Nečas, Fantrax writes Necas. Join on this."""
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


def keepers():
    """Players already locked up as keepers, read live from the draft results."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from fantrax_explore import raw_call
    data = raw_call(default_league_id(), "getDraftResults")["responses"][0]["data"]
    by_id = {s["scorerId"]: s for s in data["scorers"]}
    teams = {t["id"]: t["name"] for t in data["fantasyTeamsOrdered"]}
    out = []
    for p in data["draftPicksOrdered"]:
        if p.get("scorerId"):
            s = by_id.get(p["scorerId"], {})
            out.append({"key": ascii_name(s.get("name", "")),
                        "name": s.get("name"), "team": teams.get(p["teamId"]),
                        "round": p["round"]})
    return pd.DataFrame(out)


def build():
    pool = pd.read_csv(os.path.join(REPO, "data", "fantrax_player_pool.csv"))
    for c in ("rank", "adp", "score"):
        pool[c] = pd.to_numeric(pool[c], errors="coerce")
    pool["key"] = pool["name"].map(ascii_name)

    sk = pd.read_csv(rankings_path(f"skater_rankings_v2_{LATEST_SEASON}.csv"))
    go = pd.read_csv(rankings_path(f"goalie_rankings_v2_{LATEST_SEASON}.csv"))
    sk["ours"] = sk["total"] / 7          # 7 skater categories -> 0-100
    go["ours"] = go["total"] / 4          # 4 goalie categories -> 0-100
    go["position"] = "G"
    mine = pd.concat([sk[["name", "position", "ours"]],
                      go[["name", "position", "ours"]]])
    mine["key"] = mine["name"].map(ascii_name)

    # Some names belong to two different real players - there are two Elias
    # Petterssons on Vancouver, a centre and a defenceman, and their values
    # differ by 450 rank places. Joining on name alone silently hands one
    # man's production to the other, so duplicated names are matched on
    # position as well.
    df = pool.merge(mine[~mine.key.duplicated(keep=False)][["key", "ours"]],
                    on="key", how="left")

    ambiguous = mine[mine.key.duplicated(keep=False)]
    for _, cand in ambiguous.iterrows():
        slots = {p.strip().upper() for p in str(cand.position).split(",")}
        hit = df["key"] == cand.key
        for i in df.index[hit]:
            theirs = {p.strip().upper()
                      for p in str(df.at[i, "position"]).split(",")}
            if slots & theirs:
                df.at[i, "ours"] = cand.ours

    kept = keepers()
    df["kept_by"] = df["key"].map(dict(zip(kept.key, kept.team)))
    df = df[df["kept_by"].isna()].drop(columns=["kept_by"])

    # Replacement level: the best player nobody has to spend a pick on.
    ranked = df.dropna(subset=["ours"]).sort_values("ours", ascending=False)
    repl = float(ranked.iloc[min(ROSTERED, len(ranked) - 1)]["ours"])
    df["vor"] = df["ours"] - repl

    # Positive = falls later than he rates, i.e. you can wait on him.
    df["edge"] = df["adp"] - df["rank"]
    return df.sort_values("rank"), repl, len(kept)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int, help="show who typically lasts to this pick")
    ap.add_argument("--pos", help="filter to a position, e.g. C or G")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    df, repl, n_kept = build()
    if args.pos:
        df = df[df["position"].fillna("").str.contains(args.pos.upper())]
    if args.pick:
        df = df[df["adp"] >= args.pick]
        print(f"Likely available at pick {args.pick}:\n")

    print(f"{n_kept} keepers removed | replacement level {repl:.1f} "
          f"(the {ROSTERED + 1}th best available)\n")
    print(f"{'Fx#':>5}{'ADP':>7}{'ours':>6}{'VOR':>6}{'edge':>6}  {'player':<22}{'pos':<7}{'team':<5}")
    print("-" * 74)
    for _, r in df.head(args.top).iterrows():
        o = f"{r.ours:.0f}" if pd.notna(r.ours) else "  -"
        v = f"{r.vor:+.0f}" if pd.notna(r.vor) else "   -"
        e = f"{r.edge:+.0f}" if pd.notna(r.edge) else "   -"
        a = f"{r.adp:.0f}" if pd.notna(r.adp) else "  -"
        print(f"{r['rank']:>5.0f}{a:>7}{o:>6}{v:>6}{e:>6}  {r['name']:<22}"
              f"{str(r.position):<7}{str(r.team):<5}")

    out = os.path.join(REPO, "data", "draft_board.csv")
    cols = ["name", "position", "team", "rank", "adp", "score", "ours", "vor",
            "edge", "g", "a", "ppp", "sog", "fow", "hit", "blk"]
    df[[c for c in cols if c in df.columns]].to_csv(out, index=False)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
