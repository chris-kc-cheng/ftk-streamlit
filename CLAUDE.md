# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full multi-page app
streamlit run terminal.py

# Run a single page directly (e.g., for development)
streamlit run factors.py --server.enableCORS false --server.enableXsrfProtection false

# Streamlit runs on port 8501 by default
```

The `REDIS_URL` environment variable must be set for Redis caching to work (used by `heatmap.py` via `utils.redis_cache`). Pages using only `@st.cache_data` do not require Redis.

## Architecture

This is a multi-page Streamlit financial terminal. **`terminal.py` is the entry point** — it defines navigation and registers all pages grouped into three sections: Market, Analysis, and Model.

Each `.py` file in the root is a standalone page module:

| File | App |
|------|-----|
| `indices.py` | Equity Dashboard (Yahoo Finance data, `data/indices.csv` for metadata) |
| `yield.py` | Yield Curve |
| `currency.py` | Foreign Exchange heatmap |
| `economic.py` | Economic Indicators (CPI, unemployment) |
| `heatmap.py` | Periodic Table of Returns (asset classes, MSCI, hedge fund indices) |
| `performance.py` | Performance & Risk Analysis (fund vs benchmark) |
| `portfolio.py` | Portfolio Optimization |
| `factors.py` | Fama-French Factor Exposure |
| `peers.py` | Peer Group Analysis (URL-driven: `?fund=X&benchmark=Y`) |
| `options.py` | Option Strategies (Black-Scholes) |
| `alm.py` | Asset Liability Management (CIR model) |
| `linking.py` | Multi-Period Return Linking |

### Key patterns

- **`toolkit as ftk`** — all financial calculations use the `fintoolkit` package (imported as `toolkit`). Functions include `ftk.get_yahoo_bulk()`, `ftk.compound_return()`, `ftk.get_msci()`, `ftk.get_withintelligence_bulk()`, etc.
- **Caching** — most data-fetch functions use `@st.cache_data(ttl=3600)`. `heatmap.py` uses `@redis_cache` from `utils.py` for longer TTLs (15 days).
- **`utils.py`** — shared utilities: `format_table()` (monthly return table with YTD), `redis_cache()` decorator, `get_redis()` resource.
- **Altair** (`altair as alt`) is used for all charts, not Plotly or Matplotlib.
- **Theme** — dark theme defined in `.streamlit/config.toml` with primary color `#69BDBA`. Highlight color `#69BDBA` is used in `highlight_max()` calls.

### Data sources

- **Yahoo Finance** — via `ftk.get_yahoo_bulk(tickers, period)` — used by most market pages
- **MSCI** — via `ftk.get_msci(ids, variant)` — used in `heatmap.py`
- **WithIntelligence** — via `ftk.get_withintelligence_bulk(ids)` — hedge fund indices in `heatmap.py`
- **Local files** — `data/indices.csv` (index metadata), `data/data.csv`/`data.xlsx` (sample proprietary fund data), `data/signature.md` (footer markdown), `data/option_strategy.json`
