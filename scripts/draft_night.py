#!/usr/bin/env python3
"""
Draft-night board. Mark players as they go, see who to take next.

    streamlit run scripts/draft_night.py

Everything you mark is written to data/draft_state.json straight away, so
closing the tab, restarting the app or losing the browser does not cost you
the night's work.
"""

import json
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.valuation import (BENCH, MY_TEAM, SLOTS, TEAMS, UTIL, build,
                           load_signals, open_slots, positions_of,
                           wanted_positions)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(REPO, "data", "draft_state.json")

# Justin's 16 usable picks; R2.5/pick 17 went on Suzuki. See CONTEXT.md.
MY_PICKS = [8, 32, 41, 65, 80, 89, 104, 113, 128, 137, 150, 152, 161, 176, 185, 200]

st.set_page_config(page_title="Draft Night", layout="wide")


# --------------------------------------------------------------- state

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    return {"gone": [], "mine": []}


def save_state():
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump({"gone": st.session_state.gone,
                   "mine": st.session_state.mine}, fh, indent=1)


if "gone" not in st.session_state:
    saved = load_state()
    st.session_state.gone = saved["gone"]    # keys taken by anyone, incl. me
    st.session_state.mine = saved["mine"]    # keys on my roster, in pick order


def take(key, mine):
    if key not in st.session_state.gone:
        st.session_state.gone.append(key)
    if mine and key not in st.session_state.mine:
        st.session_state.mine.append(key)
    save_state()


def undo(key):
    st.session_state.gone = [k for k in st.session_state.gone if k != key]
    st.session_state.mine = [k for k in st.session_state.mine if k != key]
    save_state()


# --------------------------------------------------------------- data

@st.cache_data(show_spinner="Loading player pool...")
def signals():
    return load_signals()


@st.cache_data(show_spinner="Scoring...")
def board(weight, goalie_weight):
    df, levels = build(weight=weight, goalie_weight=goalie_weight, df=signals())
    return df, levels


@st.cache_data(show_spinner="Reading your keepers from Fantrax...")
def my_keepers():
    """Whatever you already hold before a single pick is made."""
    try:
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        from fantrax_explore import raw_call
        from src.fantrax import default_league_id
        from src.valuation import ascii_name
        data = raw_call(default_league_id(), "getDraftResults")["responses"][0]["data"]
        by_id = {s["scorerId"]: s for s in data["scorers"]}
        teams = {t["id"]: t["name"] for t in data["fantasyTeamsOrdered"]}
        out = []
        for p in data["draftPicksOrdered"]:
            if p.get("scorerId") and teams.get(p["teamId"]) == MY_TEAM:
                s = by_id[p["scorerId"]]
                out.append({"key": ascii_name(s["name"]), "name": s["name"],
                            "position": s.get("posShortNames", "")})
        return pd.DataFrame(out)
    except Exception as exc:                          # offline, cookie expired
        st.sidebar.warning(f"Could not read keepers ({exc}). Add them by hand.")
        return pd.DataFrame(columns=["key", "name", "position"])


# --------------------------------------------------------------- controls

st.sidebar.header("Model")
weight = st.sidebar.slider(
    "ours  ←→  Fantrax", 0.0, 1.0, 0.5, 0.05,
    help="0 trusts last season's actual play only. 1 trusts Fantrax's "
         "projection only. ADP is never part of value.")
goalie_weight = st.sidebar.slider(
    "goalie emphasis", 0.5, 1.5, 1.0, 0.05,
    help="Positional replacement already prices goalie scarcity. This is a "
         "dial for the judgement on top of it.")

df, levels = board(weight, goalie_weight)

keepers = my_keepers()
for _, k in keepers.iterrows():
    take(k.key, mine=True)

gone = set(st.session_state.gone)
mine_keys = list(st.session_state.mine)

pos_of = dict(zip(df.key, df.position))
for _, k in keepers.iterrows():
    pos_of.setdefault(k.key, k.position)
name_of = dict(zip(df.key, df.name))
for _, k in keepers.iterrows():
    name_of.setdefault(k.key, k["name"])

roster = pd.DataFrame([{"key": k, "name": name_of.get(k, k),
                        "position": pos_of.get(k, "")} for k in mine_keys])
remaining = open_slots(roster) if len(roster) else open_slots(pd.DataFrame(columns=["position"]))
wanted = wanted_positions(remaining)

available = df[~df.key.isin(gone)]

st.sidebar.divider()
st.sidebar.header("Your roster")
if len(roster):
    for _, p in roster.iterrows():
        c1, c2 = st.sidebar.columns([4, 1])
        c1.write(f"**{p['name']}**  ·  {p.position}")
        if c2.button("✕", key=f"un_{p.key}", help="remove"):
            undo(p.key)
            st.rerun()
else:
    st.sidebar.caption("nothing yet")

st.sidebar.divider()
st.sidebar.caption(f"{len(gone)} players off the board · "
                   f"{len(available)} available")
if st.sidebar.button("Reset draft", type="secondary"):
    st.session_state.gone, st.session_state.mine = [], []
    save_state()
    st.rerun()


# --------------------------------------------------------------- header

st.title("Draft Night")

taken_count = len(gone)
next_pick = next((p for p in MY_PICKS if p > taken_count), None)

cols = st.columns(8)
order = ["C", "LW", "RW", "D", "G", "UTIL", "BENCH"]
for col, pos in zip(cols, order):
    n = remaining.get(pos, 0)
    col.metric(pos, n, help=f"{pos} slots still open")
cols[7].metric("next pick", next_pick if next_pick else "—",
               help="your next selection, by overall pick number")


# --------------------------------------------------------------- recommend

def row_controls(frame, key_prefix, limit):
    for _, r in frame.head(limit).iterrows():
        c = st.columns([1, 4, 2, 2, 2, 2, 2, 2])
        c[0].write(f"**{r.board_rank}**")
        flag = " ⚠︎" if r.projection_only else ""
        c[1].write(f"{r['name']}{flag}")
        c[2].write(str(r.position))
        c[3].write(f"{r.value:+.2f}")
        c[4].write("—" if pd.isna(r.adp) else f"{r.adp:.0f}")
        c[5].write("—" if pd.isna(r.edge) else f"{r.edge:+.0f}")
        if c[6].button("gone", key=f"{key_prefix}_g_{r.key}"):
            take(r.key, mine=False)
            st.rerun()
        if c[7].button("MINE", key=f"{key_prefix}_m_{r.key}", type="primary"):
            take(r.key, mine=True)
            st.rerun()


def header_row():
    c = st.columns([1, 4, 2, 2, 2, 2, 2, 2])
    for col, label in zip(c, ["#", "player", "pos", "value", "adp", "edge", "", ""]):
        col.caption(label)


fits = available[available.slot.isin(wanted)]

tab_rec, tab_all, tab_wait = st.tabs(
    ["Recommended", "Full board", "Will they last?"])

with tab_rec:
    if not wanted:
        st.success("Every slot is filled.")
    else:
        st.caption(f"Best available that fits an open slot "
                   f"({', '.join(sorted(wanted))}). ⚠︎ = no 2025-26 scrape, "
                   f"Fantrax projection only.")
        header_row()
        row_controls(fits, "rec", 15)

        blocked = available[~available.slot.isin(wanted) & available.slot.notna()]
        if len(blocked):
            b = blocked.iloc[0]
            st.info(f"Skipping **{b['name']}** ({b.slot}) — rates "
                    f"{b.value:+.2f} but you have no {b.slot} slot left.")

with tab_all:
    q = st.text_input("search", placeholder="type a name...", key="q")
    shown = available
    if q:
        shown = shown[shown.name.str.contains(q, case=False, na=False)]
    st.caption(f"{len(shown)} players")
    header_row()
    row_controls(shown, "all", 40)

with tab_wait:
    st.caption("Players whose ADP says they should still be there at your "
               "next pick — the ones you can afford to wait on.")
    if next_pick:
        later = fits[fits.adp >= next_pick].sort_values("value", ascending=False)
        st.write(f"Likely available at pick **{next_pick}**:")
        header_row()
        row_controls(later, "wait", 15)
    else:
        st.write("No picks left.")
