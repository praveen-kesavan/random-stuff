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
    
    if not primary_offer_response.get('offers'):
        print(f"No offers found for ID {primary_offer_id}")
        print(f"Response: {primary_offer_response}")
        raise ValueError(f"No offers found for ID {primary_offer_id}")
        
    primary_offer = primary_offer_response.get('offers', [])[0]
    print(f"Primary offer discounted_skus structure: {primary_offer.get('discounted_skus')}")
    
    return OfferProcessor(primary_offer)

def process_sku(
    client: APIClient,
    processor: OfferProcessor,
    sku: str,
    excel_handler: ExcelHandler
) -> tuple[List[Dict], List[str]]:
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
    
    return offers_list, not_in_stg

def fetch_price_data(client: APIClient, skus: List[str]) -> tuple[Dict, Dict, Dict]:
    """Fetch price data for SKUs including EPP pricing."""
    regular_price_data = client.fetch_current_price(skus)
    sea_epp_data = client.fetch_current_price(skus, SITE_ID_SEA_EPP)
    general_epp_data = client.fetch_current_price(skus, SITE_ID_GENERAL_EPP)
    
    return regular_price_data, sea_epp_data, general_epp_data

def main(primary_offer_id: str):
    """Main function to orchestrate the deep discount automation process."""
    print(f"\n=== Starting Deep Discount Automation ===")
    print(f"Processing primary offer ID: {primary_offer_id}")
    
    client = APIClient()
    processor = process_primary_offer(client, primary_offer_id)
    
    print(f"\n=== Discounted SKUs Analysis ===")
    print(f"Total SKUs found: {len(processor.discounted_skus)}")
    print(f"SKU list: {processor.discounted_skus}")
    
    # Create Excel file
    excel_file = f"{primary_offer_id}.xlsx"
    print(f"\nCreating Excel file: {excel_file}")
    excel_handler = ExcelHandler(excel_file)
    
    # Store all offers data for aggregation
    print("\n=== Processing Individual SKUs ===")
    all_offers_data = {}
    
    # Process each SKU
    all_not_in_stg = []  # Collect all offer IDs not in stage
    for i, sku in enumerate(processor.discounted_skus, 1):
        print(f"\nProcessing SKU {i}/{len(processor.discounted_skus)}: {sku}")
        try:
            offers, not_in_stg = process_sku(client, processor, sku, excel_handler)
            print(f"Found {len(offers)} valid offers for SKU {sku}")
            all_offers_data[sku] = offers
            # Add new offer IDs not already in the list
            for offer_id in not_in_stg:
                if offer_id not in all_not_in_stg:
                    all_not_in_stg.append(offer_id)
        except Exception as e:
            print(f"Error processing SKU {sku}: {str(e)}")
            continue
    
    print("\n=== Processing Pricing Data ===")
    # Process pricing data in chunks
    all_regular_price_data = []
    all_sea_epp_data = []
    all_general_epp_data = []
    print("Initialized price data containers")
    
    sku_chunks = list(chunk_list(processor.discounted_skus, MAX_SKUS_PER_REQUEST))
    print(f"Split {len(processor.discounted_skus)} SKUs into {len(sku_chunks)} chunks")
    
    for i, sku_chunk in enumerate(sku_chunks, 1):
        print(f"\nProcessing chunk {i}/{len(sku_chunks)} with {len(sku_chunk)} SKUs")
        try:
            regular, sea_epp, general_epp = fetch_price_data(client, sku_chunk)
            print(f"Successfully fetched price data for chunk {i}")
            
            # API returns a list directly, not wrapped in a 'result' object
            if isinstance(regular, list):
                all_regular_price_data.extend(regular)
            else:
                all_regular_price_data.extend(regular.get('result', []))
                
            if isinstance(sea_epp, list):
                all_sea_epp_data.extend(sea_epp)
            else:
                all_sea_epp_data.extend(sea_epp.get('result', []))
                
            if isinstance(general_epp, list):
                all_general_epp_data.extend(general_epp)
            else:
                all_general_epp_data.extend(general_epp.get('result', []))
        except Exception as e:
            print(f"Error processing chunk {i}: {str(e)}")
            continue
    
    print("\n=== Creating Final Excel Output ===")
    print("Creating aggregation sheet...")
    # Create aggregation sheet
    excel_handler.create_aggregation_sheet(
        processor.discounted_skus,
        all_regular_price_data,
        all_sea_epp_data,
        all_general_epp_data,
        all_offers_data
    )
    
    print("\nSaving Excel file...")
    # Save Excel file
    excel_handler.save()
    
    print(f"\n=== Process Complete ===")
    print(f"Results saved to: {excel_file}")
    print("\n=== Offers Not Present in Stage ===")
    print("The following offer IDs were found in Production but not in Stage:")
    for offer_id in all_not_in_stg:
        print(f"- {offer_id}")
    print(f"\nTotal offers not in Stage: {len(all_not_in_stg)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py <primary_offer_id>")
        sys.exit(1)
    
    main(sys.argv[1])
