"""
Fantrax connection helper.

Fantrax publishes no official API. Everything below talks to the same
undocumented endpoint the website itself uses:

    POST https://www.fantrax.com/fxpa/req?leagueId=<league_id>
    {"msgs": [{"method": "getStandings", "data": {"leagueId": "<league_id>"}}]}

Requests are authenticated by session cookie, not by an API key or token, so
there is no way to reach a private league without first logging in as a real
user. This module keeps that login out of the code: you log in once, the
cookies are saved to disk, and every later run reuses them.

See FANTRAX.md for the full walkthrough.
"""

import os
import pickle
from typing import Optional

from requests import Session

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cookie jar produced by log_in_and_save_cookies(). Never commit this: anyone
# holding it can act as you on Fantrax. It is covered by .gitignore.
COOKIE_PATH = os.path.join(REPO_ROOT, 'fantraxloggedin.cookie')

LOGIN_URL = 'https://www.fantrax.com/login'


class FantraxAuthError(RuntimeError):
    """Raised when there is no usable cookie file."""


def load_session(cookie_path: str = COOKIE_PATH) -> Session:
    """
    Build a requests Session carrying your saved Fantrax cookies.

    Pass the result to League(league_id, session=session).
    """
    if not os.path.exists(cookie_path):
        raise FantraxAuthError(
            f"No cookie file at {cookie_path}.\n"
            f"Run: python scripts/fantrax_login.py\n"
            f"See FANTRAX.md for the manual alternative."
        )

    session = Session()
    with open(cookie_path, 'rb') as handle:
        cookies = pickle.load(handle)

    for cookie in cookies:
        # Selenium emits dicts; a plain {name: value} mapping also works
        if isinstance(cookie, dict):
            session.cookies.set(
                cookie['name'], cookie['value'], domain=cookie.get('domain', '.fantrax.com')
            )
        else:
            session.cookies.set_cookie(cookie)

    return session


def save_cookies(cookies, cookie_path: str = COOKIE_PATH) -> str:
    """Persist a cookie list to disk and return where it was written."""
    with open(cookie_path, 'wb') as handle:
        pickle.dump(cookies, handle)
    # Readable only by the owner where the OS supports it
    try:
        os.chmod(cookie_path, 0o600)
    except OSError:
        pass
    return cookie_path


def log_in_and_save_cookies(
    username: Optional[str] = None,
    password: Optional[str] = None,
    cookie_path: str = COOKIE_PATH,
    headless: bool = False,
) -> str:
    """
    Drive a real browser login once and save the resulting cookies.

    Credentials are read from the FANTRAX_USER and FANTRAX_PASS environment
    variables so they never end up in the repository. Requires:

        pip install selenium webdriver-manager

    Runs visibly by default (headless=False) so you can complete any
    two-factor or captcha step yourself.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    username = username or os.environ.get('FANTRAX_USER')
    password = password or os.environ.get('FANTRAX_PASS')

    options = Options()
    if headless:
        options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(LOGIN_URL)
        print("A browser window has opened at the Fantrax login page.")
        if username and password:
            print("FANTRAX_USER / FANTRAX_PASS are set, but Fantrax's login form "
                  "changes often, so finish signing in manually if needed.")
        input("Log in, then press Enter here to save your session cookies... ")
        cookies = driver.get_cookies()
    finally:
        driver.quit()

    if not cookies:
        raise FantraxAuthError("Login produced no cookies; nothing was saved.")

    path = save_cookies(cookies, cookie_path)
    print(f"Saved {len(cookies)} cookies to {path}")
    return path


def connect(league_id: str, cookie_path: str = COOKIE_PATH):
    """
    Return a fantraxapi League authenticated as you.

    league_id is the string in your league URL:
    https://www.fantrax.com/fantasy/league/<league_id>/...
    """
    from fantraxapi import League

    return League(league_id, session=load_session(cookie_path))
