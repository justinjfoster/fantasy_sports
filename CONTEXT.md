# Project Context

Working state of this project, written to pick things up cleanly in a later
session or on the other machine. Last updated **2026-09-21**.

`README.md` explains how to *use* the tool. This file explains *where things
stand and why*, including decisions that are not obvious from the code.

---

## The goal

Build a draft board for a fantasy hockey pool. Two independent data sources
feed it: historical NHL performance scraped from Hockey-Reference, and live
league state pulled from Fantrax.

## The league

**The Shore** — moved from Yahoo to Fantrax for 2026-27.

- **12 teams.** Season runs 2026-09-29 to 2027-04-10.
- **Draft: 2026-09-28, 8:45 PM local.** Snake, 17 rounds, 204 total picks.
  Justin drafts **8th**. (The draft timestamp sits 3h15m before the season
  start, which may be a Fantrax default rather than a set date — worth
  confirming with the commissioner.)
- Head-to-head, **all categories weighted equally**
- Skater categories (7): Goals, Assists, Power Play Points, Shots on Goal,
  **Faceoffs Won**, Hits, Blocks
- Goalie categories (4): Wins, GAA, Saves, Save Percentage
- Roster: 2C, 2LW, 2RW, 3D, 2 utility, 2G — 13 starting slots, confirmed
  against the Fantrax API — plus 4 bench. **204 roster spots league-wide**,
  which is also the replacement-level cutoff (see below).

**Pick trades:** Justin's picks are not the standard snake slots. He has **no
5th-round pick** and holds **two 13th-rounders** (13.6 and 13.8). Every team
holds 17 picks in total, before keepers consume any.

**Justin's 16 usable overall picks** (R2.5/pick 17 is spent on Suzuki):

```
8, 32, 41, 65, 80, 89, 104, 113, 128, 137, 150, 152, 161, 176, 185, 200
```

Read them live rather than trusting this list — `getDraftResults` marks a
consumed pick by attaching a `scorerId` to it.

### Keeper rules

Settled 2026-09-10. It is a keeper league with a **one-season** horizon, so a
keeper is valued purely on coming-season production.

- **Keeping costs a draft pick.** The kept player is pre-assigned into a
  specific round — the round he was drafted in last season. Undrafted players
  (waiver pickups) appear to cost a last-round (17th) pick.
- **A player kept last season cannot be kept again.**
- **1st-round picks cannot be kept.**
- **Only one player drafted in rounds 1-3 may be kept**, and per Justin this
  is exclusive with keeping others.
- **The cap is 3 keepers.** Confirmed 2026-09-21 once all 12 teams declared:
  nine kept three, none kept more.

**Settled: Justin kept Nick Suzuki only**, registered at R2.5 (overall pick
17). The analysis below backed this — keeping exactly one scored highest —
and the deadline forced it before the roster-aware work was done.

**This is the season's structural edge.** A keeper consumes a pick, so the
nine teams that kept three draft 14 players while Justin drafts **16**. Two
extra swings in a draft where ADP is badly mispriced against this league's
categories.

Read the league's declared keepers straight from the API: in `getDraftResults`,
a pick carrying a `scorerId` is a keeper, and the round it sits in is its cost.

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
6. **Strip accents before joining to Fantrax.** Hockey-Reference stores names
   with diacritics (`Martin Nečas`, `Tomáš Hertl`, `David Pastrňák`,
   `Tim Stützle`); Fantrax stores ASCII. **41 of 1038 skaters (3.9%)** are
   affected and they are not marginal players. A naive name join drops them
   silently — the row is simply absent, not wrong. Normalize both sides with
   `unicodedata.normalize("NFD", s)` and drop combining marks.

### Goalie rankings (second generation)

`scripts/goalie_rankings_v2.py` supersedes `equal_weight_goalie_rankings.py`
for decisions. The old script's category handling is correct — GAA is properly
inverted — but it ranks over the wrong population:

- **It applies no minimum games filter.** 21 of the 98 scraped goalies played
  fewer than five games, and they hold the best save percentages and GAAs in
  the league on one- and two-game samples. They cannot be rostered, but they
  sit atop two of the four categories and compress the scale every real
  starter is measured against. v2 defaults to `--min-games 25`, which leaves 59.
- It also carries the `--boost` magnitude blend described above. **The boost
  barely moves goalies** — four categories, no extreme skew — so it is a
  skater-side fix. Ranks shift by at most a place or two across the full
  0-to-1 range.

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

**Decided 2026-09-10: percentile is the primary system**, because every
category is weighted equally and percentile is scale-free across categories
whose distributions look nothing alike (faceoffs vs blocks).

Its known weakness is that it is **purely ordinal** — finishing first in
assists scores 100 whether you won by one or by thirty. That is why McDavid
falls outside its top 20 on a 138-point season while the z-score system ranks
him 1st. The agreed fix is **not** to switch to z-score, which over-corrects on
right-skewed categories like hits and faceoffs, but to add a **magnitude
boost**: score each category as a winsorized z-score (clipped at ±3) mapped
through the normal CDF back onto 0-100, then blend it with the ordinal
percentile on a tunable weight.

**Both sides now implement this** — `scripts/skater_rankings_v2.py` (built
2026-09-21) and `scripts/goalie_rankings_v2.py`, each with `--boost`
(0 = ordinal, 1 = fully magnitude-aware, default 0.5) and `--min-games`.

**What the boost actually did, and its ceiling.** McDavid moves from 22nd to
16th across the full boost range:

| boost | 0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|
| McDavid | 22 | 20 | 19 | 18 | 16 |

He cannot climb further at any setting, and the reason is worth not
rediscovering: **both scales cap at 100 per category.** His 48G / 90A /
306 SOG earns nothing beyond winning those categories, while 40 hits and 30
blocks stay near the floor.

That ceiling is **arguably correct for head-to-head categories**: a category
won 90-40 scores exactly what one won 45-44 does, so production beyond
"clearly winning" is genuinely wasted. The boost therefore redistributes
within the range rather than rewarding dominance without limit. If a future
session wants dominance to pay without bound, that is a deliberate departure
from how the league actually scores, not a bug to fix.

Recommended setting: **0.5**.

### The combined draft board

`scripts/draft_board.py` — built 2026-09-21, and the thing to actually use on
draft day. It joins the three signals this file has insisted on keeping
separate, and the disagreements between them are the product:

- **ours** — what a player did last season, scored in this league's exact
  categories, from the v2 ranking files
- **fantrax** — Fantrax's projection for the coming season, already tailored
  to the league's scoring
- **adp** — when he actually goes, across all Fantrax leagues

It removes every declared keeper (read live from `getDraftResults`), sets
**replacement = the 205th best available** (12 teams × 17 roster spots), and
reports `vor` (value over replacement) beside `edge` (`adp − rank`, so
positive means he falls later than he rates and you can wait on him).

```powershell
.\.venv\Scripts\python.exe scripts\draft_board.py
.\.venv\Scripts\python.exe scripts\draft_board.py --pick 32   # who lasts to your pick
.\.venv\Scripts\python.exe scripts\draft_board.py --pos G
```

Writes `data/draft_board.csv`, which is **gitignored** — it carries the same
proprietary Fantrax projections the player pool does.

**Two join traps it handles, both of which bit first:**

1. Accented names, as documented above.
2. **A name can belong to two different real players.** Vancouver has an Elias
   Pettersson who is a centre and an Elias Pettersson who is a defenceman; the
   rankings separate them by 450 places. A name-only join handed the
   defenceman the centre's value and floated him onto the board as a bargain.
   Duplicated names are now matched on **position** as well. Any future join
   against this data needs the same care.

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
- **`getPlayerStats` needs three calls to give you everyone *with* their
  projections.** `positionOrGroup` takes an id from the response's own
  `posOrGroupList`, and the value matters: an unrecognised one like `"ALL"`
  returns the full pool with **no stat columns for anybody**, while
  `HOCKEY_SKATING` and `POS_201` each return one group with its own
  categories. Omitting the key gives skaters only — which is why Jakub Dobes
  was missing from the first keeper analysis.
- **`rank` is relative to the view.** Skater view gives the overall rank;
  goalie view restarts at 1 and counts goalies only. Take `rank` from the
  pool view and join categories on `scorer_id`. `score` is the one column
  that is identical everywhere.
- **The pool excludes kept players** by default (`ALL_AVAILABLE`). Pass
  `statusOrTeamFilter="ALL"` to see them; `searchName` prices one player.
- Other methods that answer real questions: `getDraftResults` (draft type,
  order, every pick, and the declared keepers), `getFantasyLeagueInfo`
  (`draftDate`, season bounds, roster positions). `getLeagueRules`,
  `getDraftSettings` and `getKeepers` all return `ERROR_INVALID_REQUEST` —
  keeper *rules* are not exposed, only their consequences.

---

## The main findings

Both are the same mechanism: **Fantrax's ADP is averaged across all their
leagues, and this league's categories are not the Fantrax-wide norm.** Where
the category set diverges, the market misprices, and that gap is the edge.

### 1. Goalies are the biggest mispricing (found 2026-09-21)

**Four of the league's eleven categories are goalie categories** — W, GAA,
SV, SV% — but ADP averages across leagues that weight goalies far less. From
the 2026-09-21 board:

| Goalie | Fantrax rank | ADP | Gap |
|---|---|---|---|
| Andrei Vasilevskiy | 1 | 53 | +52 |
| Logan Thompson | 7 | 77 | +70 |
| Igor Shesterkin | 16 | 97 | +81 |
| Karel Vejmelka | 9 | 108 | +99 |
| Dustin Wolf | 22 | 193 | **+171** |

Seven goalies were kept, so supply is thinner than the raw pool suggests.
Note the constraint the board does not enforce: **only 2 goalies start**, so
value stacking beyond two is wasted.

### 2. Face-off specialists are systematically underdrafted

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

The mirror of both findings: players whose value sits in categories this
league does **not** count, or who are hyped on name alone, go far earlier
than they rate here.

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

- **The draft board is greedy on value and ignores roster construction.** It
  ranks best-available and does not know the roster is 2C / 2LW / 2RW / 3D /
  2 UTIL / 2G. Taking its top three straight would stack three goalies into
  two starting slots. **This is the next job.**
- **`analyze_your_league.py` does not run.** It reads a SQLite database built by
  `archive/sample_data.py` that was never committed (`databases/` is
  gitignored). It sits on an abandoned SQLite code path, unrelated to the
  scraper work.
- **2022 was not backfilled.** Data covers 2023-2026.
- **Rosters are empty** until the draft, so roster-aware filtering (rank only
  players not already taken) cannot be tested yet.
- The first-generation scripts (`equal_weight_rankings.py`,
  `equal_weight_goalie_rankings.py`) are superseded by the v2 pair for
  decisions, but are left in place — they are what the older rankings files
  in `rankings/` were built from.

---

## Valuing a keeper, or a pick

Worked out 2026-09-10 and worth not re-deriving. Two mistakes are easy here and
both were made before the method settled:

1. **Do not score a keeper as `pick number − overall rank`.** That treats ranks
   as interchangeable across positions. Goalie is deep relative to how many
   start: 24 goalies project better than Jakub Dobes and the league rosters
   exactly 24, so he is almost exactly replacement level despite an overall
   rank near 59.
2. **Do not value a draft pick against zero.** The draft is only 204 picks, so
   anyone with an ADP past that goes undrafted and is free on waivers. A late
   pick is worth only what it returns *above* that.

The method that survives both: rank every available player on one scale, set
**replacement = the 205th best** (12 teams × 17 spots), and score each option
as the summed value-above-replacement of the players it ends up with — keepers
plus whatever the remaining picks are expected to return. Compare options with
the same number of roster spots filled.

Applied to the 2026-27 keeper decision it says: **keep exactly one player.**
Marginal keepers are worth less than the picks they consume, because ADP
misprices this league badly enough that late picks still return real value.
Suzuki and Hertl score within a point of each other; Dobes scores *below*
replacement. Both our percentile system and Fantrax's own projections agree on
the shape of this, which is the main reason to trust it.

---

## Picking this up on the other machine

The repo carries the code and the rankings, but **three files are gitignored
and will not travel.** On a fresh clone or pull:

```bash
# 1. the session cookie is per-machine and must be re-created
python scripts/fantrax_login.py

# 2. the league id is not in the public repo
echo "<league id from the Fantrax URL>" > .fantrax_league
#    or set FANTRAX_LEAGUE_ID in the environment

# 3. regenerate the two derived CSVs (both need a live login)
python scripts/fantrax_player_pool.py --limit 600
python scripts/draft_board.py
```

The Hockey-Reference data (`data/skater_data_2023_2026.csv`,
`data/goalie_data_2023_2026.csv`) and the `rankings/` files **are** committed,
so no re-scrape is needed. On macOS `source .venv/bin/activate` works
normally; the Windows notes in Environment do not apply.

---

## Next steps

1. **Make the draft board roster-aware.** It should respect 2C / 2LW / 2RW /
   3D / 2 UTIL / 2G and stop recommending a third goalie. This is the one
   thing standing between the board and being usable as-is on draft night.
2. **Re-pull the pool in the last day or two before the draft.** ADP moves,
   and it has already moved measurably between 2026-08-16 and 2026-09-21.
3. Confirm with the commissioner: the exact wording of the rounds-1-3 keeper
   rule, and whether the 2026-09-28 20:45 draft time is real or a Fantrax
   default. (The keeper cap is now confirmed at 3 and needs no asking.)
4. During the draft, re-run `draft_board.py` between picks — it reads keepers
   and rosters live, so it reflects who is actually gone.
