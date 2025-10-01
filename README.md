# Fantasy Hockey Draft Tool

A comprehensive Python tool to help you analyze NHL player statistics and make informed decisions for your fantasy hockey draft. This tool collects real NHL data from multiple seasons and provides detailed analysis tailored to your league's specific scoring categories.

## 🏒 Features

- **Real Data Collection**: Scrapes NHL player statistics from Hockey-Reference.com
- **Multi-Season Analysis**: Collects data from 2023, 2024, and 2025 seasons
- **League-Specific Analysis**: Tailored for head-to-head fantasy hockey leagues
- **CSV Export**: Exports data in CSV format for easy analysis in Excel/Google Sheets
- **Position-Specific Rankings**: Analyzes players by position (C, LW, RW, D, G)
- **Category Analysis**: Ranks players by goals, assists, power play points, shots, hits, blocks, etc.

## 📊 Data Available

The tool collects comprehensive statistics for both skaters and goalies. **Duplicate entries are automatically cleaned** - when players are traded during a season, only their combined statistics are kept (marked as "2TM", "3TM", etc.).

### Skater Categories
- Goals, Assists, Points
- Power Play Points, Short-handed Points
- Shots on Goal, Shooting Percentage
- Faceoff Percentage (for centers)
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
python collect_multi_year_data.py
```
This will collect data from 2023-2025 seasons and save as CSV files in the `data/` folder. The data is automatically cleaned to remove duplicate entries for traded players.

### 3. Analyze the Data
```bash
python analyze_csv_data.py
```
This provides comprehensive analysis of the collected data.

### 4. League-Specific Analysis
```bash
python analyze_your_league.py
```
This analyzes data specifically for your league's scoring system.

## 📁 Project Structure

```
fantasy_sports/
├── src/                           # Core modules
│   ├── data_fetcher.py           # NHL API data fetching
│   ├── database.py               # SQLite database operations
│   ├── data_collector.py         # Orchestrates data collection
│   └── hockey_reference_scraper.py # Web scraper for real data
├── data/                         # CSV data files (cleaned, no duplicates)
│   ├── skater_data_2023_2025.csv # 3,099 skater records (cleaned)
│   └── goalie_data_2023_2025.csv # 307 goalie records (cleaned)
├── databases/                    # SQLite database files
│   ├── real_fantasy_hockey_2024.db # Real NHL data database
│   ├── sample_fantasy_hockey.db    # Sample data database
│   └── test_fantasy_hockey.db      # Test database
├── archive/                      # Archived scripts
│   ├── test_data_collection.py   # Testing scripts
│   ├── sample_data.py            # Sample data generator
│   ├── collect_data.py           # Original data collection
│   └── clean_duplicate_stats.py  # Data cleaning utility
├── collect_multi_year_data.py    # Main data collection script
├── analyze_csv_data.py           # CSV data analysis
├── analyze_your_league.py        # League-specific analysis
├── requirements.txt              # Python dependencies
└── README.md                     # This file
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
**Skaters**: Goals, Assists, Power Play Points, Shots on Goal, Faceoffs Won, Hits, Blocks

**Goalies**: Wins, Goals Against Average (GAA), Saves, Save Percentage

## 📈 Sample Analysis Output

### Top Scorers (2023-2025) - Cleaned Data
1. **Nikita Kucherov** - 144 points (2024)
2. **Nathan MacKinnon** - 140 points (2024)
3. **Connor McDavid** - 132 points (2024)

### Top Goalies - Cleaned Data
1. **Connor Hellebuyck** - 47 wins (2025)
2. **Alexandar Georgiev** - 40 wins (2023)
3. **Linus Ullmark** - 40 wins (2023)

### Data Cleaning Results
- **Skaters**: 3,676 → 3,099 records (removed 577 duplicates)
- **Goalies**: 340 → 307 records (removed 33 duplicates)
- **Result**: Each player appears only once per season with complete combined statistics

## 🔧 Customization

### Modifying Analysis
Edit `analyze_csv_data.py` to customize the analysis for your specific needs:

```python
# Example: Filter for specific seasons
latest_data = df[df['season'] == 2025]

# Example: Custom scoring system
df['fantasy_points'] = (df['goals'] * 3 + 
                       df['assists'] * 2 + 
                       df['hits'] * 0.5)
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
1. Import the CSV files from the `data/` folder
2. Create pivot tables for analysis
3. Build charts and visualizations
4. **Note**: Data is already cleaned - no duplicate entries to worry about!

### Python Analysis
```python
import pandas as pd

# Load the cleaned data (no duplicates)
skaters = pd.read_csv('data/skater_data_2023_2025.csv')
goalies = pd.read_csv('data/goalie_data_2023_2025.csv')

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

Based on the analysis of real NHL data (2023-2025, cleaned):

1. **Draft Goalies Early** - Only 2 starting spots, so scarcity makes them valuable
2. **Target Multi-Category Players** - Look for players who contribute across multiple categories
3. **Don't Ignore Peripheral Stats** - Hits and blocks can win you categories
4. **Consider Position Scarcity** - Defensemen who score are rare and valuable
5. **Look for Consistency** - Players who perform well across multiple seasons
6. **Trust the Data** - Cleaned data ensures accurate analysis without duplicate entries

## 📞 Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Verify your internet connection
3. Check the `archive/` folder for additional tools
4. Review the error messages for specific guidance

---

**Good luck with your fantasy hockey draft! 🏒**