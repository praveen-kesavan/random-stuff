"""Configuration settings for the deep discount automation project."""

# API Endpoints
STAGE_OFFER_SEARCH_URL = "https://us.ecom-stg.samsung.com/v4/price-engine/offers/_search"
PROD_OFFER_SEARCH_URL = "https://us.ecom.samsung.com/v4/price-engine/offers/_search"
STAGE_FETCH_PRICE_URL = "https://us.ecom-stg.samsung.com/v4/price-engine/product-pricing/_fetch-current-price"

# API Headers
DEFAULT_HEADERS = {
    'content-type': 'application/json'
}

# Store Types and Site IDs
STORE_TYPE_B2C = "B2C"
SITE_ID_SEA_EPP = "3155000"
SITE_ID_GENERAL_EPP = "4789760940"

# Batch Processing
MAX_SKUS_PER_REQUEST = 50

# Excel Configuration
EXCEL_SHEET_NAMES = {
    'AGGREGATION': 'Aggregation'
}