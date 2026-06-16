"""
Discord-Minecraft Bot using Webhooks with Crafty Controller
Main application entry point
"""
from flask import Flask, request, jsonify
import logging
from config import BOT_HOST, BOT_PORT, WEBHOOK_SECRET
from crafty_handler import CraftyHandler
from discord_handler import DiscordHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
crafty = CraftyHandler()


def verify_webhook(data):
    """Verify webhook authenticity using secret key"""
    # In a real implementation, you'd use HMAC-SHA256
    # For now, we'll use a simple secret comparison
    secret = request.headers.get('X-Webhook-Secret', '')
    return secret == WEBHOOK_SECRET


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'online'}), 200


@app.route('/webhook/player-join', methods=['POST'])
def on_player_join():
    """Webhook endpoint for player join events from Minecraft"""
    try:
        data = request.json
        player_name = data.get('player_name', 'Unknown')
        
        logger.info(f"Player joined: {player_name}")
        DiscordHandler.notify_player_join(player_name)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing player join: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/webhook/player-leave', methods=['POST'])
def on_player_leave():
    """Webhook endpoint for player leave events from Minecraft"""
    try:
        data = request.json
        player_name = data.get('player_name', 'Unknown')
        
        logger.info(f"Player left: {player_name}")
        DiscordHandler.notify_player_leave(player_name)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing player leave: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/webhook/chat', methods=['POST'])
def on_chat_message():
    """Webhook endpoint for chat messages from Minecraft"""
    try:
        data = request.json
        player_name = data.get('player_name', 'Unknown')
        message = data.get('message', '')
        
        logger.info(f"Chat from {player_name}: {message}")
        DiscordHandler.relay_chat_message(player_name, message)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/webhook/server-status', methods=['POST'])
def on_server_status():
    """Webhook endpoint for server status changes"""
    try:
        data = request.json
        status = data.get('status', 'unknown')
        player_count = data.get('player_count', 0)
        
        logger.info(f"Server status changed: {status}")
        DiscordHandler.notify_server_status(status, player_count)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing server status: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/server/start', methods=['POST'])
def api_start_server():
    """API endpoint to start the server"""
    try:
        success = crafty.start_server()
        if success:
            DiscordHandler.send_embed(
                'DISCORD_WEBHOOK_URL',
                title='🟢 Server Started',
                description='The server has been started',
                color='success'
            )
            return jsonify({'status': 'Server started'}), 200
        else:
            return jsonify({'error': 'Failed to start server'}), 400
    except Exception as e:
        logger.error(f"Error in start server endpoint: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/server/stop', methods=['POST'])
def api_stop_server():
    """API endpoint to stop the server"""
    try:
        success = crafty.stop_server()
        if success:
            DiscordHandler.send_embed(
                'DISCORD_WEBHOOK_URL',
                title='🔴 Server Stopped',
                description='The server has been stopped',
                color='error'
            )
            return jsonify({'status': 'Server stopped'}), 200
        else:
            return jsonify({'error': 'Failed to stop server'}), 400
    except Exception as e:
        logger.error(f"Error in stop server endpoint: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/server/restart', methods=['POST'])
def api_restart_server():
    """API endpoint to restart the server"""
    try:
        success = crafty.restart_server()
        if success:
            DiscordHandler.send_embed(
                'DISCORD_WEBHOOK_URL',
                title='🔄 Server Restarting',
                description='The server is restarting',
                color='warning'
            )
            return jsonify({'status': 'Server restarting'}), 200
        else:
            return jsonify({'error': 'Failed to restart server'}), 400
    except Exception as e:
        logger.error(f"Error in restart server endpoint: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/server/status', methods=['GET'])
def api_server_status():
    """API endpoint to get server status"""
    try:
        status = crafty.get_server_status()
        if status:
            return jsonify(status), 200
        else:
            return jsonify({'error': 'Could not retrieve status'}), 500
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/server/command', methods=['POST'])
def api_send_command():
    """API endpoint to send a command to the server"""
    try:
        data = request.json
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        success = crafty.send_command(command)
        if success:
            return jsonify({'status': f'Command sent: {command}'}), 200
        else:
            return jsonify({'error': 'Failed to send command'}), 400
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Discord-Minecraft Bot on {BOT_HOST}:{BOT_PORT}")
    app.run(host=BOT_HOST, port=BOT_PORT, debug=False)
