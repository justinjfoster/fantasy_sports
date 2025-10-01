#!/usr/bin/env python3
"""
API Connectivity Test

This script tests connectivity to the NHL API and provides alternative approaches
if the primary API is not accessible.
"""

import requests
import sys
import json

def test_nhl_api():
    """Test connectivity to the NHL API."""
    print("Testing NHL API connectivity...")
    
    # Test the main NHL API
    api_urls = [
        "https://statsapi.web.nhl.com/api/v1/teams",
        "https://statsapi.web.nhl.com/api/v1/teams?expand=team.roster",
        "https://statsapi.web.nhl.com/api/v1/people/8471214"  # Connor McDavid's ID
    ]
    
    for url in api_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success! Got {len(data.get('teams', data.get('people', [])))} items")
                return True
            else:
                print(f"✗ HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
    
    return False

def test_alternative_apis():
    """Test alternative data sources."""
    print("\nTesting alternative data sources...")
    
    # Test Hockey-Reference style endpoints (if available)
    alternatives = [
        "https://www.hockey-reference.com/",
        "https://www.nhl.com/stats/teams"
    ]
    
    for url in alternatives:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✓ Success! Status: {response.status_code}")
            else:
                print(f"✗ HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")

def main():
    """Main test function."""
    print("=" * 60)
    print("NHL API CONNECTIVITY TEST")
    print("=" * 60)
    
    # Test primary API
    if test_nhl_api():
        print("\n✓ NHL API is accessible! You can proceed with data collection.")
        print("Run: python collect_data.py --seasons 2023")
    else:
        print("\n✗ NHL API is not accessible. This could be due to:")
        print("  - Network connectivity issues")
        print("  - API endpoint changes")
        print("  - Rate limiting or blocking")
        print("\nAlternative approaches:")
        print("1. Check your internet connection")
        print("2. Try again later (API might be temporarily down)")
        print("3. Use a VPN if you're in a restricted region")
        print("4. Consider using alternative data sources")
        
        # Test alternatives
        test_alternative_apis()
        
        print("\nIf the API continues to be unavailable, you can:")
        print("- Use the database structure with manually imported data")
        print("- Implement a web scraper for hockey-reference.com")
        print("- Use a different NHL data API")

if __name__ == "__main__":
    main()
