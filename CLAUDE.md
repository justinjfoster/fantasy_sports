# CLAUDE.md

Claude Code reads this file automatically at the start of a session.

**Read [CONTEXT.md](CONTEXT.md) first.** It holds the working state: the
league's settings and keeper rules, the data pipeline and the bugs already
fixed in it, the Fantrax integration, the findings so far, and what to build
next. This file is only the short list of things that cause real mistakes.

## Time-critical

**The draft is 2026-09-28, 20:45 local.** Work is being done against that
deadline. ADP moves in the final days — re-pull the pool before relying on it.

## Never commit

This repository is **public**. Four files are gitignored and must stay that
way:

| File | Why |
|---|---|
| `fantraxloggedin.cookie` | Session credentials — anyone holding it can act as the account |
| `.fantrax_league` | The league id |
| `data/fantrax_player_pool.csv` | Fantrax's proprietary projections and ADP |
| `data/draft_board.csv` | Built from that same proprietary data |

The cookie is **per-machine**. Never copy it between the Windows desktop and
the Mac — re-run `scripts/fantrax_login.py` on each.

## Use the v2 ranking scripts

`scripts/skater_rankings_v2.py` and `scripts/goalie_rankings_v2.py` supersede
the `equal_weight_*` pair for any decision. The originals are kept only
because the older files in `rankings/` were built from them.

The v2 scripts add a games-played floor and a `--boost` magnitude blend.
**The 100-per-category ceiling is deliberate** — in head-to-head categories a
category won 90-40 scores what one won 45-44 does. Do not "fix" it without
reading the reasoning in CONTEXT.md.

## Joining player data silently drops and mismatches rows

Every join between Hockey-Reference and Fantrax has to handle both of these.
Neither fails loudly:

1. **Accents.** Hockey-Reference writes `Nečas`, `Hertl`, `Pastrňák`,
   `Stützle`; Fantrax writes ASCII. 41 of 1038 skaters are affected. Normalize
   with `unicodedata.normalize("NFD", s)` and drop combining marks.
2. **A name can be two different real players.** Vancouver has an Elias
   Pettersson at C and another at D, 450 rank places apart. Match duplicated
   names on **position** as well — `scripts/draft_board.py` shows the pattern.

## Two separate ranking systems — do not conflate them

Ours is backward-looking, from the Hockey-Reference scrape. Fantrax's is a
forward projection. They disagree, and neither is wrong. See the comparison
table in CONTEXT.md.

## Scraping

**Parse Hockey-Reference by `data-stat` attribute, never by column index.**
Doing it by index silently corrupted most categories once already.

## Running Python

On **Windows**, call the venv's interpreter directly — do not route through
`Activate.ps1`, as the execution policy is `Restricted`:

```powershell
.\.venv\Scripts\python.exe scripts\draft_board.py
```

The leading `.\` is required. On **macOS**, `source .venv/bin/activate` works
normally and none of the above applies.
