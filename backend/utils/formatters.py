"""
Formatters
Data formatting utilities
"""

from datetime import datetime, timedelta
from typing import Optional


def format_datetime(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format datetime object
    
    Args:
        dt: Datetime object
        format_string: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_string)


def format_currency(
    amount: float,
    currency: str = "USD",
    locale: str = "en_US"
) -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)
        locale: Locale for formatting
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "IDR": "Rp",
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency == "JPY":
        return f"{symbol}{int(amount):,}"
    
    return f"{symbol}{amount:,.2f}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration (e.g., "2h 30m")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    if seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    
    if seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}d {hours}h" if hours > 0 else f"{days}d"


def format_percentage(
    value: float,
    decimals: int = 1
) -> str:
    """
    Format percentage
    
    Args:
        value: Value (0-1 or 0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    # Assume if value > 1, it's already in percentage
    if value > 1:
        return f"{value:.{decimals}f}%"
    
    return f"{value * 100:.{decimals}f}%"


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_phone_number(
    phone: str,
    country_code: str = "US"
) -> str:
    """
    Format phone number
    
    Args:
        phone: Phone number
        country_code: Country code
        
    Returns:
        Formatted phone number
    """
    # Remove non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    if country_code == "US":
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone


def format_number(
    number: float,
    decimals: int = 2,
    use_separator: bool = True
) -> str:
    """
    Format number with thousands separator
    
    Args:
        number: Number to format
        decimals: Number of decimal places
        use_separator: Use thousands separator
        
    Returns:
        Formatted number string
    """
    if use_separator:
        return f"{number:,.{decimals}f}"
    
    return f"{number:.{decimals}f}"


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago")
    
    Args:
        dt: Datetime object
        
    Returns:
        Relative time string
    """
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.total_seconds() < 60:
        return "just now"
    
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    if diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    
    if diff.days < 30:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    
    if diff.days < 365:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    
    years = diff.days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"


def format_json_pretty(data: dict, indent: int = 2) -> str:
    """
    Format JSON data in pretty format
    
    Args:
        data: Dictionary to format
        indent: Indentation spaces
        
    Returns:
        Pretty-formatted JSON string
    """
    import json
    return json.dumps(data, indent=indent, sort_keys=True)
