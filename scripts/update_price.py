#!/usr/bin/env python3
"""
Fetches the current 22K gold price for Sri Lanka (LKR/gram) from two free APIs:
  - api.gold-api.com  →  gold spot price (USD/troy oz)
  - open.er-api.com   →  USD/LKR exchange rate

Updates index.html in place: DATA array, stat cards, and date strings.
Handles month rollovers automatically (drops oldest month, appends new one).
"""

import re
import sys
import json
import urllib.request
from datetime import datetime, timezone, timedelta

# ── Time ──────────────────────────────────────────────────────────────────────

SL_TZ = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(SL_TZ)

month_label = now.strftime("%b '") + now.strftime("%y")   # e.g. "May '26"
date_str    = now.strftime(f"%b {now.day}, %Y")            # e.g. "May 22, 2026"
end_month   = now.strftime("%B %Y")                        # e.g. "May 2026"
start_month = (now - timedelta(days=365)).strftime("%B %Y")

# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gold-tracker-bot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

try:
    spot_usd_per_oz = float(fetch("https://api.gold-api.com/price/XAU")["price"])
    usd_to_lkr      = float(fetch("https://open.er-api.com/v6/latest/USD")["rates"]["LKR"])
except Exception as e:
    print(f"ERROR fetching price data: {e}")
    sys.exit(1)

# 22K per gram in LKR, rounded to nearest 10
price_gram = round((spot_usd_per_oz / 31.1035) * (22 / 24) * usd_to_lkr / 10) * 10
price_pawn = price_gram * 8

if not (10_000 < price_gram < 500_000):
    print(f"ERROR: price {price_gram} is outside sane range — aborting")
    sys.exit(1)

print(f"Spot ${spot_usd_per_oz:,.2f}/oz | USD/LKR {usd_to_lkr:.2f} | 22K {price_gram:,} LKR/g")

# ── Update index.html ─────────────────────────────────────────────────────────

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Detect current live entry's month
live_m = re.search(r'month:\s*"([^"]+)"[^}]*live:\s*true', html)
live_month = live_m.group(1) if live_m else None

if live_month and live_month != month_label:
    # ── Month rollover ────────────────────────────────────────────────────────
    # 1. Strip ', live: true' from the old live entry
    html = re.sub(r',\s*live:\s*true', "", html, count=1)

    # 2. Drop the oldest DATA entry (first indented line in the array)
    html = re.sub(
        r'    \{ month: "[^"]+",\s+gram:\s*\d+,\s*note:\s*"[^"]*" \},\n',
        "",
        html,
        count=1,
    )

    # 3. Insert new live entry just before the closing ];
    new_entry = (
        f'    {{ month: "{month_label}",  gram: {price_gram}, '
        f'note: "Confirmed {date_str}", live: true }},\n'
    )
    html = html.replace("  ];\n", new_entry + "  ];\n", 1)
    print(f"Month rollover → added {month_label}")

else:
    # ── Daily update: patch gram value and note inside the live entry ─────────
    def patch_live(m):
        s = re.sub(r"gram:\s*\d+",      f"gram: {price_gram}",           m.group(0))
        s = re.sub(r'note:\s*"[^"]*"',  f'note: "Confirmed {date_str}"', s)
        return s

    html = re.sub(r"\{[^}]*live:\s*true[^}]*\}", patch_live, html)

# ── Stat cards ────────────────────────────────────────────────────────────────

def patch_stat(stat_id, value):
    global html
    html = re.sub(
        rf'(id="{stat_id}"[^>]*>)[^<]*(</div>)',
        rf'\g<1>{value}\g<2>',
        html,
    )

all_grams = [int(x) for x in re.findall(r"gram:\s*(\d+)", html)]
high_gram = max(all_grams) if all_grams else price_gram
low_gram  = min(all_grams) if all_grams else price_gram

patch_stat("today-gram", f"{price_gram:,}")
patch_stat("today-pawn", f"{price_pawn:,}")
patch_stat("stat-high",  f"{high_gram:,}")
patch_stat("stat-low",   f"{low_gram:,}")

# ── Date strings ──────────────────────────────────────────────────────────────

html = re.sub(
    r"Last 13 months[^<]+",
    f"Last 13 months — {start_month} to {end_month} &nbsp;·&nbsp; Updated {date_str}",
    html,
)

html = re.sub(
    r"(Last updated:\s*)[\w ,]+(\s*&amp;|&nbsp;|<)",
    rf"\g<1>{date_str}\g<2>",
    html,
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html updated — {price_gram:,} LKR/g | high {high_gram:,} | low {low_gram:,}")
