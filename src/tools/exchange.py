from datetime import datetime, timezone, timedelta
import pandas as pd


SYMBOL_ALIASES = {
    "BITCOIN": "BTC/USDT",
    "ETHEREUM": "ETH/USDT",
    "SOLANA": "SOL/USDT",
    "BNB": "BNB/USDT",
    "RIPPLE": "XRP/USDT",
    "XRP": "XRP/USDT",
    "DOGECOIN": "DOGE/USDT",
    "DOGE": "DOGE/USDT",
    "CARDANO": "ADA/USDT",
    "ADA": "ADA/USDT",
}

INDICATOR_DESCRIPTIONS = {
    "close_50_sma": "50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.",
    "close_200_sma": "200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.",
    "close_10_ema": "10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.",
    "macd": "MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.",
    "macds": "MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.",
    "macdh": "MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.",
    "rsi": "RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.",
    "boll": "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.",
    "boll_ub": "Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.",
    "boll_lb": "Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.",
    "atr": "ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.",
    "vwma": "VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.",
    "mfi": "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals.",
}


def _normalize_symbol(symbol: str) -> str:
    normalized = SYMBOL_ALIASES.get(symbol.upper(), symbol.upper())
    if "/" not in normalized:
        for quote in ("USDT", "BUSD", "BTC", "ETH", "BNB"):
            if normalized.endswith(quote):
                normalized = normalized[: -len(quote)] + "/" + quote
                break
    return normalized


def _fetch_ohlcv_df(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    import ccxt

    normalized = _normalize_symbol(symbol)

    since = int(datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    until = int(datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)

    exchange = ccxt.binance()
    all_ohlcv = []
    current = since
    while current < until:
        ohlcv = exchange.fetch_ohlcv(normalized, timeframe="1d", since=current, limit=500)
        if not ohlcv:
            break
        all_ohlcv.extend(ohlcv)
        current = ohlcv[-1][0] + 86400000

    if not all_ohlcv:
        return pd.DataFrame()

    df = pd.DataFrame(all_ohlcv, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms", utc=True).dt.tz_localize(None).dt.normalize()
    df = df[df["Timestamp"] < until].drop(columns=["Timestamp"]).set_index("Date")
    return df


def get_binance_ohlcv(symbol: str, start_date: str, end_date: str) -> str:
    try:
        import ccxt
    except ImportError:
        return "ccxt is not installed. Add ccxt to dependencies."

    df = _fetch_ohlcv_df(symbol, start_date, end_date)
    if df.empty:
        return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

    normalized = _normalize_symbol(symbol)
    for col in ("Open", "High", "Low", "Close"):
        df[col] = df[col].round(2)

    header = f"# Stock data for {normalized} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(df)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    return header + df.to_csv()


def get_binance_indicators(symbol: str, indicator: str, curr_date: str, look_back_days: int) -> str:
    try:
        import ccxt
        from stockstats import wrap
    except ImportError as e:
        return f"Missing dependency: {e}"

    if indicator not in INDICATOR_DESCRIPTIONS:
        return f"Indicator {indicator} is not supported. Choose from: {list(INDICATOR_DESCRIPTIONS.keys())}"

    curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    # fetch extra history so stockstats has enough data to warm up
    fetch_from = (curr_dt - timedelta(days=look_back_days + 300)).strftime("%Y-%m-%d")
    fetch_to = (curr_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    df = _fetch_ohlcv_df(symbol, fetch_from, fetch_to)
    if df.empty:
        return f"No data found for symbol '{symbol}'"

    df = df.reset_index().rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    wrapped = wrap(df)
    wrapped[indicator]  # trigger stockstats calculation

    # build date -> value lookup from index
    indicator_data = {}
    for ts, val in wrapped[indicator].items():
        indicator_data[ts.strftime("%Y-%m-%d")] = val

    before_dt = curr_dt - timedelta(days=look_back_days)

    ind_string = ""
    current = curr_dt
    while current >= before_dt:
        date_str = current.strftime("%Y-%m-%d")
        val = indicator_data.get(date_str)
        if val is not None and pd.notna(val):
            ind_string += f"{date_str}: {val}\n"
        else:
            ind_string += f"{date_str}: N/A\n"
        current -= timedelta(days=1)

    return (
        f"## {indicator} values from {before_dt.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
        + ind_string
        + "\n\n"
        + INDICATOR_DESCRIPTIONS[indicator]
    )
