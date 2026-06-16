"""
Handler for Crafty Controller API interactions
"""
import requests
import logging
from typing import Dict, List, Optional
from config import CRAFTY_API_URL, CRAFTY_API_KEY, CRAFTY_SERVER_ID

logger = logging.getLogger(__name__)


class CraftyHandler:
    """Handles interactions with Crafty Controller API"""
    
    def __init__(self):
        self.api_url = CRAFTY_API_URL
        self.api_key = CRAFTY_API_KEY
        self.server_id = CRAFTY_SERVER_ID
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_server_status(self) -> Optional[Dict]:
        """Get current server status"""
        try:
            response = requests.get(
                f'{self.api_url}/servers/{self.server_id}/status',
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return None
    
    def start_server(self) -> bool:
        """Start the Minecraft server"""
        try:
            response = requests.post(
                f'{self.api_url}/servers/{self.server_id}/start',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Server start command sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the Minecraft server"""
        try:
            response = requests.post(
                f'{self.api_url}/servers/{self.server_id}/stop',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Server stop command sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return False
    
    def restart_server(self) -> bool:
        """Restart the Minecraft server"""
        try:
            response = requests.post(
                f'{self.api_url}/servers/{self.server_id}/restart',
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Server restart command sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error restarting server: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """Send a command to the server console"""
        try:
            response = requests.post(
                f'{self.api_url}/servers/{self.server_id}/console',
                headers=self.headers,
                json={'command': command},
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Command sent: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    def get_player_list(self) -> Optional[List[str]]:
        """Get list of online players"""
        try:
            response = requests.get(
                f'{self.api_url}/servers/{self.server_id}/players',
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return data.get('players', [])
        except Exception as e:
            logger.error(f"Error getting player list: {e}")
            return None
