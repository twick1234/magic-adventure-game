#!/usr/bin/env python3
"""
🌐 Web Frontend Integration Utilities

This module provides comprehensive integration utilities for connecting
the Magic Adventure Game CrewAI system with web frontends.

Features:
- FastAPI REST API endpoints for game interactions
- WebSocket support for real-time agent responses
- Request/response serialization and validation
- Session management and state persistence
- CORS support for cross-origin requests
- API documentation and testing utilities
- Frontend helper libraries and utilities
- Response caching and optimization

Designed to be modular and scalable for various web technologies.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid
import logging

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    # Graceful degradation if FastAPI is not installed
    FastAPI = None
    print("⚠️ FastAPI not installed. Web integration will have limited functionality.")

# Import our game modules
from game_orchestrator import MagicAdventureOrchestrator, GameContext, GameState
from crewai_agents import MagicAdventureAgents
from agent_communication import AgentCommunicationHub, SharedContextDB
from error_handling import GameLogger, ErrorHandler, ErrorCategory, ErrorSeverity
from agent_config import AgentConfigurationManager

# Configure logging
logger = logging.getLogger(__name__)


# Pydantic models for API validation
if FastAPI:
    class PlayerInfo(BaseModel):
        name: str = Field(..., min_length=1, max_length=50)
        character_class: str = Field(default="Adventurer", max_length=30)
        
    class GameAction(BaseModel):
        action: str = Field(..., min_length=1)
        action_type: str = Field(default="choice")
        context: Optional[Dict[str, Any]] = None
        
    class GameResponse(BaseModel):
        success: bool
        game_state: str
        message: Optional[str] = None
        data: Optional[Dict[str, Any]] = None
        processing_time: float = 0.0
        timestamp: datetime = Field(default_factory=datetime.now)
        
    class AgentUpdate(BaseModel):
        agent_name: str
        content: str
        metadata: Optional[Dict[str, Any]] = None


class SessionManager:
    """Manages game sessions and player states"""
    
    def __init__(self):
        self.sessions = {}
        self.session_timeouts = {}
        self.cleanup_interval = 3600  # 1 hour
        
        logger.info("🎮 Initialized Session Manager")
    
    def create_session(self, player_info: Dict[str, Any]) -> str:
        """Create a new game session"""
        session_id = str(uuid.uuid4())
        
        # Initialize game context
        context = GameContext(
            player_name=player_info.get("name", "Adventurer"),
            player_class=player_info.get("character_class", "Adventurer")
        )
        
        # Create orchestrator for this session
        orchestrator = MagicAdventureOrchestrator(context)
        
        self.sessions[session_id] = {
            "id": session_id,
            "orchestrator": orchestrator,
            "context": context,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "player_info": player_info
        }
        
        # Set timeout
        self.session_timeouts[session_id] = datetime.now() + timedelta(hours=24)
        
        logger.info(f"📝 Created session {session_id} for {player_info.get('name')}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        if session_id in self.sessions:
            # Update last activity
            self.sessions[session_id]["last_activity"] = datetime.now()
            return self.sessions[session_id]
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.session_timeouts:
                del self.session_timeouts[session_id]
            logger.info(f"🗑️ Deleted session {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, timeout in self.session_timeouts.items()
            if now > timeout
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        now = datetime.now()
        active_sessions = sum(1 for s in self.sessions.values() 
                            if now - s["last_activity"] < timedelta(minutes=30))
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "oldest_session": min([s["created_at"] for s in self.sessions.values()]) if self.sessions else None,
            "newest_session": max([s["created_at"] for s in self.sessions.values()]) if self.sessions else None
        }


class WebSocketManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, List[str]] = {}
        
        logger.info("🔌 Initialized WebSocket Manager")
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket for a session"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)
        
        logger.info(f"🔗 WebSocket connected: {connection_id} for session {session_id}")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Disconnect a WebSocket"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            
            # Remove from session connections
            for session_id, conn_list in self.session_connections.items():
                if connection_id in conn_list:
                    conn_list.remove(connection_id)
                    break
            
            logger.info(f"🔌 WebSocket disconnected: {connection_id}")
    
    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        """Send message to all connections for a session"""
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id][:]:  # Copy to avoid modification during iteration
                if connection_id in self.connections:
                    try:
                        await self.connections[connection_id].send_text(json.dumps(message))
                    except Exception as e:
                        logger.warning(f"Failed to send to connection {connection_id}: {e}")
                        self.disconnect(connection_id)
    
    async def broadcast_agent_update(self, session_id: str, agent_name: str, content: str, metadata: Optional[Dict] = None):
        """Broadcast agent update to session"""
        message = {
            "type": "agent_update",
            "agent_name": agent_name,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)


class ResponseCache:
    """Cache for agent responses to improve performance"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        
        logger.info("💾 Initialized Response Cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached response"""
        if key in self.cache:
            if datetime.now() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached response"""
        # Cleanup if at max size
        if len(self.cache) >= self.max_size:
            self._cleanup_oldest()
        
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
    
    def _cleanup_oldest(self):
        """Remove oldest entries"""
        sorted_items = sorted(self.timestamps.items(), key=lambda x: x[1])
        oldest_keys = [k for k, _ in sorted_items[:self.max_size // 4]]
        
        for key in oldest_keys:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        self.timestamps.clear()


class GameAPI:
    """Main API class for the Magic Adventure Game"""
    
    def __init__(self):
        self.app = None
        self.session_manager = SessionManager()
        self.websocket_manager = WebSocketManager()
        self.response_cache = ResponseCache()
        self.game_logger = GameLogger("magic_adventure_api")
        self.error_handler = ErrorHandler(self.game_logger)
        
        if FastAPI:
            self._setup_fastapi()
        
        logger.info("🚀 Initialized Game API")
    
    def _setup_fastapi(self):
        """Setup FastAPI application"""
        self.app = FastAPI(
            title="Magic Adventure Game API",
            description="CrewAI-powered interactive fantasy adventure game",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routes
        self._add_routes()
        
        logger.info("⚙️ FastAPI application configured")
    
    def _add_routes(self):
        """Add API routes"""
        
        @self.app.post("/api/game/start", response_model=GameResponse)
        async def start_game(player_info: PlayerInfo):
            """Start a new game session"""
            try:
                self.game_logger.player_action("start_game", {"player": player_info.name})
                
                # Create session
                session_id = self.session_manager.create_session(player_info.dict())
                session = self.session_manager.get_session(session_id)
                
                # Start the game
                start_response = session["orchestrator"].start_new_game(
                    player_info.name, player_info.character_class
                )
                
                return GameResponse(
                    success=True,
                    game_state=session["context"].game_state.value,
                    data={
                        "session_id": session_id,
                        "game_content": start_response
                    }
                )
                
            except Exception as e:
                self.error_handler.handle_error(
                    e, ErrorCategory.SYSTEM_ERROR, ErrorSeverity.HIGH
                )
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/game/{session_id}/action", response_model=GameResponse)
        async def process_action(session_id: str, action: GameAction):
            """Process a player action"""
            try:
                session = self.session_manager.get_session(session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                self.game_logger.player_action("game_action", {
                    "session": session_id,
                    "action": action.action,
                    "type": action.action_type
                })
                
                # Process the action
                response = session["orchestrator"].process_player_action(
                    action.action, action.action_type
                )
                
                # Broadcast update via WebSocket
                await self.websocket_manager.send_to_session(session_id, {
                    "type": "action_result",
                    "data": response
                })
                
                return GameResponse(
                    success=True,
                    game_state=session["context"].game_state.value,
                    data=response
                )
                
            except Exception as e:
                self.error_handler.handle_error(
                    e, ErrorCategory.SYSTEM_ERROR, ErrorSeverity.MEDIUM,
                    context={"session_id": session_id}
                )
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/game/{session_id}/status", response_model=GameResponse)
        async def get_game_status(session_id: str):
            """Get current game status"""
            try:
                session = self.session_manager.get_session(session_id)
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                status = session["orchestrator"].get_game_status()
                
                return GameResponse(
                    success=True,
                    game_state=session["context"].game_state.value,
                    data=status
                )
                
            except Exception as e:
                self.error_handler.handle_error(e, ErrorCategory.SYSTEM_ERROR, ErrorSeverity.LOW)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/api/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            """WebSocket endpoint for real-time communication"""
            connection_id = await self.websocket_manager.connect(websocket, session_id)
            
            try:
                while True:
                    # Wait for messages from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Handle different message types
                    if message.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    elif message.get("type") == "action":
                        # Process action and broadcast result
                        session = self.session_manager.get_session(session_id)
                        if session:
                            response = session["orchestrator"].process_player_action(
                                message.get("action", ""), message.get("action_type", "choice")
                            )
                            await self.websocket_manager.send_to_session(session_id, {
                                "type": "action_result",
                                "data": response
                            })
                    
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(connection_id)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.websocket_manager.disconnect(connection_id)
        
        @self.app.get("/api/admin/stats")
        async def get_statistics():
            """Get system statistics (admin endpoint)"""
            session_stats = self.session_manager.get_session_statistics()
            error_stats = self.error_handler.get_error_statistics()
            performance_stats = self.game_logger.get_performance_stats()
            
            return {
                "sessions": session_stats,
                "errors": error_stats,
                "performance": performance_stats,
                "cache": {
                    "size": len(self.response_cache.cache),
                    "max_size": self.response_cache.max_size
                }
            }
        
        @self.app.get("/")
        async def root():
            """Root endpoint with basic info"""
            return {
                "name": "Magic Adventure Game API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "start_game": "/api/game/start",
                    "process_action": "/api/game/{session_id}/action",
                    "get_status": "/api/game/{session_id}/status",
                    "websocket": "/api/ws/{session_id}",
                    "docs": "/docs"
                }
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the API server"""
        if not self.app:
            raise RuntimeError("FastAPI not available. Please install: pip install fastapi uvicorn")
        
        logger.info(f"🌐 Starting Magic Adventure Game API on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, debug=debug)


class FrontendHelpers:
    """Helper utilities for frontend integration"""
    
    @staticmethod
    def generate_javascript_sdk() -> str:
        """Generate JavaScript SDK for frontend integration"""
        return '''
class MagicAdventureClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.sessionId = null;
        this.websocket = null;
        this.eventHandlers = {};
    }
    
    async startGame(playerName, characterClass = 'Adventurer') {
        const response = await fetch(`${this.baseUrl}/api/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: playerName,
                character_class: characterClass
            })
        });
        
        const data = await response.json();
        if (data.success) {
            this.sessionId = data.data.session_id;
        }
        return data;
    }
    
    async processAction(action, actionType = 'choice') {
        if (!this.sessionId) throw new Error('No active session');
        
        const response = await fetch(`${this.baseUrl}/api/game/${this.sessionId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: action,
                action_type: actionType
            })
        });
        
        return await response.json();
    }
    
    async getGameStatus() {
        if (!this.sessionId) throw new Error('No active session');
        
        const response = await fetch(`${this.baseUrl}/api/game/${this.sessionId}/status`);
        return await response.json();
    }
    
    connectWebSocket() {
        if (!this.sessionId) throw new Error('No active session');
        
        const wsUrl = `ws${this.baseUrl.slice(4)}/api/ws/${this.sessionId}`;
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.eventHandlers[data.type]) {
                this.eventHandlers[data.type](data);
            }
        };
        
        return this.websocket;
    }
    
    on(eventType, handler) {
        this.eventHandlers[eventType] = handler;
    }
}

// Usage example:
// const client = new MagicAdventureClient();
// await client.startGame('Hero Name');
// const response = await client.processAction('explore the forest');
'''
    
    @staticmethod
    def generate_html_demo() -> str:
        """Generate HTML demo page"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Magic Adventure Game</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .game-area { border: 1px solid #ccc; padding: 20px; min-height: 400px; }
        .input-area { margin-top: 20px; }
        input, button { padding: 10px; margin: 5px; }
        .story-text { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .choices { margin: 10px 0; }
        .choice-btn { display: block; margin: 5px 0; padding: 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        .choice-btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🏰 Magic Adventure Game</h1>
    
    <div id="login-screen">
        <h2>Start Your Adventure</h2>
        <input type="text" id="player-name" placeholder="Your name" />
        <select id="character-class">
            <option value="Adventurer">Adventurer</option>
            <option value="Warrior">Warrior</option>
            <option value="Mage">Mage</option>
            <option value="Rogue">Rogue</option>
        </select>
        <button onclick="startGame()">Begin Adventure</button>
    </div>
    
    <div id="game-screen" style="display:none;">
        <div class="game-area">
            <div id="story-content"></div>
            <div id="choices-content"></div>
        </div>
        
        <div class="input-area">
            <input type="text" id="action-input" placeholder="What do you do?" />
            <button onclick="processAction()">Take Action</button>
        </div>
    </div>

    <script src="magic-adventure-client.js"></script>
    <script>
        const client = new MagicAdventureClient();
        
        async function startGame() {
            const name = document.getElementById('player-name').value;
            const characterClass = document.getElementById('character-class').value;
            
            if (!name) {
                alert('Please enter your name');
                return;
            }
            
            try {
                const response = await client.startGame(name, characterClass);
                if (response.success) {
                    document.getElementById('login-screen').style.display = 'none';
                    document.getElementById('game-screen').style.display = 'block';
                    updateGameDisplay(response.data.game_content);
                }
            } catch (error) {
                alert('Failed to start game: ' + error.message);
            }
        }
        
        async function processAction() {
            const action = document.getElementById('action-input').value;
            if (!action) return;
            
            try {
                const response = await client.processAction(action);
                updateGameDisplay(response.data);
                document.getElementById('action-input').value = '';
            } catch (error) {
                alert('Action failed: ' + error.message);
            }
        }
        
        function updateGameDisplay(gameData) {
            const storyContent = document.getElementById('story-content');
            const choicesContent = document.getElementById('choices-content');
            
            if (gameData.story || gameData.story_update) {
                const storyDiv = document.createElement('div');
                storyDiv.className = 'story-text';
                storyDiv.textContent = gameData.story || gameData.story_update;
                storyContent.appendChild(storyDiv);
            }
            
            if (gameData.choices) {
                choicesContent.innerHTML = '<h3>Choose your action:</h3>';
                gameData.choices.forEach((choice, index) => {
                    const btn = document.createElement('button');
                    btn.className = 'choice-btn';
                    btn.textContent = `${index + 1}. ${choice}`;
                    btn.onclick = () => processActionChoice(choice);
                    choicesContent.appendChild(btn);
                });
            }
        }
        
        function processActionChoice(choice) {
            document.getElementById('action-input').value = choice;
            processAction();
        }
    </script>
</body>
</html>
'''


if __name__ == "__main__":
    # Demo the web integration
    print("🌐 Web Integration Demo")
    print("=" * 50)
    
    if not FastAPI:
        print("❌ FastAPI not available - install with: pip install fastapi uvicorn")
        print("📝 Generating helper files...")
        
        # Generate helper files
        helpers = FrontendHelpers()
        
        # Save JavaScript SDK
        sdk_path = Path("magic-adventure-client.js")
        with open(sdk_path, 'w') as f:
            f.write(helpers.generate_javascript_sdk())
        print(f"📄 Generated JavaScript SDK: {sdk_path}")
        
        # Save HTML demo
        demo_path = Path("demo.html")
        with open(demo_path, 'w') as f:
            f.write(helpers.generate_html_demo())
        print(f"📄 Generated HTML demo: {demo_path}")
        
    else:
        print("✅ FastAPI available - creating API instance...")
        
        # Create and configure API
        api = GameAPI()
        
        print("🚀 API configured successfully!")
        print("📡 Available endpoints:")
        print("  POST /api/game/start - Start new game")
        print("  POST /api/game/{session_id}/action - Process player action")
        print("  GET  /api/game/{session_id}/status - Get game status")
        print("  WS   /api/ws/{session_id} - WebSocket connection")
        print("  GET  /api/admin/stats - System statistics")
        
        print("\n🎮 To start the server, run:")
        print("  python web_integration.py --serve")
        print("  or")
        print("  api.run()")
        
        # Check if we should start the server
        if "--serve" in sys.argv:
            try:
                api.run(debug=True)
            except KeyboardInterrupt:
                print("\n👋 Server stopped")
    
    print("✨ Demo completed successfully!")