"""API client for posting tracking data."""

import logging
import requests
from typing import Optional
from config.config import Config

log = logging.getLogger(__name__)


class APIClient:
    """Client for posting people counting data to external APIs."""
    
    def __init__(self, config: Config):
        """Initialize the API client.
        
        Args:
            config: Configuration object containing API settings
        """
        self.config = config
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Set up the requests session with default headers and timeout."""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PeopleCounterAPI/1.0'
        })
        # Set a reasonable timeout for API calls
        self.session.timeout = 30
    
    def post_data(self, total: int, total_down: int, total_up: int, delta: int) -> Optional[requests.Response]:
        """Post counting data to the configured API endpoint.
        
        Args:
            total: Total people count
            total_down: Total people entering
            total_up: Total people exiting
            delta: Change in count
            
        Returns:
            Response object if successful, None if failed
        """
        if not self.config.enable_api or not self.config.api_url:
            log.warning("API not enabled or URL not configured")
            return None
        
        payload = {
            'apparaat': self.config.device,
            'binnen': total_down,
            'buiten': total_up,
            'delta': delta,
            'totaal': total
        }
        
        try:
            log.info(f"Posting to API - total: {total}, down: {total_down}, up: {total_up}, delta: {delta}")
            response = self.session.post(self.config.api_url, json=payload)
            response.raise_for_status()
            
            log.info(f"API response: {response.status_code} - {response.text[:200]}")
            return response
            
        except requests.exceptions.Timeout:
            log.error("API request timed out")
        except requests.exceptions.ConnectionError:
            log.error(f"Failed to connect to API: {self.config.api_url}")
        except requests.exceptions.HTTPError as e:
            log.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            log.error(f"API request failed: {e}")
        except Exception as e:
            log.error(f"Unexpected error during API call: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """Test the API connection.
        
        Returns:
            True if connection test successful, False otherwise
        """
        if not self.config.api_url:
            log.error("No API URL configured")
            return False
        
        try:
            # Send a test payload with zero values
            test_payload = {
                'apparaat': f"{self.config.device}_test",
                'binnen': 0,
                'buiten': 0,
                'delta': 0,
                'totaal': 0
            }
            
            response = self.session.post(self.config.api_url, json=test_payload)
            response.raise_for_status()
            
            log.info(f"API connection test successful: {response.status_code}")
            return True
            
        except Exception as e:
            log.error(f"API connection test failed: {e}")
            return False
    
    def update_config(self, new_config: Config) -> None:
        """Update the API configuration.
        
        Args:
            new_config: New configuration object
        """
        self.config = new_config
        log.info("API client configuration updated")
    
    def get_status(self) -> dict:
        """Get the current status of the API client.
        
        Returns:
            Dictionary with client status information
        """
        return {
            "enabled": self.config.enable_api,
            "url": self.config.api_url,
            "device": self.config.device,
            "interval": self.config.api_interval,
            "session_active": self.session is not None
        }
    
    def close(self) -> None:
        """Close the API client and clean up resources."""
        if self.session:
            self.session.close()
            log.info("API client session closed")