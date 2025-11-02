"""Process and filter offers based on business rules."""

from typing import Dict, List, Set

class OfferProcessor:
    def __init__(self, primary_offer: Dict):
        self.primary_offer = primary_offer
        self.primary_offer_id = primary_offer.get('offer_id')
        self.discounted_skus = self._extract_discounted_skus()

    def _extract_discounted_skus(self) -> List[str]:
        """Extract all discounted SKUs from the primary offer."""
        return self.primary_offer.get('discounted_skus', [])

    def filter_duplicate_offers(self, stg_offers: List[Dict], prod_offers: List[Dict]) -> tuple[List[Dict], Set[str]]:
        """Remove duplicate offers between stage and prod environments."""
        stg_offer_ids = {offer['offer_id'] for offer in stg_offers}
        not_in_stg = set()
        filtered_offers = []

        for offer in prod_offers:
            offer_id = offer['offer_id']
            if offer_id not in stg_offer_ids:
                not_in_stg.add(offer_id)
                filtered_offers.append(offer)

        return filtered_offers, not_in_stg

    def filter_by_sku(self, offers: List[Dict], sku: str) -> List[Dict]:
        """Filter offers to only include those that have the SKU in discounted_skus."""
        return [
            offer for offer in offers
            if sku in offer.get('discounted_skus', [])
        ]

    def filter_non_stackable(self, offers: List[Dict]) -> List[Dict]:
        """Remove offers based on non-stackable rules."""
        # Get non-stackable offer IDs from primary offer
        primary_non_stackable = set(self.primary_offer.get('non_stackable_offer_ids', []))
        
        filtered_offers = []
        for offer in offers:
            offer_id = offer['offer_id']
            offer_non_stackable = set(offer.get('non_stackable_offer_ids', []))
            
            # Skip if primary offer ID is in this offer's non-stackable list
            if self.primary_offer_id in offer_non_stackable:
                continue
                
            # Skip if this offer's ID is in primary offer's non-stackable list
            if offer_id in primary_non_stackable:
                continue
                
            filtered_offers.append(offer)
            
        return filtered_offers

    def get_discount_description(self, offer: Dict, sku: str) -> Dict:
        """Get the discount description object for a specific SKU."""
        descriptions = offer.get('discount_description', [])
        for desc in descriptions:
            if sku in desc.get('skus', []):
                return {
                    'value': desc.get('value'),
                    'type': desc.get('type')
                }
        return {}