# Connecting to Fantrax

Notes and tooling for pulling your league's data out of Fantrax, now that the
league has moved off Yahoo.

## The short version

**Fantrax has no official public API.** There is no developer portal, no API
key, no documented endpoints, and no support if it breaks. What exists is the
private JSON endpoint the Fantrax website itself calls, which the community
has reverse-engineered:

```
POST https://www.fantrax.com/fxpa/req?leagueId=<league_id>
Content-Type: application/json

{"msgs": [{"method": "getStandings", "data": {"leagueId": "<league_id>"}}]}
```

Every operation goes through that one URL. The `method` name selects what you
get back.

**Authentication is by session cookie, not by API key.** There is no way to
read a private league without logging in as a real user first. That is the
only genuinely fiddly part of the setup, and the steps below deal with it.

Confirmed working as of August 2026: the endpoint is live and returns
structured JSON, including a clear `NOT_MEMBER_OF_LEAGUE` error when you are
not authenticated for the league you asked for.

## Setup

### 1. Install

```bash
pip install -r requirements.txt          # includes fantraxapi
pip install selenium webdriver-manager   # only for the automated login below
```

We use [`fantraxapi`](https://github.com/meisnate12/FantraxAPI), an unofficial
wrapper. Worth knowing: its author built and tested it against an **NHL**
league, so hockey is the best-supported case.

### 2. Configure your league ID

Open your league on Fantrax and look at the URL:

```
https://www.fantrax.com/fantasy/league/abcd1234efgh5678/home
                                       ^^^^^^^^^^^^^^^^
                                       this is your league ID
```

**This repository is public**, so the league ID is kept out of it. Store it in
either place — both are gitignored:

```bash
# a one-line file in the repo root
echo abcd1234efgh5678 > .fantrax_league

# or an environment variable
export FANTRAX_LEAGUE_ID=abcd1234efgh5678     # macOS
setx FANTRAX_LEAGUE_ID abcd1234efgh5678       # Windows
```

With either set, the scripts take no arguments. You can still pass a league ID
explicitly to override it.

### 3. Log in once

```bash
python scripts/fantrax_login.py
```

A browser window opens on the Fantrax login page. Sign in normally — including
any two-factor step — then press Enter in the terminal. Your session cookies
are saved to `fantraxloggedin.cookie`.

**Your password is never read, stored, or seen by this code.** You type it into
Fantrax's own page. Only the resulting cookies are saved.

The cookie file is gitignored, and you should treat it like a password: anyone
who has it can act as you on Fantrax. Do not commit it, and do not sync it to
the other machine — just run the login again there.

### 4. Look around

```bash
python scripts/fantrax_explore.py
```

Prints teams, standings, a roster, and recent transactions.

## Manual login (no Selenium)

If you would rather not install Selenium, or the automated login breaks:

1. Log in to Fantrax in Chrome.
2. Open DevTools (F12) → **Application** tab → **Cookies** → `https://www.fantrax.com`.
3. Copy the value of the `JSESSIONID` cookie (and `uig` if present).
4. Run this once:

```python
import sys
sys.path.insert(0, '.')
from src.fantrax import save_cookies

save_cookies([
    {"name": "JSESSIONID", "value": "PASTE_VALUE_HERE", "domain": ".fantrax.com"},
    {"name": "uig",        "value": "PASTE_VALUE_HERE", "domain": ".fantrax.com"},
])
```

## Using it from your own code

```python
from src.fantrax import connect

league = connect("abcd1234efgh5678")

print(league.name, league.year)

for team in league.teams:
    print(team)

standings = league.standings()
for rank in standings.ranks.values():
    print(rank)
```

## Discovering more endpoints

The wrapper only implements a handful of methods:

| Method | What it returns |
|---|---|
| `getFantasyLeagueInfo` | League settings, positions, scoring periods |
| `getStandings` | Standings and records |
| `getTeamRosterInfo` | A team's roster |
| `getLiveScoringStats` | Live matchup scoring |
| `getTransactionDetailsHistory` | Add/drop/trade history |
| `getPendingTransactions` | Pending claims |
| `getTradeBlocks` | Trade block (needs auth) |
| `getRefObject` | Reference data (players, teams) |

Fantrax's site uses many more. To find them: open your league in Chrome with
DevTools on the **Network** tab, click around the UI, and watch the requests to
`/fxpa/req`. Each request payload contains the `method` name. Then call it
directly:

```python
from scripts.fantrax_explore import raw_call

data = raw_call("abcd1234efgh5678", "getStandings")
print(data)
```

`raw_call` returns the parsed JSON untouched, so it works for any method,
including ones the wrapper does not know about.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `No cookie file at ...` | Run `python scripts/fantrax_login.py` |
| `NotLoggedIn: Not Logged in` | Cookies expired; log in again |
| `NotMemberOfLeague` | Wrong league ID, **or** the saved cookies belong to an account that is not in that league |
| `Invalid JSON Response` | Fantrax returned an HTML error page, usually rate limiting — wait and retry |
| Selenium cannot find Chrome | `pip install webdriver-manager`, or use the manual cookie steps above |

## Caveats worth knowing up front

- **This can break without warning.** It is an undocumented internal endpoint.
  Fantrax owes no stability guarantees and may change or block it.
- **Be gentle.** This is the same backend serving their website. Do not poll in
  a tight loop; cache what you pull.
- **Not every league type is equally supported.** The wrapper was built against
  an NHL H2H *points* league. Ours is H2H *categories*, so some objects may come
  back shaped differently or empty. `raw_call` is the fallback when a wrapper
  method does not fit.
- **Check the terms of service** before doing anything heavier than reading your
  own league.

## How this fits the rest of the repo

The scraper in `src/hockey_reference_scraper.py` supplies *historical NHL
performance* — the raw material for the draft rankings. Fantrax supplies *your
league's state*: rosters, standings, who is on waivers, what has been traded.

The interesting combination is joining them: rank the available player pool by
`rankings/equal_weight_skater_rankings_2026.csv` while filtering out everyone
already rostered in your league. Nothing in the repo does that yet.
