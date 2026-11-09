COUNTRY_CODES = {"NL": "NL", "Netherlands": "NL"}


def country_code(country: str) -> str:
    try:
        return COUNTRY_CODES[country]
    except KeyError as error:
        raise ValueError(f"Unsupported test-data country: {country}") from error
