"""API client for interacting with Samsung's e-commerce APIs."""

import json
import requests
from typing import Dict, List, Optional
import config

class APIClient:
    def __init__(self):
        self.headers = config.DEFAULT_HEADERS
        self.session = requests.Session()

    def search_offers_by_id(self, offer_id: str, is_prod: bool = False) -> Dict:
        """Search for offers by offer ID."""
        url = config.PROD_OFFER_SEARCH_URL if is_prod else config.STAGE_OFFER_SEARCH_URL
        payload = {"offer_ids": [offer_id]}
        
        response = self.session.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def search_offers_by_sku(self, sku: str, is_prod: bool = False) -> Dict:
        """Search for offers by SKU."""
        url = config.PROD_OFFER_SEARCH_URL if is_prod else config.STAGE_OFFER_SEARCH_URL
        payload = {
            "skus": [sku],
            "filter_current_offers": True
        }
        
        response = self.session.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def fetch_current_price(self, skus: List[str], site_id: Optional[str] = None) -> Dict:
        """Fetch current price information for SKUs."""
        url = config.STAGE_FETCH_PRICE_URL
        payload = {
            "sku": skus,
            "store_type": config.STORE_TYPE_B2C
        }
        
        if site_id:
            payload["site_id"] = site_id
        
        response = self.session.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()