#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Ultra Minimal (Emergency Fix)
No external dependencies except built-in modules
"""

import os
import json
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class GameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🏰 Magic Adventure Game - LIVE!</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        .title {{
            font-size: 3em;
            color: #ffd700;
            margin: 20px 0;
        }}
        .game-area {{
            width: 600px;
            height: 400px;
            background: linear-gradient(to bottom, #87CEEB 0%, #98FB98 30%, #228B22 100%);
            border: 4px solid #ffd700;
            margin: 20px auto;
            position: relative;
            cursor: pointer;
        }}
        .character {{
            position: absolute;
            font-size: 40px;
            left: 50%;
            top: 70%;
            transform: translate(-50%, -50%);
            transition: all 0.5s ease;
        }}
        .btn {{
            background: #ffd700;
            color: #1a1a2e;
            border: none;
            padding: 15px 30px;
            margin: 10px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        }}
        .success {{
            background: rgba(0, 255, 0, 0.2);
            border: 2px solid #00ff00;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            font-size: 1.3em;
        }}
    </style>
</head>
<body>
    <h1 class="title">🏰 Magic Adventure Game</h1>
    
    <div class="success">
        🎉 <strong>SUCCESSFULLY DEPLOYED!</strong> 🎉<br>
        Your game is now live on the web!
    </div>
    
    <div class="game-area" onclick="moveCharacter(event)" id="gameArea">
        <div class="character" id="character">🧙‍♂️</div>
    </div>
    
    <div>
        <button class="btn" onclick="castSpell()">✨ Cast Spell</button>
        <button class="btn" onclick="explore()">🗺️ Explore</button>
        <button class="btn" onclick="findTreasure()">💎 Find Treasure</button>
    </div>
    
    <div id="messages" style="margin-top: 20px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
        <div>🌟 Welcome to your Magic Adventure Game!</div>
        <div>🎮 Click anywhere on the game area to move your character!</div>
    </div>

    <script>
        function moveCharacter(event) {{
            const gameArea = document.getElementById('gameArea');
            const character = document.getElementById('character');
            const rect = gameArea.getBoundingClientRect();
            
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;
            
            character.style.left = x + '%';
            character.style.top = y + '%';
            
            addMessage('🚶 You moved to a new magical location!');
        }}
        
        function castSpell() {{
            addMessage('✨ You cast a powerful spell! Magic sparkles in the air!');
        }}
        
        function explore() {{
            const discoveries = [
                '🗺️ You found a hidden cave!',
                '🏰 You discovered ancient ruins!',
                '🌊 You reached a mystical lake!',
                '🌳 You entered an enchanted forest!'
            ];
            addMessage(discoveries[Math.floor(Math.random() * discoveries.length)]);
        }}
        
        function findTreasure() {{
            addMessage('💎 You found a chest full of magical gems!');
        }}
        
        function addMessage(message) {{
            const messagesDiv = document.getElementById('messages');
            const messageElement = document.createElement('div');
            messageElement.innerHTML = new Date().toLocaleTimeString() + ': ' + message;
            messageElement.style.marginTop = '5px';
            messageElement.style.color = '#a8dadc';
            messagesDiv.appendChild(messageElement);
        }}
    </script>
</body>
</html>"""
            self.wfile.write(html.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'message': 'Ultra minimal game running!'
            }
            self.wfile.write(json.dumps(health_data).encode())
            
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), GameHandler)
    
    print(f"🏰 Ultra Minimal Magic Game starting on port {port}")
    print("🌐 No external dependencies - guaranteed to work!")
    
    server.serve_forever()