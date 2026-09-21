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
                           keepers, load_signals, open_slots, positions_of,
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


@st.cache_data(show_spinner="Reading keepers from Fantrax...")
def all_keepers():
    """
    Every player already locked up league-wide, not just yours.

    The pool now contains kept players so they can be priced, so the board has
    to remove other teams' keepers itself rather than letting the endpoint do
    it. Yours go onto your roster; everyone else's just come off the board.
    """
    try:
        return keepers()
    except Exception as exc:                          # offline, cookie expired
        st.sidebar.warning(f"Could not read keepers ({exc}). Mark them by hand.")
        return pd.DataFrame(columns=["key", "name", "team", "position", "round"])


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

kept = all_keepers()
for _, k in kept.iterrows():
    take(k.key, mine=(k.team == MY_TEAM))

gone = set(st.session_state.gone)
mine_keys = list(st.session_state.mine)

pos_of = dict(zip(df.key, df.position))
name_of = dict(zip(df.key, df.name))
rank_of = dict(zip(df.key, df.board_rank))
value_of = dict(zip(df.key, df.value))
adp_of = dict(zip(df.key, df.adp))
for _, k in kept.iterrows():
    pos_of.setdefault(k.key, k.position)
    name_of.setdefault(k.key, k["name"])

roster = pd.DataFrame([{"key": k, "name": name_of.get(k, k),
                        "position": pos_of.get(k, "")} for k in mine_keys])
remaining = open_slots(roster) if len(roster) else open_slots(pd.DataFrame(columns=["position"]))
wanted = wanted_positions(remaining)

available = df[~df.key.isin(gone)]

st.sidebar.divider()
st.sidebar.header("Your roster")
if len(roster):
    total = 0.0
    for n, p in enumerate(roster.itertuples(), start=1):
        rk = rank_of.get(p.key)
        val = value_of.get(p.key)
        adp = adp_of.get(p.key)
        if val is not None and val == val:
            total += float(val)
        c1, c2 = st.sidebar.columns([5, 1])
        # Where he ranked on the board against where the market had him: a
        # positive steal means you got him later than he rates.
        steal = ""
        if rk is not None and adp is not None and adp == adp:
            steal = f" · steal {adp - rk:+.0f}"
        head = f"**{p.name}**  ·  {p.position}"
        body = (f"#{int(rk)}  ·  {float(val):+.2f}{steal}"
                if rk is not None and val is not None and val == val
                else "not on the board")
        c1.markdown(f"{head}  \n<span style='opacity:.65;font-size:.85em'>"
                    f"{n}. {body}</span>", unsafe_allow_html=True)
        if c2.button("✕", key=f"un_{p.key}", help="remove"):
            undo(p.key)
            st.rerun()
    st.sidebar.metric("roster value", f"{total:+.2f}",
                      help="Summed value-over-replacement of everyone you "
                           "hold. Higher is better; it is only comparable "
                           "against the same blend weight.")
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

# Your next pick is simply the next unused entry in MY_PICKS. It cannot be
# derived from how many players are off the board: the 32 keepers sit at
# reserved slots scattered through the draft rather than consuming the first
# 32 picks, so counting them as picks made jumps you straight to the 4th round
# before a single selection has happened.
keeper_keys = set(kept.key)
my_drafted = [k for k in mine_keys if k not in keeper_keys]
next_pick = (MY_PICKS[len(my_drafted)]
             if len(my_drafted) < len(MY_PICKS) else None)

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
