from typing import Annotated
from datetime import datetime


def get_news(
    ticker: Annotated[str, "ticker symbol or asset name, e.g. BITCOIN, BTC"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        return "ddgs is not installed. Add ddgs to dependencies."

    month_year = datetime.strptime(end_date, "%Y-%m-%d").strftime("%B %Y")
    queries = [
        f"{ticker} news {month_year}",
        f"{ticker} price {month_year} forecast analytics",
        f"{ticker} negative news {month_year} price drop regulatory problems",
        f"{ticker} negative news {month_year} problems regulator crackdown",
        f"{ticker} security hackers fraud regulation negative news problems",
    ]
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    seen_titles: set = set()
    all_results = []
    try:
        for query in queries:
            results = DDGS().news(query, max_results=20)
            for article in results:
                title = article.get("title", "")
                if title not in seen_titles:
                    seen_titles.add(title)
                    all_results.append(article)
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"

    if not all_results:
        return f"No news found for {ticker} between {start_date} and {end_date}"

    news_str = ""
    count = 0

    for article in all_results:
        pub_date_str = article.get("date", "")
        if pub_date_str:
            try:
                pub_dt = datetime.fromisoformat(pub_date_str[:10])
                if not (start_dt <= pub_dt <= end_dt):
                    continue
            except ValueError:
                pass

        title = article.get("title", "No title")
        body = article.get("body", "")
        source = article.get("source", "Unknown")
        url = article.get("url", "")

        news_str += f"### {title} (source: {source})\n"
        if body:
            news_str += f"{body}\n"
        if url:
            news_str += f"Link: {url}\n"
        news_str += "\n"
        count += 1

    if count == 0:
        return f"No news found for {ticker} between {start_date} and {end_date}"

    return f"## {ticker} News, from {start_date} to {end_date}:\n\n{news_str}"


def get_global_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    limit: Annotated[int, "Maximum number of articles to return"] = 10,
) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        return "ddgs is not installed. Add ddgs to dependencies."

    queries = [
        "cryptocurrency market Bitcoin outlook",
        "crypto regulation macroeconomics",
        "Bitcoin Ethereum price analysis",
        "global crypto market news",
    ]

    seen_titles: set = set()
    news_str = ""
    count = 0

    try:
        for query in queries:
            if count >= limit:
                break
            results = DDGS().news(query, max_results=limit)
            for article in results:
                if count >= limit:
                    break
                title = article.get("title", "No title")
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                body = article.get("body", "")
                source = article.get("source", "Unknown")
                url = article.get("url", "")

                news_str += f"### {title} (source: {source})\n"
                if body:
                    news_str += f"{body}\n"
                if url:
                    news_str += f"Link: {url}\n"
                news_str += "\n"
                count += 1
    except Exception as e:
        return f"Error fetching global news: {str(e)}"

    if not news_str:
        return f"No global news found for {curr_date}"

    return f"## Global Crypto Market News as of {curr_date}:\n\n{news_str}"
