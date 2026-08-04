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

# API host. api.twitter.com and api.x.com serve the same v2 endpoints, but
# each must be on the cloud environment's network allowlist separately.
# api.twitter.com is the current default because it's the one allowlisted;
# switch to "api.x.com" only after adding that host to the allowlist too.
API_HOST = "api.twitter.com"

# How far back to look for posts, in hours.
LOOKBACK_HOURS = 24

# Max results to fetch per API call (10-100).
MAX_RESULTS_PER_CALL = 100

# How many pages to follow per query before stopping. Each page is another
# billed API call against your monthly post-read cap, so raise carefully.
MAX_PAGES_PER_QUERY = 3

# English only, no retweets, no replies.
EXTRA_FILTERS = "lang:en -is:retweet -is:reply"
