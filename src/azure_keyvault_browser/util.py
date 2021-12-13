from datetime import datetime


def replace_last(string: str, find: str, replace: str) -> str:
    """Replace the last occurrence of a string.

    Args:
        string (str): The string to replace.
        find (str): The string to find.
        replace (str): The string to replace with.

    Returns:
        str: The replaced string.
    """

    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]


def format_datetime(dt: datetime) -> str:
    """Format a datetime object to a string.

    Args:
        dt (datetime): The datetime object to format.

    Returns:
        str: The formatted datetime.
    """

    return dt.strftime("%Y-%m-%d %H:%M:%S")
