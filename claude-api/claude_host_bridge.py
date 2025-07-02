#!/usr/bin/env python3
"""
Bridge to use host's claude command via SSH or direct execution
"""

import os
import json
import subprocess
import logging
import time

logger = logging.getLogger(__name__)

class ClaudeHostBridge:
    """Use the host's claude installation"""
    
    def __init__(self):
        # Check if we're in Docker by looking for .dockerenv
        self.in_docker = os.path.exists('/.dockerenv')
        self.setup_complete = False
        
        if self.in_docker:
            logger.info("Running in Docker container")
            # In production, we'll need to set up SSH or use a socket
            # For now, we'll use a simple approach
            self.setup_complete = self.setup_docker_bridge()
        else:
            logger.info("Running on host system")
            self.setup_complete = self.check_host_claude()
    
    def setup_docker_bridge(self):
        """Setup bridge from Docker to host"""
        # For MVP, we'll use a mounted volume approach
        # The host will run a listener that the container can communicate with
        return True
    
    def check_host_claude(self):
        """Check if claude is available on host"""
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Host claude version: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.error(f"Failed to check host claude: {e}")
        return False
    
    def send_message(self, message, model="claude-opus-4-20250514", web_search=True):
        """Send message to claude and stream response"""
        if not self.setup_complete:
            yield json.dumps({
                "error": "Claude bridge not properly configured"
            }) + "\n"
            return
        
        # For now, return a helpful message about the setup
        yield json.dumps({
            "content": "Claude integration is being set up. The host system has claude-code installed and authenticated.\n"
        }) + "\n"
        
        yield json.dumps({
            "content": "To complete the integration:\n"
        }) + "\n"
        
        yield json.dumps({
            "content": "1. The claude command is available at: /home/ubuntu/.npm-global/bin/claude\n"
        }) + "\n"
        
        yield json.dumps({
            "content": "2. Credentials are stored at: /home/ubuntu/.claude/.credentials.json\n" 
        }) + "\n"
        
        yield json.dumps({
            "content": "3. You can test claude directly on the host with: claude chat\n"
        }) + "\n"
        
        yield json.dumps({
            "status": "complete"
        }) + "\n"