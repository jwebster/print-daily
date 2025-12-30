# Bible reading plan functions
# Adapted from bible-reading-planner/lambda/bible_plan.py

from datetime import date, timedelta


def book_abbreviations(book):
    mapping = {
        "Genesis": "Gen.",
        "Exodus": "Ex.",
        "Leviticus": "Lev.",
        "Numbers": "Num.",
        "Deuteronomy": "Deut.",
        "Joshua": "Josh.",
        "Judges": "Judg.",
        "Ruth": "Ruth",
        "1 Samuel": "1 Sam.",
        "2 Samuel": "2 Sam.",
        "1 Kings": "1 Kings",
        "2 Kings": "2 Kings",
        "1 Chronicles": "1 Chron.",
        "2 Chronicles": "2 Chron.",
        "Ezra": "Ezra",
        "Nehemiah": "Neh.",
        "Esther": "Est.",
        "Job": "Job",
        "Psalms": "Ps.",
        "Proverbs": "Prov",
        "Ecclesiastes": "Eccles.",
        "Song of Solomon": "Song",
        "Song of Songs": "Song",
        "Isaiah": "Isa.",
        "Jeremiah": "Jer.",
        "Lamentations": "Lam.",
        "Ezekiel": "Ezek.",
        "Daniel": "Dan.",
        "Hosea": "Hos.",
        "Joel": "Joel",
        "Amos": "Amos",
        "Obadiah": "Obad.",
        "Jonah": "Jonah",
        "Micah": "Micah",
        "Nahum": "Nahum",
        "Habakkuk": "Hab.",
        "Zephaniah": "Zeph.",
        "Haggai": "Hag.",
        "Zechariah": "Zech.",
        "Malachi": "Mal.",
        "Matthew": "Matt.",
        "Mark": "Mark",
        "Luke": "Luke",
        "John": "John",
        "Acts": "Acts",
        "Romans": "Rom.",
        "1 Corinthians": "1 Cor.",
        "2 Corinthians": "2 Cor.",
        "Galatians": "Gal.",
        "Ephesians": "Eph.",
        "Philippians": "Phil.",
        "Colossians": "Col.",
        "1 Thessalonians": "1 Thess.",
        "2 Thessalonians": "2 Thess.",
        "1 Timothy": "1 Tim.",
        "2 Timothy": "2 Tim.",
        "Titus": "Titus",
        "Philemon": "Philem.",
        "Hebrews": "Heb.",
        "James": "James",
        "1 Peter": "1 Pet.",
        "2 Peter": "2 Pet.",
        "1 John": "1 John",
        "2 John": "2 John",
        "3 John": "3 John",
        "Jude": "Jude",
        "Revelation": "Rev",
    }
    return mapping.get(book, book)


def expand_book(book, chapters, start=0, step=1):
    book_short = book_abbreviations(book)
    if start > 0:
        start = start - 1
    if step == 1:
        return [f"{book_short} {r+1}" for r in range(start, chapters)]
    else:
        readings = []
        for r in range(start, chapters, step):
            up_to = min(r + step, chapters)
            readings.append(f"{book_short} {r+1} - {up_to}")
        return readings


def old_yr1(n):
    readings = []

    readings.extend(expand_book("Genesis", 50))
    readings.extend(expand_book("Exodus", 40))
    readings.extend(expand_book("Joshua", 11))
    readings.extend(expand_book("Judges", 9, start=6))
    readings.extend(expand_book("Ruth", 4))
    readings.extend(expand_book("1 Samuel", 30))
    readings.extend(expand_book("2 Samuel", 24))
    readings.extend(expand_book("1 Kings", 22))
    readings.extend(expand_book("Ezra", 10))
    readings.append(f"{book_abbreviations('Nehemiah')} 1")
    readings.append(f"{book_abbreviations('Nehemiah')} 2-3")
    readings.append(f"{book_abbreviations('Nehemiah')} 4")
    readings.append(f"{book_abbreviations('Nehemiah')} 5")
    readings.append(f"{book_abbreviations('Nehemiah')} 6-7")
    readings.append(f"{book_abbreviations('Nehemiah')} 8")
    readings.append(f"{book_abbreviations('Nehemiah')} 9")
    readings.append(f"{book_abbreviations('Nehemiah')} 10")
    readings.append(f"{book_abbreviations('Nehemiah')} 11-13")
    readings.extend(expand_book("Esther", 10))
    readings.extend(expand_book("Isaiah", 6))
    readings.extend(expand_book("Isaiah", 66, start=40))
    readings.extend(expand_book("Daniel", 6))
    readings.extend(expand_book("Jonah", 4))

    try:
        return readings[n]
    except IndexError:
        return ""


def new(n):
    readings = []

    readings.extend(expand_book("Luke", 24))
    readings.extend(expand_book("Acts", 28))
    readings.extend(expand_book("Romans", 16))
    readings.extend(expand_book("Matthew", 28))
    readings.extend(expand_book("1 Corinthians", 16))
    readings.extend(expand_book("2 Corinthians", 13))
    readings.extend(expand_book("Galatians", 6))
    readings.extend(expand_book("Ephesians", 6))
    readings.extend(expand_book("Philippians", 4))
    readings.extend(expand_book("Colossians", 4))
    readings.extend(expand_book("Mark", 16))
    readings.extend(expand_book("1 Thessalonians", 5))
    readings.extend(expand_book("2 Thessalonians", 3))
    readings.extend(expand_book("1 Timothy", 6))
    readings.extend(expand_book("2 Timothy", 4))
    readings.extend(expand_book("Titus", 3))
    readings.append(f"{book_abbreviations('Philemon')}")
    readings.extend(expand_book("Hebrews", 13))
    readings.extend(expand_book("John", 21))
    readings.extend(expand_book("James", 5))
    readings.extend(expand_book("1 Peter", 5))
    readings.extend(expand_book("2 Peter", 3))
    readings.extend(expand_book("1 John", 5))
    readings.append(f"{book_abbreviations('2 John')}")
    readings.append(f"{book_abbreviations('3 John')}")
    readings.append(f"{book_abbreviations('Jude')}")
    readings.extend(expand_book("Revelation", 22))

    try:
        return readings[n]
    except IndexError:
        return ""


def psalms(n):
    readings = []

    short = (
        3, 11, 13, 23, 29, 32, 39, 43, 52, 57, 63, 69, 76, 79, 86, 92, 99,
        104, 111, 116, 120, 122, 137,
    )
    r = 1
    while r < 119:
        if r not in short:
            readings.append(f"{book_abbreviations('Psalms')} {r}")
            r += 1
        else:
            readings.append(f"{book_abbreviations('Psalms')} {r} - {r+1}")
            r += 2

    readings.append(f"{book_abbreviations('Psalms')} 119 v1-32")
    readings.append(f"{book_abbreviations('Psalms')} 119 v33-96")
    readings.append(f"{book_abbreviations('Psalms')} 119 v97-144")
    readings.append(f"{book_abbreviations('Psalms')} 119 v145-176")
    r = 120  # Continue after Psalm 119
    while r < 151:
        if r not in short:
            readings.append(f"{book_abbreviations('Psalms')} {r}")
            r += 1
        else:
            readings.append(f"{book_abbreviations('Psalms')} {r} - {r+1}")
            r += 2

    try:
        return readings[n]
    except IndexError:
        return ""


def count_weekdays(start: date, end: date) -> int:
    """Count weekdays (Mon-Fri) between start (inclusive) and end (exclusive)."""
    count = 0
    current = start
    while current < end:
        if current.weekday() < 5:  # Mon-Fri
            count += 1
        current += timedelta(days=1)
    return count


def get_todays_readings(for_date: date = None) -> list[str] | None:
    """
    Get bible readings for a given date.
    Returns None if it's a weekend (no readings).
    Returns list of [OT, Psalms, NT] readings for weekdays.
    """
    if for_date is None:
        for_date = date.today()

    # No readings on weekends
    if for_date.weekday() >= 5:
        return None

    # Calculate reading index from Jan 1 of the year
    year_start = date(for_date.year, 1, 1)
    reading_index = count_weekdays(year_start, for_date)

    return [
        old_yr1(reading_index),
        psalms(reading_index),
        new(reading_index),
    ]
