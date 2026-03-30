# Estimated shipping costs (USD) to Australia by country of origin.
# Adjust values in this table to reflect real-world shipping rates.
SHIPPING_TABLE: dict[str, float] = {
    "Australia": 8.0,
    "New Zealand": 12.0,
    "United Kingdom": 18.0,
    "United States": 22.0,
    "Canada": 22.0,
    "Germany": 20.0,
    "France": 20.0,
    "Netherlands": 20.0,
    "Belgium": 20.0,
    "Italy": 20.0,
    "Spain": 20.0,
    "Sweden": 20.0,
    "Denmark": 20.0,
    "Norway": 22.0,
    "Switzerland": 22.0,
    "Austria": 20.0,
    "Poland": 20.0,
    "Czech Republic": 20.0,
    "Finland": 20.0,
    "Portugal": 20.0,
    "Japan": 18.0,
    "South Korea": 18.0,
    "Hong Kong": 16.0,
    "Singapore": 16.0,
}


def get_shipping_cost(ships_from: str | None, fallback: float = 22.0) -> float:
    """Return estimated USD shipping cost to Australia for a given origin country."""
    if ships_from is None:
        return fallback
    return SHIPPING_TABLE.get(ships_from, fallback)
