"""Configuration for the daily longevity digest.

Edit KEYWORDS and ACCOUNTS to tune what counts as "longevity-adjacent."
Handles in ACCOUNTS are not guaranteed to be correct/current -- verify
and adjust before relying on them.
"""

# Keyword/phrase queries (OR'd together). Keep each list short enough that
# the combined query stays under the API's query-length limit; the search
# script automatically splits into multiple calls if needed.
KEYWORDS = [
    "longevity",
    "healthspan",
    "biohacking",
    "biological age",
    "epigenetic clock",
    "senolytics",
    "senescent cells",
    "NAD+",
    "rapamycin",
    "metformin longevity",
    "autophagy",
    "caloric restriction",
    "VO2 max",
    "lifespan extension",
    "anti-aging",
    "longevity clinic",
]

# X accounts to always include, regardless of keyword match (minus the @).
ACCOUNTS = [
    "PeterAttiaMD",
    "bryan_johnson",
    "davidasinclair",
    "hubermanlab",
]

# How far back to look for posts, in hours.
LOOKBACK_HOURS = 24

# Max results to fetch per API call (10-100).
MAX_RESULTS_PER_CALL = 100

# English only, skip retweets/replies noise.
EXTRA_FILTERS = "lang:en -is:retweet"
