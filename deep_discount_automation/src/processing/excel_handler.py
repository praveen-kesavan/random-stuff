"""Handle Excel file operations for storing offer and pricing data."""

import pandas as pd
from typing import Dict, List
from .. import config

class ExcelHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.writer = pd.ExcelWriter(filename, engine='openpyxl')

    def create_sku_sheet(self, sku: str, offers: List[Dict]) -> None:
        """Create a sheet for a specific SKU with offer details."""
        data = []
        for offer in offers:
            row = {
                'offer_id': offer.get('offer_id'),
                'name': offer.get('name'),
                'type': offer.get('type'),
                'channel': offer.get('channel'),
                'coupon_code_triggered': offer.get('coupon_code_triggered'),
                'trigger_tags': ','.join(offer.get('trigger_tags', [])),
                'concurrent': offer.get('concurrent'),
                'apply_mode': offer.get('apply_mode'),
                'applicable_sites': ','.join(offer.get('applicable_sites', [])),
                'restricted_skus': ','.join(offer.get('restricted_skus', []))
            }
            
            # Add discount description specific to the SKU
            discount = self._get_sku_discount(offer, sku)
            row.update({
                'discount_value': discount.get('value'),
                'discount_type': discount.get('type')
            })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_excel(self.writer, sheet_name=sku, index=False)

    def create_aggregation_sheet(
        self,
        skus: List[str],
        price_data: Dict,
        sea_epp_data: Dict,
        general_epp_data: Dict,
        offers_data: Dict
    ) -> None:
        """Create the aggregation sheet with all pricing and offer information."""
        data = []
        
        for sku in skus:
            row = {'SKU': sku}
            
            # Add pricing information
            sku_price = self._get_sku_price_info(price_data, sku)
            row.update({
                'MSRP': sku_price.get('msrp_price'),
                'Sale Price': sku_price.get('sale_price')
            })
            
            # Add EPP discounts
            sea_epp = self._get_epp_discount(sea_epp_data, sku)
            general_epp = self._get_epp_discount(general_epp_data, sku)
            
            row.update({
                'SEA EPP Type': sea_epp.get('type'),
                'SEA EPP Value': sea_epp.get('value'),
                'General EPP Type': general_epp.get('type'),
                'General EPP Value': general_epp.get('value')
            })
            
            # Add offer information
            sku_offers = offers_data.get(sku, [])
            for i, offer in enumerate(sku_offers, 1):
                discount = self._get_sku_discount(offer, sku)
                row.update({
                    f'Offer {i} ID': offer.get('offer_id'),
                    f'Offer {i} Value': discount.get('value'),
                    f'Offer {i} Type': discount.get('type')
                })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_excel(self.writer, sheet_name=config.EXCEL_SHEET_NAMES['AGGREGATION'], index=False)

    def save(self) -> None:
        """Save and close the Excel file."""
        self.writer.close()

    @staticmethod
    def _get_sku_discount(offer: Dict, sku: str) -> Dict:
        """Extract discount information for a specific SKU from an offer."""
        for desc in offer.get('discount_description', []):
            if sku in desc.get('skus', []):
                return {
                    'value': desc.get('value'),
                    'type': desc.get('type')
                }
        return {}

    @staticmethod
    def _get_sku_price_info(price_data: Dict, sku: str) -> Dict:
        """Extract price information for a specific SKU."""
        for item in price_data.get('result', []):
            if item.get('sku') == sku:
                return item
        return {}

    @staticmethod
    def _get_epp_discount(epp_data: Dict, sku: str) -> Dict:
        """Extract EPP discount information for a specific SKU."""
        for item in epp_data.get('result', []):
            if item.get('sku') == sku:
                for discount in item.get('entity_discounts', []):
                    return {
                        'type': discount.get('type'),
                        'value': discount.get('value')
                    }
        return {}