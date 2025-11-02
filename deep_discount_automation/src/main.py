"""Main script for deep discount automation."""

import os
from typing import List, Dict
from api.client import APIClient
from processing.offer_processor import OfferProcessor
from processing.excel_handler import ExcelHandler
from config import MAX_SKUS_PER_REQUEST, SITE_ID_SEA_EPP, SITE_ID_GENERAL_EPP

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def process_primary_offer(client: APIClient, primary_offer_id: str) -> OfferProcessor:
    """Process the primary offer and return an offer processor instance."""
    # Get primary offer details
    primary_offer_response = client.search_offers_by_id(primary_offer_id)
    primary_offer = primary_offer_response.get('offers', [])[0]
    
    return OfferProcessor(primary_offer)

def process_sku(
    client: APIClient,
    processor: OfferProcessor,
    sku: str,
    excel_handler: ExcelHandler
) -> None:
    """Process a single SKU and create its sheet in the Excel file."""
    # Get offers for the SKU from both environments
    stg_response = client.search_offers_by_sku(sku)
    prod_response = client.search_offers_by_sku(sku, is_prod=True)
    
    stg_offers = stg_response.get('offers', [])
    prod_offers = prod_response.get('offers', [])
    
    # Filter offers
    offers_list, not_in_stg = processor.filter_duplicate_offers(stg_offers, prod_offers)
    offers_list = processor.filter_by_sku(offers_list, sku)
    offers_list = processor.filter_non_stackable(offers_list)
    
    # Create SKU sheet
    excel_handler.create_sku_sheet(sku, offers_list)
    
    return offers_list

def fetch_price_data(client: APIClient, skus: List[str]) -> tuple[Dict, Dict, Dict]:
    """Fetch price data for SKUs including EPP pricing."""
    regular_price_data = client.fetch_current_price(skus)
    sea_epp_data = client.fetch_current_price(skus, SITE_ID_SEA_EPP)
    general_epp_data = client.fetch_current_price(skus, SITE_ID_GENERAL_EPP)
    
    return regular_price_data, sea_epp_data, general_epp_data

def main(primary_offer_id: str):
    """Main function to orchestrate the deep discount automation process."""
    client = APIClient()
    processor = process_primary_offer(client, primary_offer_id)
    
    # Create Excel file
    excel_file = f"{primary_offer_id}.xlsx"
    excel_handler = ExcelHandler(excel_file)
    
    # Store all offers data for aggregation
    all_offers_data = {}
    
    # Process each SKU
    for sku in processor.discounted_skus:
        offers = process_sku(client, processor, sku, excel_handler)
        all_offers_data[sku] = offers
    
    # Process pricing data in chunks
    all_regular_price_data = {'result': []}
    all_sea_epp_data = {'result': []}
    all_general_epp_data = {'result': []}
    
    for sku_chunk in chunk_list(processor.discounted_skus, MAX_SKUS_PER_REQUEST):
        regular, sea_epp, general_epp = fetch_price_data(client, sku_chunk)
        
        all_regular_price_data['result'].extend(regular.get('result', []))
        all_sea_epp_data['result'].extend(sea_epp.get('result', []))
        all_general_epp_data['result'].extend(general_epp.get('result', []))
    
    # Create aggregation sheet
    excel_handler.create_aggregation_sheet(
        processor.discounted_skus,
        all_regular_price_data,
        all_sea_epp_data,
        all_general_epp_data,
        all_offers_data
    )
    
    # Save Excel file
    excel_handler.save()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py <primary_offer_id>")
        sys.exit(1)
    
    main(sys.argv[1])