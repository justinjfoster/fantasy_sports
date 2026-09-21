"""
One value scale for every draftable player, blended from two systems.

The project keeps three signals deliberately apart (see CONTEXT.md). This
module turns two of them into a single ordering and leaves the third alone:

    ours      what a player actually did in 2025-26, scored in this league's
              categories, as a percentile summed across them
    fantrax   Fantrax's projection for 2026-27, their own 0-100 value formula
    adp       NOT part of value. It says when a player will be gone, under
              other leagues' scoring. It stays beside the value as `edge`,
              which is where the bargains show up.

Blending the two is not averaging two columns: they are in different units and
each has its own idea of what a replacement-level player looks like. So each
system is scored against its OWN positional replacement, and the two resulting
value-over-replacement numbers are standardised before they are mixed. A blend
weight of 0 is pure `ours`, 1 is pure Fantrax.

Why per-position replacement rather than one overall line: the league starts
exactly 24 goalies, so the 25th best goalie is free and every goalie above him
is worth only the gap to that line. A single "205th best player" cutoff treats
a goalie and a centre as interchangeable and they are not.
"""

import os
import unicodedata

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEAMS, ROUNDS = 12, 17
SLOTS = {'C': 2, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2}
UTIL = 2
BENCH = 4
MY_TEAM = 'justinjjfoster'

# Category counts, which is what makes `ours` a summed rather than averaged
# score: a skater's total spans 7 categories, a goalie's 4.
SKATER_CATEGORIES = 7
GOALIE_CATEGORIES = 4


def ascii_name(s):
    """Hockey-Reference writes Nečas, Fantrax writes Necas. Join on this."""
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


def positions_of(value):
    return {p.strip().upper() for p in str(value).split(',') if p.strip()}


def is_goalie(value):
    return 'G' in positions_of(value)


def load_signals():
    """The Fantrax pool with our own rankings joined onto it."""
    from src.rankings_data import LATEST_SEASON, rankings_path

    pool = pd.read_csv(os.path.join(REPO, "data", "fantrax_player_pool.csv"))
    for c in ("rank", "adp", "score"):
        pool[c] = pd.to_numeric(pool[c], errors="coerce")
    pool["key"] = pool["name"].map(ascii_name)

    sk = pd.read_csv(rankings_path(f"skater_rankings_v2_{LATEST_SEASON}.csv"))
    go = pd.read_csv(rankings_path(f"goalie_rankings_v2_{LATEST_SEASON}.csv"))
    go["position"] = "G"
    # `total` is already summed across each group's categories.
    mine = pd.concat([sk[["name", "position", "total"]],
                      go[["name", "position", "total"]]])
    mine = mine.rename(columns={"total": "ours"})
    mine["key"] = mine["name"].map(ascii_name)

    df = pool.merge(mine[~mine.key.duplicated(keep=False)][["key", "ours"]],
                    on="key", how="left")

    # A name can belong to two different real players - Vancouver has an Elias
    # Pettersson at C and another at D, 450 rank places apart. Joining on name
    # alone hands one man's production to the other, so duplicated names are
    # matched on position too.
    for _, cand in mine[mine.key.duplicated(keep=False)].iterrows():
        eligible = positions_of(cand.position)
        for i in df.index[df["key"] == cand.key]:
            if eligible & positions_of(df.at[i, "position"]):
                df.at[i, "ours"] = cand.ours

    df["projection_only"] = df["ours"].isna()
    return df


def replacement_levels(df, value_col):
    """
    The best player at each position that nobody has to spend a pick on.

    Slots are filled from the top down, scarcest position first so that
    multi-position players land where they are actually needed, then the 24
    utility slots from whichever skaters are left - which is what raises the
    bar at every skater position. Whoever is still unclaimed at a position is
    that position's replacement.
    """
    pool = df.dropna(subset=[value_col]).sort_values(value_col, ascending=False)
    eligible = {pos: pool.position.map(lambda v: pos in positions_of(v))
                for pos in SLOTS}

    taken = set()
    for pos in sorted(SLOTS, key=lambda p: eligible[p].sum() / (SLOTS[p] * TEAMS)):
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
        if i not in taken and not is_goalie(pool.at[i, 'position']):
            taken.add(i)
            need -= 1

    levels = {}
    for pos in SLOTS:
        for i in pool.index[eligible[pos]]:
            if i not in taken:
                levels[pos] = float(pool.at[i, value_col])
                break
        levels.setdefault(pos, float(pool[value_col].min()))
    return levels


def value_over_replacement(df, value_col):
    """VOR against whichever eligible position treats the player best."""
    levels = replacement_levels(df, value_col)

    def score(row):
        v = row[value_col]
        if pd.isna(v):
            return pd.Series({'vor': float('nan'), 'slot': None})
        cands = [(v - levels[p], p) for p in positions_of(row.position) if p in levels]
        if not cands:
            return pd.Series({'vor': float('nan'), 'slot': None})
        vor, pos = max(cands)
        return pd.Series({'vor': vor, 'slot': pos})

    return df.apply(score, axis=1), levels


def build(weight=0.5, goalie_weight=1.0, df=None):
    """
    Rank every player on a blend of the two systems.

    weight        0 = our rankings only, 1 = Fantrax only, 0.5 = even
    goalie_weight multiplies goalie value after standardising. Positional
                  replacement already prices goalie scarcity; this is a dial
                  for the judgement on top of it, not a second correction.

    Returns the frame sorted best-first with a 1..N `board_rank`.
    """
    if df is None:
        df = load_signals()
    df = df.copy()

    ours_vor, ours_levels = value_over_replacement(df, "ours")
    fntx_vor, fntx_levels = value_over_replacement(df, "score")
    df["ours_vor"], df["slot"] = ours_vor["vor"], ours_vor["slot"]
    df["fntx_vor"] = fntx_vor["vor"]
    # A player absent from our scrape has no `ours` slot; fall back to the
    # Fantrax one so rookies still get a position.
    df["slot"] = df["slot"].fillna(fntx_vor["slot"])

    # The two VORs are in different units - ours in percentile-points summed
    # over 7 or 4 categories, Fantrax's on their own 0-100 formula - so they
    # are standardised before mixing. Without this the blend weight would not
    # mean what it says.
    for col in ("ours_vor", "fntx_vor"):
        sd = df[col].std()
        df[col + "_z"] = df[col] / sd if sd and sd == sd else 0.0

    goalie = df["position"].map(is_goalie)
    for col in ("ours_vor_z", "fntx_vor_z"):
        df.loc[goalie, col] *= goalie_weight

    # Where we have no scrape for a player, the blend degenerates to Fantrax
    # rather than dropping him: that is the only way rookies appear at all.
    blended = (1 - weight) * df["ours_vor_z"] + weight * df["fntx_vor_z"]
    df["value"] = blended.where(~df["projection_only"], df["fntx_vor_z"])

    df = df.sort_values("value", ascending=False).reset_index(drop=True)
    df["board_rank"] = df.index + 1
    # Positive = he falls later than he rates here, so you can wait on him.
    df["edge"] = df["adp"] - df["board_rank"]
    return df, {"ours": ours_levels, "fantrax": fntx_levels}


def open_slots(roster):
    """
    What is still unfilled, given the players you already hold.

    `roster` is a DataFrame with a `position` column. A second goalie closes
    G and a third can never reopen it, because utility takes skaters only.
    """
    remaining = dict(SLOTS)
    util = UTIL
    bench = BENCH
    for _, player in roster.iterrows():
        eligible = positions_of(player.position)
        for pos in sorted(eligible, key=lambda p: remaining.get(p, 0), reverse=True):
            if remaining.get(pos, 0) > 0:
                remaining[pos] -= 1
                break
        else:
            if util > 0 and not eligible & {'G'}:
                util -= 1
            elif bench > 0:
                bench -= 1
    remaining['UTIL'] = util
    remaining['BENCH'] = bench
    return remaining


def wanted_positions(remaining):
    """
    Which positions a pick should go to right now.

    The bench deliberately does NOT open everything up. Four bench spots are
    open for most of the draft, so counting them would admit every position at
    every pick and the roster constraint would mean nothing - a third goalie
    would keep being offered while a starting slot sat empty. Starters first;
    the bench only opens once every starting slot is filled.
    """
    wanted = {p for p, n in remaining.items()
              if n and p not in ('UTIL', 'BENCH')}
    if remaining.get('UTIL'):
        wanted |= {'C', 'LW', 'RW', 'D'}       # utility takes any skater
    if wanted:
        return wanted
    return set(SLOTS) if remaining.get('BENCH') else set()

def keepers():
    """
    Every player already locked up league-wide, read live from Fantrax.

    Returns a frame with `key`, `name`, `team`, `position` and `round` - the
    round a keeper sits in is what he cost his owner. The player pool now
    includes these players so they can be priced, which means filtering them
    is this project's job rather than the endpoint's.
    """
    import sys as _sys
    _sys.path.insert(0, os.path.join(REPO, "scripts"))
    from fantrax_explore import raw_call

    from src.fantrax import default_league_id

    data = raw_call(default_league_id(), "getDraftResults")["responses"][0]["data"]
    by_id = {s["scorerId"]: s for s in data["scorers"]}
    teams = {t["id"]: t["name"] for t in data["fantasyTeamsOrdered"]}
    out = []
    for pick in data["draftPicksOrdered"]:
        if pick.get("scorerId"):
            s = by_id.get(pick["scorerId"], {})
            out.append({"key": ascii_name(s.get("name", "")),
                        "name": s.get("name", ""),
                        "team": teams.get(pick["teamId"], ""),
                        "position": s.get("posShortNames", ""),
                        "round": pick["round"]})
    return pd.DataFrame(out,
                        columns=["key", "name", "team", "position", "round"])
