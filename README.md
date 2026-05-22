# 22K Gold Price Tracker · Sri Lanka

Interactive chart tracking 22 Karat gold prices in Sri Lanka (LKR) over the last 13 months.

**Live site:** https://prasannavasan.github.io/gold-tracker-lk/

## Features

- Today's price per gram and per pawn (8g — the local standard)
- 13-month area chart with hover tooltips and average reference line
- Monthly data table with 12-month high/low
- Zero dependencies — pure HTML/CSS/JS, single file

## Auto-update

A GitHub Actions workflow runs every day at **9:00 AM Sri Lanka time (UTC+5:30)**. It:

1. Fetches the gold spot price in USD from [api.gold-api.com](https://api.gold-api.com)
2. Fetches the USD → LKR exchange rate from [open.er-api.com](https://open.er-api.com)
3. Calculates the 22K price per gram: `(spot_usd/oz ÷ 31.1035) × (22/24) × usd_lkr`, rounded to nearest 10
4. Updates `index.html` in place and commits the change
5. GitHub Pages redeploys automatically — the live site reflects the new price within ~2 minutes

To trigger a manual update: [Actions → Update 22K Gold Price → Run workflow](https://github.com/prasannavasan/gold-tracker-lk/actions/workflows/update-price.yml)

> **Note:** The price is derived from the international spot price converted to LKR. Sri Lankan retail prices include import duties and jeweller margins. The formula is calibrated to match indicative retail rates but may vary by ±1–2% from what a specific jeweller quotes.

## Data sources

Spot price: [api.gold-api.com](https://api.gold-api.com) · Exchange rate: [open.er-api.com](https://open.er-api.com)  
Historical reference: ideabeam.com, goldenchennai.com, goodreturns.in, goldrate24.com, goldpricez.com  
Prices are indicative. 1 pawn = 8 grams.
