"""
Earnings-related tools for the FMP MCP server
"""
from typing import Optional

from src.api.client import fmp_api_request, FMP_V3_URL
from src.tools.utils import format_number, json_to_csv


async def get_earnings_calendar(from_date: Optional[str] = None, to_date: Optional[str] = None, format: str = "markdown") -> str:
    """
    Get upcoming and recent earnings announcements across all companies

    Args:
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Earnings calendar data
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    data = await fmp_api_request("earnings-calendar", params)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching earnings calendar: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return "No earnings calendar data found for the specified date range"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Earnings Calendar"]
    if from_date or to_date:
        result.append(f"**Period**: {from_date or '...'} to {to_date or '...'}")
    result.append(f"**Total entries**: {len(data)}")
    result.append("")

    for entry in data[:50]:  # Cap at 50 entries
        symbol = entry.get('symbol', 'N/A')
        date = entry.get('date', 'N/A')
        eps_est = entry.get('epsEstimated', 'N/A')
        eps_act = entry.get('eps', None)
        rev_est = entry.get('revenueEstimated', 'N/A')
        rev_act = entry.get('revenue', None)
        time = entry.get('time', '')

        line = f"**{symbol}** ({date}{', ' + time if time else ''})"
        if eps_act is not None:
            line += f" — EPS: {format_number(eps_act)} (est: {format_number(eps_est)})"
        else:
            line += f" — EPS est: {format_number(eps_est)}"
        if rev_act is not None:
            line += f", Rev: ${format_number(rev_act)} (est: ${format_number(rev_est)})"
        else:
            line += f", Rev est: ${format_number(rev_est)}"
        result.append(line)

    if len(data) > 50:
        result.append(f"\n*...and {len(data) - 50} more entries*")

    return "\n".join(result)


async def get_earnings_surprises(symbol: str, format: str = "markdown") -> str:
    """
    Get historical earnings surprises (actual vs estimated EPS) for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Earnings surprise history
    """
    data = await fmp_api_request(f"earnings-surprises/{symbol}", base_url=FMP_V3_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching earnings surprises for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No earnings surprise data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Earnings Surprises for {symbol}"]
    result.append("")
    result.append("| Date | Actual EPS | Estimated EPS | Surprise |")
    result.append("|------|-----------|--------------|----------|")

    for entry in data[:20]:  # Last 20 quarters
        date = entry.get('date', 'N/A')
        actual = entry.get('actualEarningResult', 'N/A')
        estimated = entry.get('estimatedEarning', 'N/A')
        if isinstance(actual, (int, float)) and isinstance(estimated, (int, float)) and estimated != 0:
            surprise_pct = ((actual - estimated) / abs(estimated)) * 100
            surprise_str = f"{surprise_pct:+.1f}%"
        else:
            surprise_str = "N/A"
        result.append(f"| {date} | {format_number(actual)} | {format_number(estimated)} | {surprise_str} |")

    return "\n".join(result)
