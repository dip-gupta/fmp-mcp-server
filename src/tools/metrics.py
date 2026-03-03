"""
Financial metrics and ratios tools for the FMP MCP server
"""
from src.api.client import fmp_api_request
from src.tools.utils import format_number, pct as _pct, json_to_csv


async def get_key_metrics(symbol: str, period: str = "annual", limit: int = 1, format: str = "csv") -> str:
    """
    Get key financial metrics for a company (revenue per share, PE, EV/EBITDA, ROIC, etc.)

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-40)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Key financial metrics
    """
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"
    if not 1 <= limit <= 40:
        return "Error: limit must be between 1 and 40"

    data = await fmp_api_request("key-metrics", {"symbol": symbol, "period": period, "limit": limit})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching key metrics for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No key metrics data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Key Metrics for {symbol}"]

    for m in data:
        result.append(f"\n## Period: {m.get('date', 'Unknown')}")
        result.append("")

        result.append("### Valuation")
        result.append(f"**Market Cap**: ${format_number(m.get('marketCap', 'N/A'))}")
        result.append(f"**Enterprise Value**: ${format_number(m.get('enterpriseValue', 'N/A'))}")
        result.append(f"**PE Ratio**: {format_number(m.get('peRatio', 'N/A'))}")
        result.append(f"**Price to Sales**: {format_number(m.get('priceToSalesRatio', 'N/A'))}")
        result.append(f"**PB Ratio**: {format_number(m.get('pbRatio', 'N/A'))}")
        result.append(f"**EV/EBITDA**: {format_number(m.get('evToEbitda', 'N/A'))}")
        result.append(f"**EV/Operating CF**: {format_number(m.get('evToOperatingCashFlow', 'N/A'))}")
        result.append(f"**EV/FCF**: {format_number(m.get('evToFreeCashFlow', 'N/A'))}")
        result.append("")

        result.append("### Per Share")
        result.append(f"**Revenue per Share**: ${format_number(m.get('revenuePerShare', 'N/A'))}")
        result.append(f"**Net Income per Share**: ${format_number(m.get('netIncomePerShare', 'N/A'))}")
        result.append(f"**Operating CF per Share**: ${format_number(m.get('operatingCashFlowPerShare', 'N/A'))}")
        result.append(f"**FCF per Share**: ${format_number(m.get('freeCashFlowPerShare', 'N/A'))}")
        result.append(f"**Book Value per Share**: ${format_number(m.get('bookValuePerShare', 'N/A'))}")
        result.append(f"**Tangible Book Value per Share**: ${format_number(m.get('tangibleBookValuePerShare', 'N/A'))}")
        result.append("")

        result.append("### Returns & Profitability")
        result.append(f"**ROIC**: {_pct(m.get('roic', 'N/A'))}")
        result.append(f"**ROE**: {_pct(m.get('roe', 'N/A'))}")
        result.append(f"**Return on Tangible Assets**: {_pct(m.get('returnOnTangibleAssets', 'N/A'))}")
        result.append(f"**Earnings Yield**: {_pct(m.get('earningsYield', 'N/A'))}")
        result.append(f"**FCF Yield**: {_pct(m.get('freeCashFlowYield', 'N/A'))}")
        result.append(f"**Dividend Yield**: {_pct(m.get('dividendYield', 'N/A'))}")
        result.append("")

        result.append("### Leverage & Liquidity")
        result.append(f"**Debt to Equity**: {format_number(m.get('debtToEquity', 'N/A'))}")
        result.append(f"**Debt to Assets**: {format_number(m.get('debtToAssets', 'N/A'))}")
        result.append(f"**Net Debt to EBITDA**: {format_number(m.get('netDebtToEBITDA', 'N/A'))}")
        result.append(f"**Current Ratio**: {format_number(m.get('currentRatio', 'N/A'))}")
        result.append(f"**Interest Coverage**: {format_number(m.get('interestCoverage', 'N/A'))}")
        result.append(f"**Working Capital**: ${format_number(m.get('workingCapital', 'N/A'))}")

    return "\n".join(result)


async def get_key_metrics_ttm(symbol: str) -> str:
    """
    Get trailing twelve months (TTM) key financial metrics for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        TTM key financial metrics
    """
    data = await fmp_api_request("key-metrics-ttm", {"symbol": symbol})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching TTM key metrics for {symbol}: {data.get('message', 'Unknown error')}"
    if not data:
        return f"No TTM key metrics data found for symbol {symbol}"

    # API may return list or dict
    m = data[0] if isinstance(data, list) else data

    result = [f"# Key Metrics TTM for {symbol}"]
    result.append("")
    result.append("### Valuation")
    result.append(f"**Market Cap**: ${format_number(m.get('marketCapTTM', 'N/A'))}")
    result.append(f"**Enterprise Value**: ${format_number(m.get('enterpriseValueTTM', 'N/A'))}")
    result.append(f"**PE Ratio**: {format_number(m.get('peRatioTTM', 'N/A'))}")
    result.append(f"**Price to Sales**: {format_number(m.get('priceToSalesRatioTTM', 'N/A'))}")
    result.append(f"**PB Ratio**: {format_number(m.get('pbRatioTTM', 'N/A'))}")
    result.append(f"**EV/EBITDA**: {format_number(m.get('evToEbitdaTTM', 'N/A'))}")
    result.append(f"**EV/FCF**: {format_number(m.get('evToFreeCashFlowTTM', 'N/A'))}")
    result.append("")
    result.append("### Per Share")
    result.append(f"**Revenue per Share**: ${format_number(m.get('revenuePerShareTTM', 'N/A'))}")
    result.append(f"**Net Income per Share**: ${format_number(m.get('netIncomePerShareTTM', 'N/A'))}")
    result.append(f"**Operating CF per Share**: ${format_number(m.get('operatingCashFlowPerShareTTM', 'N/A'))}")
    result.append(f"**FCF per Share**: ${format_number(m.get('freeCashFlowPerShareTTM', 'N/A'))}")
    result.append(f"**Book Value per Share**: ${format_number(m.get('bookValuePerShareTTM', 'N/A'))}")
    result.append("")
    result.append("### Returns & Profitability")
    result.append(f"**ROIC**: {_pct(m.get('roicTTM', 'N/A'))}")
    result.append(f"**ROE**: {_pct(m.get('roeTTM', 'N/A'))}")
    result.append(f"**Earnings Yield**: {_pct(m.get('earningsYieldTTM', 'N/A'))}")
    result.append(f"**FCF Yield**: {_pct(m.get('freeCashFlowYieldTTM', 'N/A'))}")
    result.append(f"**Dividend Yield**: {_pct(m.get('dividendYieldTTM', 'N/A'))}")
    result.append("")
    result.append("### Leverage & Liquidity")
    result.append(f"**Debt to Equity**: {format_number(m.get('debtToEquityTTM', 'N/A'))}")
    result.append(f"**Debt to Assets**: {format_number(m.get('debtToAssetsTTM', 'N/A'))}")
    result.append(f"**Net Debt to EBITDA**: {format_number(m.get('netDebtToEBITDATTM', 'N/A'))}")
    result.append(f"**Current Ratio**: {format_number(m.get('currentRatioTTM', 'N/A'))}")
    result.append(f"**Interest Coverage**: {format_number(m.get('interestCoverageTTM', 'N/A'))}")

    return "\n".join(result)


async def get_financial_ratios(symbol: str, period: str = "annual", limit: int = 1, format: str = "csv") -> str:
    """
    Get financial ratios for a company (margins, returns, efficiency, leverage ratios)

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-40)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Financial ratios data
    """
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"
    if not 1 <= limit <= 40:
        return "Error: limit must be between 1 and 40"

    data = await fmp_api_request("ratios", {"symbol": symbol, "period": period, "limit": limit})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching financial ratios for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No financial ratios data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Financial Ratios for {symbol}"]

    for r in data:
        result.append(f"\n## Period: {r.get('date', 'Unknown')}")
        result.append("")

        result.append("### Profitability")
        result.append(f"**Gross Profit Margin**: {_pct(r.get('grossProfitMargin', 'N/A'))}")
        result.append(f"**Operating Profit Margin**: {_pct(r.get('operatingProfitMargin', 'N/A'))}")
        result.append(f"**Net Profit Margin**: {_pct(r.get('netProfitMargin', 'N/A'))}")
        result.append(f"**EBITDA Margin**: {_pct(r.get('ebitdaMargin', 'N/A'))}")
        result.append(f"**Effective Tax Rate**: {_pct(r.get('effectiveTaxRate', 'N/A'))}")
        result.append("")

        result.append("### Returns")
        result.append(f"**ROE**: {_pct(r.get('returnOnEquity', 'N/A'))}")
        result.append(f"**ROA**: {_pct(r.get('returnOnAssets', 'N/A'))}")
        result.append(f"**ROIC**: {_pct(r.get('returnOnCapitalEmployed', 'N/A'))}")
        result.append("")

        result.append("### Liquidity")
        result.append(f"**Current Ratio**: {format_number(r.get('currentRatio', 'N/A'))}")
        result.append(f"**Quick Ratio**: {format_number(r.get('quickRatio', 'N/A'))}")
        result.append(f"**Cash Ratio**: {format_number(r.get('cashRatio', 'N/A'))}")
        result.append("")

        result.append("### Leverage")
        result.append(f"**Debt Ratio**: {format_number(r.get('debtRatio', 'N/A'))}")
        result.append(f"**Debt/Equity**: {format_number(r.get('debtEquityRatio', 'N/A'))}")
        result.append(f"**Interest Coverage**: {format_number(r.get('interestCoverage', 'N/A'))}")
        result.append("")

        result.append("### Efficiency")
        result.append(f"**Asset Turnover**: {format_number(r.get('assetTurnover', 'N/A'))}")
        result.append(f"**Inventory Turnover**: {format_number(r.get('inventoryTurnover', 'N/A'))}")
        result.append(f"**Receivables Turnover**: {format_number(r.get('receivablesTurnover', 'N/A'))}")
        result.append(f"**Days Sales Outstanding**: {format_number(r.get('daysOfSalesOutstanding', 'N/A'))}")
        result.append(f"**Days Inventory Outstanding**: {format_number(r.get('daysOfInventoryOutstanding', 'N/A'))}")
        result.append(f"**Days Payables Outstanding**: {format_number(r.get('daysOfPayablesOutstanding', 'N/A'))}")
        result.append(f"**Operating Cycle**: {format_number(r.get('operatingCycle', 'N/A'))}")
        result.append(f"**Cash Conversion Cycle**: {format_number(r.get('cashConversionCycle', 'N/A'))}")
        result.append("")

        result.append("### Valuation")
        result.append(f"**PE Ratio**: {format_number(r.get('priceEarningsRatio', 'N/A'))}")
        result.append(f"**Price to Book**: {format_number(r.get('priceToBookRatio', 'N/A'))}")
        result.append(f"**Price to Sales**: {format_number(r.get('priceToSalesRatio', 'N/A'))}")
        result.append(f"**Price to FCF**: {format_number(r.get('priceToFreeCashFlowsRatio', 'N/A'))}")
        result.append(f"**EV/EBITDA**: {format_number(r.get('enterpriseValueOverEBITDA', 'N/A'))}")
        result.append(f"**Price/Earnings to Growth**: {format_number(r.get('priceEarningsToGrowthRatio', 'N/A'))}")

    return "\n".join(result)


async def get_financial_ratios_ttm(symbol: str) -> str:
    """
    Get trailing twelve months (TTM) financial ratios for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        TTM financial ratios
    """
    data = await fmp_api_request("ratios-ttm", {"symbol": symbol})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching TTM ratios for {symbol}: {data.get('message', 'Unknown error')}"
    if not data:
        return f"No TTM ratios data found for symbol {symbol}"

    r = data[0] if isinstance(data, list) else data

    result = [f"# Financial Ratios TTM for {symbol}"]
    result.append("")
    result.append("### Profitability")
    result.append(f"**Gross Profit Margin**: {_pct(r.get('grossProfitMarginTTM', 'N/A'))}")
    result.append(f"**Operating Profit Margin**: {_pct(r.get('operatingProfitMarginTTM', 'N/A'))}")
    result.append(f"**Net Profit Margin**: {_pct(r.get('netProfitMarginTTM', 'N/A'))}")
    result.append(f"**EBITDA Margin**: {_pct(r.get('ebitdaMarginTTM', 'N/A'))}")
    result.append("")
    result.append("### Returns")
    result.append(f"**ROE**: {_pct(r.get('returnOnEquityTTM', 'N/A'))}")
    result.append(f"**ROA**: {_pct(r.get('returnOnAssetsTTM', 'N/A'))}")
    result.append(f"**ROIC**: {_pct(r.get('returnOnCapitalEmployedTTM', 'N/A'))}")
    result.append("")
    result.append("### Liquidity")
    result.append(f"**Current Ratio**: {format_number(r.get('currentRatioTTM', 'N/A'))}")
    result.append(f"**Quick Ratio**: {format_number(r.get('quickRatioTTM', 'N/A'))}")
    result.append(f"**Cash Ratio**: {format_number(r.get('cashRatioTTM', 'N/A'))}")
    result.append("")
    result.append("### Leverage")
    result.append(f"**Debt Ratio**: {format_number(r.get('debtRatioTTM', 'N/A'))}")
    result.append(f"**Debt/Equity**: {format_number(r.get('debtEquityRatioTTM', 'N/A'))}")
    result.append(f"**Interest Coverage**: {format_number(r.get('interestCoverageTTM', 'N/A'))}")
    result.append("")
    result.append("### Valuation")
    result.append(f"**PE Ratio**: {format_number(r.get('priceEarningsRatioTTM', 'N/A'))}")
    result.append(f"**Price to Book**: {format_number(r.get('priceToBookRatioTTM', 'N/A'))}")
    result.append(f"**Price to Sales**: {format_number(r.get('priceToSalesRatioTTM', 'N/A'))}")
    result.append(f"**Price to FCF**: {format_number(r.get('priceToFreeCashFlowsRatioTTM', 'N/A'))}")
    result.append(f"**EV/EBITDA**: {format_number(r.get('enterpriseValueOverEBITDATTM', 'N/A'))}")
    result.append(f"**Dividend Yield**: {_pct(r.get('dividendYieldTTM', 'N/A'))}")

    return "\n".join(result)
