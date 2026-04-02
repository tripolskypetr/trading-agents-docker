<p align="center">
  <img src="https://github.com/tripolskypetr/trading-agents-docker/raw/master/assets/logo.png" height="115px" alt="trading-agents-docker" />
</p>

<p align="center">
  <strong>Docker wrapper for TradingAgents — LLM-powered crypto trading analysis</strong><br>
  FastAPI HTTP interface over TradingAgents multi-agent framework.<br>
  Binance OHLCV · DuckDuckGo news · stockstats indicators · no API key required for data.
</p>

## What's inside

[TradingAgents](https://github.com/TauricResearch/TradingAgents) is a multi-agent LLM framework that mirrors a real trading firm. This repo wraps it in a Docker container with a REST API and replaces stock-market data sources with crypto-native ones.

**Active analysts:**

| Analyst | Tools | Source |
|---------|-------|--------|
| Market | OHLCV, technical indicators (RSI, MACD, ATR, Bollinger…) | Binance via ccxt + stockstats |
| Social | Crypto news search | DuckDuckGo (ddgs) |
| News | Crypto news + global macro search | DuckDuckGo (ddgs) |

Fundamentals analyst is disabled — balance sheets and income statements don't apply to crypto assets.

## How it works

1. `POST /api/v1/propagate` triggers the full agent pipeline for a given ticker and date
2. Market analyst fetches OHLCV and computes indicators from Binance
3. Social and news analysts search DuckDuckGo with negative-biased queries to surface risk signals
4. Bull/bear researchers debate, trader proposes a plan, risk team reviews
5. Portfolio manager issues a final decision: `BUY | OVERWEIGHT | HOLD | UNDERWEIGHT | SELL`

## Quick start

```bash
# Clone and build agent source
make build

# Copy and fill in your LLM API keys
cp example/.env.example example/.env

# Run locally
make start
```

Or with Docker:

```bash
make build
make publish

cd example
cp .env.example .env
# edit .env
docker compose up
```

## API

Base URL: `http://localhost:8080`

`GET /` — redirects to Swagger UI at `/docs`

---

### `POST /api/v1/propagate`

Run the full multi-agent analysis for a ticker and date.

```json
{
  "company_name": "BITCOIN",
  "trade_date": "2026-01-15"
}
```

Response:

```json
{
  "final_state": {
    "company_of_interest": "BITCOIN",
    "trade_date": "2026-01-15",
    "market_report": "...",
    "sentiment_report": "...",
    "news_report": "...",
    "fundamentals_report": "...",
    "investment_plan": "...",
    "trader_investment_plan": "...",
    "final_trade_decision": "...",
    "investment_debate_state": { ... },
    "risk_debate_state": { ... }
  },
  "signal": "BUY"
}
```

`signal` is one of: `BUY`, `OVERWEIGHT`, `HOLD`, `UNDERWEIGHT`, `SELL`

---

### `POST /api/v1/reflect_and_remember`

Update agent memory based on trade outcome. Call after a position is closed.

```json
{ "returns_losses": -0.05 }
```

---

### `POST /api/v1/process_signal`

Extract a rating from a raw analyst report text.

```json
{ "full_signal": "Based on the analysis, we recommend buying..." }
```

Response: `{ "result": "BUY" }`

---

### `GET /api/v1/health`

```json
{ "status": "ok", "graph_loaded": true }
```

## Configuration

All configuration is via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | LLM provider: `openai`, `anthropic`, `google`, `xai`, `openrouter`, `ollama` |
| `DEEP_THINK_LLM` | `gpt-5.4` | Model for deep reasoning (researchers, risk team) |
| `QUICK_THINK_LLM` | `gpt-5.4-mini` | Model for quick tasks (signal extraction) |
| `OPENAI_API_KEY` | — | OpenAI key |
| `ANTHROPIC_API_KEY` | — | Anthropic key |
| `GOOGLE_API_KEY` | — | Google key |
| `XAI_API_KEY` | — | xAI key |
| `OPENROUTER_API_KEY` | — | OpenRouter key |
| `PORT` | `8080` | HTTP port |

## Project structure

```
src/
  main.py          — FastAPI app, vendor registration, agent initialization
  agent/           — TradingAgents source (populated by make build)
  tools/
    exchange.py    — Binance OHLCV + indicators via ccxt + stockstats
    news.py        — DuckDuckGo news search
    fundamentals.py — No-op stubs for stock-only tools
scripts/
  linux/
    build.sh       — Clone TradingAgents into src/agent
    start.sh       — Load .env and run locally via uv
    publish.sh     — Build and push Docker image
  win/
    build.bat      — Windows equivalent of build.sh
    start.bat      — Windows equivalent of start.sh
    publish.bat    — Windows equivalent of publish.sh
example/
  docker-compose.yml
  .env.example
```
