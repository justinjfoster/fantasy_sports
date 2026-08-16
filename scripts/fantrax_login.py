#!/usr/bin/env python3
"""
One-time Fantrax login.

Opens a browser, waits for you to sign in, and saves the session cookies so
the other Fantrax scripts can reach your league. Run this again whenever the
cookies expire (you will see a "Not Logged In" error).

    pip install selenium webdriver-manager
    python scripts/fantrax_login.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

from src.fantrax import COOKIE_PATH, log_in_and_save_cookies


def main():
    print("=" * 60)
    print("FANTRAX LOGIN")
    print("=" * 60)
    print("Your password is never read or stored by this script - you type it")
    print("into the Fantrax page itself. Only the resulting session cookies")
    print("are saved, to:")
    print(f"  {COOKIE_PATH}")
    print("That file is gitignored. Treat it like a password.")
    print("=" * 60)

    try:
        log_in_and_save_cookies()
    except ImportError:
        print("\nSelenium is not installed. Either:")
        print("  pip install selenium webdriver-manager")
        print("or follow the manual cookie steps in FANTRAX.md")
        sys.exit(1)
    except Exception as e:
        print(f"\nLogin failed: {type(e).__name__}: {e}")
        sys.exit(1)

    print("\nDone. Now try:")
    print("  python scripts/fantrax_explore.py <your_league_id>")


if __name__ == "__main__":
    main()
