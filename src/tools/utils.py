"""
Shared utilities for FMP MCP tools
"""
import io
import csv
from typing import Any, List, Dict


def format_number(value: Any) -> str:
    """Format a number with commas, or return as-is if not a number"""
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return str(value)


def pct(value: Any) -> str:
    """Format a value as percentage if numeric (assumes decimal input like 0.25 → 25.00%)"""
    if isinstance(value, (int, float)):
        return f"{value * 100:.2f}%"
    return str(value)


def pct_raw(value: Any) -> str:
    """Format a value as percentage if numeric (assumes already percentage like 5.2 → 5.20%)"""
    if isinstance(value, (int, float)):
        return f"{value:.2f}%"
    return str(value)


def json_to_csv(data: List[Dict]) -> str:
    """
    Convert a list of flat dicts (API JSON response) to CSV string.
    Uses all keys from the first record as headers.
    """
    if not data or not isinstance(data, list) or len(data) == 0:
        return ""

    # Collect all keys across all records to handle sparse data
    headers = list(data[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction='ignore')
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    return output.getvalue()
