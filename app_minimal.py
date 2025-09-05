#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Minimal Web Application
**Version:** v1.2.0 - Python 3.13 Compatible
**Created:** September 5, 2025

Ultra-minimal Flask application with no database dependencies
Guaranteed to work on Render with Python 3.13
"""

import os
import json
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'magic-adventure-secret-key-2025')
CORS(app)

# Simple in-memory game state
game_state = {
    'online_players': random.randint(25, 75),
    'active_quests': random.randint(10, 30),
    'world_evolution_score': round(random.uniform(7.0, 9.5), 1),
    'world_name': 'Mystic Realms',
    'weather': 'Sunny with magical breezes',
    'last_update': datetime.now().isoformat()
}

@app.route('/')
def index():
    """Main game interface"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏰 Magic Adventure Game - Live!</title>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }}

        .stars {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }}

        .star {{
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }}

        @keyframes twinkle {{
            0%, 100% {{ opacity: 0.3; transform: scale(1); }}
            50% {{ opacity: 1; transform: scale(1.2); }}
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            animation: fadeIn 2s ease-in;
        }}

        .title {{
            font-size: 4em;
            color: #ffd700;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite alternate;
        }}

        @keyframes glow {{
            from {{ text-shadow: 3px 3px 6px rgba(0,0,0,0.8), 0 0 20px #ffd700; }}
            to {{ text-shadow: 3px 3px 6px rgba(0,0,0,0.8), 0 0 30px #ffd700, 0 0 40px #ffd700; }}
        }}

        .subtitle {{
            font-size: 1.4em;
            color: #a8dadc;
            margin-bottom: 30px;
        }}

        .game-canvas {{
            width: 100%;
            height: 500px;
            background: linear-gradient(to bottom, #87CEEB 0%, #98FB98 30%, #228B22 100%);
            border: 4px solid #ffd700;
            border-radius: 15px;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
        }}

        .character {{
            position: absolute;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, #8B4513, #654321);
            border-radius: 50%;
            transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            border: 3px solid #ffd700;
            left: 50%;
            top: 70%;
            transform: translate(-50%, -50%);
            animation: bounce 3s infinite;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
            cursor: pointer;
        }}

        .character:before {{
            content: "🧙‍♂️";
            font-size: 40px;
            position: absolute;
            top: -8px;
            left: 8px;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
        }}

        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translate(-50%, -50%) translateY(0); }}
            40% {{ transform: translate(-50%, -50%) translateY(-15px); }}
            60% {{ transform: translate(-50%, -50%) translateY(-8px); }}
        }}

        .game-ui {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}

        .panel {{
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid #ffd700;
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}

        .panel h3 {{
            color: #ffd700;
            margin-bottom: 20px;
            font-size: 1.5em;
            text-align: center;
        }}

        .status-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            padding: 8px 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 4px solid #ffd700;
        }}

        .btn {{
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            color: #1a1a2e;
            border: none;
            padding: 15px 30px;
            border-radius: 30px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 8px;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }}

        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.5);
        }}

        .success-message {{
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }}
        }}

        .demo-info {{
            background: rgba(255, 165, 0, 0.1);
            border: 2px solid #ffa500;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-50px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 768px) {{
            .title {{
                font-size: 2.5em;
            }}
            
            .game-canvas {{
                height: 300px;
            }}
            
            .container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="stars" id="stars"></div>
    
    <div class="container">
        <div class="header">
            <h1 class="title">🏰 Magic Adventure Game</h1>
            <p class="subtitle">✨ A Living World Powered by AI Agents ✨</p>
            
            <div class="success-message">
                🎉 <strong>Successfully Deployed on Render!</strong> 🎉<br>
                Your Magic Adventure Game is now live on the web!
            </div>
        </div>

        <div class="demo-info">
            <h3>🚀 Live Demo Features</h3>
            <p>Click anywhere on the game canvas to move your character around the magical world!</p>
        </div>

        <div class="game-canvas" id="gameCanvas" onclick="moveCharacter(event)">
            <div class="character" id="character"></div>
        </div>

        <div class="game-ui">
            <div class="panel">
                <h3>🧙‍♂️ Character Status</h3>
                <div class="status-item">
                    <span>Name:</span>
                    <span id="characterName">Hero</span>
                </div>
                <div class="status-item">
                    <span>Level:</span>
                    <span>1</span>
                </div>
                <div class="status-item">
                    <span>Health:</span>
                    <span>100/100</span>
                </div>
                <div class="status-item">
                    <span>Mana:</span>
                    <span>50/50</span>
                </div>
                <button class="btn" onclick="changeCharacterName()">New Character</button>
            </div>

            <div class="panel">
                <h3>🌍 World Status</h3>
                <div class="status-item">
                    <span>World:</span>
                    <span>{game_state['world_name']}</span>
                </div>
                <div class="status-item">
                    <span>Online Players:</span>
                    <span>{game_state['online_players']}</span>
                </div>
                <div class="status-item">
                    <span>Active Quests:</span>
                    <span>{game_state['active_quests']}</span>
                </div>
                <div class="status-item">
                    <span>Evolution Score:</span>
                    <span>{game_state['world_evolution_score']}/10</span>
                </div>
                <div class="status-item">
                    <span>Weather:</span>
                    <span>{game_state['weather']}</span>
                </div>
            </div>

            <div class="panel">
                <h3>🤖 AI Agents Status</h3>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>🌍 Terrain Sculptor:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>🏰 Structure Architect:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>🦌 Ecosystem Manager:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>🌦️ Weather Controller:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>📚 Story Weaver:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>⚔️ Quest Master:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>⚖️ Balance Guardian:</span>
                    <span>Active</span>
                </div>
                <div class="status-item" style="background: rgba(0, 255, 0, 0.1);">
                    <span>🎉 Event Coordinator:</span>
                    <span>Active</span>
                </div>
                <button class="btn" onclick="updateAgentStatus()">Refresh Status</button>
            </div>
        </div>

        <div class="panel">
            <h3>🎮 Game Controls</h3>
            <p style="text-align: center; margin-bottom: 20px;">
                Welcome to your Magic Adventure Game! This is a live demonstration of the web interface.
            </p>
            <div style="text-align: center;">
                <button class="btn" onclick="exploreWorld()">🗺️ Explore World</button>
                <button class="btn" onclick="castSpell()">✨ Cast Spell</button>
                <button class="btn" onclick="findTreasure()">💎 Find Treasure</button>
            </div>
            <div id="gameMessages" style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px; min-height: 100px;">
                <div style="color: #ffd700;"><strong>🏰 System:</strong> Welcome to the Magic Adventure Game!</div>
                <div style="color: #a8dadc;"><strong>✨ Hint:</strong> Click anywhere on the game canvas above to move your character!</div>
            </div>
        </div>
    </div>

    <script>
        // Create animated stars
        function createStars() {{
            const starsContainer = document.getElementById('stars');
            for (let i = 0; i < 150; i++) {{
                const star = document.createElement('div');
                star.className = 'star';
                star.style.left = Math.random() * 100 + '%';
                star.style.top = Math.random() * 100 + '%';
                star.style.width = Math.random() * 4 + 1 + 'px';
                star.style.height = star.style.width;
                star.style.animationDelay = Math.random() * 3 + 's';
                starsContainer.appendChild(star);
            }}
        }}

        // Move character to clicked position
        function moveCharacter(event) {{
            const canvas = document.getElementById('gameCanvas');
            const character = document.getElementById('character');
            const rect = canvas.getBoundingClientRect();
            
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;
            
            character.style.left = x + '%';
            character.style.top = y + '%';
            
            addGameMessage('🚶 You moved to a new location in the magical realm!');
            
            // Random discoveries
            setTimeout(() => {{
                const discoveries = [
                    '✨ You found some magical sparkles!',
                    '🌺 A beautiful flower blooms where you stepped!',
                    '🦋 Magical butterflies flutter around you!',
                    '💫 You sense ancient magic in this area!',
                    '🍄 You discovered a glowing mushroom!'
                ];
                if (Math.random() < 0.4) {{
                    addGameMessage(discoveries[Math.floor(Math.random() * discoveries.length)]);
                }}
            }}, 800);
        }}

        function changeCharacterName() {{
            const newName = prompt('Enter your new character name:', 'Hero');
            if (newName && newName.trim()) {{
                document.getElementById('characterName').textContent = newName.trim();
                addGameMessage(`🎭 Your character is now known as ${{newName.trim()}}!`);
            }}
        }}

        function exploreWorld() {{
            const explorations = [
                '🗺️ You discovered a hidden cave filled with crystals!',
                '🏰 You found the ruins of an ancient castle!',
                '🌊 You reached a mystical lake with healing waters!',
                '🌳 You entered a forest where trees whisper secrets!',
                '⛰️ You climbed a mountain and saw the entire realm!'
            ];
            addGameMessage(explorations[Math.floor(Math.random() * explorations.length)]);
        }}

        function castSpell() {{
            const spells = [
                '✨ Your spell illuminated the darkness around you!',
                '🔥 You conjured magical flames that dance in the air!',
                '❄️ You created beautiful ice crystals that sparkle!',
                '🌿 Your magic made flowers bloom instantly!',
                '⚡ Lightning crackles from your fingertips!'
            ];
            addGameMessage(spells[Math.floor(Math.random() * spells.length)]);
        }}

        function findTreasure() {{
            const treasures = [
                '💎 You found a chest filled with magical gems!',
                '👑 You discovered a golden crown of ancient kings!',
                '📜 You found a scroll with powerful spells!',
                '🗝️ You obtained a key to unlock hidden doors!',
                '💰 You found a pouch of enchanted gold coins!'
            ];
            addGameMessage(treasures[Math.floor(Math.random() * treasures.length)]);
        }}

        function updateAgentStatus() {{
            addGameMessage('🤖 AI Agent status refreshed - All 8 agents are working to evolve the world!');
        }}

        function addGameMessage(message) {{
            const messagesDiv = document.getElementById('gameMessages');
            const messageElement = document.createElement('div');
            messageElement.innerHTML = `<strong>${{new Date().toLocaleTimeString()}}:</strong> ${{message}}`;
            messageElement.style.color = '#a8dadc';
            messageElement.style.marginTop = '5px';
            messagesDiv.appendChild(messageElement);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}

        // Initialize the game
        document.addEventListener('DOMContentLoaded', function() {{
            createStars();
            addGameMessage('🌟 Magic Adventure Game successfully loaded!');
            addGameMessage('🎮 Click on the game canvas above to move your character around!');
            
            // Auto-move character occasionally for demo
            setInterval(() => {{
                if (Math.random() < 0.1) {{
                    const canvas = document.getElementById('gameCanvas');
                    const character = document.getElementById('character');
                    const x = Math.random() * 80 + 10;
                    const y = Math.random() * 60 + 20;
                    character.style.left = x + '%';
                    character.style.top = y + '%';
                    addGameMessage('🌟 The magical realm shifts around you...');
                }}
            }}, 15000);
        }});
    </script>
</body>
</html>
    """

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.2.0',
        'message': 'Magic Adventure Game is running successfully!',
        'python_version': '3.13',
        'deployment': 'render'
    }), 200

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    # Update some values for demo
    game_state['online_players'] = random.randint(25, 75)
    game_state['active_quests'] = random.randint(10, 30)
    game_state['last_update'] = datetime.now().isoformat()
    
    return jsonify(game_state), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🏰 Starting Magic Adventure Game on port {port}")
    print(f"🌐 Version: 1.2.0 - Python 3.13 Compatible")
    print(f"🎮 No database dependencies - guaranteed to work!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )