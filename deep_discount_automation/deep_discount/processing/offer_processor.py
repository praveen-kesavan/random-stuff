"""Process and filter offers based on business rules."""

from typing import Dict, List, Set

class OfferProcessor:
    def __init__(self, primary_offer: Dict):
        self.primary_offer = primary_offer
        self.primary_offer_id = primary_offer.get('offer_id')
        self.discounted_skus = self._extract_discounted_skus()

    def _extract_discounted_skus(self) -> List[str]:
        """Extract all discounted SKUs from the primary offer.
        
        The discounted_skus structure is like:
        [
            {
                'groups': [
                    {
                        'skus': ['SKU1', 'SKU2', 'SKU3'],
                        'quantity': 1
                    }
                ]
            }
        ]
        """
        all_skus = set()  # Using set to avoid duplicates
        discounted_skus_array = self.primary_offer.get('discounted_skus', [])
        
        for discount_group in discounted_skus_array:
            groups = discount_group.get('groups', [])
            for group in groups:
                skus = group.get('skus', [])
                all_skus.update(skus)
        
        print(f"Extracted SKUs from primary offer: {list(all_skus)}")  # Debug print
        return list(all_skus)

    def filter_duplicate_offers(self, stg_offers: List[Dict], prod_offers: List[Dict]) -> tuple[List[Dict], List[str]]:
        """Compare offers between stage and prod environments.
        
        Args:
            stg_offers: List of offer constructs from stage environment
            prod_offers: List of offer constructs from prod environment
            
        Returns:
            tuple containing:
            - stg_offers: Complete list of stage offer constructs
            - not_in_stg: List of offer IDs that exist in prod but not in stage
        """
        print(f"\n=== Comparing Stage and Prod Offers ===")
        print(f"Stage offers count: {len(stg_offers)}")
        print(f"Prod offers count: {len(prod_offers)}")
        
        # Get all offer IDs from both environments
        stg_offer_ids = [offer['offer_id'] for offer in stg_offers]
        prod_offer_ids = [offer['offer_id'] for offer in prod_offers]
        
        print(f"Stage offer IDs: {stg_offer_ids}")
        print(f"Prod offer IDs: {prod_offer_ids}")
        
        # Find offers in prod that are not in stage
        not_in_stg = [offer_id for offer_id in prod_offer_ids if offer_id not in stg_offer_ids]
        
        print(f"Offers unique to prod (not in stage): {not_in_stg}")
        print(f"Will proceed with stage offers for further processing")
        
        return stg_offers, not_in_stg

    def filter_by_sku(self, offers: List[Dict], sku: str) -> List[Dict]:
        """Filter offers to only include those that have the SKU in discounted_skus.
        
        Args:
            offers: List of complete offer constructs
            sku: The SKU to filter by
            
        Returns:
            List of complete offer constructs that include the specified SKU
        """
        print(f"\n=== Filtering by SKU: {sku} ===")
        print(f"Input offers count: {len(offers)}")
        
        filtered = []  # Will contain complete offer constructs
        for offer in offers:
            # Extract SKUs from the nested structure
            offer_skus = set()
            for discount_group in offer.get('discounted_skus', []):
                for group in discount_group.get('groups', []):
                    offer_skus.update(group.get('skus', []))
            
            if sku in offer_skus:
                print(f"Offer {offer.get('offer_id')} includes SKU {sku}")
                print(f"Including offer construct: "
                      f"ID={offer.get('offer_id')}, "
                      f"Name={offer.get('name')}, "
                      f"Type={offer.get('type')}")
                # Keep the complete offer construct
                filtered.append(offer)
            else:
                print(f"Offer {offer.get('offer_id')} does not include SKU {sku}")
                print(f"Offer's SKUs: {offer_skus}")

        print(f"Filtered offers count: {len(filtered)}")
        if filtered:
            print("\nVerifying filtered offer constructs:")
            for offer in filtered:
                print(f"\nOffer {offer.get('offer_id')}:")
                print(f"- Name: {offer.get('name')}")
                print(f"- Type: {offer.get('type')}")
                print(f"- Channel: {offer.get('channel')}")
                print(f"- Has discount_description: {bool(offer.get('discount_description'))}")
                
        return filtered

    def filter_non_stackable(self, offers: List[Dict]) -> List[Dict]:
        """Remove offers based on non-stackable rules."""
        print(f"\n=== Filtering Non-stackable Offers ===")
        print(f"Input offers count: {len(offers)}")
        
        # Get non-stackable offer IDs from primary offer
        primary_offer_restrictions = self.primary_offer.get('offer_id_restriction', {})
        primary_non_stackable = set(primary_offer_restrictions.get('non_stackable_offer_ids', []))
        print(f"Primary offer ({self.primary_offer_id}) non-stackable IDs: {primary_non_stackable}")
        
        filtered_offers = []
        for offer in offers:
            offer_id = offer['offer_id']
            offer_name = offer.get('name', '')  # Get offer name for logging
            print(f"\nChecking offer: ID={offer_id}, Name={offer_name}")
            
            # Get offer's non-stackable IDs
            offer_restrictions = offer.get('offer_id_restriction', {})
            offer_non_stackable = offer_restrictions.get('non_stackable_offer_ids', [])
            print(f"Offer's non-stackable IDs: {offer_non_stackable}")
            
            # Check if primary offer ID is in this offer's non-stackable list
            if self.primary_offer_id in offer_non_stackable:
                print(f"SKIP: Primary offer {self.primary_offer_id} is in offer's non-stackable list")
                continue
            
            # Check if this offer's ID is in primary offer's non-stackable list
            if offer_id in primary_non_stackable:
                print(f"SKIP: Offer {offer_id} is in primary offer's non-stackable list")
                continue
            
            print(f"INCLUDE: Offer {offer_id} passes non-stackable rules")
            filtered_offers.append(offer)
        
        print(f"\nNon-stackable filtering results:")
        print(f"- Input offers: {len(offers)}")
        print(f"- Filtered offers: {len(filtered_offers)}")
        print(f"- Removed offers: {len(offers) - len(filtered_offers)}")
        
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