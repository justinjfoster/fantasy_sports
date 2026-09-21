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
    python scripts/draft_board.py --pick 32     # who is likely there at pick 32
    python scripts/draft_board.py --pos C
    python scripts/draft_board.py --next        # what to actually take, given
                                                # the slots you still have open
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

# One team's starting roster, then the bench. 13 starters + 4 = 17 rounds.
SLOTS = {'C': 2, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2}
UTIL = 2
BENCH = 4
ROSTERED = TEAMS * ROUNDS

MY_TEAM = 'justinjjfoster'


def ascii_name(s):
    """Hockey-Reference writes Nečas, Fantrax writes Necas. Join on this."""
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


def positions_of(value):
    return {p.strip().upper() for p in str(value).split(',') if p.strip()}


def draft_results():
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from fantrax_explore import raw_call
    return raw_call(default_league_id(), "getDraftResults")["responses"][0]["data"]


def keepers(data):
    """Players already locked up as keepers, read live from the draft results."""
    by_id = {s["scorerId"]: s for s in data["scorers"]}
    teams = {t["id"]: t["name"] for t in data["fantasyTeamsOrdered"]}
    out = []
    for p in data["draftPicksOrdered"]:
        if p.get("scorerId"):
            s = by_id.get(p["scorerId"], {})
            out.append({"key": ascii_name(s.get("name", "")),
                        "name": s.get("name"), "team": teams.get(p["teamId"]),
                        "position": s.get("posShortNames", ""), "round": p["round"]})
    return pd.DataFrame(out)


def open_slots(kept):
    """
    What is still unfilled on your own roster.

    Everything you have already locked up - today just the keepers, during the
    draft everything you have taken - is assigned to a slot before this
    reports what is left, so a second goalie closes G and a third never opens.
    """
    remaining = dict(SLOTS)
    util = UTIL
    mine = kept[kept.team == MY_TEAM] if len(kept) else kept
    for _, player in mine.iterrows():
        eligible = positions_of(player.position)
        for pos in sorted(eligible, key=lambda p: remaining.get(p, 0), reverse=True):
            if remaining.get(pos, 0) > 0:
                remaining[pos] -= 1
                break
        else:
            if util > 0 and 'G' not in eligible:
                util -= 1
    remaining['UTIL'] = util
    return remaining


def replacement_levels(df, value_col='ours'):
    """
    The replacement level at each position, which is what makes a pick's value
    comparable across positions.

    Not the 205th best player overall: that treats a goalie and a centre as
    interchangeable, and they are not. The league starts exactly 24 goalies,
    so the 25th best goalie is free and every goalie above him is worth only
    the gap to that line. A goalie who rates 20 points better than the best
    skater can still be the worse pick.

    Slots are filled from the top down, scarcest position first so that
    multi-position players land where they are actually needed, and utility
    afterwards from whichever skaters are left - which is what raises the bar
    at every skater position.
    """
    pool = df.dropna(subset=[value_col]).sort_values(value_col, ascending=False)
    eligible = {pos: pool.position.map(lambda v: pos in positions_of(v))
                for pos in SLOTS}

    taken = set()
    order = sorted(SLOTS, key=lambda p: eligible[p].sum() / (SLOTS[p] * TEAMS))
    for pos in order:
        need = SLOTS[pos] * TEAMS
        for i in pool.index[eligible[pos]]:
            if need == 0:
                break
            if i not in taken:
                taken.add(i)
                need -= 1

    need = UTIL * TEAMS
    for i in pool.index:
        if need == 0:
            break
        if i not in taken and 'G' not in positions_of(pool.at[i, 'position']):
            taken.add(i)
            need -= 1

    levels = {}
    for pos in SLOTS:
        for i in pool.index[eligible[pos]]:
            if i not in taken:
                levels[pos] = float(pool.at[i, value_col])
                break
    return levels


def assign_value(df, levels):
    """VOR against the position that gives the player his best case."""
    def best(row):
        if pd.isna(row.ours):
            return pd.Series({'slot': None, 'vor': float('nan')})
        cands = [(row.ours - levels[p], p) for p in positions_of(row.position)
                 if p in levels]
        if not cands:
            return pd.Series({'slot': None, 'vor': float('nan')})
        vor, pos = max(cands)
        return pd.Series({'slot': pos, 'vor': vor})
    return df.join(df.apply(best, axis=1))


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
        slots = positions_of(cand.position)
        hit = df["key"] == cand.key
        for i in df.index[hit]:
            if slots & positions_of(df.at[i, "position"]):
                df.at[i, "ours"] = cand.ours

    results = draft_results()
    kept = keepers(results)

    # The pool already hides kept players behind its ALL_AVAILABLE default,
    # but do not rely on that: a pull made with statusOrTeamFilter="ALL" has
    # them in, and they are not draftable either way.
    df["kept_by"] = df["key"].map(dict(zip(kept.key, kept.team)))
    df = df[df["kept_by"].isna()].drop(columns=["kept_by"])

    levels = replacement_levels(df)
    df = assign_value(df, levels)

    # Positive = falls later than he rates, i.e. you can wait on him.
    df["edge"] = df["adp"] - df["rank"]
    return df.sort_values("rank"), levels, kept


def show(df, title, top):
    print(f"\n{title}")
    print(f"{'Fx#':>5}{'ADP':>7}{'ours':>6}{'VOR':>6}{'edge':>6}  {'player':<22}{'pos':<8}{'slot':<5}{'team'}")
    print("-" * 82)
    for _, r in df.head(top).iterrows():
        o = f"{r.ours:.0f}" if pd.notna(r.ours) else "  -"
        v = f"{r.vor:+.0f}" if pd.notna(r.vor) else "   -"
        e = f"{r.edge:+.0f}" if pd.notna(r.edge) else "   -"
        a = f"{r.adp:.0f}" if pd.notna(r.adp) else "  -"
        print(f"{r['rank']:>5.0f}{a:>7}{o:>6}{v:>6}{e:>6}  {r['name']:<22}"
              f"{str(r.position):<8}{str(r.slot or '-'):<5}{str(r.team)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int, help="show who typically lasts to this pick")
    ap.add_argument("--pos", help="filter to a position, e.g. C or G")
    ap.add_argument("--next", action="store_true",
                    help="what to take, given the slots you still have open")
    ap.add_argument("--top", type=int, default=40)
    args = ap.parse_args()

    df, levels, kept = build()
    remaining = open_slots(kept)

    print(f"{len(kept)} keepers removed")
    print("replacement level by position (the best player you can have for free):")
    for pos in list(SLOTS):
        print(f"    {pos:<4} {levels[pos]:>6.1f}   ({SLOTS[pos] * TEAMS} start league-wide)")
    print(f"\nyour open slots: "
          + ", ".join(f"{p} {n}" for p, n in remaining.items() if n) 
          + f"  (+{BENCH} bench)")

    if args.pos:
        df = df[df["position"].fillna("").str.contains(args.pos.upper())]
    if args.pick:
        df = df[df["adp"] >= args.pick]

    if args.next:
        wanted = {p for p, n in remaining.items() if n and p != 'UTIL'}
        if remaining.get('UTIL'):
            wanted |= {'C', 'LW', 'RW', 'D'}       # utility takes any skater
        fits = df[df.slot.isin(wanted)].sort_values("vor", ascending=False)
        show(fits, f"Best available that fits an open slot ({', '.join(sorted(wanted))}):",
             args.top)
        blocked = df[~df.slot.isin(wanted) & df.slot.notna()]
        if len(blocked):
            top_blocked = blocked.sort_values("vor", ascending=False).iloc[0]
            print(f"\nskipped: {top_blocked['name']} ({top_blocked.slot}) rates "
                  f"{top_blocked.vor:+.0f} but you have no {top_blocked.slot} slot left")
    else:
        title = (f"Likely available at pick {args.pick}:" if args.pick
                 else "Best available, by Fantrax rank:")
        show(df, title, args.top)

    out = os.path.join(REPO, "data", "draft_board.csv")
    cols = ["name", "position", "team", "slot", "rank", "adp", "score", "ours",
            "vor", "edge", "g", "a", "ppp", "sog", "fow", "hit", "blk",
            "w", "gaa", "sv", "sv_pct"]
    df[[c for c in cols if c in df.columns]].to_csv(out, index=False)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
