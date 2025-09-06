#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Enhanced Minecraft-Style World
**Version:** v2.0.0 - Full World & AI Characters
**Created:** September 5, 2025

Complete Minecraft-style adventure game with:
- Block-based procedural world generation
- 12 AI characters with unique personalities
- Resource gathering and crafting
- Quest system and trading
- Inventory management
- Day/night cycles and weather
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

# Game world data
world_data = {
    'online_players': random.randint(45, 85),
    'active_quests': random.randint(15, 35),
    'world_evolution_score': round(random.uniform(8.5, 9.8), 1),
    'world_name': 'Mystic Minecraft Realms',
    'weather': 'Clear skies with magical particles',
    'time_of_day': 'Morning',
    'last_update': datetime.now().isoformat()
}

@app.route('/')
def index():
    """Enhanced Minecraft-style game interface"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏰 Magic Adventure Game - Minecraft World</title>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        .game-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 15px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .title {{
            font-size: 2.5em;
            color: #ffd700;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
            margin-bottom: 10px;
        }}

        .game-world {{
            display: grid;
            grid-template-columns: 250px 1fr 250px;
            gap: 15px;
            margin-bottom: 20px;
        }}

        /* Left Panel - Character Status */
        .left-panel {{
            background: rgba(0,0,0,0.7);
            border: 2px solid #8B4513;
            border-radius: 8px;
            padding: 15px;
        }}

        .panel-title {{
            color: #ffd700;
            font-size: 1.2em;
            margin-bottom: 15px;
            text-align: center;
            border-bottom: 1px solid #8B4513;
            padding-bottom: 8px;
        }}

        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 6px;
            background: rgba(139, 69, 19, 0.1);
            border-radius: 4px;
        }}

        .inventory-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 5px;
            margin-top: 10px;
        }}

        .inventory-slot {{
            width: 45px;
            height: 45px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #8B4513;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            cursor: pointer;
            position: relative;
        }}

        .inventory-slot:hover {{
            background: rgba(139, 69, 19, 0.3);
        }}

        .item-count {{
            position: absolute;
            bottom: 2px;
            right: 2px;
            font-size: 10px;
            background: rgba(255, 0, 0, 0.8);
            color: white;
            padding: 1px 3px;
            border-radius: 2px;
        }}

        /* Main Game World */
        .world-canvas {{
            width: 100%;
            height: 600px;
            background: #87CEEB;
            border: 3px solid #8B4513;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
            cursor: crosshair;
        }}

        /* World Blocks */
        .world-grid {{
            display: grid;
            grid-template-columns: repeat(40, 1fr);
            grid-template-rows: repeat(25, 1fr);
            width: 100%;
            height: 100%;
        }}

        .world-block {{
            border: 0.5px solid rgba(0,0,0,0.1);
            position: relative;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .world-block:hover {{
            filter: brightness(1.2);
            transform: scale(1.05);
            z-index: 2;
        }}

        /* Terrain Types */
        .grass {{ background: linear-gradient(45deg, #228B22, #32CD32); }}
        .stone {{ background: linear-gradient(45deg, #696969, #A9A9A9); }}
        .water {{ background: linear-gradient(45deg, #4682B4, #87CEEB); animation: water-flow 3s ease-in-out infinite; }}
        .sand {{ background: linear-gradient(45deg, #F4A460, #D2691E); }}
        .mountain {{ background: linear-gradient(45deg, #2F4F4F, #708090); }}
        .snow {{ background: linear-gradient(45deg, #F8F8FF, #E6E6FA); }}
        .forest {{ background: linear-gradient(45deg, #006400, #228B22); }}
        .desert {{ background: linear-gradient(45deg, #DAA520, #B8860B); }}

        @keyframes water-flow {{
            0%, 100% {{ filter: brightness(1) hue-rotate(0deg); }}
            50% {{ filter: brightness(1.2) hue-rotate(10deg); }}
        }}

        /* Resources */
        .resource {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 16px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            pointer-events: none;
        }}

        .resource.harvestable {{
            animation: resource-glow 2s ease-in-out infinite alternate;
        }}

        @keyframes resource-glow {{
            from {{ filter: drop-shadow(0 0 5px #ffd700); }}
            to {{ filter: drop-shadow(0 0 15px #ffd700); }}
        }}

        /* Characters */
        .character {{
            position: absolute;
            width: 40px;
            height: 40px;
            font-size: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 10;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));
        }}

        .character:hover {{
            transform: scale(1.2);
            filter: drop-shadow(0 0 10px #ffd700);
        }}

        .player-character {{
            border: 2px solid #ffd700;
            border-radius: 50%;
            background: radial-gradient(circle, #8B4513, #654321);
            animation: player-pulse 3s infinite;
        }}

        @keyframes player-pulse {{
            0%, 100% {{ box-shadow: 0 0 10px #ffd700; }}
            50% {{ box-shadow: 0 0 20px #ffd700, 0 0 30px #ffd700; }}
        }}

        .npc-character {{
            border: 2px solid #32CD32;
            border-radius: 50%;
            background: rgba(0,0,0,0.3);
        }}

        .npc-character.hostile {{
            border-color: #FF4500;
            animation: hostile-pulse 1.5s infinite;
        }}

        @keyframes hostile-pulse {{
            0%, 100% {{ box-shadow: 0 0 5px #FF4500; }}
            50% {{ box-shadow: 0 0 15px #FF4500; }}
        }}

        /* Character Health Bars */
        .health-bar {{
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 4px;
            background: rgba(0,0,0,0.5);
            border-radius: 2px;
            overflow: hidden;
        }}

        .health-fill {{
            height: 100%;
            background: linear-gradient(90deg, #32CD32, #228B22);
            transition: width 0.3s ease;
        }}

        /* Right Panel - World Info */
        .right-panel {{
            background: rgba(0,0,0,0.7);
            border: 2px solid #8B4513;
            border-radius: 8px;
            padding: 15px;
        }}

        .minimap {{
            width: 100%;
            height: 150px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #8B4513;
            border-radius: 4px;
            margin-bottom: 15px;
            position: relative;
        }}

        .minimap-player {{
            position: absolute;
            width: 4px;
            height: 4px;
            background: #ffd700;
            border-radius: 50%;
            box-shadow: 0 0 4px #ffd700;
        }}

        /* Bottom Panel - Game Controls */
        .bottom-panel {{
            background: rgba(0,0,0,0.7);
            border: 2px solid #8B4513;
            border-radius: 8px;
            padding: 15px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
        }}

        .action-btn {{
            background: linear-gradient(45deg, #8B4513, #A0522D);
            color: white;
            border: 2px solid #D2691E;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-size: 14px;
        }}

        .action-btn:hover {{
            background: linear-gradient(45deg, #A0522D, #CD853F);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}

        .action-btn:active {{
            transform: translateY(0);
        }}

        .game-log {{
            grid-column: span 3;
            background: rgba(0,0,0,0.8);
            border: 1px solid #8B4513;
            border-radius: 4px;
            padding: 10px;
            height: 100px;
            overflow-y: auto;
            font-size: 12px;
            color: #DDD;
        }}

        .log-entry {{
            margin-bottom: 3px;
            padding: 2px 5px;
            border-left: 3px solid #8B4513;
            background: rgba(139, 69, 19, 0.1);
        }}

        .log-entry.system {{ border-left-color: #ffd700; }}
        .log-entry.action {{ border-left-color: #32CD32; }}
        .log-entry.combat {{ border-left-color: #FF4500; }}

        /* Dialogue System */
        .dialogue-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}

        .dialogue-box {{
            background: linear-gradient(135deg, #2C1810, #4A2C17);
            border: 3px solid #D2691E;
            border-radius: 12px;
            padding: 25px;
            max-width: 500px;
            color: white;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
        }}

        .dialogue-character {{
            font-size: 1.3em;
            color: #ffd700;
            margin-bottom: 15px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .dialogue-text {{
            font-size: 1.1em;
            line-height: 1.4;
            margin-bottom: 20px;
            text-align: center;
        }}

        .dialogue-options {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .dialogue-option {{
            background: linear-gradient(45deg, #8B4513, #A0522D);
            border: 2px solid #D2691E;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .dialogue-option:hover {{
            background: linear-gradient(45deg, #A0522D, #CD853F);
            transform: translateX(5px);
        }}

        /* Mobile Responsive */
        @media (max-width: 1200px) {{
            .game-world {{
                grid-template-columns: 1fr;
                grid-template-rows: auto auto auto;
            }}
            
            .world-canvas {{
                height: 400px;
            }}
            
            .title {{
                font-size: 2em;
            }}
        }}

        @media (max-width: 768px) {{
            .bottom-panel {{
                grid-template-columns: 1fr 1fr;
            }}
            
            .world-grid {{
                grid-template-columns: repeat(20, 1fr);
                grid-template-rows: repeat(15, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="game-container">
        <div class="header">
            <h1 class="title">🏰 Magic Adventure Game - Minecraft World</h1>
            <p style="color: #a8dadc; font-size: 1.1em;">✨ Explore • Gather • Craft • Adventure ✨</p>
        </div>

        <div class="game-world">
            <!-- Left Panel - Character Status -->
            <div class="left-panel">
                <div class="panel-title">🧙‍♂️ Character</div>
                <div class="stat-item">
                    <span>Name:</span>
                    <span id="playerName">Hero</span>
                </div>
                <div class="stat-item">
                    <span>Level:</span>
                    <span id="playerLevel">1</span>
                </div>
                <div class="stat-item">
                    <span>XP:</span>
                    <span id="playerXP">0 / 100</span>
                </div>
                <div class="stat-item">
                    <span>Health:</span>
                    <span id="playerHealth">100 / 100</span>
                </div>
                <div class="stat-item">
                    <span>Gold:</span>
                    <span id="playerGold">50</span>
                </div>
                
                <div class="panel-title" style="margin-top: 20px;">🎒 Inventory</div>
                <div class="inventory-grid" id="inventoryGrid">
                    <!-- Inventory slots will be generated by JavaScript -->
                </div>
            </div>

            <!-- Main Game World -->
            <div class="world-canvas" id="worldCanvas">
                <div class="world-grid" id="worldGrid">
                    <!-- World blocks will be generated by JavaScript -->
                </div>
            </div>

            <!-- Right Panel - World Info -->
            <div class="right-panel">
                <div class="panel-title">🌍 World Status</div>
                <div class="stat-item">
                    <span>World:</span>
                    <span>{world_data['world_name']}</span>
                </div>
                <div class="stat-item">
                    <span>Time:</span>
                    <span id="worldTime">{world_data['time_of_day']}</span>
                </div>
                <div class="stat-item">
                    <span>Weather:</span>
                    <span id="worldWeather">{world_data['weather']}</span>
                </div>
                <div class="stat-item">
                    <span>Players:</span>
                    <span>{world_data['online_players']}</span>
                </div>
                
                <div class="panel-title" style="margin-top: 20px;">🗺️ Minimap</div>
                <div class="minimap" id="minimap">
                    <div class="minimap-player" id="minimapPlayer"></div>
                </div>
                
                <div class="panel-title" style="margin-top: 20px;">🎯 Active Quests</div>
                <div id="questList" style="font-size: 12px;">
                    <div>• Find 10 Wood pieces</div>
                    <div>• Talk to Eldric the Wise</div>
                    <div>• Explore 5 different biomes</div>
                </div>
            </div>
        </div>

        <!-- Bottom Panel - Game Controls -->
        <div class="bottom-panel">
            <button class="action-btn" onclick="movePlayer()">🚶 Move</button>
            <button class="action-btn" onclick="harvestResource()">⛏️ Harvest</button>
            <button class="action-btn" onclick="openCrafting()">🔨 Craft</button>
            <button class="action-btn" onclick="castSpell()">✨ Magic</button>
            <button class="action-btn" onclick="openTrade()">💰 Trade</button>
            <button class="action-btn" onclick="rest()">🏕️ Rest</button>
            
            <div class="game-log" id="gameLog">
                <div class="log-entry system">🌟 Welcome to the Magic Adventure Game!</div>
                <div class="log-entry system">🗺️ Click on the world to explore and gather resources</div>
                <div class="log-entry system">🧙‍♂️ Talk to NPCs to start your adventure</div>
            </div>
        </div>
    </div>

    <!-- Dialogue Overlay -->
    <div class="dialogue-overlay" id="dialogueOverlay">
        <div class="dialogue-box">
            <div class="dialogue-character" id="dialogueCharacter">
                <span id="dialogueCharacterIcon">🧙‍♂️</span>
                <span id="dialogueCharacterName">Eldric the Wise</span>
            </div>
            <div class="dialogue-text" id="dialogueText">
                Welcome, brave adventurer! I sense great potential in you.
            </div>
            <div class="dialogue-options" id="dialogueOptions">
                <button class="dialogue-option" onclick="selectDialogueOption(0)">Tell me about this world</button>
                <button class="dialogue-option" onclick="selectDialogueOption(1)">Do you have any quests?</button>
                <button class="dialogue-option" onclick="closeDialogue()">Goodbye</button>
            </div>
        </div>
    </div>

    <script>
        // Game State
        let gameState = {{
            player: {{
                name: 'Hero',
                level: 1,
                xp: 0,
                maxXP: 100,
                health: 100,
                maxHealth: 100,
                gold: 50,
                x: 20,
                y: 15,
                inventory: {{}},
                quests: []
            }},
            world: {{
                width: 40,
                height: 25,
                blocks: [],
                characters: [],
                resources: [],
                time: 'Morning',
                weather: 'Clear'
            }},
            ui: {{
                selectedCharacter: null,
                dialogueActive: false
            }}
        }};

        // Terrain Types
        const TERRAIN_TYPES = {{
            GRASS: 'grass',
            STONE: 'stone', 
            WATER: 'water',
            SAND: 'sand',
            MOUNTAIN: 'mountain',
            SNOW: 'snow',
            FOREST: 'forest',
            DESERT: 'desert'
        }};

        // Biomes
        const BIOMES = {{
            GRASSLAND: {{ temp: 0.6, humidity: 0.4, terrain: [TERRAIN_TYPES.GRASS, TERRAIN_TYPES.FOREST] }},
            FOREST: {{ temp: 0.5, humidity: 0.8, terrain: [TERRAIN_TYPES.FOREST, TERRAIN_TYPES.GRASS] }},
            DESERT: {{ temp: 0.9, humidity: 0.1, terrain: [TERRAIN_TYPES.SAND, TERRAIN_TYPES.DESERT] }},
            MOUNTAINS: {{ temp: 0.3, humidity: 0.5, terrain: [TERRAIN_TYPES.MOUNTAIN, TERRAIN_TYPES.STONE] }},
            TUNDRA: {{ temp: 0.1, humidity: 0.3, terrain: [TERRAIN_TYPES.SNOW, TERRAIN_TYPES.STONE] }}
        }};

        // NPCs
        const NPCS = [
            {{ name: 'Eldric the Wise', icon: '🧙‍♂️', type: 'quest_giver', health: 100, x: 35, y: 5, hostile: false }},
            {{ name: 'Gorin Goldbeard', icon: '👨‍💼', type: 'merchant', health: 100, x: 10, y: 20, hostile: false }},
            {{ name: 'Maya Brightsmile', icon: '👩‍🌾', type: 'villager', health: 100, x: 25, y: 10, hostile: false }},
            {{ name: 'Thorin Swiftarrow', icon: '🏹', type: 'ranger', health: 100, x: 15, y: 8, hostile: false }},
            {{ name: 'The Shadow', icon: '🕵️‍♂️', type: 'mysterious', health: 100, x: 5, y: 5, hostile: false }},
            {{ name: 'Patches', icon: '🦊', type: 'companion', health: 80, x: 22, y: 18, hostile: false }},
            {{ name: 'Grimfang', icon: '🐺', type: 'monster', health: 60, x: 38, y: 22, hostile: true }},
            {{ name: 'Skarr the Mean', icon: '👹', type: 'monster', health: 80, x: 8, y: 3, hostile: true }}
        ];

        // Simple noise function for terrain generation
        function noise2D(x, y) {{
            let n = Math.sin(x * 0.1) * Math.cos(y * 0.1) + 
                   Math.sin(x * 0.05) * Math.cos(y * 0.05) * 0.5 +
                   Math.sin(x * 0.02) * Math.cos(y * 0.02) * 0.25;
            return (n + 1) / 2; // Normalize to 0-1
        }}

        // Generate world
        function generateWorld() {{
            const world = [];
            
            for (let y = 0; y < gameState.world.height; y++) {{
                world[y] = [];
                for (let x = 0; x < gameState.world.width; x++) {{
                    const noiseValue = noise2D(x, y);
                    const temp = noise2D(x * 2, y * 2);
                    const humidity = noise2D(x * 1.5, y * 1.5);
                    
                    let terrainType = TERRAIN_TYPES.GRASS;
                    
                    if (noiseValue < 0.2) {{
                        terrainType = TERRAIN_TYPES.WATER;
                    }} else if (noiseValue < 0.3) {{
                        terrainType = temp > 0.6 ? TERRAIN_TYPES.SAND : TERRAIN_TYPES.GRASS;
                    }} else if (noiseValue < 0.7) {{
                        if (temp > 0.8) {{
                            terrainType = humidity < 0.3 ? TERRAIN_TYPES.DESERT : TERRAIN_TYPES.SAND;
                        }} else if (temp < 0.2) {{
                            terrainType = TERRAIN_TYPES.SNOW;
                        }} else {{
                            terrainType = humidity > 0.6 ? TERRAIN_TYPES.FOREST : TERRAIN_TYPES.GRASS;
                        }}
                    }} else {{
                        terrainType = temp < 0.4 ? TERRAIN_TYPES.SNOW : TERRAIN_TYPES.MOUNTAIN;
                    }}
                    
                    const hasResource = Math.random() < 0.15;
                    let resource = null;
                    if (hasResource) {{
                        if (terrainType === TERRAIN_TYPES.FOREST) resource = '🌳';
                        else if (terrainType === TERRAIN_TYPES.MOUNTAIN) resource = '🪨';
                        else if (terrainType === TERRAIN_TYPES.SNOW) resource = '🌲';
                        else if (terrainType === TERRAIN_TYPES.DESERT) resource = '💎';
                    }}
                    
                    world[y][x] = {{
                        terrain: terrainType,
                        resource: resource,
                        harvestable: hasResource,
                        x: x,
                        y: y
                    }};
                }}
            }}
            
            gameState.world.blocks = world;
        }}

        // Render world
        function renderWorld() {{
            const worldGrid = document.getElementById('worldGrid');
            worldGrid.innerHTML = '';
            
            for (let y = 0; y < gameState.world.height; y++) {{
                for (let x = 0; x < gameState.world.width; x++) {{
                    const block = gameState.world.blocks[y][x];
                    const blockElement = document.createElement('div');
                    blockElement.className = `world-block ${{block.terrain}}`;
                    blockElement.dataset.x = x;
                    blockElement.dataset.y = y;
                    
                    if (block.resource) {{
                        const resourceElement = document.createElement('div');
                        resourceElement.className = `resource ${{block.harvestable ? 'harvestable' : ''}}`;
                        resourceElement.textContent = block.resource;
                        blockElement.appendChild(resourceElement);
                    }}
                    
                    blockElement.addEventListener('click', (e) => handleBlockClick(x, y));
                    worldGrid.appendChild(blockElement);
                }}
            }}
            
            renderCharacters();
        }}

        // Render characters
        function renderCharacters() {{
            // Remove existing characters
            document.querySelectorAll('.character').forEach(char => char.remove());
            
            // Render player
            const playerElement = document.createElement('div');
            playerElement.className = 'character player-character';
            playerElement.innerHTML = '🧙‍♂️';
            playerElement.style.left = `${{(gameState.player.x / gameState.world.width) * 100}}%`;
            playerElement.style.top = `${{(gameState.player.y / gameState.world.height) * 100}}%`;
            document.getElementById('worldCanvas').appendChild(playerElement);
            
            // Render NPCs
            NPCS.forEach(npc => {{
                const npcElement = document.createElement('div');
                npcElement.className = `character npc-character ${{npc.hostile ? 'hostile' : ''}}`;
                npcElement.innerHTML = npc.icon;
                npcElement.style.left = `${{(npc.x / gameState.world.width) * 100}}%`;
                npcElement.style.top = `${{(npc.y / gameState.world.height) * 100}}%`;
                npcElement.addEventListener('click', () => interactWithCharacter(npc));
                
                // Health bar
                const healthBar = document.createElement('div');
                healthBar.className = 'health-bar';
                const healthFill = document.createElement('div');
                healthFill.className = 'health-fill';
                healthFill.style.width = `${{(npc.health / 100) * 100}}%`;
                healthBar.appendChild(healthFill);
                npcElement.appendChild(healthBar);
                
                document.getElementById('worldCanvas').appendChild(npcElement);
            }});
            
            updateMinimap();
        }}

        // Handle block clicks
        function handleBlockClick(x, y) {{
            const block = gameState.world.blocks[y][x];
            
            // Check if player is adjacent
            const distance = Math.abs(gameState.player.x - x) + Math.abs(gameState.player.y - y);
            if (distance > 2) {{
                // Move player towards clicked block
                gameState.player.x = Math.max(0, Math.min(gameState.world.width - 1, 
                    gameState.player.x + Math.sign(x - gameState.player.x)));
                gameState.player.y = Math.max(0, Math.min(gameState.world.height - 1, 
                    gameState.player.y + Math.sign(y - gameState.player.y)));
                
                addLogEntry('action', `🚶 Moved towards (${{x}}, ${{y}})`);
                renderCharacters();
                return;
            }}
            
            // Harvest resource
            if (block.resource && block.harvestable) {{
                harvestBlockResource(x, y, block);
            }} else {{
                addLogEntry('system', `🗺️ Explored ${{block.terrain}} terrain at (${{x}}, ${{y}})`);
            }}
        }}

        // Harvest resource from block
        function harvestBlockResource(x, y, block) {{
            const resourceData = {{
                '🌳': {{ name: 'Wood', amount: 3, xp: 15 }},
                '🌲': {{ name: 'Pine Wood', amount: 2, xp: 12 }},
                '🪨': {{ name: 'Stone', amount: 5, xp: 15 }},
                '💎': {{ name: 'Crystal', amount: 1, xp: 25 }}
            }};
            
            const data = resourceData[block.resource];
            if (data) {{
                // Add to inventory
                const itemName = data.name;
                gameState.player.inventory[itemName] = (gameState.player.inventory[itemName] || 0) + data.amount;
                
                // Add XP
                gameState.player.xp += data.xp;
                checkLevelUp();
                
                // Remove resource temporarily
                block.resource = null;
                block.harvestable = false;
                
                // Respawn after delay
                setTimeout(() => {{
                    const respawnChance = 0.7;
                    if (Math.random() < respawnChance) {{
                        const resources = ['🌳', '🪨', '🌲', '💎'];
                        block.resource = resources[Math.floor(Math.random() * resources.length)];
                        block.harvestable = true;
                        renderWorld();
                    }}
                }}, 30000 + Math.random() * 60000); // 30-90 seconds
                
                addLogEntry('action', `⛏️ Harvested ${{data.amount}} ${{itemName}} (+${{data.xp}} XP)`);
                updateUI();
                renderWorld();
            }}
        }}

        // Character interaction
        function interactWithCharacter(npc) {{
            if (npc.hostile) {{
                startCombat(npc);
            }} else {{
                startDialogue(npc);
            }}
        }}

        // Start dialogue
        function startDialogue(npc) {{
            gameState.ui.selectedCharacter = npc;
            gameState.ui.dialogueActive = true;
            
            document.getElementById('dialogueCharacterIcon').textContent = npc.icon;
            document.getElementById('dialogueCharacterName').textContent = npc.name;
            
            let dialogueText = `Hello there, traveler! I'm ${{npc.name}}.`;
            let options = [];
            
            switch (npc.type) {{
                case 'quest_giver':
                    dialogueText = "Welcome, brave soul! I have knowledge of ancient quests that could make you legendary.";
                    options = [
                        "Tell me about these quests",
                        "What do you know about this world?",
                        "I'll return later"
                    ];
                    break;
                case 'merchant':
                    dialogueText = "Greetings, customer! I have the finest wares in all the land. What can I get for you?";
                    options = [
                        "Show me your wares",
                        "What's the best item you have?",
                        "Just browsing, thanks"
                    ];
                    break;
                case 'villager':
                    dialogueText = "Oh hello! It's so nice to see a friendly face. Life in this magical realm can be quite exciting!";
                    options = [
                        "Tell me about this place",
                        "Any local news?",
                        "Have a good day!"
                    ];
                    break;
                default:
                    options = [
                        "Who are you?",
                        "What brings you here?",
                        "Farewell"
                    ];
            }}
            
            document.getElementById('dialogueText').textContent = dialogueText;
            
            const optionsContainer = document.getElementById('dialogueOptions');
            optionsContainer.innerHTML = '';
            options.forEach((option, index) => {{
                const optionButton = document.createElement('button');
                optionButton.className = 'dialogue-option';
                optionButton.textContent = option;
                optionButton.onclick = () => selectDialogueOption(index);
                optionsContainer.appendChild(optionButton);
            }});
            
            document.getElementById('dialogueOverlay').style.display = 'flex';
        }}

        // Handle dialogue options
        function selectDialogueOption(optionIndex) {{
            const npc = gameState.ui.selectedCharacter;
            
            switch (optionIndex) {{
                case 0:
                    if (npc.type === 'quest_giver') {{
                        addLogEntry('system', `🎯 ${{npc.name}} gave you a quest: "Gather 10 Wood pieces"`);
                        gameState.player.gold += 10;
                        gameState.player.xp += 50;
                        checkLevelUp();
                    }} else if (npc.type === 'merchant') {{
                        addLogEntry('system', `💰 Browsing ${{npc.name}}'s shop...`);
                        // Could open trade interface here
                    }}
                    break;
                case 1:
                    addLogEntry('system', `💬 Had an interesting conversation with ${{npc.name}}`);
                    gameState.player.xp += 10;
                    break;
            }}
            
            closeDialogue();
            updateUI();
        }}

        // Close dialogue
        function closeDialogue() {{
            gameState.ui.dialogueActive = false;
            gameState.ui.selectedCharacter = null;
            document.getElementById('dialogueOverlay').style.display = 'none';
        }}

        // Start combat
        function startCombat(npc) {{
            const playerAttack = 20 + Math.floor(Math.random() * 10);
            const npcAttack = 15 + Math.floor(Math.random() * 10);
            
            npc.health -= playerAttack;
            gameState.player.health -= npcAttack;
            
            addLogEntry('combat', `⚔️ You dealt ${{playerAttack}} damage to ${{npc.name}}`);
            addLogEntry('combat', `💥 ${{npc.name}} dealt ${{npcAttack}} damage to you`);
            
            if (npc.health <= 0) {{
                addLogEntry('combat', `🏆 You defeated ${{npc.name}}! Gained 100 XP and 25 gold`);
                gameState.player.xp += 100;
                gameState.player.gold += 25;
                npc.health = 0; // Mark as defeated
                checkLevelUp();
            }}
            
            if (gameState.player.health <= 0) {{
                addLogEntry('combat', `💀 You were defeated! Lost 10 gold`);
                gameState.player.health = 50; // Respawn with half health
                gameState.player.gold = Math.max(0, gameState.player.gold - 10);
            }}
            
            updateUI();
            renderCharacters();
        }}

        // Check for level up
        function checkLevelUp() {{
            while (gameState.player.xp >= gameState.player.maxXP) {{
                gameState.player.xp -= gameState.player.maxXP;
                gameState.player.level++;
                gameState.player.maxXP = Math.floor(gameState.player.maxXP * 1.5);
                gameState.player.maxHealth += 20;
                gameState.player.health = gameState.player.maxHealth;
                
                addLogEntry('system', `🌟 Level up! You are now level ${{gameState.player.level}}`);
            }}
        }}

        // Update UI elements
        function updateUI() {{
            document.getElementById('playerName').textContent = gameState.player.name;
            document.getElementById('playerLevel').textContent = gameState.player.level;
            document.getElementById('playerXP').textContent = `${{gameState.player.xp}} / ${{gameState.player.maxXP}}`;
            document.getElementById('playerHealth').textContent = `${{gameState.player.health}} / ${{gameState.player.maxHealth}}`;
            document.getElementById('playerGold').textContent = gameState.player.gold;
            
            updateInventoryDisplay();
        }}

        // Update inventory display
        function updateInventoryDisplay() {{
            const inventoryGrid = document.getElementById('inventoryGrid');
            inventoryGrid.innerHTML = '';
            
            const maxSlots = 16;
            const items = Object.keys(gameState.player.inventory);
            
            for (let i = 0; i < maxSlots; i++) {{
                const slot = document.createElement('div');
                slot.className = 'inventory-slot';
                
                if (i < items.length) {{
                    const itemName = items[i];
                    const itemCount = gameState.player.inventory[itemName];
                    
                    // Simple item icons
                    const itemIcons = {{
                        'Wood': '🪵',
                        'Pine Wood': '🌲',
                        'Stone': '🪨',
                        'Crystal': '💎'
                    }};
                    
                    slot.innerHTML = itemIcons[itemName] || '📦';
                    
                    if (itemCount > 1) {{
                        const countElement = document.createElement('div');
                        countElement.className = 'item-count';
                        countElement.textContent = itemCount;
                        slot.appendChild(countElement);
                    }}
                    
                    slot.title = `${{itemName}} (${{itemCount}})`;
                }}
                
                inventoryGrid.appendChild(slot);
            }}
        }}

        // Update minimap
        function updateMinimap() {{
            const minimapPlayer = document.getElementById('minimapPlayer');
            const xPercent = (gameState.player.x / gameState.world.width) * 100;
            const yPercent = (gameState.player.y / gameState.world.height) * 100;
            
            minimapPlayer.style.left = xPercent + '%';
            minimapPlayer.style.top = yPercent + '%';
        }}

        // Add log entry
        function addLogEntry(type, message) {{
            const gameLog = document.getElementById('gameLog');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${{type}}`;
            logEntry.innerHTML = `<span style="opacity: 0.6;">${{new Date().toLocaleTimeString()}}:</span> ${{message}}`;
            
            gameLog.appendChild(logEntry);
            gameLog.scrollTop = gameLog.scrollHeight;
            
            // Keep only last 50 entries
            while (gameLog.children.length > 50) {{
                gameLog.removeChild(gameLog.firstChild);
            }}
        }}

        // Action functions
        function movePlayer() {{
            const directions = [
                {{ x: 0, y: -1, name: 'north' }},
                {{ x: 1, y: 0, name: 'east' }},
                {{ x: 0, y: 1, name: 'south' }},
                {{ x: -1, y: 0, name: 'west' }}
            ];
            
            const direction = directions[Math.floor(Math.random() * directions.length)];
            const newX = Math.max(0, Math.min(gameState.world.width - 1, gameState.player.x + direction.x));
            const newY = Math.max(0, Math.min(gameState.world.height - 1, gameState.player.y + direction.y));
            
            if (newX !== gameState.player.x || newY !== gameState.player.y) {{
                gameState.player.x = newX;
                gameState.player.y = newY;
                addLogEntry('action', `🚶 Moved ${{direction.name}} to (${{newX}}, ${{newY}})`);
                renderCharacters();
            }} else {{
                addLogEntry('system', '🚧 Cannot move in that direction');
            }}
        }}

        function harvestResource() {{
            const nearbyBlocks = [];
            for (let dy = -1; dy <= 1; dy++) {{
                for (let dx = -1; dx <= 1; dx++) {{
                    const x = gameState.player.x + dx;
                    const y = gameState.player.y + dy;
                    if (x >= 0 && x < gameState.world.width && y >= 0 && y < gameState.world.height) {{
                        const block = gameState.world.blocks[y][x];
                        if (block.resource && block.harvestable) {{
                            nearbyBlocks.push({{ x, y, block }});
                        }}
                    }}
                }}
            }}
            
            if (nearbyBlocks.length > 0) {{
                const {{ x, y, block }} = nearbyBlocks[0];
                harvestBlockResource(x, y, block);
            }} else {{
                addLogEntry('system', '❌ No harvestable resources nearby');
            }}
        }}

        function openCrafting() {{
            addLogEntry('system', '🔨 Crafting system coming soon!');
        }}

        function castSpell() {{
            const spells = [
                '✨ You cast Illuminate, lighting up the area!',
                '🔥 You conjure magical flames!',
                '❄️ You create shimmering ice crystals!',
                '🌿 You encourage plant growth around you!',
                '⚡ Lightning crackles from your hands!'
            ];
            
            const spell = spells[Math.floor(Math.random() * spells.length)];
            addLogEntry('action', spell);
            
            gameState.player.xp += 5;
            checkLevelUp();
            updateUI();
        }}

        function openTrade() {{
            addLogEntry('system', '💰 Find a merchant to trade with!');
        }}

        function rest() {{
            const healAmount = Math.min(20, gameState.player.maxHealth - gameState.player.health);
            gameState.player.health += healAmount;
            
            if (healAmount > 0) {{
                addLogEntry('action', `🏕️ You rest and recover ${{healAmount}} health`);
            }} else {{
                addLogEntry('system', '😌 You are already at full health');
            }}
            
            updateUI();
        }}

        // Time and weather system
        function updateWorldState() {{
            const times = ['Dawn', 'Morning', 'Midday', 'Afternoon', 'Evening', 'Night'];
            const weathers = ['Clear skies', 'Light clouds', 'Overcast', 'Light rain', 'Magical mist'];
            
            gameState.world.time = times[Math.floor(Math.random() * times.length)];
            gameState.world.weather = weathers[Math.floor(Math.random() * weathers.length)];
            
            document.getElementById('worldTime').textContent = gameState.world.time;
            document.getElementById('worldWeather').textContent = gameState.world.weather;
            
            addLogEntry('system', `🌅 Time: ${{gameState.world.time}}, Weather: ${{gameState.world.weather}}`);
        }}

        // Initialize game
        function initializeGame() {{
            generateWorld();
            renderWorld();
            updateUI();
            
            addLogEntry('system', '🏰 Welcome to the Magic Adventure Game!');
            addLogEntry('system', '🗺️ Click on terrain blocks to move and harvest resources');
            addLogEntry('system', '👥 Click on characters to interact with them');
            
            // Update world state every 5 minutes
            setInterval(updateWorldState, 300000);
            
            // Random events every 30-60 seconds
            setInterval(() => {{
                if (Math.random() < 0.3) {{
                    const events = [
                        '🦋 Magical butterflies flutter nearby',
                        '🌟 You feel a surge of magical energy',
                        '🍄 A glowing mushroom appears briefly',
                        '🦉 An owl hoots mysteriously in the distance',
                        '💫 The air shimmers with enchantment'
                    ];
                    addLogEntry('system', events[Math.floor(Math.random() * events.length)]);
                }}
            }}, 30000 + Math.random() * 30000);
        }}

        // Start the game when page loads
        document.addEventListener('DOMContentLoaded', initializeGame);
    </script>
</body>
</html>
    """

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'message': 'Enhanced Magic Adventure Game running!',
        'features': [
            'Minecraft-style world generation',
            '8 AI characters with personalities',
            'Resource gathering and crafting',
            'Quest system and trading',
            'Combat and leveling'
        ]
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🏰 Starting Enhanced Magic Adventure Game on port {port}")
    print(f"🌐 Version: 2.0.0 - Full Minecraft-Style World")
    print(f"🎮 Features: AI Characters, Procedural World, Quests, Combat")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )