# print-daily

A daily newspaper PDF generator that prints automatically each morning. Curates news from The Guardian using Claude AI, includes weather, bible readings, and Readwise highlights.

## Features

- **AI-Curated News** - Claude selects and summarizes the most relevant stories based on your interests
- **Local Weather** - Current conditions and forecast for your location
- **Bible Readings** - Daily reading plan covering OT, Psalms, and NT
- **Daily Verse** - Rotating selection of scripture verses
- **Readwise Highlights** - Random highlight from your saved books
- **Magazine Layout** - Clean A4 design with Montserrat typography

## Sample Output

```
+---------------------------------------------+
| MONDAY                               12°C   |
| 30 December 2025               Partly cloudy|
| Witney, Oxfordshire              H 15° L 8° |
+---------------------------------------------+
| THE GUARDIAN                                |
|                                             |
| [Top Story - detailed 7-10 sentence summary]|
|                                             |
| [Second Story - detailed summary]           |
|                                             |
| [Third Story]      | IN BRIEF               |
| [shorter summary]  | - Headline             |
|                    | - Headline             |
|                    | - Headline             |
+---------------------------------------------+
| "Quote from your Readwise highlights"       |
|                        -- Author, Book      |
+---------------------------------------------+
| "Daily verse"      | TODAY'S READINGS       |
| -- Reference       | Gen. 1 - Ps. 1 - Lk 1  |
+---------------------------------------------+
```

## Requirements

- Python 3.10+
- macOS, Linux, or Windows
- Printer (for automatic printing)

## Installation

```bash
git clone https://github.com/yourusername/print-daily.git
cd print-daily
pip install -r requirements.txt
```

## Configuration

### API Keys

Copy the example environment file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:

| Key | Required | Description | Get it from |
|-----|----------|-------------|-------------|
| `GUARDIAN_API_KEY` | Yes | Access to Guardian content | [Guardian Open Platform](https://open-platform.theguardian.com/) |
| `ANTHROPIC_API_KEY` | No | AI news curation | [Anthropic Console](https://console.anthropic.com/) |
| `READWISE_TOKEN` | No | Book highlights | [Readwise Access Token](https://readwise.io/access_token) |

**Fallback behavior:**
- Without `ANTHROPIC_API_KEY`: Uses raw Guardian article summaries (no AI curation)
- Without `READWISE_TOKEN`: Highlights section is omitted

### Weather Location

Edit `data_sources/weather.py` to change the weather location:

```python
# Your location coordinates
WITNEY_LAT = 51.7856  # latitude
WITNEY_LON = -1.4857  # longitude
```

Find coordinates at [latlong.net](https://www.latlong.net/).

### News Interests

Customize the AI prompt in `data_sources/claude_summarizer.py`:

```python
SYSTEM_PROMPT = """Your reader is interested in:
- UK and world politics
- Climate and environment
- Technology and AI
- Significant world events

NOT interested in: sport, celebrities, entertainment...
```

### Bible Reading Plan

The reading plan follows a weekday schedule (Mon-Fri). Modify the functions in `data_sources/bible_readings.py` to customize:
- `old_yr1()` - Old Testament readings
- `psalms()` - Psalm readings
- `new()` - New Testament readings

## Usage

```bash
# Preview without printing (opens in default PDF viewer)
python generate_daily.py --preview

# Save to file
python generate_daily.py --save output.pdf

# Print to default printer
python generate_daily.py

# Generate for a specific date
python generate_daily.py --date 2025-01-15

# Skip AI curation (use raw Guardian summaries)
python generate_daily.py --no-ai
```

## Automatic Daily Printing (macOS)

### Setup

1. Copy and edit the launchd plist:

```bash
cp com.jwebster.print-daily.plist ~/Library/LaunchAgents/
```

2. Edit `~/Library/LaunchAgents/com.jwebster.print-daily.plist`:
   - Update Python path (run `which python3` to find it)
   - Update installation path

3. Create logs directory:

```bash
mkdir -p logs
```

4. Load the schedule:

```bash
launchctl load ~/Library/LaunchAgents/com.jwebster.print-daily.plist
```

### Management

```bash
# Check status
launchctl list | grep print-daily

# Disable
launchctl unload ~/Library/LaunchAgents/com.jwebster.print-daily.plist

# View logs
tail -f logs/stdout.log
tail -f logs/stderr.log
```

### Other Platforms

**Linux (systemd):** Create a systemd timer and service unit.

**Windows:** Use Task Scheduler to run `python generate_daily.py` daily.

## Project Structure

```
print-daily/
├── generate_daily.py          # Main entry point
├── pdf_generator.py           # ReportLab PDF layout
├── data_sources/
│   ├── guardian.py            # Guardian API client
│   ├── weather.py             # Open-Meteo weather
│   ├── bible_readings.py      # Reading plan logic
│   ├── bible_verse.py         # Daily verse rotation
│   ├── readwise.py            # Readwise highlights
│   └── claude_summarizer.py   # AI news curation
├── fonts/                     # Montserrat font files
├── tests/                     # Unit tests
├── logs/                      # Scheduled job logs
├── .env.example               # Environment template
└── com.jwebster.print-daily.plist  # macOS schedule
```

## Development

### Setup

```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### Code Quality

The project uses:
- Type hints for function signatures
- Dataclasses for structured data
- Logging for warnings/errors
- Graceful fallbacks for API failures

## API Rate Limits

| API | Limit | Notes |
|-----|-------|-------|
| Guardian | 500 req/day (free tier) | More than enough for daily use |
| Open-Meteo | Unlimited | Free, no key required |
| Claude | Based on plan | One request per generation |
| Readwise | Reasonable use | One request per generation |

## Troubleshooting

**PDF won't print:**
- Check printer is connected: `lpstat -p`
- Try printing manually: `lp output.pdf`

**Weather shows wrong location:**
- Verify coordinates in `data_sources/weather.py`
- Check API response: `python -c "from data_sources.weather import get_weather; print(get_weather())"`

**AI curation not working:**
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Check logs for API errors
- Try `--no-ai` flag to use fallback

**No Readwise highlights:**
- Verify `READWISE_TOKEN` is set in `.env`
- Ensure you have highlights in your Readwise account

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [The Guardian](https://www.theguardian.com/) for the Open Platform API
- [Open-Meteo](https://open-meteo.com/) for free weather data
- [Anthropic](https://www.anthropic.com/) for Claude AI
- [Readwise](https://readwise.io/) for the highlights API
- [Google Fonts](https://fonts.google.com/specimen/Montserrat) for Montserrat
