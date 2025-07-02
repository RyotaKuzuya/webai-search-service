#!/usr/bin/env python3
"""
Client to communicate with the host's claude bridge server
"""

import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class ClaudeBridgeClient:
    """Client for the host's claude bridge server"""
    
    def __init__(self):
        # Use the actual host IP (Docker bridge network gateway)
        self.bridge_url = "http://xxx.xxx.xxx.xxx:8585"
        # Alternative IPs to try
        self.fallback_urls = [
            "http://xxx.xxx.xxx.xxx:8585",
            "http://host.docker.internal:8585"
        ]
        self.check_bridge()
    
    def check_bridge(self):
        """Check if bridge server is available"""
        urls_to_try = [self.bridge_url] + self.fallback_urls
        for url in urls_to_try:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    logger.info(f"Bridge server available at {url}")
                    self.bridge_url = url
                    return True
            except Exception as e:
                logger.debug(f"Failed to connect to {url}: {e}")
                continue
        logger.warning("Bridge server not available at any known address")
        return False
    
    def send_message(self, message, model="claude-opus-4-20250514", web_search=True):
        """Send message to bridge server and stream response"""
        try:
            # Add web search hint if enabled
            if web_search:
                message = f"{message}\n\n(Please use web search if you need current information)"
            
            # Send request to bridge
            response = requests.post(
                f"{self.bridge_url}/chat",
                json={
                    "message": message,
                    "model": model
                },
                stream=True,
                timeout=120
            )
            
            if response.status_code != 200:
                yield json.dumps({
                    "error": f"Bridge server error: {response.status_code}"
                }) + "\n"
                return
            
            # Stream response
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8') + "\n"
                    
        except requests.exceptions.ConnectionError:
            yield json.dumps({
                "error": "Cannot connect to Claude bridge server. Please ensure it's running on the host."
            }) + "\n"
        except Exception as e:
            logger.error(f"Bridge client error: {e}")
            yield json.dumps({
                "error": f"Bridge communication error: {str(e)}"
            }) + "\n"