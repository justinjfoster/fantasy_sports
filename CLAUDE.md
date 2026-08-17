# CLAUDE.md

Claude Code reads this file automatically at the start of a session.

**Read [CONTEXT.md](CONTEXT.md) first.** It holds the working state of this
project: the league's settings, the data pipeline and the bugs already fixed in
it, the Fantrax integration, open questions, and what to build next.

Points that cause mistakes if missed:

- **There are two separate ranking systems** — ours from the Hockey-Reference
  scrape, and Fantrax's own from their projections. They disagree, and neither
  is wrong. Do not conflate them. See the comparison table in CONTEXT.md.
- **Parse Hockey-Reference by `data-stat` attribute, never by column index.**
  Doing it by index silently corrupted most categories once already.
- **This repository is public.** Never commit `fantraxloggedin.cookie`,
  `.fantrax_league`, or `data/fantrax_player_pool.csv`.
- **On Windows, run `.\.venv\Scripts\python.exe` directly.** Do not route
  through `Activate.ps1`; the execution policy is `Restricted`.
