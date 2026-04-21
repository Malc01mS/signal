PROFILE = """
Malcolm is a Canadian mechanical engineer, mid-20s, working as a Channel Planning Manager
at Tesla in Fremont, California. He reads broadly across macro/capital markets, geopolitics,
technology, strategic frameworks, and wealth architecture. He listens to major long-form
podcasts daily (All In, Dwarkesh, Lex Fridman, Acquired, Founders/Senra, Good Fellows,
American Optimist, Invest Like the Best, Relentless, Shawn Ryan, Conversations with Tyler
Cowan, Hoover Institution talks) and is active on X/Twitter. He does not need recaps of
current events or anything already widely circulated through these channels.

He needs: mechanisms that explain why structural forces are moving the way they are,
theses forming before they reach consensus, research that exposes what most people
haven't named yet, and directional indicators that sharpen how he allocates attention
and capital. Investment thesis framing is welcome when the evidence supports it.

Intellectual anchors: Lyn Alden's long-term debt cycle framework, hard asset positioning,
realpolitik as geopolitical lens, the Fourth Turning cycle framework, Austrian/Chicago
economics tension, semiconductor supply chain structure, AI industrial policy.
"""

PILLARS = [
    "macro_capital",
    "geopolitics_power",
    "tech_industry",
    "wealth_architecture",
    "long_game",
    "stack",
]

SEMANTIC_SCHOLAR_FIELDS = [
    "Economics",
    "Political Science",
    "Computer Science",
    "Engineering",
    "Business",
]

SEMANTIC_SCHOLAR_KEYWORDS = [
    "monetary policy", "debt cycle", "fiscal dominance", "commodity supercycle",
    "geopolitics", "supply chain", "semiconductor", "industrial policy",
    "artificial intelligence", "energy transition", "manufacturing",
    "immigration policy", "tax policy", "equity compensation",
    "long-run growth", "historical cycles", "institutional design",
    "dollar hegemony", "multipolar", "trade policy", "tariffs",
]

RSS_SOURCES = [
    # Economics & finance
    "https://doomberg.substack.com/feed",           # Doomberg — energy, commodities
    "https://noahpinion.substack.com/feed",         # Noah Smith — economics
    "https://marginalrevolution.com/feed",          # Tyler Cowen — economics, ideas
    "https://www.federalreserve.gov/feeds/working_papers.xml",  # Fed research
    # Geopolitics & policy
    "https://palladiummag.com/feed",               # Palladium — state capacity, geopolitics
    "https://www.project-syndicate.org/rss",        # Project Syndicate — global economics
    "https://www.brookings.edu/feed/",              # Brookings — policy research
    # Long-form / ideas
    "https://astralcodexten.substack.com/feed",     # Scott Alexander — reasoning, ideas
]

SCORING_THRESHOLDS = {
    "high_alpha": 44,
    "include": 38,
    "cut": 0,
}

MAX_ITEMS_PER_PILLAR = 3
MAX_TOTAL_ITEMS = 12
