# Getting Started with Fantasy Hockey Draft Tool

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data
```bash
python sample_data.py
```

### 3. Run Analysis
```bash
python analyze_sample_data.py
```

That's it! You now have a working fantasy hockey analysis tool.

## What You Get

The sample data includes:
- **24 NHL players** (including 4 goalies)
- **3 seasons** of data (2021, 2022, 2023)
- **Realistic statistics** based on player skill levels
- **Complete analysis** showing rankings by various categories

## Sample Output

The analysis will show you:
- 🏆 Top scorers, goal scorers, and assist leaders
- ⚡ Power play specialists
- 💪 Physical players (hits + blocked shots)
- 🛡️ Top goalies by wins, save percentage, and shutouts
- 🌟 Fantasy value rankings based on customizable scoring
- 📈 Season-to-season improvements

## Customizing for Your League

### Fantasy Scoring System

Edit the `analyze_sample_data.py` file to match your league's scoring:

```python
# Example: Goals (3), Assists (2), Plus/Minus (1), etc.
fantasy_points = (
    player['goals'] * 3 +
    player['assists'] * 2 +
    player['plus_minus'] * 1 +
    # Add your league's categories here
)
```

### Adding More Players

To add more players to the sample data:
1. Edit the `players` list in `sample_data.py`
2. Add skill levels in the `skill_levels` dictionary
3. Re-run `python sample_data.py`

## Next Steps

1. **Collect Real Data**: If you have API access, use `python collect_data.py --seasons 2023`
2. **Customize Analysis**: Modify the analysis scripts for your specific needs
3. **Add Projections**: Incorporate current season data and expert projections
4. **Build Interface**: Create a web dashboard for easier analysis

## Troubleshooting

- **API Issues**: The NHL API may not be accessible in all environments. Use sample data instead.
- **Database Errors**: Delete the database file and re-run the sample data generator.
- **Import Errors**: Make sure you've installed all dependencies with `pip install -r requirements.txt`

## Files Overview

- `sample_data.py` - Generates realistic sample data
- `analyze_sample_data.py` - Comprehensive analysis of the data
- `collect_data.py` - Collects real data from NHL API
- `src/database.py` - Database operations
- `src/data_fetcher.py` - NHL API interface
- `src/hockey_reference_scraper.py` - Alternative data source

Happy drafting! 🏒
