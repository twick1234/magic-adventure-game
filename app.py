#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Web Application
**Version:** v1.0.0
**Created:** September 4, 2025 - 2:35 PM UTC

Main web application for deployment on Render.com
Serves the interactive game interface and manages user sessions.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DEBUG'] = os.environ.get('FLASK_ENV') != 'production'

# Initialize extensions
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Database and Cache connections
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost:5432/magic_adventure')
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

try:
    redis_client = redis.from_url(REDIS_URL)
    logger.info("✅ Connected to Redis cache")
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}")
    redis_client = None

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

@app.route('/')
def index():
    """Main game interface"""
    return render_template('game.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                conn.close()
            db_status = "healthy"
        else:
            db_status = "unhealthy"
        
        # Test Redis connection
        if redis_client:
            redis_client.ping()
            cache_status = "healthy"
        else:
            cache_status = "unavailable"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'cache': cache_status,
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/register', methods=['POST'])
def register_user():
    """User registration endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email address required'}), 400
        if not password or len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Save to database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if user exists
                cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                if cur.fetchone():
                    return jsonify({'error': 'Username or email already exists'}), 409
                
                # Create user (simulate table exists)
                # cur.execute("""
                #     INSERT INTO users (username, email, password_hash, created_at, is_active)
                #     VALUES (%s, %s, %s, NOW(), true)
                #     RETURNING id, username, email, created_at
                # """, (username, email, password_hash))
                # user = cur.fetchone()
                # conn.commit()
                
                # For demo, return success without actual DB insert
                user = {
                    'id': 1,
                    'username': username,
                    'email': email,
                    'created_at': datetime.now().isoformat()
                }
                
        finally:
            conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # For demo purposes, accept any login
        if len(username) >= 3 and len(password) >= 8:
            session['user_id'] = 1
            session['username'] = username
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': 1,
                    'username': username,
                    'last_login': datetime.now().isoformat()
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/game-state')
def get_game_state():
    """Get current game state"""
    try:
        # Get cached agent status if available
        agent_status = {}
        if redis_client:
            try:
                cached_health = redis_client.get("system:health")
                if cached_health:
                    agent_status = json.loads(cached_health)
            except Exception:
                pass
        
        # Simulate game world state
        world_state = {
            'world_name': 'Mystic Realms',
            'online_players': 42,
            'active_quests': 18,
            'world_evolution_score': 8.7,
            'last_update': datetime.now().isoformat(),
            'ai_agents': agent_status
        }
        
        return jsonify(world_state), 200
        
    except Exception as e:
        logger.error(f"Game state error: {e}")
        return jsonify({'error': 'Failed to get game state'}), 500

@app.route('/api/character/create', methods=['POST'])
def create_character():
    """Create a new character"""
    try:
        data = request.get_json()
        character_name = data.get('name', '').strip()
        character_class = data.get('class', 'warrior')
        
        if not character_name or len(character_name) < 2:
            return jsonify({'error': 'Character name must be at least 2 characters'}), 400
        
        # Simulate character creation
        character = {
            'id': secrets.randbelow(10000),
            'name': character_name,
            'class': character_class,
            'level': 1,
            'experience': 0,
            'health': 100,
            'mana': 50,
            'position': {'x': 0, 'y': 70, 'z': 0},
            'stats': {
                'strength': 10,
                'intelligence': 10,
                'dexterity': 10,
                'constitution': 10
            },
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'character': character
        }), 201
        
    except Exception as e:
        logger.error(f"Character creation error: {e}")
        return jsonify({'error': 'Failed to create character'}), 500

# WebSocket Events for Real-time Game Updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to Magic Adventure Game!'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_world')
def handle_join_world(data):
    """Handle player joining the world"""
    world_name = data.get('world', 'main_world')
    character_name = data.get('character', 'Anonymous')
    
    join_room(world_name)
    
    # Notify other players
    emit('player_joined', {
        'character': character_name,
        'message': f'{character_name} has entered the world!'
    }, room=world_name, include_self=False)
    
    # Send world info to the joining player
    emit('world_info', {
        'world_name': 'Mystic Realms',
        'biome': 'Enchanted Forest',
        'weather': 'Sunny with light breeze',
        'time_of_day': 'Afternoon',
        'nearby_players': ['Hero123', 'MagicUser', 'AdventurerX']
    })

@socketio.on('player_action')
def handle_player_action(data):
    """Handle player actions in the game"""
    action_type = data.get('type')
    character = data.get('character')
    world = data.get('world', 'main_world')
    
    if action_type == 'move':
        # Broadcast movement to other players in the same world
        emit('player_moved', {
            'character': character,
            'position': data.get('position'),
            'timestamp': datetime.now().isoformat()
        }, room=world, include_self=False)
    
    elif action_type == 'chat':
        # Broadcast chat message
        emit('chat_message', {
            'character': character,
            'message': data.get('message'),
            'timestamp': datetime.now().isoformat()
        }, room=world)
    
    elif action_type == 'interact':
        # Handle world interactions
        emit('interaction_result', {
            'success': True,
            'message': f'{character} interacted with {data.get("target")}',
            'reward': 'Found 5 gold coins!'
        })

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🏰 Starting Magic Adventure Game on port {port}")
    logger.info(f"🌐 Environment: {'Production' if not app.config['DEBUG'] else 'Development'}")
    
    # Run with socketio for WebSocket support
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )