# print-daily

A daily newspaper PDF generator that prints automatically at 6:30am. Curates news from The Guardian using Claude AI, includes weather, bible readings, and Readwise highlights.

## Features

- **AI-Curated News**: Claude selects and summarizes the most relevant stories based on your interests (politics, climate, technology, world events)
- **Weather**: Current conditions and forecast for your location
- **Bible Readings**: Daily reading plan with OT, Psalms, and NT
- **Daily Verse**: Rotating selection of scripture verses
- **Readwise Highlights**: Random highlight from your saved books
- **Magazine Layout**: Clean A4 design with Montserrat typography

## Sample Output

```
┌─────────────────────────────────────────────┐
│ TUESDAY                              5°C    │
│ 30 December 2025               Partly cloudy│
│ Witney, Oxfordshire              H 8° L 2°  │
├─────────────────────────────────────────────┤
│ THE GUARDIAN                                │
│                                             │
│ [Top Story 1 - detailed summary]            │
│ [Top Story 2 - detailed summary]            │
│                                             │
│ [Story 3]          │ IN BRIEF               │
│ [shorter]          │ • Headline             │
│                    │ • Headline             │
│                    │ • Headline             │
├─────────────────────────────────────────────┤
│ "Quote from your Readwise highlights"       │
│                        — Author, Book Title │
├─────────────────────────────────────────────┤
│ "Verse text"       │ TODAY'S READINGS       │
│ — Reference        │ Gen. 1 · Ps. 1 · Luke 1│
└─────────────────────────────────────────────┘
```

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/yourusername/print-daily.git
cd print-daily
pip install -r requirements.txt
```

### 2. Configure API keys

Copy the example environment file and add your keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

| Key | Required | Get it from |
|-----|----------|-------------|
| `GUARDIAN_API_KEY` | Yes | [Guardian Open Platform](https://open-platform.theguardian.com/) |
| `ANTHROPIC_API_KEY` | No | [Anthropic Console](https://console.anthropic.com/) |
| `READWISE_TOKEN` | No | [Readwise](https://readwise.io/access_token) |

Without `ANTHROPIC_API_KEY`, raw Guardian summaries are used instead of AI curation.
Without `READWISE_TOKEN`, the highlights section is omitted.

### 3. Test it

```bash
# Preview without printing
python generate_daily.py --preview

# Save to file
python generate_daily.py --save daily.pdf

# Print to default printer
python generate_daily.py
```

## Automatic Daily Printing (macOS)

Enable the 6:30am schedule:

```bash
ln -s $(pwd)/com.jwebster.print-daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jwebster.print-daily.plist
```

Check status:
```bash
launchctl list | grep print-daily
```

Disable:
```bash
launchctl unload ~/Library/LaunchAgents/com.jwebster.print-daily.plist
```

## Configuration

### Location

Edit `data_sources/weather.py` to change the weather location:

```python
WITNEY_LAT = 51.7856
WITNEY_LON = -1.4857
```

### News Interests

Edit the system prompt in `data_sources/claude_summarizer.py`:

```python
SYSTEM_PROMPT = """Your reader is interested in:
- UK and world politics
- Climate and environment
- Technology and AI
- Significant world events

NOT interested in: sport, celebrities, entertainment...
```

### Bible Reading Plan

The reading plan in `data_sources/bible_readings.py` follows a weekday schedule covering OT, Psalms, and NT. Modify the `old_yr1()`, `psalms()`, and `new()` functions to customize.

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
├── fonts/                     # Montserrat font files (included)
├── logs/                      # Scheduled job logs
├── .env                       # API keys (not in git)
├── .env.example               # Template for .env
├── requirements.txt
└── com.jwebster.print-daily.plist  # launchd schedule
```

## License

MIT
