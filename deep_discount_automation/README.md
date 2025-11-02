# Deep Discount Automation

This project automates the process of analyzing deep discount offers for Samsung's e-commerce platform. It processes offers across staging and production environments, analyzes SKUs, and generates detailed Excel reports.

## Features

- Fetches and compares offers between staging and production environments
- Processes multiple SKUs and their associated offers
- Handles non-stackable offer filtering
- Generates detailed Excel reports with:
  - Individual SKU sheets with offer details
  - Aggregation sheet with pricing and EPP information
- Supports batch processing for large SKU lists

## Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - pandas
  - openpyxl
  - python-dotenv

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script by providing a primary offer ID:

```bash
python src/main.py <primary_offer_id>
```

The script will:
1. Fetch the primary offer details
2. Process each SKU in the offer's discounted_skus array
3. Generate an Excel file named `<primary_offer_id>.xlsx` containing:
   - Individual sheets for each SKU with offer details
   - An aggregation sheet with pricing and EPP information

## Excel Output Format

### SKU Sheets
Each SKU gets its own sheet containing:
- Offer ID
- Offer Name
- Type
- Channel
- Value and Type (from discount_description)
- Coupon Code Triggered
- Trigger Tags
- Concurrent
- Apply Mode
- Applicable Sites
- Restricted SKUs

### Aggregation Sheet
The first sheet contains:
- SKU IDs
- MSRP Price
- Sale Price
- SEA EPP Information
- General EPP Information
- Offer Details