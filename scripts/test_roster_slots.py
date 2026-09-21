#!/usr/bin/env python3
"""
Slot arithmetic for the draft board, checked against rosters we invent.

Rosters are empty until draft night, so the cases that matter most - the board
must stop offering goalies once both goalie slots are full, and must not let
the bench quietly reopen them - cannot be observed from live data until it is
too late to fix. These simulate them.

    python scripts/test_roster_slots.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.valuation import BENCH, SLOTS, UTIL, open_slots, wanted_positions


def roster(*positions):
    return pd.DataFrame([{'position': p} for p in positions])


SLOT_CASES = [
    ("empty", roster(),
     {'C': 2, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2, 'BENCH': 4}),

    ("one keeper at C", roster('C'),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2, 'BENCH': 4}),

    ("both goalie slots full", roster('C', 'G', 'G'),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 0, 'UTIL': 2, 'BENCH': 4}),

    # A third goalie has no starting slot and utility is skaters only, so he
    # falls to the bench. Nothing may go negative, nothing may reopen.
    ("a third goalie goes to the bench", roster('C', 'G', 'G', 'G'),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 0, 'UTIL': 2, 'BENCH': 3}),

    ("centres fill up", roster('C', 'C'),
     {'C': 0, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2, 'BENCH': 4}),

    # Dual-eligible players must land where there is room, not where they are
    # listed first.
    ("C,LW spills to LW once C is full", roster('C', 'C', 'C,LW'),
     {'C': 0, 'LW': 1, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2, 'BENCH': 4}),

    ("skaters overflow into utility", roster('C', 'C', 'C', 'C'),
     {'C': 0, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 0, 'BENCH': 4}),
]

# The bench is open for almost the whole draft. If it counted toward what we
# recommend, every position would be wanted at every pick and the roster
# constraint would mean nothing.
WANTED_CASES = [
    ("goalies offered while G is open", roster('C'), True),
    ("goalies NOT offered once G is full", roster('C', 'G', 'G'), False),
    ("goalies offered again once every starter is filled",
     roster('C', 'C', 'LW', 'LW', 'RW', 'RW', 'D', 'D', 'D', 'G', 'G', 'C', 'LW'),
     True),
]


def main():
    failed = 0

    for label, players, expected in SLOT_CASES:
        actual = open_slots(players)
        ok = actual == expected
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
        if not ok:
            print(f"       expected {expected}")
            print(f"       actual   {actual}")

    for label, players, goalie_expected in WANTED_CASES:
        wanted = wanted_positions(open_slots(players))
        ok = ('G' in wanted) == goalie_expected
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
        if not ok:
            print(f"       wanted {sorted(wanted)}, G expected {goalie_expected}")

    total = len(SLOT_CASES) + len(WANTED_CASES)
    print(f"\n{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
