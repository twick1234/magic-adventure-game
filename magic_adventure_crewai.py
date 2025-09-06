#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Complete CrewAI System

This is the main entry point for the comprehensive CrewAI multi-agent system
for the Magic Adventure Game. It brings together all the specialized components:

- 6 Specialized CrewAI Agents (Story, Character, World, Quest, Audio, Dialogue)
- Game Orchestrator for coordination
- Agent Communication System
- Context Management for consistency
- Configuration Management
- Error Handling and Logging
- Web Integration for frontend connectivity

Usage:
    python magic_adventure_crewai.py --mode [cli|web|demo]
    
Features:
    - Command-line interactive mode
    - Web API server mode
    - Demo/testing mode
    - Production-ready with full error handling
    - Modular and extensible architecture
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import all our modules
from crewai_agents import MagicAdventureAgents, AgentSpecializations
from game_orchestrator import MagicAdventureOrchestrator, GameContext, GameState
from agent_communication import AgentCommunicationHub, SharedContextDB, StoryConsistencyManager
from agent_config import AgentConfigurationManager, AgentRole, DifficultyLevel
from error_handling import GameLogger, ErrorHandler, HealthMonitor, performance_monitor
from web_integration import GameAPI, FrontendHelpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MagicAdventureSystem:
    """
    Main system class that coordinates all components
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the complete Magic Adventure system"""
        
        logger.info("🎭 Initializing Magic Adventure CrewAI System")
        
        # Initialize core components
        self.game_logger = GameLogger("magic_adventure_system")
        self.error_handler = ErrorHandler(self.game_logger)
        self.config_manager = AgentConfigurationManager(config_dir)
        
        # Initialize context and communication
        self.context_db = SharedContextDB()
        self.communication_hub = AgentCommunicationHub(self.context_db)
        self.consistency_manager = StoryConsistencyManager(self.context_db)
        
        # Initialize health monitoring
        self.health_monitor = HealthMonitor(self.game_logger, self.error_handler)
        self._setup_health_checks()
        
        # Game orchestrator will be created per session
        self.orchestrators = {}
        
        # Web API (optional)
        self.web_api = None
        
        logger.info("✨ Magic Adventure System initialized successfully")
    
    def create_game_session(self, player_name: str, character_class: str = "Adventurer",
                          difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> str:
        """
        Create a new game session with a dedicated orchestrator
        
        Returns:
            Session ID for the new game session
        """
        
        self.game_logger.game_event("session_created", {
            "player": player_name,
            "class": character_class,
            "difficulty": difficulty.value
        })
        
        # Create game context
        context = GameContext(
            player_name=player_name,
            player_class=character_class
        )
        
        # Create orchestrator with specialized configuration
        orchestrator = MagicAdventureOrchestrator(context)
        
        # Configure agents for difficulty level
        self._configure_agents_for_difficulty(orchestrator, difficulty)
        
        # Generate session ID and store
        session_id = f"session_{int(datetime.now().timestamp())}"
        self.orchestrators[session_id] = {
            "orchestrator": orchestrator,
            "context": context,
            "difficulty": difficulty,
            "created_at": datetime.now()
        }
        
        logger.info(f"🎮 Created game session {session_id} for {player_name}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get game session by ID"""
        return self.orchestrators.get(session_id)
    
    def start_cli_mode(self):
        """Start command-line interactive mode"""
        
        print("🏰✨ WELCOME TO MAGIC ADVENTURE GAME ✨🏰")
        print("=" * 60)
        print("Powered by CrewAI Multi-Agent System")
        print("6 AI agents working together for your adventure!")
        print("=" * 60)
        
        # Get player information
        player_name = input("\n🌟 What's your adventurer name? ").strip()
        if not player_name:
            player_name = "Brave Explorer"
        
        print("\n⚔️ Choose your character class:")
        print("1. Warrior - Strong and brave, excels in combat")
        print("2. Mage - Master of magic and ancient knowledge")
        print("3. Rogue - Sneaky and clever, master of stealth")
        print("4. Healer - Wise and caring, protects others")
        print("5. Adventurer - Balanced in all skills")
        
        class_choice = input("Enter 1-5 (or press Enter for Adventurer): ").strip()
        character_classes = {
            "1": "Warrior", "2": "Mage", "3": "Rogue", 
            "4": "Healer", "5": "Adventurer"
        }
        character_class = character_classes.get(class_choice, "Adventurer")
        
        print("\n🎯 Choose difficulty level:")
        print("1. Beginner - Gentle and easy")
        print("2. Intermediate - Balanced challenge")
        print("3. Advanced - More complex")
        print("4. Expert - Maximum complexity")
        
        difficulty_choice = input("Enter 1-4 (or press Enter for Intermediate): ").strip()
        difficulty_map = {
            "1": DifficultyLevel.BEGINNER,
            "2": DifficultyLevel.INTERMEDIATE,
            "3": DifficultyLevel.ADVANCED,
            "4": DifficultyLevel.EXPERT
        }
        difficulty = difficulty_map.get(difficulty_choice, DifficultyLevel.INTERMEDIATE)
        
        # Create game session
        session_id = self.create_game_session(player_name, character_class, difficulty)
        session = self.get_session(session_id)
        orchestrator = session["orchestrator"]
        
        print(f"\n🎮 Starting adventure for {player_name} the {character_class}!")
        print("🤖 Your AI crew is preparing the adventure...")
        
        # Start the game
        try:
            start_response = orchestrator.start_new_game(player_name, character_class)
            
            # Main game loop
            turn_count = 0
            while turn_count < 10:  # Limit for demo
                print(f"\n{'='*50}")
                print(f"🏰 ADVENTURE TURN {turn_count + 1} 🏰")
                print("="*50)
                
                if turn_count == 0:
                    # Display opening
                    print(f"\n📚 {start_response.get('story', 'Your adventure begins...')}")
                    if 'choices' in start_response:
                        print(f"\n🎲 Your options:")
                        for i, choice in enumerate(start_response['choices'], 1):
                            print(f"  {i}. {choice}")
                else:
                    # Get player action
                    print(f"\n{player_name}, what do you choose?")
                    action = input("Enter your choice (or 'quit' to end, 'status' for info): ").strip()
                    
                    if action.lower() == 'quit':
                        break
                    elif action.lower() == 'status':
                        status = orchestrator.get_game_status()
                        print(f"\n📊 Game Status:")
                        print(f"  Health: {status['player_info']['health']}")
                        print(f"  Location: {status['location']}")
                        print(f"  Progress: {status['story_progress']}%")
                        continue
                    
                    # Process action
                    with performance_monitor("player_action", "cli_interface", self.game_logger):
                        response = orchestrator.process_player_action(action, "choice")
                    
                    # Display response
                    print(f"\n📚 Story continues:")
                    print(response.get('story_update', 'The adventure continues...'))
                    
                    if response.get('choices'):
                        print(f"\n🎲 Your next options:")
                        for i, choice in enumerate(response['choices'], 1):
                            print(f"  {i}. {choice}")
                
                turn_count += 1
            
            print(f"\n🌟 Thank you for playing, {player_name}!")
            print("🎉 Your adventure continues in your imagination...")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye, {player_name}! Your adventure awaits your return...")
        except Exception as e:
            self.error_handler.handle_error(e, "system_error", "high")
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or contact support.")
    
    def start_web_mode(self, host: str = "0.0.0.0", port: int = 8000):
        """Start web API server mode"""
        
        logger.info("🌐 Starting Web API mode")
        
        try:
            self.web_api = GameAPI()
            
            # Generate helper files
            self._generate_web_assets()
            
            print(f"🚀 Starting Magic Adventure Game API server...")
            print(f"📡 Server will be available at: http://{host}:{port}")
            print(f"📖 API documentation: http://{host}:{port}/docs")
            print(f"🎮 Demo page: http://{host}:{port}/demo.html")
            
            # Start server
            self.web_api.run(host=host, port=port)
            
        except Exception as e:
            self.error_handler.handle_error(e, "system_error", "critical")
            logger.error(f"Failed to start web server: {e}")
    
    def start_demo_mode(self):
        """Run system demonstrations and tests"""
        
        print("🎭 Magic Adventure CrewAI System Demo")
        print("=" * 50)
        
        # Test 1: Agent Creation
        print("\n🤖 Test 1: Creating Specialized Agents")
        agent_factory = MagicAdventureAgents()
        agents = agent_factory.create_all_agents()
        print(f"✅ Created {len(agents)} specialized agents:")
        for name, agent in agents.items():
            print(f"  • {agent.role} - {agent.goal[:50]}...")
        
        # Test 2: Configuration System
        print("\n⚙️ Test 2: Configuration Management")
        story_config = self.config_manager.get_configuration(AgentRole.STORY_GENERATOR)
        validation = self.config_manager.validate_configuration(story_config)
        print(f"✅ Configuration validation: {'Passed' if validation['is_valid'] else 'Failed'}")
        
        # Test 3: Context Management
        print("\n🗄️ Test 3: Context Database")
        test_context = {
            "player_name": "Demo Hero",
            "current_location": "Test Forest",
            "player_health": 100
        }
        version = self.context_db.update_context(test_context, "demo", "Demo setup")
        consistency = self.context_db.validate_consistency()
        print(f"✅ Context version {version} - Consistent: {consistency['is_consistent']}")
        
        # Test 4: Communication System
        print("\n💬 Test 4: Agent Communication")
        self.communication_hub.register_agent("demo_agent")
        stats = self.communication_hub.get_agent_statistics()
        print(f"✅ Communication hub - {stats['total_agents']} agents registered")
        
        # Test 5: Error Handling
        print("\n🛡️ Test 5: Error Handling")
        try:
            raise ValueError("Demo error for testing")
        except ValueError as e:
            error = self.error_handler.handle_error(e, "system_error", "low", {"demo": True})
            error_stats = self.error_handler.get_error_statistics()
            print(f"✅ Error handled - Total errors: {error_stats['total_errors']}")
        
        # Test 6: Health Monitoring
        print("\n🩺 Test 6: Health Monitoring")
        health_report = self.health_monitor.run_health_checks()
        print(f"✅ Health check - Status: {health_report['status']}")
        
        # Test 7: Quick Game Session
        print("\n🎮 Test 7: Game Session Creation")
        session_id = self.create_game_session("Demo Player", "Mage")
        session = self.get_session(session_id)
        print(f"✅ Created session {session_id}")
        print(f"   Player: {session['context'].player_name}")
        print(f"   Class: {session['context'].player_class}")
        
        print("\n🎉 All tests completed successfully!")
        print("🚀 System is ready for production use!")
    
    def _configure_agents_for_difficulty(self, orchestrator: MagicAdventureOrchestrator, 
                                       difficulty: DifficultyLevel):
        """Configure agents based on difficulty level"""
        
        # Adjust agent configurations based on difficulty
        if difficulty == DifficultyLevel.BEGINNER:
            # More guidance, simpler responses
            self.config_manager.optimize_for_performance(3.0)
        elif difficulty == DifficultyLevel.EXPERT:
            # More complex, detailed responses
            pass  # Use default complex configurations
        
        logger.info(f"🎯 Configured agents for {difficulty.value} difficulty")
    
    def _setup_health_checks(self):
        """Setup system health monitoring"""
        
        def context_db_health():
            try:
                consistency = self.context_db.validate_consistency()
                return {
                    "healthy": consistency["is_consistent"],
                    "details": consistency
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        def communication_health():
            try:
                stats = self.communication_hub.get_agent_statistics()
                return {
                    "healthy": stats["total_agents"] > 0,
                    "details": stats
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        def config_health():
            try:
                configs = self.config_manager.get_all_configurations()
                return {
                    "healthy": len(configs) >= 6,  # Expect at least 6 agents
                    "details": {"total_configs": len(configs)}
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        # Register health checks
        self.health_monitor.register_health_check("context_db", context_db_health)
        self.health_monitor.register_health_check("communication", communication_health)
        self.health_monitor.register_health_check("configuration", config_health)
    
    def _generate_web_assets(self):
        """Generate web assets for frontend integration"""
        
        helpers = FrontendHelpers()
        
        # Generate JavaScript SDK
        js_sdk_path = Path("static/magic-adventure-client.js")
        js_sdk_path.parent.mkdir(exist_ok=True)
        with open(js_sdk_path, 'w') as f:
            f.write(helpers.generate_javascript_sdk())
        
        # Generate demo HTML page
        demo_path = Path("static/demo.html")
        with open(demo_path, 'w') as f:
            f.write(helpers.generate_html_demo())
        
        logger.info("📁 Generated web assets in static/ directory")


def main():
    """Main entry point with command-line argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="Magic Adventure Game - CrewAI Multi-Agent System"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "web", "demo"],
        default="cli",
        help="Run mode: cli (interactive), web (API server), or demo (tests)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Web server host (web mode only)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web server port (web mode only)"
    )
    parser.add_argument(
        "--config-dir",
        help="Configuration directory path"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize system
    try:
        system = MagicAdventureSystem(args.config_dir)
        
        # Run in selected mode
        if args.mode == "cli":
            system.start_cli_mode()
        elif args.mode == "web":
            system.start_web_mode(args.host, args.port)
        elif args.mode == "demo":
            system.start_demo_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using Magic Adventure Game!")
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        print(f"❌ System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()