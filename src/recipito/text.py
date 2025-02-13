"""Text processing utilities."""


def convert_characters(text: str) -> str:
    """Convert unicode fractions and symbols to standard text."""
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
