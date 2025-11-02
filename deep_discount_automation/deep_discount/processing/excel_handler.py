"""Handle Excel file operations for storing offer and pricing data."""

import pandas as pd
from typing import Dict, List
from deep_discount import config

class ExcelHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.writer = pd.ExcelWriter(filename, engine='openpyxl')

    def create_sku_sheet(self, sku: str, offers: List[Dict]) -> None:
        """Create a sheet for a specific SKU with offer details.
        
        Args:
            sku: The SKU to create a sheet for
            offers: List of offer dictionaries containing offer details and discounted_skus arrays
        """
        print(f"\n=== Creating Sheet for SKU: {sku} ===")
        
        # Filter offers to only include those where SKU is in at least one discounted_skus array
        filtered_offers = [
            offer for offer in offers 
            if any(sku in discount_desc.get('skus', []) 
                  for discount_desc in offer.get('discount_description', []))
        ]
        
        print(f"Number of offers to process after filtering: {len(filtered_offers)}")
        
        data = []
        for i, offer in enumerate(filtered_offers, 1):
            print(f"\nProcessing offer {i}/{len(filtered_offers)} - ID: {offer.get('offer_id')}")
            row = {
                'offer_id': offer.get('offer_id'),
                'name': offer.get('name'),  # Using 'name' field directly
                'type': offer.get('type'),
                'channel': offer.get('channel'),
                'exclude_ir': offer.get('exclude_ir'),  # Added new field
                'exclude_epp': offer.get('exclude_epp'),  # Added new field
                'coupon_code_triggered': offer.get('coupon_code_triggered'),
                'trigger_tags': ','.join(offer.get('trigger_tags', [])) if offer.get('trigger_tags') else '',
                'concurrent': offer.get('concurrent'),
                'apply_mode': offer.get('apply_mode'),
                'applicable_sites': ','.join(str(site) for site in offer.get('applicable_sites', [])) if offer.get('applicable_sites') else '',
                'restricted_skus': ','.join(offer.get('restricted_skus', [])) if offer.get('restricted_skus') else ''
            }
            
            # Add discount description specific to the SKU
            discount = self._get_sku_discount(offer, sku)
            print(f"Discount details for SKU {sku}: {discount}")
            row.update({
                'discount_value': discount.get('value'),
                'discount_type': discount.get('type')
            })
            
            print(f"Row data for offer {offer.get('offer_id')}:")
            for key, value in row.items():
                print(f"- {key}: {value}")
            
            data.append(row)
        
        print(f"\nCreating DataFrame with {len(data)} rows")
        df = pd.DataFrame(data)
        
        # Convert SKU to string to ensure it's a valid sheet name
        sheet_name = str(sku)
        original_sheet_name = sheet_name
        
        # Excel has a 31 character limit for sheet names
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
            print(f"Sheet name truncated from {original_sheet_name} to {sheet_name}")
            
        # Replace invalid characters in sheet name
        invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
        for char in invalid_chars:
            if char in sheet_name:
                sheet_name = sheet_name.replace(char, '_')
                print(f"Replaced invalid character '{char}' in sheet name")
            
        print(f"Writing sheet: {sheet_name}")
        df.to_excel(self.writer, sheet_name=sheet_name, index=False)

    def create_aggregation_sheet(
        self,
        skus: List[str],
        price_data: Dict,
        sea_epp_data: Dict,
        general_epp_data: Dict,
        offers_data: Dict
    ) -> None:
        """Create the aggregation sheet with all pricing and offer information."""
        print(f"\n=== Creating Aggregation Sheet ===")
        print(f"Processing {len(skus)} SKUs")
        data = []
        
        for i, sku in enumerate(skus, 1):
            print(f"\nProcessing SKU {i}/{len(skus)}: {sku}")
            row = {'SKU': sku}
            
            # Add pricing information
            print("Fetching price information...")
            sku_price = self._get_sku_price_info(price_data, sku)
            print(f"Price info: MSRP={sku_price.get('msrp_price')}, Sale Price={sku_price.get('sale_price')}")
            row.update({
                'MSRP': sku_price.get('msrp_price'),
                'Sale Price': sku_price.get('sale_price')
            })
            
            # Add EPP discounts
            print("Fetching EPP discount information...")
            sea_epp = self._get_epp_discount(sea_epp_data, sku)
            general_epp = self._get_epp_discount(general_epp_data, sku)
            
            print(f"SEA EPP: Type={sea_epp.get('type')}, Value={sea_epp.get('value')}")
            print(f"General EPP: Type={general_epp.get('type')}, Value={general_epp.get('value')}")
            
            row.update({
                'SEA EPP Type': sea_epp.get('type'),
                'SEA EPP Value': sea_epp.get('value'),
                'General EPP Type': general_epp.get('type'),
                'General EPP Value': general_epp.get('value')
            })
            
            # Add offer information
            sku_offers = offers_data.get(sku, [])
            print(f"Processing {len(sku_offers)} offers for SKU")
            
            for i, offer in enumerate(sku_offers, 1):
                discount = self._get_sku_discount(offer, sku)
                print(f"Offer {i}: ID={offer.get('offer_id')}, "
                      f"Value={discount.get('value')}, Type={discount.get('type')}")
                row.update({
                    f'Offer {i} ID': offer.get('offer_id'),
                    f'Offer {i} Value': discount.get('value'),
                    f'Offer {i} Type': discount.get('type')
                })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        # Use string sheet name and ensure it's valid
        sheet_name = str(config.EXCEL_SHEET_NAMES['AGGREGATION'])
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
        for char in invalid_chars:
            sheet_name = sheet_name.replace(char, '_')
            
        df.to_excel(self.writer, sheet_name=sheet_name, index=False)

    def save(self) -> None:
        """Save and close the Excel file."""
        self.writer.close()

    @staticmethod
    def _get_sku_discount(offer: Dict, sku: str) -> Dict:
        """Extract discount information for a specific SKU from an offer.
        
        Args:
            offer: The offer dictionary containing discount descriptions
            sku: The SKU to find discount information for
            
        Returns:
            Dict containing discount value (as int) and type
        """
        for desc in offer.get('discount_description', []):
            if sku in desc.get('skus', []):
                value = desc.get('value')
                # Ensure value is treated as int, but don't convert if None
                return {
                    'value': value if value is None else int(value),
                    'type': desc.get('type')
                }
        return {}

    @staticmethod
    def _get_sku_price_info(price_data: List[Dict], sku: str) -> Dict:
        """Extract price information for a specific SKU from the price data response.
        
        Args:
            price_data: List of price data items from fetch-current-price API response
            sku: The SKU to find price information for
            
        Returns:
            Dict containing MSRP and sale price information for the SKU
        """
        print(f"\nExtracting price info for SKU: {sku}")
        
        # Handle invalid or empty price data
        if not isinstance(price_data, list) or not price_data:
            print(f"Warning: Invalid or empty price data for SKU: {sku}")
            return {}
            
        for item in price_data:
            if not isinstance(item, dict):
                continue
                
            if item.get('sku') == sku:
                msrp_price = item.get('msrp_price', {}).get('value')
                sale_price = item.get('sale_price', {}).get('value')
                min_price = item.get('min_price', {}).get('value')
                min_epp_price = item.get('min_epp_price', {}).get('value')
                list_price = item.get('list_price', {}).get('value')
                
                print(f"Found price info for {sku}:")
                print(f"- MSRP: ${msrp_price if msrp_price else 'N/A'}")
                print(f"- Sale Price: ${sale_price if sale_price else 'N/A'}")
                print(f"- Min Price: ${min_price if min_price else 'N/A'}")
                print(f"- Min EPP Price: ${min_epp_price if min_epp_price else 'N/A'}")
                print(f"- List Price: ${list_price if list_price else 'N/A'}")
                
                return {
                    'msrp_price': msrp_price,
                    'sale_price': sale_price,
                    'min_price': min_price,
                    'min_epp_price': min_epp_price,
                    'list_price': list_price
                }
                
        print(f"No price info found for SKU: {sku}")
        return {}    @staticmethod
    def _get_epp_discount(epp_data: List[Dict], sku: str) -> Dict:
        """Extract EPP discount information for a specific SKU.
        
        Args:
            epp_data: List of EPP data items from API response
            sku: The SKU to find EPP discount information for
            
        Returns:
            Dict containing discount type (string) and value (integer)
        """
        print(f"\nExtracting EPP discount info for SKU: {sku}")
        
        if not isinstance(epp_data, list) or not epp_data:
            print(f"Warning: Invalid or empty EPP data for SKU: {sku}")
            return {}
            
        for item in epp_data:
            if item.get('sku') == sku:
                for discount in item.get('entity_discounts', []):
                    if isinstance(discount, dict):
                        discount_data = discount.get('discount', {})
                        discount_info = {
                            'type': discount_data.get('type'),  # Keep as string
                            'value': discount_data.get('value')  # Keep as integer
                        }
                        print(f"Found EPP discount for {sku}:")
                        print(f"- Type: {discount_info['type']}")
                        print(f"- Value: {discount_info['value']}")
                        return discount_info
        print(f"No EPP discount found for SKU: {sku}")
        return {}