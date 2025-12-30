# Daily bible verse selection
# Curated verses that rotate through the year

from datetime import date

VERSES = [
    ("Trust in the LORD with all your heart and lean not on your own understanding.", "Proverbs 3:5"),
    ("The LORD is my shepherd; I shall not want.", "Psalm 23:1"),
    ("For I know the plans I have for you, declares the LORD, plans to prosper you and not to harm you, plans to give you hope and a future.", "Jeremiah 29:11"),
    ("Be strong and courageous. Do not be afraid; do not be discouraged, for the LORD your God will be with you wherever you go.", "Joshua 1:9"),
    ("I can do all things through Christ who strengthens me.", "Philippians 4:13"),
    ("The LORD is my light and my salvation; whom shall I fear?", "Psalm 27:1"),
    ("Come to me, all you who are weary and burdened, and I will give you rest.", "Matthew 11:28"),
    ("But seek first his kingdom and his righteousness, and all these things will be given to you as well.", "Matthew 6:33"),
    ("And we know that in all things God works for the good of those who love him.", "Romans 8:28"),
    ("The steadfast love of the LORD never ceases; his mercies never come to an end; they are new every morning.", "Lamentations 3:22-23"),
    ("Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God.", "Philippians 4:6"),
    ("For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.", "John 3:16"),
    ("The LORD bless you and keep you; the LORD make his face shine on you and be gracious to you.", "Numbers 6:24-25"),
    ("Be still, and know that I am God.", "Psalm 46:10"),
    ("Your word is a lamp for my feet, a light on my path.", "Psalm 119:105"),
    ("Cast all your anxiety on him because he cares for you.", "1 Peter 5:7"),
    ("The grass withers and the flowers fall, but the word of our God endures forever.", "Isaiah 40:8"),
    ("Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged.", "Joshua 1:9"),
    ("But the fruit of the Spirit is love, joy, peace, forbearance, kindness, goodness, faithfulness, gentleness and self-control.", "Galatians 5:22-23"),
    ("He has shown you, O mortal, what is good. And what does the LORD require of you? To act justly and to love mercy and to walk humbly with your God.", "Micah 6:8"),
    ("Create in me a pure heart, O God, and renew a steadfast spirit within me.", "Psalm 51:10"),
    ("The name of the LORD is a fortified tower; the righteous run to it and are safe.", "Proverbs 18:10"),
    ("Blessed are the peacemakers, for they will be called children of God.", "Matthew 5:9"),
    ("This is the day that the LORD has made; let us rejoice and be glad in it.", "Psalm 118:24"),
    ("In the beginning was the Word, and the Word was with God, and the Word was God.", "John 1:1"),
    ("The heavens declare the glory of God; the skies proclaim the work of his hands.", "Psalm 19:1"),
    ("Love is patient, love is kind. It does not envy, it does not boast, it is not proud.", "1 Corinthians 13:4"),
    ("Therefore, if anyone is in Christ, the new creation has come: The old has gone, the new is here!", "2 Corinthians 5:17"),
    ("Wait for the LORD; be strong and take heart and wait for the LORD.", "Psalm 27:14"),
    ("Great is the LORD and most worthy of praise; his greatness no one can fathom.", "Psalm 145:3"),
    ("The LORD is close to the brokenhearted and saves those who are crushed in spirit.", "Psalm 34:18"),
]


def get_daily_verse(for_date: date = None) -> tuple[str, str]:
    """
    Get the verse for a given date.
    Returns (verse_text, reference) tuple.
    Cycles through the verse list based on day of year.
    """
    if for_date is None:
        for_date = date.today()

    day_of_year = for_date.timetuple().tm_yday
    verse_index = day_of_year % len(VERSES)

    return VERSES[verse_index]
