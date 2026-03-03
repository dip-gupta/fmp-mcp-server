"""
Financial statement-related tools for the FMP MCP server

This module contains tools related to the Financial Statements section of the Financial Modeling Prep API
"""
from typing import Dict, Any, Optional, List, Union

from src.api.client import fmp_api_request
from src.tools.utils import format_number, json_to_csv


async def get_income_statement(symbol: str, period: str = "annual", limit: int = 1, format: str = "markdown") -> str:
    """
    Get income statement for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-120)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Income statement data
    """
    # Validate inputs
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"

    if not 1 <= limit <= 120:
        return "Error: limit must be between 1 and 120"

    endpoint = "income-statement"
    params = {"symbol": symbol, "period": period, "limit": limit}

    # Call API
    data = await fmp_api_request(endpoint, params)

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching income statement for {symbol}: {data.get('message', 'Unknown error')}"

    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No income statement data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    # Format the response
    result = [f"# Income Statement for {symbol}"]
    
    for statement in data:
        # Header information
        result.append(f"\n## Period: {statement.get('date', 'Unknown')}")
        result.append(f"**Report Type**: {statement.get('period', 'Unknown').capitalize()}")
        result.append(f"**Currency**: {statement.get('reportedCurrency', 'USD')}")
        result.append(f"**Fiscal Year**: {statement.get('fiscalYear', 'N/A')}")
        result.append(f"**Filing Date**: {statement.get('filingDate', 'N/A')}")
        result.append(f"**Accepted Date**: {statement.get('acceptedDate', 'N/A')}")
        result.append(f"**CIK**: {statement.get('cik', 'N/A')}")
        result.append("")
        
        # Revenue section
        result.append("### Revenue Metrics")
        result.append(f"**Revenue**: ${format_number(statement.get('revenue', 'N/A'))}")
        result.append(f"**Cost of Revenue**: ${format_number(statement.get('costOfRevenue', 'N/A'))}")
        result.append(f"**Gross Profit**: ${format_number(statement.get('grossProfit', 'N/A'))}")
        result.append("")
        
        # Expense section
        result.append("### Expense Breakdown")
        result.append(f"**Research and Development**: ${format_number(statement.get('researchAndDevelopmentExpenses', 'N/A'))}")
        result.append(f"**Selling, General, and Administrative**: ${format_number(statement.get('sellingGeneralAndAdministrativeExpenses', 'N/A'))}")
        result.append(f"**General and Administrative**: ${format_number(statement.get('generalAndAdministrativeExpenses', 'N/A'))}")
        result.append(f"**Selling and Marketing**: ${format_number(statement.get('sellingAndMarketingExpenses', 'N/A'))}")
        result.append(f"**Other Expenses**: ${format_number(statement.get('otherExpenses', 'N/A'))}")
        result.append(f"**Operating Expenses**: ${format_number(statement.get('operatingExpenses', 'N/A'))}")
        result.append(f"**Cost and Expenses**: ${format_number(statement.get('costAndExpenses', 'N/A'))}")
        result.append(f"**Depreciation and Amortization**: ${format_number(statement.get('depreciationAndAmortization', 'N/A'))}")
        result.append("")
        
        # Income and profitability
        result.append("### Income and Profitability")
        result.append(f"**Net Interest Income**: ${format_number(statement.get('netInterestIncome', 'N/A'))}")
        result.append(f"**Interest Income**: ${format_number(statement.get('interestIncome', 'N/A'))}")
        result.append(f"**Interest Expense**: ${format_number(statement.get('interestExpense', 'N/A'))}")
        result.append(f"**Non-Operating Income**: ${format_number(statement.get('nonOperatingIncomeExcludingInterest', 'N/A'))}")
        result.append(f"**Other Income/Expenses Net**: ${format_number(statement.get('totalOtherIncomeExpensesNet', 'N/A'))}")
        result.append("")
        
        # Operating metrics
        result.append("### Operating Metrics")
        result.append(f"**Operating Income**: ${format_number(statement.get('operatingIncome', 'N/A'))}")
        result.append(f"**EBITDA**: ${format_number(statement.get('ebitda', 'N/A'))}")
        result.append(f"**EBIT**: ${format_number(statement.get('ebit', 'N/A'))}")
        result.append("")
        
        # Tax and net income
        result.append("### Tax and Net Income")
        result.append(f"**Income Before Tax**: ${format_number(statement.get('incomeBeforeTax', 'N/A'))}")
        result.append(f"**Income Tax Expense**: ${format_number(statement.get('incomeTaxExpense', 'N/A'))}")
        result.append(f"**Net Income from Continuing Operations**: ${format_number(statement.get('netIncomeFromContinuingOperations', 'N/A'))}")
        result.append(f"**Net Income from Discontinued Operations**: ${format_number(statement.get('netIncomeFromDiscontinuedOperations', 'N/A'))}")
        result.append(f"**Other Adjustments to Net Income**: ${format_number(statement.get('otherAdjustmentsToNetIncome', 'N/A'))}")
        result.append(f"**Net Income Deductions**: ${format_number(statement.get('netIncomeDeductions', 'N/A'))}")
        result.append(f"**Net Income**: ${format_number(statement.get('netIncome', 'N/A'))}")
        result.append(f"**Bottom Line Net Income**: ${format_number(statement.get('bottomLineNetIncome', 'N/A'))}")
        result.append("")
        
        # Per share data
        result.append("### Per Share Data")
        result.append(f"**EPS**: ${format_number(statement.get('eps', 'N/A'))}")
        result.append(f"**EPS Diluted**: ${format_number(statement.get('epsDiluted', 'N/A'))}")
        result.append(f"**Weighted Average Shares Outstanding**: {format_number(statement.get('weightedAverageShsOut', 'N/A'))}")
        result.append(f"**Weighted Average Shares Outstanding (Diluted)**: {format_number(statement.get('weightedAverageShsOutDil', 'N/A'))}")
    
    return "\n".join(result)


async def get_balance_sheet(symbol: str, period: str = "annual", limit: int = 1, format: str = "markdown") -> str:
    """
    Get balance sheet statement for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-120)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Balance sheet data
    """
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"
    if not 1 <= limit <= 120:
        return "Error: limit must be between 1 and 120"

    data = await fmp_api_request("balance-sheet-statement", {"symbol": symbol, "period": period, "limit": limit})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching balance sheet for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No balance sheet data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Balance Sheet for {symbol}"]

    for stmt in data:
        result.append(f"\n## Period: {stmt.get('date', 'Unknown')}")
        result.append(f"**Report Type**: {stmt.get('period', 'Unknown').capitalize()}")
        result.append(f"**Currency**: {stmt.get('reportedCurrency', 'USD')}")
        result.append("")

        result.append("### Assets")
        result.append(f"**Cash and Cash Equivalents**: ${format_number(stmt.get('cashAndCashEquivalents', 'N/A'))}")
        result.append(f"**Short-Term Investments**: ${format_number(stmt.get('shortTermInvestments', 'N/A'))}")
        result.append(f"**Cash and Short-Term Investments**: ${format_number(stmt.get('cashAndShortTermInvestments', 'N/A'))}")
        result.append(f"**Net Receivables**: ${format_number(stmt.get('netReceivables', 'N/A'))}")
        result.append(f"**Inventory**: ${format_number(stmt.get('inventory', 'N/A'))}")
        result.append(f"**Other Current Assets**: ${format_number(stmt.get('otherCurrentAssets', 'N/A'))}")
        result.append(f"**Total Current Assets**: ${format_number(stmt.get('totalCurrentAssets', 'N/A'))}")
        result.append(f"**Property, Plant & Equipment (Net)**: ${format_number(stmt.get('propertyPlantEquipmentNet', 'N/A'))}")
        result.append(f"**Goodwill**: ${format_number(stmt.get('goodwill', 'N/A'))}")
        result.append(f"**Intangible Assets**: ${format_number(stmt.get('intangibleAssets', 'N/A'))}")
        result.append(f"**Long-Term Investments**: ${format_number(stmt.get('longTermInvestments', 'N/A'))}")
        result.append(f"**Other Non-Current Assets**: ${format_number(stmt.get('otherNonCurrentAssets', 'N/A'))}")
        result.append(f"**Total Non-Current Assets**: ${format_number(stmt.get('totalNonCurrentAssets', 'N/A'))}")
        result.append(f"**Total Assets**: ${format_number(stmt.get('totalAssets', 'N/A'))}")
        result.append("")

        result.append("### Liabilities")
        result.append(f"**Accounts Payable**: ${format_number(stmt.get('accountPayables', 'N/A'))}")
        result.append(f"**Short-Term Debt**: ${format_number(stmt.get('shortTermDebt', 'N/A'))}")
        result.append(f"**Deferred Revenue (Current)**: ${format_number(stmt.get('deferredRevenue', 'N/A'))}")
        result.append(f"**Other Current Liabilities**: ${format_number(stmt.get('otherCurrentLiabilities', 'N/A'))}")
        result.append(f"**Total Current Liabilities**: ${format_number(stmt.get('totalCurrentLiabilities', 'N/A'))}")
        result.append(f"**Long-Term Debt**: ${format_number(stmt.get('longTermDebt', 'N/A'))}")
        result.append(f"**Other Non-Current Liabilities**: ${format_number(stmt.get('otherNonCurrentLiabilities', 'N/A'))}")
        result.append(f"**Total Non-Current Liabilities**: ${format_number(stmt.get('totalNonCurrentLiabilities', 'N/A'))}")
        result.append(f"**Total Liabilities**: ${format_number(stmt.get('totalLiabilities', 'N/A'))}")
        result.append("")

        result.append("### Equity")
        result.append(f"**Common Stock**: ${format_number(stmt.get('commonStock', 'N/A'))}")
        result.append(f"**Retained Earnings**: ${format_number(stmt.get('retainedEarnings', 'N/A'))}")
        result.append(f"**Other Comprehensive Income/Loss**: ${format_number(stmt.get('accumulatedOtherComprehensiveIncomeLoss', 'N/A'))}")
        result.append(f"**Total Stockholders' Equity**: ${format_number(stmt.get('totalStockholdersEquity', 'N/A'))}")
        result.append(f"**Total Equity**: ${format_number(stmt.get('totalEquity', 'N/A'))}")
        result.append(f"**Total Liabilities & Equity**: ${format_number(stmt.get('totalLiabilitiesAndStockholdersEquity', 'N/A'))}")
        result.append("")

        result.append("### Key Metrics")
        result.append(f"**Total Debt**: ${format_number(stmt.get('totalDebt', 'N/A'))}")
        result.append(f"**Net Debt**: ${format_number(stmt.get('netDebt', 'N/A'))}")
        result.append(f"**Total Investments**: ${format_number(stmt.get('totalInvestments', 'N/A'))}")

    return "\n".join(result)


async def get_cash_flow_statement(symbol: str, period: str = "annual", limit: int = 1, format: str = "markdown") -> str:
    """
    Get cash flow statement for a company

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: Data period - "annual" or "quarter"
        limit: Number of periods to return (1-120)
        format: Output format - "markdown" for readable text, "csv" for raw CSV data

    Returns:
        Cash flow statement data
    """
    if period not in ["annual", "quarter"]:
        return "Error: period must be 'annual' or 'quarter'"
    if not 1 <= limit <= 120:
        return "Error: limit must be between 1 and 120"

    data = await fmp_api_request("cash-flow-statement", {"symbol": symbol, "period": period, "limit": limit})

    if isinstance(data, dict) and "error" in data:
        return f"Error fetching cash flow statement for {symbol}: {data.get('message', 'Unknown error')}"
    if not data or not isinstance(data, list) or len(data) == 0:
        return f"No cash flow statement data found for symbol {symbol}"

    if format == "csv":
        return json_to_csv(data)

    result = [f"# Cash Flow Statement for {symbol}"]

    for stmt in data:
        result.append(f"\n## Period: {stmt.get('date', 'Unknown')}")
        result.append(f"**Report Type**: {stmt.get('period', 'Unknown').capitalize()}")
        result.append(f"**Currency**: {stmt.get('reportedCurrency', 'USD')}")
        result.append("")

        result.append("### Operating Activities")
        result.append(f"**Net Income**: ${format_number(stmt.get('netIncome', 'N/A'))}")
        result.append(f"**Depreciation & Amortization**: ${format_number(stmt.get('depreciationAndAmortization', 'N/A'))}")
        result.append(f"**Stock-Based Compensation**: ${format_number(stmt.get('stockBasedCompensation', 'N/A'))}")
        result.append(f"**Change in Working Capital**: ${format_number(stmt.get('changeInWorkingCapital', 'N/A'))}")
        result.append(f"**Accounts Receivables**: ${format_number(stmt.get('accountsReceivables', 'N/A'))}")
        result.append(f"**Inventory**: ${format_number(stmt.get('inventory', 'N/A'))}")
        result.append(f"**Accounts Payables**: ${format_number(stmt.get('accountsPayables', 'N/A'))}")
        result.append(f"**Other Working Capital**: ${format_number(stmt.get('otherWorkingCapital', 'N/A'))}")
        result.append(f"**Other Non-Cash Items**: ${format_number(stmt.get('otherNonCashItems', 'N/A'))}")
        result.append(f"**Operating Cash Flow**: ${format_number(stmt.get('operatingCashFlow', 'N/A'))}")
        result.append("")

        result.append("### Investing Activities")
        result.append(f"**Capital Expenditure**: ${format_number(stmt.get('capitalExpenditure', 'N/A'))}")
        result.append(f"**Acquisitions (Net)**: ${format_number(stmt.get('acquisitionsNet', 'N/A'))}")
        result.append(f"**Purchases of Investments**: ${format_number(stmt.get('purchasesOfInvestments', 'N/A'))}")
        result.append(f"**Sales/Maturities of Investments**: ${format_number(stmt.get('salesMaturitiesOfInvestments', 'N/A'))}")
        result.append(f"**Other Investing Activities**: ${format_number(stmt.get('otherInvestingActivites', 'N/A'))}")
        result.append(f"**Investing Cash Flow**: ${format_number(stmt.get('netCashUsedForInvestingActivites', 'N/A'))}")
        result.append("")

        result.append("### Financing Activities")
        result.append(f"**Debt Repayment**: ${format_number(stmt.get('debtRepayment', 'N/A'))}")
        result.append(f"**Common Stock Issued**: ${format_number(stmt.get('commonStockIssued', 'N/A'))}")
        result.append(f"**Common Stock Repurchased**: ${format_number(stmt.get('commonStockRepurchased', 'N/A'))}")
        result.append(f"**Dividends Paid**: ${format_number(stmt.get('dividendsPaid', 'N/A'))}")
        result.append(f"**Other Financing Activities**: ${format_number(stmt.get('otherFinancingActivites', 'N/A'))}")
        result.append(f"**Financing Cash Flow**: ${format_number(stmt.get('netCashUsedProvidedByFinancingActivities', 'N/A'))}")
        result.append("")

        result.append("### Summary")
        result.append(f"**Net Change in Cash**: ${format_number(stmt.get('netChangeInCash', 'N/A'))}")
        result.append(f"**Cash at End of Period**: ${format_number(stmt.get('cashAtEndOfPeriod', 'N/A'))}")
        result.append(f"**Cash at Beginning of Period**: ${format_number(stmt.get('cashAtBeginningOfPeriod', 'N/A'))}")
        result.append(f"**Free Cash Flow**: ${format_number(stmt.get('freeCashFlow', 'N/A'))}")

    return "\n".join(result)
