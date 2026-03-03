"""
Market data tools for the FMP MCP server
"""
from typing import Optional

from src.api.client import fmp_api_request, FMP_V3_URL
from src.tools.utils import format_number, pct_raw as _pct, json_to_csv


async def get_enterprise_value(symbol: str, period: str = "annual", limit: int = 1, format: str = "markdown") -> str:
    """
    Get enterprise value and its components for a company over time

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-40)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Enterprise value breakdown
    """
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"
    if not 1 <= limit <= 40:
        return "Error: limit must be between 1 and 40"

    data = await fmp_api_request("enterprise-values", {"symbol": symbol, "period": period, "limit": limit})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching enterprise value for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No enterprise value data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Enterprise Value for {symbol}"]

    for ev in data:
        result.append(f"\n## {ev.get('date', 'Unknown')}")
        result.append(f"**Stock Price**: ${format_number(ev.get('stockPrice', 'N/A'))}")
        result.append(f"**Shares Outstanding**: {format_number(ev.get('numberOfShares', 'N/A'))}")
        result.append(f"**Market Cap**: ${format_number(ev.get('marketCapitalization', 'N/A'))}")
        result.append(f"**(+) Total Debt**: ${format_number(ev.get('addTotalDebt', 'N/A'))}")
        result.append(f"**(-) Cash & Equivalents**: ${format_number(ev.get('minusCashAndCashEquivalents', 'N/A'))}")
        result.append(f"**Enterprise Value**: ${format_number(ev.get('enterpriseValue', 'N/A'))}")
        result.append("")

    return "\n".join(result)


async def get_sector_performance() -> str:
    """
    Get current performance of all market sectors (Technology, Healthcare, etc.)

    Returns:
        Sector performance data with percentage changes
    """
    data = await fmp_api_request("sector-performance", base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching sector performance: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No sector performance data available"

    result = ["# Sector Performance"]
    result.append("")
    result.append("| Sector | Change |")
    result.append("|--------|--------|")

    for sector in data:
        name = sector.get('sector', 'N/A')
        change = sector.get('changesPercentage', 'N/A')
        result.append(f"| {name} | {change} |")

    return "\n".join(result)


async def get_sp500_constituents() -> str:
    """
    Get list of all S&P 500 constituent companies with sector and sub-industry

    Returns:
        S&P 500 constituents list
    """
    data = await fmp_api_request("sp500_constituent", base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching S&P 500 constituents: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No S&P 500 constituent data available"

    result = ["# S&P 500 Constituents"]
    result.append(f"**Total**: {len(data)} companies")
    result.append("")

    # Group by sector
    sectors = {}
    for c in data:
        sector = c.get('sector', 'Unknown')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(c)

    for sector in sorted(sectors.keys()):
        companies = sectors[sector]
        tickers = [c.get('symbol', '?') for c in sorted(companies, key=lambda x: x.get('symbol', ''))]
        result.append(f"## {sector} ({len(companies)})")
        result.append(", ".join(tickers))
        result.append("")

    return "\n".join(result)


async def get_stock_news(tickers: Optional[str] = None, limit: int = 20, format: str = "markdown") -> str:
    """
    Get latest stock market news, optionally filtered by ticker(s)

    Args:
        tickers: Comma-separated ticker symbols to filter (e.g., "AAPL,MSFT"). Optional — returns general market news if omitted.
        limit: Number of news articles to return (1-50)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Stock news articles
    """
    if not 1 <= limit <= 50:
        return "Error: limit must be between 1 and 50"

    params = {"limit": limit}
    if tickers:
        params["tickers"] = tickers

    data = await fmp_api_request("stock_news", params, base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching stock news: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No stock news found"

    if format == "csv":
        return json_to_csv(data)

    title = f"# Stock News" + (f" for {tickers}" if tickers else "")
    result = [title]
    result.append("")

    for article in data:
        pub_date = article.get('publishedDate', 'N/A')
        headline = article.get('title', 'N/A')
        source = article.get('site', 'N/A')
        symbol = article.get('symbol', '')
        text = article.get('text', '')

        result.append(f"### {headline}")
        result.append(f"**Source**: {source} | **Date**: {pub_date}" + (f" | **Ticker**: {symbol}" if symbol else ""))
        if text:
            # Truncate long text
            summary = text[:300] + "..." if len(text) > 300 else text
            result.append(f"{summary}")
        result.append("")

    return "\n".join(result)


async def get_economic_calendar(from_date: Optional[str] = None, to_date: Optional[str] = None, format: str = "markdown") -> str:
    """
    Get economic calendar events (GDP, CPI, unemployment, Fed decisions, etc.)

    Args:
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Economic calendar events
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    data = await fmp_api_request("economic-calendar", params)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching economic calendar: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No economic calendar events found for the specified date range"

    if format == "csv":
        return json_to_csv(data)

    result = ["# Economic Calendar"]
    if from_date or to_date:
        result.append(f"**Period**: {from_date or '...'} to {to_date or '...'}")
    result.append(f"**Total events**: {len(data)}")
    result.append("")

    for event in data[:40]:
        date = event.get('date', 'N/A')
        name = event.get('event', 'N/A')
        country = event.get('country', '')
        actual = event.get('actual', None)
        estimate = event.get('estimate', None)
        previous = event.get('previous', None)

        line = f"**{name}**" + (f" ({country})" if country else "") + f" — {date}"
        result.append(line)
        details = []
        if actual is not None:
            details.append(f"Actual: {format_number(actual)}")
        if estimate is not None:
            details.append(f"Est: {format_number(estimate)}")
        if previous is not None:
            details.append(f"Prev: {format_number(previous)}")
        if details:
            result.append("  " + " | ".join(details))
        result.append("")

    if len(data) > 40:
        result.append(f"*...and {len(data) - 40} more events*")

    return "\n".join(result)


async def get_ipo_calendar(from_date: Optional[str] = None, to_date: Optional[str] = None, format: str = "markdown") -> str:
    """
    Get upcoming and recent IPO (Initial Public Offering) calendar

    Args:
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        IPO calendar data
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    data = await fmp_api_request("ipo_calendar", params, base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching IPO calendar: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No IPO calendar data found for the specified date range"

    if format == "csv":
        return json_to_csv(data)

    result = ["# IPO Calendar"]
    if from_date or to_date:
        result.append(f"**Period**: {from_date or '...'} to {to_date or '...'}")
    result.append(f"**Total**: {len(data)}")
    result.append("")

    for ipo in data[:30]:
        symbol = ipo.get('symbol', 'N/A')
        company = ipo.get('company', 'N/A')
        date = ipo.get('date', 'N/A')
        exchange = ipo.get('exchange', '')
        price_range = ipo.get('priceRange', 'N/A')
        shares = ipo.get('shares', None)

        result.append(f"### {company} ({symbol})")
        result.append(f"**Date**: {date}" + (f" | **Exchange**: {exchange}" if exchange else ""))
        result.append(f"**Price Range**: {price_range}")
        if isinstance(shares, (int, float)):
            result.append(f"**Shares Offered**: {format_number(shares)}")
        result.append("")

    return "\n".join(result)
