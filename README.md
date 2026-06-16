# Discord-Minecraft Bot with Crafty Controller

A Python bot that integrates Discord webhooks with a Minecraft server using Crafty Controller. This bot enables real-time notifications and server management through Discord.

## Features

- 🔔 **Player Join/Leave Notifications** - Automatically notify Discord when players join or leave
- 💬 **Chat Relay** - Relay chat messages from Minecraft to Discord
- 📊 **Server Status Updates** - Send server status changes to Discord
- 🎮 **Server Management** - Start, stop, and restart the server via API endpoints
- 🎯 **Console Commands** - Send commands to the server console

## Requirements

- Python 3.8+
- Flask 2.3.3
- Crafty Controller installed and accessible
- Discord Webhook URLs

## Installation

1. **Clone or extract the project**
   ```bash
   cd HomeLabMecanicsAPI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your settings:
     ```
     DISCORD_WEBHOOK_URL=your_webhook_url
     CRAFTY_API_URL=http://localhost:8000/api
     CRAFTY_API_KEY=your_crafty_api_key
     CRAFTY_SERVER_ID=1
     WEBHOOK_SECRET=your_secret_key
     ```

## Configuration

### Discord Setup

1. Go to your Discord Server Settings → Integrations → Webhooks
2. Click "Create Webhook"
3. Copy the webhook URL and paste it in `.env`

### Crafty Controller Setup

1. Ensure Crafty Controller is running
2. Get your API key from Crafty Controller settings
3. Find your server ID in Crafty
4. Update the `.env` file with these values

## Running the Bot

```bash
python bot.py
```

The bot will start on `http://localhost:5000` by default.

## API Endpoints

### Webhook Endpoints (POST)
- `/webhook/player-join` - Player join event
- `/webhook/player-leave` - Player leave event
- `/webhook/chat` - Chat message relay
- `/webhook/server-status` - Server status change

**Example webhook payload:**
```json
{
  "player_name": "Steve",
  "message": "Hello world!",
  "status": "online",
  "player_count": 5
}
```

### Control Endpoints

- `GET /api/server/status` - Get current server status
- `POST /api/server/start` - Start the server
- `POST /api/server/stop` - Stop the server
- `POST /api/server/restart` - Restart the server
- `POST /api/server/command` - Send a console command

**Example command request:**
```json
{
  "command": "say Hello from Discord!"
}
```

### Health Check

- `GET /health` - Check if bot is running

## Integration with Minecraft Server

To set up webhooks from your Minecraft server to this bot:

1. Install a Minecraft plugin that supports webhooks (e.g., WebhookPlugin, ServerUtils)
2. Configure the plugin to send events to:
   - Player joins: `http://your-bot-ip:5000/webhook/player-join`
   - Player leaves: `http://your-bot-ip:5000/webhook/player-leave`
   - Chat messages: `http://your-bot-ip:5000/webhook/chat`
   - Server status: `http://your-bot-ip:5000/webhook/server-status`

## Project Structure

```
.
├── bot.py                    # Main Flask application
├── config.py                 # Configuration management
├── crafty_handler.py         # Crafty Controller API handler
├── discord_handler.py        # Discord webhook handler
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_WEBHOOK_URL` | Main Discord webhook for notifications | `https://discord.com/api/webhooks/...` |
| `DISCORD_CHANNEL_WEBHOOK` | Channel webhook for chat relay | `https://discord.com/api/webhooks/...` |
| `CRAFTY_API_URL` | Crafty Controller API endpoint | `http://localhost:8000/api` |
| `CRAFTY_API_KEY` | API key for Crafty authentication | Your API key |
| `CRAFTY_SERVER_ID` | Server ID in Crafty | `1` |
| `BOT_PORT` | Port to run the bot on | `5000` |
| `BOT_HOST` | Host to bind the bot to | `0.0.0.0` |
| `WEBHOOK_SECRET` | Secret for webhook verification | Your secret key |

## Logging

The bot logs all events to the console. Important information includes:
- Webhook events received
- Discord notifications sent
- Crafty Controller API calls
- Errors and exceptions

## Troubleshooting

### Bot not receiving webhooks
- Check that the bot is running on the correct port
- Verify firewall rules allow incoming connections
- Ensure webhook URLs are correctly configured

### Discord messages not appearing
- Verify webhook URLs are valid
- Check Discord server permissions
- Look for error messages in bot logs

### Can't connect to Crafty Controller
- Ensure Crafty is running and accessible
- Verify API URL and key are correct
- Check network connectivity

## License

This project is provided as-is for personal use.

## Support

For issues or questions, check the logs and verify your configuration against the `.env.example` file.
