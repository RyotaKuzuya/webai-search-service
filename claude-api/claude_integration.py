#!/usr/bin/env python3
"""
Claude integration using the host's claude-code installation
"""

import os
import json
import subprocess
import time
import uuid
import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class ClaudeIntegration:
    """Integration with Claude Code using host credentials"""
    
    def __init__(self):
        # Copy host credentials to container
        self.setup_credentials()
        
    def setup_credentials(self):
        """Setup Claude credentials from host"""
        host_cred_path = Path("/claude-home/.credentials.json")
        container_cred_path = Path.home() / ".claude" / ".credentials.json"
        
        # Create claude directory if not exists
        container_cred_path.parent.mkdir(parents=True, exist_ok=True)
        
        if host_cred_path.exists():
            # Copy credentials from mounted volume
            shutil.copy2(host_cred_path, container_cred_path)
            os.chmod(container_cred_path, 0o600)
            logger.info("Claude credentials copied from host")
            
            # Also copy settings if they exist
            host_settings = Path("/claude-home/settings.json")
            if host_settings.exists():
                shutil.copy2(host_settings, container_cred_path.parent / "settings.json")
                
        else:
            logger.warning("No host credentials found at /claude-home/.credentials.json")
    
    def check_claude_command(self):
        """Check if claude command is available"""
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Claude version: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"Claude command failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to check claude command: {e}")
            return False
    
    def send_message(self, message, model="claude-opus-4-20250514", web_search=True):
        """Send a message to Claude and stream the response"""
        try:
            # Prepare the command
            cmd = ['claude', 'chat', '--model', model]
            
            # Add web search hint to message if enabled
            if web_search:
                enhanced_message = f"{message}\n\n(Please use web search if you need current information)"
            else:
                enhanced_message = message
            
            logger.info(f"Sending to Claude: {enhanced_message[:100]}...")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Send the message
            process.stdin.write(enhanced_message + "\n")
            process.stdin.flush()
            process.stdin.close()
            
            # Stream the output
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Skip empty lines and system messages
                if line.strip() and not line.startswith("Human:") and not line.startswith("Assistant:"):
                    yield json.dumps({
                        "content": line.rstrip()
                    }) + "\n"
            
            # Wait for process to complete
            process.wait(timeout=120)
            
            # Check for errors
            if process.returncode != 0:
                stderr = process.stderr.read()
                logger.error(f"Claude process failed: {stderr}")
                yield json.dumps({
                    "error": f"Claude process failed: {stderr}"
                }) + "\n"
            else:
                # Send completion signal
                yield json.dumps({
                    "status": "complete"
                }) + "\n"
                
        except subprocess.TimeoutExpired:
            process.kill()
            yield json.dumps({
                "error": "Request timed out"
            }) + "\n"
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            yield json.dumps({
                "error": f"Failed to communicate with Claude: {str(e)}"
            }) + "\n"