"""API client for interacting with Samsung's e-commerce APIs."""

import json
import requests
from typing import Dict, List, Optional
import config

class APIClient:
    def __init__(self):
        self.headers = {
            'content-type': 'application/json',
            'Cookie': 'ecom_session_id_USA=M2E0ZWFkNmYtMzJhNy00NTE2LThhODYtZGE3YmZmMTI3NDRj; ecom_vi_USA=Y2U1YzkyNzUtZTZlMy00MDVkLWIwYzctODBmMzg5MTg3ZThi'
        }
        self.session = requests.Session()

    def search_offers_by_id(self, offer_id: str, is_prod: bool = False) -> Dict:
        """Search for offers by offer ID."""
        url = config.PROD_OFFER_SEARCH_URL if is_prod else config.STAGE_OFFER_SEARCH_URL
        payload = {"offer_ids": [offer_id]}
        
        try:
            response = self.session.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error searching offers by ID: {e}")
            print(f"Response content: {response.text}")
            raise

    def search_offers_by_sku(self, sku: str, is_prod: bool = False) -> Dict:
        """Search for offers by SKU."""
        url = config.PROD_OFFER_SEARCH_URL if is_prod else config.STAGE_OFFER_SEARCH_URL
        # Ensure SKU is a string and create the payload exactly as in the sample cURL
        payload = {
            "skus": [str(sku)],
            "filter_current_offers": True
        }
        
        try:
            print(f"Making request to {url} with payload: {json.dumps(payload)}")  # Debug print
            response = self.session.post(url, headers=self.headers, json=payload)
            print(f"Response status: {response.status_code}")  # Debug print
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error searching offers by SKU: {e}")
            print(f"Response content: {response.text}")
            print(f"Request headers: {self.headers}")  # Debug print
            raise

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