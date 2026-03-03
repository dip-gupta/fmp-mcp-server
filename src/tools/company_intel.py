"""
Company intelligence tools for the FMP MCP server
"""
from src.api.client import fmp_api_request, FMP_V4_URL
from src.tools.utils import format_number, json_to_csv


async def get_company_peers(symbol: str) -> str:
    """
    Get peer companies (comparable companies in same sector/industry)

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        List of peer company tickers
    """
    data = await fmp_api_request("stock-peers", {"symbol": symbol})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching peers for {symbol}: {data.get('message', 'Unknown error')}"
    if not data:
        return f"No peer data found for symbol {symbol}"

    # API returns list with one object containing peersList
    item = data[0] if isinstance(data, list) and len(data) > 0 else data
    peers = item.get('peersList', [])

    if not peers:
        return f"No peers found for {symbol}"

    result = [f"# Peer Companies for {symbol}"]
    result.append("")
    result.append(f"**Peers**: {', '.join(peers)}")
    result.append(f"**Count**: {len(peers)}")

    return "\n".join(result)


async def get_company_outlook(symbol: str) -> str:
    """
    Get comprehensive company outlook (profile, metrics, ratios, rating, insider trades, key executives) in a single call

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        Comprehensive company outlook data
    """
    data = await fmp_api_request("company-outlook", {"symbol": symbol}, base_url=FMP_V4_URL)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching company outlook for {symbol}: {data.get('message', 'Unknown error')}"
    if not data:
        return f"No outlook data found for symbol {symbol}"

    result = [f"# Company Outlook for {symbol}"]
    result.append("")

    # Profile section
    profile = data.get('profile', {})
    if profile:
        result.append("## Profile")
        result.append(f"**Company**: {profile.get('companyName', 'N/A')}")
        result.append(f"**Sector**: {profile.get('sector', 'N/A')}")
        result.append(f"**Industry**: {profile.get('industry', 'N/A')}")
        result.append(f"**Market Cap**: ${format_number(profile.get('mktCap', 'N/A'))}")
        result.append(f"**Price**: ${format_number(profile.get('price', 'N/A'))}")
        result.append(f"**Beta**: {format_number(profile.get('beta', 'N/A'))}")
        result.append(f"**52W Range**: ${format_number(profile.get('range', 'N/A'))}")
        result.append(f"**Avg Volume**: {format_number(profile.get('volAvg', 'N/A'))}")
        result.append(f"**CEO**: {profile.get('ceo', 'N/A')}")
        result.append(f"**Employees**: {format_number(profile.get('fullTimeEmployees', 'N/A'))}")
        result.append(f"**IPO Date**: {profile.get('ipoDate', 'N/A')}")
        result.append("")

    # Rating section
    rating = data.get('rating', [])
    if rating:
        r = rating[0] if isinstance(rating, list) else rating
        result.append("## Rating")
        result.append(f"**Overall Rating**: {r.get('ratingScore', 'N/A')}/5 — {r.get('ratingRecommendation', 'N/A')}")
        result.append(f"**DCF Score**: {r.get('ratingDetailsDCFScore', 'N/A')}/5")
        result.append(f"**ROE Score**: {r.get('ratingDetailsROEScore', 'N/A')}/5")
        result.append(f"**ROA Score**: {r.get('ratingDetailsROAScore', 'N/A')}/5")
        result.append(f"**PE Score**: {r.get('ratingDetailsPEScore', 'N/A')}/5")
        result.append(f"**PB Score**: {r.get('ratingDetailsPBScore', 'N/A')}/5")
        result.append("")

    # Key metrics (latest)
    metrics = data.get('metrics', {})
    if isinstance(metrics, list) and len(metrics) > 0:
        m = metrics[0]
        result.append("## Latest Key Metrics")
        result.append(f"**Date**: {m.get('date', 'N/A')}")
        result.append(f"**Revenue per Share**: ${format_number(m.get('revenuePerShare', 'N/A'))}")
        result.append(f"**PE Ratio**: {format_number(m.get('peRatio', 'N/A'))}")
        result.append(f"**EV/EBITDA**: {format_number(m.get('evToEbitda', 'N/A'))}")
        result.append(f"**ROIC**: {format_number(m.get('roic', 'N/A'))}")
        result.append(f"**Dividend Yield**: {format_number(m.get('dividendYield', 'N/A'))}")
        result.append("")

    # Key executives
    executives = data.get('keyExecutives', [])
    if executives:
        result.append("## Key Executives")
        for exec_ in executives[:10]:
            name = exec_.get('name', 'N/A')
            title = exec_.get('title', 'N/A')
            pay = exec_.get('pay', None)
            pay_str = f" — Pay: ${format_number(pay)}" if isinstance(pay, (int, float)) and pay > 0 else ""
            result.append(f"- **{name}**: {title}{pay_str}")
        result.append("")

    # Stock news (latest)
    news = data.get('stockNews', [])
    if news:
        result.append("## Recent News")
        for n in news[:5]:
            title = n.get('title', 'N/A')
            date = n.get('publishedDate', 'N/A')
            result.append(f"- [{title}] ({date})")
        result.append("")

    return "\n".join(result)


async def get_revenue_product_segmentation(symbol: str, period: str = "annual") -> str:
    """
    Get revenue breakdown by product/business segment for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"

    Returns:
        Revenue segmentation by product
    """
    params = {"symbol": symbol, "period": period}
    data = await fmp_api_request("revenue-product-segmentation", params)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching product segmentation for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or (isinstance(data, list) and len(data) == 0):
        return f"No product segmentation data found for symbol {symbol}"

    result = [f"# Revenue by Product Segment for {symbol}"]
    result.append("")

    # API returns list of objects, each with a date-keyed dict
    for entry in data[:8]:  # Last 8 periods
        if isinstance(entry, dict):
            for date_key, segments in entry.items():
                if isinstance(segments, dict):
                    result.append(f"## {date_key}")
                    total = sum(v for v in segments.values() if isinstance(v, (int, float)))
                    for seg_name, seg_val in sorted(segments.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True):
                        if isinstance(seg_val, (int, float)):
                            pct = (seg_val / total * 100) if total > 0 else 0
                            result.append(f"- **{seg_name}**: ${format_number(round(seg_val))} ({pct:.1f}%)")
                    if total > 0:
                        result.append(f"- **Total**: ${format_number(round(total))}")
                    result.append("")

    return "\n".join(result)


async def get_revenue_geographic_segmentation(symbol: str, period: str = "annual") -> str:
    """
    Get revenue breakdown by geographic region for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"

    Returns:
        Revenue segmentation by geography
    """
    params = {"symbol": symbol, "period": period}
    data = await fmp_api_request("revenue-geographic-segmentation", params)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching geographic segmentation for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or (isinstance(data, list) and len(data) == 0):
        return f"No geographic segmentation data found for symbol {symbol}"

    result = [f"# Revenue by Geography for {symbol}"]
    result.append("")

    for entry in data[:8]:
        if isinstance(entry, dict):
            for date_key, segments in entry.items():
                if isinstance(segments, dict):
                    result.append(f"## {date_key}")
                    total = sum(v for v in segments.values() if isinstance(v, (int, float)))
                    for geo_name, geo_val in sorted(segments.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True):
                        if isinstance(geo_val, (int, float)):
                            pct = (geo_val / total * 100) if total > 0 else 0
                            result.append(f"- **{geo_name}**: ${format_number(round(geo_val))} ({pct:.1f}%)")
                    if total > 0:
                        result.append(f"- **Total**: ${format_number(round(total))}")
                    result.append("")

    return "\n".join(result)


async def get_employee_count(symbol: str, format: str = "csv") -> str:
    """
    Get historical employee count for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Employee count history
    """
    data = await fmp_api_request("employee-count", {"symbol": symbol})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching employee count for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No employee count data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Employee Count for {symbol}"]
    result.append("")

    # Show company name from first entry
    if data[0].get('companyName'):
        result.append(f"**Company**: {data[0]['companyName']}")
        result.append("")

    result.append("| Period | Employee Count | Source |")
    result.append("|--------|---------------|--------|")

    for entry in data[:20]:
        period = entry.get('periodOfReport', entry.get('filingDate', 'N/A'))
        count = format_number(entry.get('employeeCount', 'N/A'))
        source = entry.get('source', 'N/A')
        result.append(f"| {period} | {count} | {source} |")

    return "\n".join(result)
