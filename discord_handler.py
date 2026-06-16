"""
Handler for Discord Webhook interactions
"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime
from config import DISCORD_WEBHOOK_URL, DISCORD_CHANNEL_WEBHOOK

logger = logging.getLogger(__name__)


class DiscordHandler:
    """Handles Discord webhook communications"""
    
    # Color codes for embeds
    COLORS = {
        'info': 0x3498db,      # Blue
        'success': 0x2ecc71,   # Green
        'warning': 0xf39c12,   # Orange
        'error': 0xe74c3c,     # Red
        'online': 0x2ecc71,    # Green
        'offline': 0xe74c3c,   # Red
    }
    
    @staticmethod
    def send_embed(webhook_url: str, title: str, description: str, 
                   color: str = 'info', fields: Optional[list] = None) -> bool:
        """Send an embed message to Discord"""
        if not webhook_url:
            logger.warning("No webhook URL provided")
            return False
        
        try:
            embed = {
                'title': title,
                'description': description,
                'color': DiscordHandler.COLORS.get(color, 0x3498db),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'footer': {'text': 'MinecraftBot'},
            }
            
            if fields:
                embed['fields'] = fields
            
            payload = {'embeds': [embed]}
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Discord message sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Error sending Discord embed: {e}")
            return False
    
    @staticmethod
    def send_message(webhook_url: str, content: str) -> bool:
        """Send a plain text message to Discord"""
        if not webhook_url:
            logger.warning("No webhook URL provided")
            return False
        
        try:
            payload = {'content': content}
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Discord message sent")
            return True
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            return False
    
    @staticmethod
    def notify_player_join(player_name: str) -> bool:
        """Notify Discord that a player joined"""
        return DiscordHandler.send_embed(
            DISCORD_WEBHOOK_URL,
            title='🟢 Player Joined',
            description=f'**{player_name}** has joined the server',
            color='success'
        )
    
    @staticmethod
    def notify_player_leave(player_name: str) -> bool:
        """Notify Discord that a player left"""
        return DiscordHandler.send_embed(
            DISCORD_WEBHOOK_URL,
            title='🔴 Player Left',
            description=f'**{player_name}** has left the server',
            color='warning'
        )
    
    @staticmethod
    def notify_server_status(status: str, player_count: int = 0) -> bool:
        """Notify Discord of server status change"""
        is_online = status.lower() in ['online', 'running', 'started']
        color = 'online' if is_online else 'offline'
        
        return DiscordHandler.send_embed(
            DISCORD_WEBHOOK_URL,
            title=f'🖥️ Server {status.title()}',
            description=f'The Minecraft server is now **{status}**',
            color=color,
            fields=[
                {'name': 'Online Players', 'value': str(player_count), 'inline': True}
            ]
        )
    
    @staticmethod
    def relay_chat_message(player_name: str, message: str) -> bool:
        """Relay a chat message from Minecraft to Discord"""
        return DiscordHandler.send_message(
            DISCORD_CHANNEL_WEBHOOK,
            f'**{player_name}**: {message}'
        )
    
    @staticmethod
    def send_status_report(server_status: Dict) -> bool:
        """Send a detailed server status report to Discord"""
        return DiscordHandler.send_embed(
            DISCORD_WEBHOOK_URL,
            title='📊 Server Status Report',
            description='Current Minecraft server status',
            color='info',
            fields=[
                {'name': 'Status', 'value': server_status.get('status', 'Unknown'), 'inline': True},
                {'name': 'Players Online', 'value': str(server_status.get('player_count', 0)), 'inline': True},
                {'name': 'Uptime', 'value': server_status.get('uptime', 'N/A'), 'inline': True},
            ]
        )
