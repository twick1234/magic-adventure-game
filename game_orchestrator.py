#!/usr/bin/env python3
"""
🎭 Magic Adventure Game Orchestrator

This module implements the main CrewAI orchestrator that coordinates all agents
and manages the game state for the Magic Adventure Game. It handles:

- Agent coordination and task delegation
- Game state management and persistence  
- Context sharing between agents
- Response processing and formatting
- Error handling and fallback systems
- Web frontend integration

The orchestrator ensures all agents work together seamlessly to create
a cohesive, engaging gaming experience.
"""

from crewai import Task, Crew, Process
from crewai_agents import MagicAdventureAgents, AgentSpecializations
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
import time
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameState(Enum):
    """Enumeration of possible game states"""
    INITIALIZING = "initializing"
    BEGINNING = "beginning"
    EXPLORING = "exploring"
    IN_DIALOGUE = "in_dialogue"
    IN_COMBAT = "in_combat"
    PUZZLE_SOLVING = "puzzle_solving"
    STORY_CLIMAX = "story_climax"
    ENDING = "ending"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class GameContext:
    """Comprehensive game context that agents share"""
    player_name: str = "Brave Adventurer"
    player_health: int = 100
    player_mana: int = 50
    player_level: int = 1
    player_class: str = "Adventurer"
    player_items: List[str] = field(default_factory=list)
    player_abilities: List[str] = field(default_factory=list)
    
    current_location: str = "Starting Area"
    previous_locations: List[str] = field(default_factory=list)
    discovered_locations: List[str] = field(default_factory=list)
    
    active_quests: List[Dict[str, Any]] = field(default_factory=list)
    completed_quests: List[Dict[str, Any]] = field(default_factory=list)
    available_npcs: List[Dict[str, Any]] = field(default_factory=list)
    
    story_progress: int = 0
    major_story_beats: List[str] = field(default_factory=list)
    player_choices: List[Dict[str, Any]] = field(default_factory=list)
    
    current_audio: Dict[str, str] = field(default_factory=dict)
    ambient_sounds: List[str] = field(default_factory=list)
    
    game_state: GameState = GameState.INITIALIZING
    session_start_time: datetime = field(default_factory=datetime.now)
    last_action_time: datetime = field(default_factory=datetime.now)
    
    world_knowledge: Dict[str, Any] = field(default_factory=dict)
    character_relationships: Dict[str, Any] = field(default_factory=dict)
    
    def to_context_string(self) -> str:
        """Convert game context to a string for agent consumption"""
        return f"""
GAME CONTEXT:
=============
Player: {self.player_name} (Level {self.player_level} {self.player_class})
Health: {self.player_health}/100 | Mana: {self.player_mana}/100
Location: {self.current_location}
Items: {', '.join(self.player_items) if self.player_items else 'None'}
Abilities: {', '.join(self.player_abilities) if self.player_abilities else 'None'}

STORY PROGRESS: {self.story_progress}%
Active Quests: {len(self.active_quests)}
Game State: {self.game_state.value}
Previous Choices: {len(self.player_choices)}

WORLD KNOWLEDGE:
{json.dumps(self.world_knowledge, indent=2) if self.world_knowledge else 'Building...'}

RELATIONSHIPS:
{json.dumps(self.character_relationships, indent=2) if self.character_relationships else 'Developing...'}
"""


@dataclass 
class AgentResponse:
    """Structured response from an agent"""
    agent_name: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class MagicAdventureOrchestrator:
    """
    Main orchestrator for the Magic Adventure Game CrewAI system
    """
    
    def __init__(self, context: Optional[GameContext] = None):
        """
        Initialize the game orchestrator
        
        Args:
            context: Initial game context, creates default if not provided
        """
        self.context = context or GameContext()
        self.agents = {}
        self.agent_factory = MagicAdventureAgents(self.context.to_dict())
        self.response_cache = {}
        self.fallback_enabled = True
        self.max_retries = 3
        
        logger.info("🎭 Initializing Magic Adventure Orchestrator")
        self._initialize_agents()
        self._initialize_world_knowledge()
    
    def _initialize_agents(self):
        """Create and initialize all specialized agents"""
        try:
            self.agents = self.agent_factory.create_all_agents()
            logger.info(f"✨ Successfully initialized {len(self.agents)} agents")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise
    
    def _initialize_world_knowledge(self):
        """Initialize base world knowledge and character relationships"""
        self.context.world_knowledge = {
            "magical_elements": ["crystals", "ancient_runes", "enchanted_items"],
            "creature_types": ["dragons", "fairies", "unicorns", "phoenixes"],
            "location_features": ["mystical_forests", "crystal_caves", "floating_islands"],
            "magic_schools": ["elemental", "healing", "illusion", "divination"]
        }
        
        self.context.character_relationships = {
            "trust_levels": {},
            "friendship_bonds": {},
            "rivalry_tensions": {},
            "mentor_connections": {}
        }
    
    def start_new_game(self, player_name: str, player_class: str = "Adventurer") -> Dict[str, Any]:
        """
        Start a new game session
        
        Args:
            player_name: Name of the player character
            player_class: Character class (Warrior, Mage, Rogue, etc.)
            
        Returns:
            Dictionary containing the initial game setup response
        """
        logger.info(f"🎮 Starting new game for {player_name} ({player_class})")
        
        # Update context
        self.context.player_name = player_name
        self.context.player_class = player_class
        self.context.game_state = GameState.BEGINNING
        self.context.session_start_time = datetime.now()
        
        # Create initialization tasks
        tasks = self._create_game_start_tasks()
        
        # Execute the crew
        try:
            results = self._execute_crew(tasks, "game_initialization")
            return self._format_game_start_response(results)
        except Exception as e:
            logger.error(f"❌ Failed to start new game: {e}")
            return self._generate_fallback_start()
    
    def process_player_action(self, action: str, action_type: str = "choice") -> Dict[str, Any]:
        """
        Process a player action and generate appropriate responses
        
        Args:
            action: The player's action/choice
            action_type: Type of action (choice, movement, dialogue, etc.)
            
        Returns:
            Dictionary containing all agent responses and game state updates
        """
        logger.info(f"🎯 Processing player action: {action} (type: {action_type})")
        
        # Update context with player action
        self.context.last_action_time = datetime.now()
        self.context.player_choices.append({
            "action": action,
            "type": action_type,
            "timestamp": datetime.now().isoformat(),
            "location": self.context.current_location
        })
        
        # Create tasks based on action type
        tasks = self._create_action_response_tasks(action, action_type)
        
        # Execute the crew
        try:
            results = self._execute_crew(tasks, f"action_{action_type}")
            response = self._format_action_response(results, action)
            
            # Update game state based on responses
            self._update_game_state_from_responses(results)
            
            return response
        except Exception as e:
            logger.error(f"❌ Failed to process player action: {e}")
            return self._generate_fallback_response(action, action_type)
    
    def get_game_status(self) -> Dict[str, Any]:
        """Get current game status and statistics"""
        session_duration = (datetime.now() - self.context.session_start_time).total_seconds()
        
        return {
            "game_state": self.context.game_state.value,
            "player_info": {
                "name": self.context.player_name,
                "class": self.context.player_class,
                "level": self.context.player_level,
                "health": self.context.player_health,
                "mana": self.context.player_mana
            },
            "location": self.context.current_location,
            "story_progress": self.context.story_progress,
            "session_duration": session_duration,
            "choices_made": len(self.context.player_choices),
            "quests_completed": len(self.context.completed_quests),
            "locations_discovered": len(self.context.discovered_locations)
        }
    
    def save_game_state(self) -> Dict[str, Any]:
        """Save the current game state to a serializable format"""
        return {
            "context": self.context.__dict__,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def load_game_state(self, saved_state: Dict[str, Any]) -> bool:
        """
        Load a previously saved game state
        
        Args:
            saved_state: Dictionary containing saved game state
            
        Returns:
            Boolean indicating success
        """
        try:
            context_data = saved_state["context"]
            self.context = GameContext(**context_data)
            logger.info("💾 Game state loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load game state: {e}")
            return False
    
    def _create_game_start_tasks(self) -> List[Task]:
        """Create tasks for game initialization"""
        tasks = []
        
        # Story Generator: Create opening narrative
        story_task = Task(
            description=f"""Create an engaging opening narrative for {self.context.player_name}, 
            a {self.context.player_class}, beginning their magical adventure. The opening should:
            - Set an enchanting, welcoming tone
            - Introduce the magical world and its possibilities
            - Present an initial hook or mystery to drive the story forward
            - Be 3-4 sentences that capture imagination
            - Include sensory details that make the world feel alive
            
            Context: {self.context.to_context_string()}""",
            expected_output="An immersive opening narrative that sets the stage for adventure",
            agent=self.agents["story_generator"]
        )
        
        # World Builder: Establish starting location
        world_task = Task(
            description=f"""Describe the starting location where {self.context.player_name} 
            begins their adventure. Create a vivid, detailed description that includes:
            - Rich sensory details (sights, sounds, smells, atmosphere)
            - Interesting environmental features that suggest adventure
            - Hints at the magical nature of the world
            - Elements that invite exploration
            - Safe but intriguing aspects appropriate for a starting area
            
            Context: {self.context.to_context_string()}""",
            expected_output="A detailed description of the starting location",
            agent=self.agents["world_builder"]
        )
        
        # Character Behavior: Introduce key NPCs
        character_task = Task(
            description=f"""Introduce 1-2 initial characters that {self.context.player_name} 
            might encounter at the start of their adventure. For each character, provide:
            - Name, appearance, and personality traits
            - Their role in the world and potential relationship to the player
            - Distinctive dialogue or mannerisms
            - How they might guide or assist the new adventurer
            - Make them memorable and engaging
            
            Context: {self.context.to_context_string()}""",
            expected_output="Descriptions of initial NPCs the player will encounter",
            agent=self.agents["character_behavior"]
        )
        
        # Quest Master: Provide initial objectives
        quest_task = Task(
            description=f"""Design the initial objectives and potential paths for 
            {self.context.player_name}'s adventure. Include:
            - A clear but flexible main objective
            - 2-3 different approaches the player could take
            - Hints at broader adventures to come
            - Appropriate difficulty for a beginning adventurer
            - Elements that encourage exploration and choice
            
            Context: {self.context.to_context_string()}""",
            expected_output="Initial quest objectives and player options",
            agent=self.agents["quest_master"]
        )
        
        # Audio Coordinator: Set the audio scene
        audio_task = Task(
            description=f"""Recommend audio elements to enhance {self.context.player_name}'s 
            starting experience. Include:
            - Appropriate ambient sounds for the starting location
            - Background music style that fits the opening mood
            - Audio cues that could accompany key story moments
            - Sound effects that would enhance immersion
            
            Context: {self.context.to_context_string()}""",
            expected_output="Audio recommendations for the game opening",
            agent=self.agents["audio_coordinator"]
        )
        
        tasks.extend([story_task, world_task, character_task, quest_task, audio_task])
        return tasks
    
    def _create_action_response_tasks(self, action: str, action_type: str) -> List[Task]:
        """Create tasks to respond to player actions"""
        tasks = []
        context_str = self.context.to_context_string()
        
        # Story Generator: Advance the narrative
        story_task = Task(
            description=f"""Based on {self.context.player_name}'s action "{action}", 
            continue the adventure narrative. The response should:
            - Logically follow from the player's choice
            - Advance the story in an engaging way
            - Maintain consistency with previous events
            - Create new opportunities for interaction
            - Be 2-3 sentences describing what happens next
            
            Action Type: {action_type}
            Player Action: {action}
            Context: {context_str}""",
            expected_output="Story continuation based on player action",
            agent=self.agents["story_generator"]
        )
        
        # Character Behavior: Character reactions
        if self.context.available_npcs or "talk" in action.lower() or "dialogue" in action_type:
            character_task = Task(
                description=f"""Generate character reactions to {self.context.player_name}'s 
                action "{action}". Consider:
                - How existing characters would respond
                - Whether new characters might appear
                - Character emotional states and motivations
                - Relationship changes based on the action
                - Authentic dialogue that fits each character
                
                Action Type: {action_type}
                Context: {context_str}""",
                expected_output="Character responses and reactions to the player's action",
                agent=self.agents["character_behavior"]
            )
            tasks.append(character_task)
        
        # World Builder: Environmental changes
        if "move" in action.lower() or "explore" in action.lower() or action_type in ["movement", "exploration"]:
            world_task = Task(
                description=f"""Describe environmental changes or new locations revealed 
                by {self.context.player_name}'s action "{action}". Include:
                - New or changed environmental details
                - Location transitions if movement occurred
                - Interactive elements the player might notice
                - Atmospheric changes that enhance immersion
                
                Action Type: {action_type}
                Context: {context_str}""",
                expected_output="Environmental descriptions and changes",
                agent=self.agents["world_builder"]
            )
            tasks.append(world_task)
        
        # Quest Master: Update objectives and provide choices
        quest_task = Task(
            description=f"""Based on {self.context.player_name}'s action "{action}", 
            provide updated quest status and new player options. Include:
            - Progress on current objectives
            - New opportunities or challenges that arise
            - 3 clear choices for what the player can do next
            - Each choice should lead to different types of experiences
            - Maintain appropriate challenge progression
            
            Action Type: {action_type}
            Context: {context_str}""",
            expected_output="Quest updates and player choice options",
            agent=self.agents["quest_master"]
        )
        
        # Dialogue Creator: Generate conversation options
        dialogue_task = Task(
            description=f"""Create contextual dialogue options and responses related to 
            {self.context.player_name}'s action "{action}". Include:
            - Natural conversation flows with any NPCs present
            - Player dialogue options if interaction is possible
            - Character-specific speech patterns and personalities
            - Dialogue that serves story and character development
            
            Action Type: {action_type}
            Context: {context_str}""",
            expected_output="Dialogue options and character speech",
            agent=self.agents["dialogue_creator"]
        )
        
        # Audio Coordinator: Update audio landscape
        audio_task = Task(
            description=f"""Recommend audio changes based on {self.context.player_name}'s 
            action "{action}". Consider:
            - New ambient sounds for changed situations
            - Music transitions that reflect story development
            - Sound effects that accompany the action
            - Audio cues that enhance the emotional impact
            
            Action Type: {action_type}
            Context: {context_str}""",
            expected_output="Audio updates and recommendations",
            agent=self.agents["audio_coordinator"]
        )
        
        tasks.extend([story_task, quest_task, dialogue_task, audio_task])
        return tasks
    
    def _execute_crew(self, tasks: List[Task], task_group: str) -> Dict[str, Any]:
        """Execute a crew with the given tasks"""
        start_time = time.time()
        
        try:
            # Create crew with all relevant agents
            crew_agents = [task.agent for task in tasks]
            crew = Crew(
                agents=crew_agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                memory=True,
                max_rpm=10  # Rate limiting
            )
            
            # Execute crew
            logger.info(f"🚀 Executing crew for {task_group}")
            result = crew.kickoff()
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Crew execution completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "processing_time": processing_time,
                "task_group": task_group
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Crew execution failed after {processing_time:.2f}s: {e}")
            
            if self.fallback_enabled:
                return self._generate_fallback_crew_result(task_group, str(e))
            else:
                raise
    
    def _format_game_start_response(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format the game start response for the frontend"""
        return {
            "type": "game_start",
            "success": results.get("success", False),
            "story": results.get("story", ""),
            "location": results.get("location", ""),
            "characters": results.get("characters", []),
            "objectives": results.get("objectives", []),
            "audio": results.get("audio", {}),
            "game_state": self.context.game_state.value,
            "processing_time": results.get("processing_time", 0.0)
        }
    
    def _format_action_response(self, results: Dict[str, Any], action: str) -> Dict[str, Any]:
        """Format action response for the frontend"""
        return {
            "type": "action_response",
            "success": results.get("success", False),
            "player_action": action,
            "story_update": results.get("story", ""),
            "character_reactions": results.get("characters", []),
            "location_update": results.get("location", ""),
            "quest_update": results.get("quests", {}),
            "dialogue_options": results.get("dialogue", []),
            "audio_update": results.get("audio", {}),
            "choices": results.get("choices", []),
            "game_state": self.context.game_state.value,
            "processing_time": results.get("processing_time", 0.0)
        }
    
    def _update_game_state_from_responses(self, results: Dict[str, Any]):
        """Update internal game state based on agent responses"""
        # This would contain logic to parse agent responses and update
        # the game context accordingly
        self.context.story_progress += 5  # Example increment
        
        # Update other context elements based on agent responses
        if "location_change" in results:
            new_location = results["location_change"]
            if new_location != self.context.current_location:
                self.context.previous_locations.append(self.context.current_location)
                self.context.current_location = new_location
                if new_location not in self.context.discovered_locations:
                    self.context.discovered_locations.append(new_location)
    
    def _generate_fallback_start(self) -> Dict[str, Any]:
        """Generate fallback response for game start if AI fails"""
        logger.info("🔄 Generating fallback game start response")
        
        return {
            "type": "game_start",
            "success": True,
            "story": f"Welcome, {self.context.player_name}! You find yourself at the edge of an enchanted forest, where ancient magic still flows through the trees and mysterious paths wind into the unknown.",
            "location": "Edge of the Enchanted Forest",
            "characters": [{"name": "Wise Owl", "description": "A friendly owl perched nearby, watching you with knowing eyes"}],
            "objectives": ["Explore the forest paths", "Meet the local forest inhabitants", "Discover your first magical item"],
            "audio": {"music": "mystical_forest_ambience", "sounds": ["rustling_leaves", "distant_bird_calls"]},
            "game_state": self.context.game_state.value,
            "processing_time": 0.1,
            "fallback_used": True
        }
    
    def _generate_fallback_response(self, action: str, action_type: str) -> Dict[str, Any]:
        """Generate fallback response if AI processing fails"""
        logger.info(f"🔄 Generating fallback response for action: {action}")
        
        return {
            "type": "action_response",
            "success": True,
            "player_action": action,
            "story_update": f"Your action leads you deeper into the adventure, {self.context.player_name}. The path ahead remains full of possibilities.",
            "choices": [
                "Continue exploring the area",
                "Look for other adventurers to meet",
                "Search for helpful items or clues"
            ],
            "game_state": self.context.game_state.value,
            "processing_time": 0.1,
            "fallback_used": True
        }
    
    def _generate_fallback_crew_result(self, task_group: str, error_msg: str) -> Dict[str, Any]:
        """Generate fallback crew result"""
        return {
            "success": True,
            "result": f"Fallback response for {task_group}",
            "processing_time": 0.1,
            "task_group": task_group,
            "fallback_used": True,
            "original_error": error_msg
        }


if __name__ == "__main__":
    # Demo the orchestrator
    print("🎭 Magic Adventure Orchestrator Demo")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = MagicAdventureOrchestrator()
    
    # Start a new game
    print("\n🎮 Starting new game...")
    start_response = orchestrator.start_new_game("Demo Hero", "Mage")
    print(f"Game started: {start_response.get('success', False)}")
    
    # Process a player action
    print("\n🎯 Processing player action...")
    action_response = orchestrator.process_player_action("explore the forest", "exploration")
    print(f"Action processed: {action_response.get('success', False)}")
    
    # Get game status
    print("\n📊 Game Status:")
    status = orchestrator.get_game_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✨ Demo completed successfully!")