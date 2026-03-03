"""
Ownership and filing tools for the FMP MCP server
"""
from typing import Optional

from src.api.client import fmp_api_request, FMP_V3_URL, FMP_V4_URL
from src.tools.utils import format_number, json_to_csv


async def get_insider_trading(symbol: str, limit: int = 20, format: str = "csv") -> str:
    """
    Get recent insider trading activity for a company (Form 4 filings)

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        limit: Number of transactions to return (1-100)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Insider trading transactions
    """
    if not 1 <= limit <= 100:
        return "Error: limit must be between 1 and 100"

    data = await fmp_api_request("insider-trading", {"symbol": symbol, "limit": limit}, base_url=FMP_V4_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching insider trading for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No insider trading data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Insider Trading for {symbol}"]
    result.append(f"**Recent transactions**: {len(data)}")
    result.append("")

    for t in data:
        date = t.get('transactionDate', t.get('filingDate', 'N/A'))
        name = t.get('reportingName', 'Unknown')
        title = t.get('typeOfOwner', '')
        tx_type = t.get('transactionType', 'N/A')
        shares = t.get('securitiesTransacted', 'N/A')
        price = t.get('price', 'N/A')
        value = t.get('securitiesTransacted', 0) * t.get('price', 0) if isinstance(t.get('securitiesTransacted'), (int, float)) and isinstance(t.get('price'), (int, float)) else None

        result.append(f"### {name}" + (f" ({title})" if title else ""))
        result.append(f"**Date**: {date}")
        result.append(f"**Type**: {tx_type}")
        result.append(f"**Shares**: {format_number(shares)}")
        result.append(f"**Price**: ${format_number(price)}")
        if value:
            result.append(f"**Value**: ${format_number(round(value))}")
        result.append("")

    return "\n".join(result)


async def get_institutional_holders(symbol: str, format: str = "csv") -> str:
    """
    Get institutional holders (top funds/institutions) for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Institutional holder data
    """
    data = await fmp_api_request(f"institutional-holder/{symbol}", base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching institutional holders for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No institutional holder data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Institutional Holders for {symbol}"]
    result.append(f"**Total holders returned**: {len(data)}")
    result.append("")
    result.append("| Holder | Shares | Value | % Change | Date Filed |")
    result.append("|--------|--------|-------|----------|------------|")

    for h in data[:30]:  # Top 30
        holder = h.get('holder', 'N/A')
        shares = format_number(h.get('shares', 'N/A'))
        value = h.get('value', None)
        value_str = f"${format_number(value)}" if isinstance(value, (int, float)) else "N/A"
        change = h.get('change', None)
        change_str = f"{change:+,}" if isinstance(change, (int, float)) else "N/A"
        date = h.get('dateReported', 'N/A')
        result.append(f"| {holder} | {shares} | {value_str} | {change_str} | {date} |")

    return "\n".join(result)


async def get_13f_filings(cik: str, date: Optional[str] = None, format: str = "csv") -> str:
    """
    Get 13F filing holdings for an institutional investor by CIK number

    Args:
        cik: SEC Central Index Key for the institution (e.g., 0001067983 for Berkshire Hathaway)
        date: Filing date in YYYY-MM-DD format (optional, returns latest if omitted)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        13F filing holdings data
    """
    params = {}
    if date:
        params["date"] = date

    data = await fmp_api_request(f"form-thirteen/{cik}", params, base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching 13F filing for CIK {cik}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No 13F filing data found for CIK {cik}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# 13F Filing for CIK {cik}"]
    if date:
        result.append(f"**Filing date**: {date}")
    result.append(f"**Holdings returned**: {len(data)}")
    result.append("")
    result.append("| Company | Ticker | Shares | Value ($000s) | Type |")
    result.append("|---------|--------|--------|--------------|------|")

    for h in data[:50]:  # Top 50 holdings
        name = h.get('nameOfIssuer', 'N/A')
        ticker = h.get('tickercusip', h.get('cusip', 'N/A'))
        shares = format_number(h.get('shares', 'N/A'))
        value = format_number(h.get('value', 'N/A'))
        type_ = h.get('type', 'N/A')
        result.append(f"| {name} | {ticker} | {shares} | {value} | {type_} |")

    if len(data) > 50:
        result.append(f"\n*...and {len(data) - 50} more holdings*")

    return "\n".join(result)
