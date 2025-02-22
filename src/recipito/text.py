"""Text processing utilities."""


def convert_characters(text: str) -> str:
    """Convert unicode fractions and symbols to standard text.
    
    This function replaces unicode fraction characters and special symbols with
    their ASCII text equivalents.

    Args:
        text: The input text containing unicode characters to convert.

    Returns:
        The text with unicode fractions and symbols converted to standard ASCII.

    Example:
        >>> convert_characters("½ cup")
        "1/2 cup"
        >>> convert_characters("25° C")
        "25° C"
    """
    fraction_map = {
        "\u00bc": "1/4",
        "\u00bd": "1/2",
        "\u00be": "3/4",
        "\u2153": "1/3",
        "\u2154": "2/3",
        "\u2155": "1/5",
        "\u2156": "2/5",
        "\u2157": "3/5",
        "\u2158": "4/5",
        "\u2159": "1/6",
        "\u215a": "5/6",
        "\u215b": "1/8",
        "\u215c": "3/8",
        "\u215d": "5/8",
        "\u215e": "7/8",
        "\u00b0": "°",  # Convert unicode degree symbol to standard degree symbol
    }
    for unicode_char, replacement in fraction_map.items():
        text = text.replace(unicode_char, replacement)
    return text
