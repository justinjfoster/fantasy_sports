# Fantasy Hockey Draft Tool

A comprehensive Python tool to help you analyze NHL player statistics and make informed decisions for your fantasy hockey draft. This tool collects real NHL data from multiple seasons and provides detailed analysis tailored to your league's specific scoring categories.

## 🏒 Features

- **Real Data Collection**: Scrapes NHL player statistics from Hockey-Reference.com
- **Multi-Season Analysis**: Collects data from 2023, 2024, 2025, and 2026 seasons
- **Face-off Wins Data**: Includes face-off wins for skaters
- **Advanced Ranking Systems**: Multiple ranking approaches for different league types
- **Equal Weight Rankings**: Perfect for leagues where all categories are equally weighted
- **CSV Export**: Exports data and rankings in CSV format for easy analysis
- **Position-Specific Rankings**: Analyzes players by position (C, LW, RW, D, G)
- **Automatic Data Cleaning**: Removes duplicate entries for traded players

## 📊 Data Available

The tool collects comprehensive statistics for both skaters and goalies. **Duplicate entries are automatically cleaned** - when players are traded during a season, only their combined statistics are kept (marked as "2TM", "3TM", etc.).

### Skater Categories
- Goals, Assists, Points
- Power Play Points, Short-handed Points
- Shots on Goal, Shooting Percentage
- **Face-off Wins** (newly added)
- Face-off Percentage (for centers)
- Hits, Blocked Shots
- Plus/Minus, Penalty Minutes
- Game-winning Goals, Time on Ice

### Goalie Categories
- Wins, Losses, Ties, Overtime Losses
- Goals Against Average (GAA)
- Save Percentage, Saves
- Shutouts, Shots Against

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Collect Real NHL Data
```bash
# Default: the last four seasons
python collect_multi_year_data.py

# Or name the seasons explicitly
python collect_multi_year_data.py 2026
python collect_multi_year_data.py 2023 2024 2025 2026
```
Hockey-Reference labels a season by the year it **ends**, so `2026` means the
2025-26 season. Output lands in `data/`, and duplicate entries for traded
players are removed automatically (only the combined `2TM`/`3TM` row is kept).

Every cell is located by its `data-stat` attribute rather than by column
position, and the scraper aborts with an error if Hockey-Reference stops
publishing a column it depends on. An earlier position-based version silently
mapped most categories to the wrong statistic.

### 3. Generate Rankings (NEW!)
For **equal weight leagues** (all categories weighted equally):
```bash
python scripts/equal_weight_rankings.py
```

For **custom weighted leagues**:
```bash
python scripts/rank_players_2025.py
```

### 4. Analyze the Data
```bash
python analyze_csv_data.py
```
This provides comprehensive analysis of the collected data.

## 🏆 Ranking Systems

### Equal Weight Rankings (Recommended for Most Leagues)
Perfect for leagues where all categories are equally weighted:

**Skaters (7 categories):** Goals, Assists, Power Play Points, Hits, Blocked Shots, Face-off Wins, Shots
**Goalies (4 categories):** Wins, Saves, Save Percentage, Goals Against Average

```bash
# Generate equal weight rankings
python scripts/equal_weight_rankings.py
```

**Output Files:**
- `rankings/equal_weight_skater_rankings_2026.csv`
- `rankings/equal_weight_goalie_rankings_2026.csv`

### Alternative Ranking Systems
Multiple approaches for different league types:

```bash
# Compare different ranking methods
python scripts/alternative_rankings.py
```

**Available Systems:**
1. **Weighted Categories** - Emphasizes scoring categories appropriately
2. **Percentile-Based** - Treats all categories equally (best for equal weight leagues)
3. **Z-Score Based** - Most statistically accurate
4. **Position-Adjusted** - Accounts for position scarcity
5. **Efficiency-Based** - Per-game basis (good for injury-prone players)

## 📁 Project Structure

```
fantasy_sports/
├── src/                                    # Core modules
│   ├── data_fetcher.py                    # NHL API data fetching
│   ├── database.py                        # SQLite database operations
│   ├── data_collector.py                  # Orchestrates data collection
│   ├── rankings_data.py                   # Shared loading for ranking scripts
│   └── hockey_reference_scraper.py        # Web scraper for real data
├── data/                                  # CSV data files (cleaned, no duplicates)
│   ├── skater_data_2023_2026.csv         # 4,141 skater records (cleaned)
│   └── goalie_data_2023_2026.csv         # 406 goalie records (cleaned)
├── rankings/                              # Generated ranking files
│   ├── equal_weight_skater_rankings_2026.csv
│   ├── equal_weight_goalie_rankings_2026.csv
│   ├── skater_rankings_2026.csv
│   └── goalie_rankings_2026.csv
├── scripts/                               # Ranking and analysis scripts
│   ├── rank_players_2025.py              # Main ranking script
│   ├── equal_weight_rankings.py          # Equal weight skater rankings
│   ├── equal_weight_goalie_rankings.py   # Equal weight goalie rankings
│   ├── alternative_rankings.py           # Multiple ranking systems
│   └── recommended_rankings.py           # Recommended approaches
├── databases/                             # SQLite database files
│   ├── real_fantasy_hockey_2024.db       # Real NHL data database
│   ├── sample_fantasy_hockey.db          # Sample data database
│   └── test_fantasy_hockey.db            # Test database
├── archive/                               # Archived scripts
│   ├── test_data_collection.py           # Testing scripts
│   ├── sample_data.py                    # Sample data generator
│   ├── collect_data.py                   # Original data collection
│   └── clean_duplicate_stats.py          # Data cleaning utility
├── collect_multi_year_data.py            # Main data collection script
├── analyze_csv_data.py                   # CSV data analysis
├── analyze_your_league.py                # League-specific analysis
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

## 🎯 League Settings Supported

This tool is designed for head-to-head fantasy hockey leagues with the following settings:

### Roster Requirements
- 2 Centers (C)
- 2 Right Wings (RW)  
- 2 Left Wings (LW)
- 3 Defensemen (D)
- 2 Utility (any skater position)
- 2 Goalies (G)
- 4 Bench spots

### Scoring Categories
**Skaters**: Goals, Assists, Power Play Points, Shots on Goal, **Faceoffs Won**, Hits, Blocks

**Goalies**: Wins, Goals Against Average (GAA), Saves, Save Percentage

## 📈 Sample Analysis Output

### Top Skaters (2026) - Equal Weight Percentile Rankings
1. **Mika Zibanejad** (C) - 638.6 points - Contributes in every category
2. **Tim Stützle** (LW) - 632.1 points - Scoring plus peripherals
3. **Macklin Celebrini** (F) - 629.5 points - Elite young producer
4. **Nick Suzuki** (C) - 629.5 points - Power play and face-off volume
5. **Tage Thompson** (C) - 625.7 points - Goals and shot volume

Note that the percentile system rewards breadth over peak value, so a player
who is very good in all seven categories outranks one who is historically
dominant in four. Connor McDavid tops the **z-score** system instead. Compare
them with `python scripts/alternative_rankings.py` before settling on a board.

### Top Goalies (2026) - Equal Weight Rankings
1. **Andrei Vasilevskiy** - 368.9 points - Most wins, strong across the board
2. **Logan Thompson** - 366.8 points - Save volume and percentage
3. **Scott Wedgewood** - 358.2 points - Best SV% and GAA
4. **Igor Shesterkin** - 341.8 points - Elite rate stats
5. **Daniel Vladař** - 335.2 points - Strong GAA

### Data Cleaning Results
- **Skaters**: 4,882 → 4,141 records (removed 741 duplicates)
- **Goalies**: 442 → 406 records (removed 36 duplicates)
- **Result**: Each player appears only once per season with complete combined statistics

## 🔧 Customization

### Modifying Rankings
Edit the ranking scripts to customize for your specific league:

```python
# Example: Custom weights for weighted system
weights = {
    'goals': 3.0,           # High weight - primary scoring
    'assists': 2.5,         # High weight - primary scoring  
    'power_play_points': 2.0, # Medium-high - special teams
    'shots': 1.5,           # Medium - volume stat
    'face_off_wins': 1.0,   # Variable by position
    'hits': 0.8,            # Lower weight - peripheral
    'blocked_shots': 0.8    # Lower weight - peripheral
}
```

### Adding New Categories
The scraper can be extended to collect additional statistics by modifying `src/hockey_reference_scraper.py`.

### Data Cleaning
The tool automatically handles duplicate entries for traded players:
- **Problem**: Players traded during a season appear multiple times (once per team + combined stats)
- **Solution**: Keeps only the combined statistics (marked as "2TM", "3TM", etc.)
- **Result**: Each player appears exactly once per season with complete statistics
- **Example**: Bo Horvat (2023) traded from VAN to NYI → only "2TM" entry kept with 79 games, 70 points

## 📊 Data Usage

### Excel/Google Sheets
1. Import the CSV files from the `data/` or `rankings/` folders
2. Create pivot tables for analysis
3. Build charts and visualizations
4. **Note**: Data is already cleaned - no duplicate entries to worry about!

### Python Analysis
```python
import pandas as pd

# Load the cleaned data (no duplicates)
skaters = pd.read_csv('data/skater_data_2023_2026.csv')
goalies = pd.read_csv('data/goalie_data_2023_2026.csv')

# Load rankings
skater_rankings = pd.read_csv('rankings/equal_weight_skater_rankings_2026.csv')
goalie_rankings = pd.read_csv('rankings/equal_weight_goalie_rankings_2026.csv')

# Filter and analyze
top_scorers = skaters.nlargest(20, 'points')
elite_goalies = goalies[goalies['wins'] >= 30]

# Each player appears only once per season with combined stats
print(f"Unique players: {skaters['name'].nunique()}")
```

## 🛠️ Technical Details

### Data Sources
- **Primary**: Hockey-Reference.com (real NHL statistics)
- **Backup**: NHL API (when accessible)
- **Sample Data**: Generated realistic data for testing

### File Organization
- **CSV Files**: `data/` folder contains cleaned CSV files for analysis
- **Ranking Files**: `rankings/` folder contains generated player rankings
- **Scripts**: `scripts/` folder contains ranking and analysis tools
- **Database Files**: `databases/` folder contains SQLite databases
- **Archived Scripts**: `archive/` folder contains development and testing scripts

### Rate Limiting
The scraper includes built-in rate limiting (1 second delay) to be respectful to the data source.

### Data Quality
- Validates data before saving
- Handles missing values gracefully
- Includes error handling and logging
- **Automatically removes duplicate entries** for traded players
- Keeps only combined statistics (2TM, 3TM, etc.) for accurate analysis
- **Face-off wins data** properly extracted and included

## 📝 Dependencies

- `requests` - HTTP requests for web scraping
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical operations
- `beautifulsoup4` - HTML parsing
- `tqdm` - Progress bars
- `python-dotenv` - Environment variables

## 🤝 Contributing

This is a personal project, but feel free to fork and modify for your own fantasy hockey needs!

### Adding New Features
1. Fork the repository
2. Create a new branch
3. Add your feature
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for personal use. Please respect the terms of service of Hockey-Reference.com when using the scraper.

## 🏆 Draft Tips

Based on the analysis of real NHL data (2023-2026, cleaned):

1. **Use Equal Weight Rankings** - Perfect for most fantasy leagues
2. **Draft Goalies Early** - Only 2 starting spots, so scarcity makes them valuable
3. **Target Multi-Category Players** - Look for players who contribute across multiple categories
4. **Don't Ignore Face-off Wins** - Centers with high face-off wins are extremely valuable
5. **Consider Position Scarcity** - Defensemen who score are rare and valuable
6. **Look for Consistency** - Players who perform well across multiple seasons
7. **Trust the Data** - Cleaned data ensures accurate analysis without duplicate entries

## 📞 Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Verify your internet connection
3. Check the `archive/` folder for additional tools
4. Review the error messages for specific guidance

---

**Good luck with your fantasy hockey draft! 🏒**