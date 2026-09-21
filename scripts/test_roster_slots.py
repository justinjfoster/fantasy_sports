#!/usr/bin/env python3
"""
Slot arithmetic for the draft board, checked against rosters we invent.

Rosters are empty until draft night, so the one case that matters most - the
board must stop offering goalies once both goalie slots are full - cannot be
observed from live data until it is too late to fix. These simulate it.

    python scripts/test_roster_slots.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from draft_board import MY_TEAM, SLOTS, UTIL, open_slots


def roster(*players):
    return pd.DataFrame([{'team': MY_TEAM, 'name': n, 'position': p}
                         for n, p in players])


SUZ = ('Nick Suzuki', 'C')

CASES = [
    ("keepers only", roster(SUZ),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2}),

    ("one goalie", roster(SUZ, ('Vasilevskiy', 'G')),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 1, 'UTIL': 2}),

    ("both goalie slots full", roster(SUZ, ('Vasilevskiy', 'G'), ('Thompson', 'G')),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 0, 'UTIL': 2}),

    # A third goalie cannot play anywhere: G is closed and utility is skaters
    # only, so nothing may go negative and no slot may reopen.
    ("a third goalie fits nowhere",
     roster(SUZ, ('Vasilevskiy', 'G'), ('Thompson', 'G'), ('Sorokin', 'G')),
     {'C': 1, 'LW': 2, 'RW': 2, 'D': 3, 'G': 0, 'UTIL': 2}),

    ("centres fill up", roster(SUZ, ('MacKinnon', 'C')),
     {'C': 0, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2}),

    # Dual-eligible players must land where there is room, not where they are
    # listed first.
    ("C,LW spills to LW once C is full",
     roster(SUZ, ('MacKinnon', 'C'), ('Draisaitl', 'C,LW')),
     {'C': 0, 'LW': 1, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 2}),

    ("skaters overflow into utility",
     roster(SUZ, ('MacKinnon', 'C'), ('Celebrini', 'C'), ('Eichel', 'C')),
     {'C': 0, 'LW': 2, 'RW': 2, 'D': 3, 'G': 2, 'UTIL': 0}),
]


def main():
    failed = 0
    for label, players, expected in CASES:
        actual = open_slots(players)
        ok = actual == expected
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
        if not ok:
            print(f"       expected {expected}")
            print(f"       actual   {actual}")

    total = sum(SLOTS.values()) + UTIL
    empty = open_slots(roster())
    if sum(empty.values()) != total:
        print(f"FAIL an empty roster should have all {total} starting slots open")
        failed += 1

    print(f"\n{len(CASES) + 1 - failed}/{len(CASES) + 1} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
