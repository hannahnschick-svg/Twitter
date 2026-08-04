"""Configuration for the daily longevity digest.

Edit KEYWORDS and ACCOUNTS to tune what counts as "longevity-adjacent."
Handles in ACCOUNTS are not guaranteed to be correct/current -- verify
and adjust before relying on them.
"""
import os

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

# API host. api.twitter.com and api.x.com serve the same v2 endpoints.
# Locally either works. Inside the Claude Code cloud sandbox only hosts on
# the environment's network allowlist resolve, and api.x.com is not on it
# by default -- set X_API_HOST=api.twitter.com there, or allowlist api.x.com.
API_HOST = os.environ.get("X_API_HOST", "api.x.com")

# How far back to look for posts, in hours.
LOOKBACK_HOURS = 24

# Max results to fetch per API call (10-100).
MAX_RESULTS_PER_CALL = 100

# How many pages to follow per query before stopping. Each page is another
# billed API call against your monthly post-read cap, so raise carefully.
MAX_PAGES_PER_QUERY = 3

# English only, no retweets, no replies.
EXTRA_FILTERS = "lang:en -is:retweet -is:reply"
