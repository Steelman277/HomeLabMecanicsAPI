"""
Configuration file for Discord-Minecraft Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')  # Your Discord Webhook URL
DISCORD_CHANNEL_WEBHOOK = os.getenv('DISCORD_CHANNEL_WEBHOOK', '')  # For channel messages

# Crafty Controller Configuration
CRAFTY_API_URL = os.getenv('CRAFTY_API_URL', 'http://localhost:8000/api')  # Crafty API endpoint
CRAFTY_API_KEY = os.getenv('CRAFTY_API_KEY', '')  # Crafty API key
CRAFTY_SERVER_ID = os.getenv('CRAFTY_SERVER_ID', '1')  # Server ID in Crafty

# Bot Configuration
BOT_NAME = os.getenv('BOT_NAME', 'MinecraftBot')
BOT_PORT = int(os.getenv('BOT_PORT', 5000))
BOT_HOST = os.getenv('BOT_HOST', '0.0.0.0')

# Webhook Secret (for validating incoming webhooks)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-key')
