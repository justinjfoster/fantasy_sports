# Project Context

Working state of this project, written to pick things up cleanly in a later
session or on the other machine. Last updated **2026-08-16**.

`README.md` explains how to *use* the tool. This file explains *where things
stand and why*, including decisions that are not obvious from the code.

---

## The goal

Build a draft board for a fantasy hockey pool. Two independent data sources
feed it: historical NHL performance scraped from Hockey-Reference, and live
league state pulled from Fantrax.

## The league

**The Shore** — moved from Yahoo to Fantrax for 2026-27.

- 6 teams. Season runs 2026-09-29 to 2027-04-10. **Draft has not happened yet.**
- Head-to-head, **all categories weighted equally**
- Skater categories (7): Goals, Assists, Power Play Points, Shots on Goal,
  **Faceoffs Won**, Hits, Blocks
- Goalie categories (4): Wins, GAA, Saves, Save Percentage
- Roster: 2C, 2LW, 2RW, 3D, 2 utility, 2G — 13 starting slots, confirmed
  against the Fantrax API — plus 4 bench

**Open question:** is this redraft or keeper/dynasty? It changes how to read
ADP on prospects entirely, and has not been established.

---

## Two separate ranking systems — do not conflate them

This has caused confusion once already. There are two, they disagree, and
neither is wrong.

|  | **Ours** | **Fantrax's** |
|---|---|---|
| File | `rankings/equal_weight_skater_rankings_2026.csv` | `data/fantrax_player_pool.csv` (gitignored) |
| Source | Hockey-Reference scrape | Fantrax's own projections |
| Computed by | our scripts in `scripts/` | **Fantrax** — we only read the column |
| Measures | what players **actually did**, 2023-2026 | what Fantrax **predicts** for 2026-27 |
| Players | 940 skaters | 7,514 |
| Top 3 | Zibanejad, Stützle, Suzuki | MacKinnon, McDavid, Celebrini |

The clearest illustration: **Gavin McKenna is absent from our system entirely.**
He has never played an NHL game, so Hockey-Reference has nothing to scrape.
Fantrax still ranks him 326th, because their rank is a forecast.

A third signal, distinct from both: **ADP** is not a value measure at all. It
says *when a player will be gone*, under other leagues' scoring rules.

---

## Data pipeline

### Hockey-Reference scraper

`src/hockey_reference_scraper.py` → `collect_multi_year_data.py` → `data/`

```bash
python collect_multi_year_data.py 2023 2024 2025 2026
```

Hockey-Reference labels a season by the year it **ends**: `2026` is 2025-26.

Current data: `data/skater_data_2023_2026.csv` (4,141 rows),
`data/goalie_data_2023_2026.csv` (406 rows), both deduplicated.

**Hard-won lessons — do not regress these:**

1. **Parse by `data-stat` attribute, never by column index.** The original
   scraper used hardcoded positions and silently mapped most categories to the
   wrong statistic: only 2 of 7 skater categories and 3 of 4 goalie categories
   were correct. `hits` was never captured at all; goalie `saves` and
   `shots_against` were swapped. The `data-stat` names are stable (verified
   byte-identical on the 2023 and 2026 pages); the positions are not.
2. **Hockey-Reference publishes no PPP or SHP column.** Both must be computed
   as goals + assists. Grabbing a neighbouring column is what caused the
   original bug.
3. **Hockey-Reference lists goalies on the skater page** (~100/season). Filter
   `position != 'G'` before ranking skaters — `src/rankings_data.py` does this.
4. **Validate every scrape with two identities** that catch column shifts
   instantly: `G + A == PTS` for skaters, `SA - SV == GA` for goalies.
5. **Deduplicate traded players** by keeping only the combined `2TM`/`3TM` row.
   But never dedupe on name alone: there are genuinely two Elias Petterssons,
   two Sebastian Ahos and two Matt Murrays in the data.

### Ranking scripts

All load through `src/rankings_data.py`, which selects one season and drops
goalies from the skater table. **Change `LATEST_SEASON` there to retarget every
script at once.**

- `scripts/equal_weight_rankings.py` — the main one; percentile, z-score,
  normalized and position-adjusted systems
- `scripts/equal_weight_goalie_rankings.py`
- `scripts/rank_players_2025.py` — name is stale, it follows `LATEST_SEASON`
- `scripts/alternative_rankings.py`, `scripts/recommended_rankings.py` — print
  comparisons, write no files

**Unresolved modelling choice:** the percentile system rewards breadth over
peak value, so McDavid falls outside its top 20 despite a 138-point season
while well-rounded players top it. The z-score system ranks him 1st. Which to
draft from has not been decided. Compare with `alternative_rankings.py`.

### Fantrax

See **[FANTRAX.md](FANTRAX.md)** for the full walkthrough. Summary:

- **No official API.** One undocumented endpoint, `POST /fxpa/req`, authenticated
  by **session cookie** rather than a token.
- `scripts/fantrax_login.py` once, then `scripts/fantrax_explore.py` and
  `scripts/fantrax_player_pool.py`.
- `getPlayerStats` is the valuable endpoint: the full pool with **ADP**,
  percent drafted, a league-tailored `score`, and Fantrax's projections in our
  exact categories. There is no standalone ADP method.
- Its stats are **projections, not past performance** — which is why players
  with no NHL history still carry a rank.

---

## The main finding so far

**Face-off specialists are systematically underdrafted in this league.**

Fantrax's ADP is averaged across all their leagues, most of which do not count
faceoffs. Ours does. From the 2026-08-16 pull:

| Player | ADP | Fantrax rank | Projected FOW |
|---|---|---|---|
| Jordan Staal | 290.6 | 126 | 838 |
| Chandler Stephenson | 290.5 | 158 | 738 |
| Elias Lindholm | 239.1 | 102 | 692 |
| Alexander Wennberg | 285.2 | 134 | 637 |

The mirror image, drafted 150-250 picks *earlier* than they rank here, is hyped
young wingers and defensemen projected for **zero** faceoff wins: Demidov
(ADP 95 / rank 344), Byram (104 / 352), McKenna (115 / 326), Clarke (79 / 256).

Our own percentile rankings independently reach the same conclusion from
different data: face-off volume dominates them.

---

## Environment

Python 3.14, `.venv` in the repo root (self-ignoring). `pip install -r requirements.txt`,
plus `selenium webdriver-manager` for the Fantrax login.

**On Windows, call the venv's Python directly:**

```powershell
cd C:\Users\Justi\Documents\coding\fantasy_sports
.\.venv\Scripts\python.exe scripts\fantrax_player_pool.py
```

- The `.\` prefix is required. A bare `.venv\Scripts\python.exe` fails with
  `The module '.venv' could not be loaded`, because PowerShell reads a leading
  `.` as the dot-sourcing operator.
- **Do not use `Activate.ps1`** — the default execution policy is `Restricted`
  and it fails. Calling `python.exe` directly needs no policy change.
- `Get-ExecutionPolicy` alone reports the *process* scope and can look
  permissive; use `Get-ExecutionPolicy -List`.

On macOS, `source .venv/bin/activate` works normally.

---

## This repository is public

Three things are deliberately kept out of it, all gitignored:

| File | Why |
|---|---|
| `fantraxloggedin.cookie` | Session credentials. Anyone holding it can act as the account. Never commit or sync between machines — re-run the login on each. |
| `.fantrax_league` | The league id. Read via `FANTRAX_LEAGUE_ID` or this file. |
| `data/fantrax_player_pool.csv` | Fantrax's proprietary projections and aggregate ADP. Regenerate rather than redistribute. |

---

## Known broken / not done

- **`analyze_your_league.py` does not run.** It reads a SQLite database built by
  `archive/sample_data.py` that was never committed (`databases/` is
  gitignored). It sits on an abandoned SQLite code path, unrelated to the
  scraper work.
- **2022 was not backfilled.** Data covers 2023-2026.
- **No combined draft board yet.** This is the obvious next build: join our
  rankings, Fantrax's projected rank/score, and ADP into one table, so agreement
  between the two independent sources signals confidence and divergence flags
  players worth a look — sorted by when each will actually be available.
- **Rosters are empty** until the draft, so roster-aware filtering (rank only
  players not already taken) cannot be tested yet.

---

## Next steps

1. Establish whether the league is redraft or keeper — it gates how prospects
   are treated.
2. Decide between percentile and z-score as the primary ranking.
3. Build the combined draft board.
4. Re-pull the Fantrax pool closer to the draft; ADP moves.
