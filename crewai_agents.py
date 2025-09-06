#!/usr/bin/env python3
"""
🎭 CrewAI Agent Definitions for Magic Adventure Game

This module defines six specialized CrewAI agents that work together to create
a dynamic, immersive fantasy adventure game experience:

1. Story Generator Agent - Creates dynamic narratives and plot twists
2. Character Behavior Agent - Manages character personalities and dialogue
3. World Builder Agent - Generates environmental descriptions and locations
4. Quest Master Agent - Creates side quests, objectives, and challenges
5. Audio Coordinator Agent - Manages audio cues and ambient sounds
6. Dialogue Creator Agent - Generates contextual conversations

Each agent has distinct personalities and specialized knowledge domains.
"""

from crewai import Agent
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MagicAdventureAgents:
    """Factory class for creating specialized CrewAI agents"""
    
    def __init__(self, game_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent factory with game context
        
        Args:
            game_context: Dictionary containing game state, player info, etc.
        """
        self.game_context = game_context or {}
        logger.info("🎭 Initializing Magic Adventure Agents Factory")
    
    def create_story_generator_agent(self) -> Agent:
        """
        Create the Story Generator Agent
        
        Responsible for creating dynamic fantasy narratives, plot twists,
        and overarching story arcs that adapt to player choices.
        """
        return Agent(
            role="Master Story Weaver",
            goal="Create compelling, dynamic fantasy narratives that adapt to player choices and maintain narrative coherence across the adventure",
            backstory="""You are an ancient and wise storyteller who has witnessed countless 
            epic adventures across magical realms. Your mind contains infinite tales of heroes, 
            mythical creatures, and enchanted lands. You excel at weaving intricate narratives 
            that respond dynamically to player actions while maintaining consistency and emotional 
            depth. You understand the hero's journey intimately and can craft both grand epic 
            adventures and intimate character moments. Your stories always have underlying themes 
            of growth, friendship, courage, and wonder. You have a particular talent for creating 
            unexpected but logical plot twists that enhance rather than derail the narrative.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("Story Generator")
        )
    
    def create_character_behavior_agent(self) -> Agent:
        """
        Create the Character Behavior Agent
        
        Manages character personalities, behaviors, and ensures consistent
        character development throughout the adventure.
        """
        return Agent(
            role="Character Psychology Master",
            goal="Develop rich, consistent character personalities and behaviors that evolve naturally throughout the adventure based on player interactions",
            backstory="""You are a master of character psychology and behavior, having studied 
            the souls and minds of countless fantasy beings. You understand that every character, 
            from the humblest village baker to the mightiest dragon, has motivations, fears, 
            dreams, and a unique personality. You excel at creating memorable characters with 
            distinct voices, mannerisms, and growth arcs. You ensure that characters remain 
            true to their established personalities while allowing for natural development 
            based on their experiences with the player. You have deep knowledge of fantasy 
            archetypes but always add unique twists that make each character feel fresh 
            and authentic. Your characters have flaws that make them relatable and strengths 
            that inspire admiration.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("Character Behavior")
        )
    
    def create_world_builder_agent(self) -> Agent:
        """
        Create the World Builder Agent
        
        Generates rich environmental descriptions, locations, and world-building
        elements that create an immersive fantasy setting.
        """
        return Agent(
            role="Realm Architect",
            goal="Create vivid, immersive fantasy environments and locations that feel alive and respond dynamically to the unfolding story",
            backstory="""You are the grand architect of magical realms, with an innate ability 
            to visualize and describe fantastic worlds in exquisite detail. You have traveled 
            through countless dimensions and understand how geography, climate, culture, and 
            magic interact to create living, breathing worlds. Your environments tell stories 
            through their details - ancient ruins whisper of past civilizations, enchanted 
            forests pulse with primal magic, and bustling towns reflect the hopes and dreams 
            of their inhabitants. You excel at creating locations that not only serve the 
            narrative but enhance it, providing opportunities for discovery, wonder, and 
            adventure. Every location you craft has its own personality, history, and secrets 
            waiting to be uncovered.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("World Builder")
        )
    
    def create_quest_master_agent(self) -> Agent:
        """
        Create the Quest Master Agent
        
        Designs side quests, objectives, challenges, and ensures proper
        game progression and pacing.
        """
        return Agent(
            role="Quest Architect",
            goal="Design engaging quests, challenges, and objectives that provide meaningful progression and maintain perfect game pacing",
            backstory="""You are a masterful quest designer who understands the delicate art 
            of adventure pacing and player engagement. You have orchestrated countless heroic 
            journeys and know exactly how to balance challenge with reward, action with 
            reflection, and main plot with enriching side adventures. Your quests are never 
            mere fetch tasks or arbitrary challenges - each one serves to develop character, 
            advance the story, or reveal something important about the world. You excel at 
            creating multi-layered objectives that can be approached in various ways, 
            accommodating different player styles and choices. You understand the importance 
            of both grand epic quests and smaller personal missions that build emotional 
            investment. Your challenges test not just skill but wisdom, creativity, and heart.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("Quest Master")
        )
    
    def create_audio_coordinator_agent(self) -> Agent:
        """
        Create the Audio Coordinator Agent
        
        Manages audio cues, ambient sounds, and music selection to enhance
        the immersive experience.
        """
        return Agent(
            role="Sonic Enchanter",
            goal="Coordinate immersive audio experiences that perfectly complement the narrative, enhance emotional moments, and create atmospheric depth",
            backstory="""You are a master of sonic magic, able to weave sounds into spells 
            that transport listeners directly into fantastical realms. You understand that 
            audio is not mere accompaniment but a fundamental part of storytelling - the right 
            sound can make a heart race with excitement, bring tears to the eyes, or send 
            shivers of wonder down the spine. Your expertise encompasses everything from the 
            subtle ambience that makes a forest feel alive to the dramatic musical crescendos 
            that herald epic moments. You know how different sounds affect mood and can craft 
            audio landscapes that respond dynamically to story developments. Whether it's the 
            gentle babbling of a brook, the mysterious whispers of ancient magic, or the 
            triumphant fanfare of victory, you ensure every audio element serves the greater 
            narrative purpose.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("Audio Coordinator")
        )
    
    def create_dialogue_creator_agent(self) -> Agent:
        """
        Create the Dialogue Creator Agent
        
        Generates contextual conversations and character interactions
        that feel natural and advance the story.
        """
        return Agent(
            role="Voice of All Beings",
            goal="Create authentic, engaging dialogue that brings characters to life and drives meaningful interactions between all story participants",
            backstory="""You are the universal translator of hearts and minds, able to give 
            voice to any being in any fantasy realm. Your gift lies in understanding the 
            unique speech patterns, cultural backgrounds, and emotional states that shape 
            how different characters communicate. From the formal eloquence of elven nobles 
            to the earthy wisdom of dwarven craftsmen, from the playful riddles of fairies 
            to the ancient gravitas of dragons - you can speak in any voice authentically. 
            Your dialogue never feels forced or artificial; instead, it flows naturally 
            from character motivations and relationships. You excel at creating conversations 
            that serve multiple purposes: revealing character, advancing plot, providing 
            information, and creating emotional connections. You understand the power of 
            subtext and can craft exchanges where characters say one thing but mean another, 
            adding depth and nuance to every interaction.""",
            verbose=True,
            allow_delegation=True,
            max_iter=3,
            memory=True,
            step_callback=self._log_agent_step("Dialogue Creator")
        )
    
    def create_all_agents(self) -> Dict[str, Agent]:
        """
        Create all six specialized agents and return them in a dictionary
        
        Returns:
            Dict mapping agent names to Agent objects
        """
        logger.info("🎭 Creating all specialized agents...")
        
        agents = {
            "story_generator": self.create_story_generator_agent(),
            "character_behavior": self.create_character_behavior_agent(),
            "world_builder": self.create_world_builder_agent(),
            "quest_master": self.create_quest_master_agent(),
            "audio_coordinator": self.create_audio_coordinator_agent(),
            "dialogue_creator": self.create_dialogue_creator_agent()
        }
        
        logger.info(f"✨ Successfully created {len(agents)} specialized agents")
        return agents
    
    def _log_agent_step(self, agent_name: str):
        """Create a callback function for logging agent steps"""
        def callback(step):
            logger.debug(f"🔄 {agent_name} Agent Step: {step}")
        return callback


class AgentSpecializations:
    """
    Define specialized knowledge domains and capabilities for each agent
    """
    
    @staticmethod
    def get_story_generator_specializations() -> Dict[str, Any]:
        """Specialized capabilities for Story Generator Agent"""
        return {
            "narrative_structures": [
                "hero_journey", "three_act_structure", "branching_narrative",
                "episodic_structure", "mystery_structure", "adventure_arc"
            ],
            "story_elements": [
                "plot_twists", "character_arcs", "foreshadowing", "pacing",
                "conflict_resolution", "theme_development", "world_integration"
            ],
            "genres": [
                "high_fantasy", "fairy_tale", "adventure", "mystery",
                "coming_of_age", "magical_realism", "epic_fantasy"
            ],
            "mood_capabilities": [
                "whimsical", "mysterious", "heroic", "cozy", "epic",
                "suspenseful", "heartwarming", "magical"
            ]
        }
    
    @staticmethod
    def get_character_behavior_specializations() -> Dict[str, Any]:
        """Specialized capabilities for Character Behavior Agent"""
        return {
            "personality_types": [
                "brave_hero", "wise_mentor", "trickster", "loyal_friend",
                "mysterious_stranger", "comic_relief", "noble_leader", "reluctant_hero"
            ],
            "character_archetypes": [
                "warrior", "mage", "rogue", "healer", "bard", "ranger",
                "paladin", "druid", "artificer", "warlock"
            ],
            "behavioral_traits": [
                "speech_patterns", "mannerisms", "quirks", "habits",
                "fears", "motivations", "relationships", "growth_potential"
            ],
            "species_knowledge": [
                "human", "elf", "dwarf", "halfling", "gnome", "orc",
                "dragon", "fairy", "centaur", "phoenix", "unicorn"
            ]
        }
    
    @staticmethod
    def get_world_builder_specializations() -> Dict[str, Any]:
        """Specialized capabilities for World Builder Agent"""
        return {
            "location_types": [
                "enchanted_forest", "crystal_caves", "floating_islands",
                "ancient_ruins", "magical_cities", "mystical_lakes",
                "dragon_lairs", "fairy_circles", "wizard_towers"
            ],
            "environmental_elements": [
                "weather_magic", "seasonal_changes", "day_night_cycles",
                "magical_phenomena", "flora_fauna", "geological_features"
            ],
            "cultural_aspects": [
                "civilizations", "traditions", "languages", "customs",
                "architecture", "art", "music", "festivals"
            ],
            "sensory_details": [
                "visual_descriptions", "ambient_sounds", "scents",
                "textures", "atmospheric_conditions", "lighting"
            ]
        }
    
    @staticmethod
    def get_quest_master_specializations() -> Dict[str, Any]:
        """Specialized capabilities for Quest Master Agent"""
        return {
            "quest_types": [
                "main_story", "side_quest", "fetch_quest", "escort_mission",
                "puzzle_quest", "combat_challenge", "social_interaction",
                "exploration", "rescue_mission", "mystery_solving"
            ],
            "difficulty_scaling": [
                "beginner_friendly", "moderate_challenge", "expert_level",
                "adaptive_difficulty", "skill_based", "choice_dependent"
            ],
            "reward_systems": [
                "experience_points", "magical_items", "story_progression",
                "character_development", "relationship_building", "world_unlocking"
            ],
            "pacing_elements": [
                "action_sequences", "quiet_moments", "revelation_points",
                "building_tension", "climax_moments", "resolution_phases"
            ]
        }
    
    @staticmethod
    def get_audio_coordinator_specializations() -> Dict[str, Any]:
        """Specialized capabilities for Audio Coordinator Agent"""
        return {
            "music_genres": [
                "epic_orchestral", "celtic_fantasy", "ambient_mystical",
                "heroic_themes", "mysterious_ambience", "peaceful_melodies",
                "battle_music", "magical_soundscapes"
            ],
            "sound_categories": [
                "environmental_sounds", "character_voices", "magic_effects",
                "combat_sounds", "ambient_noise", "emotional_cues"
            ],
            "audio_moods": [
                "triumphant", "mysterious", "peaceful", "tense",
                "magical", "adventurous", "cozy", "epic"
            ],
            "timing_expertise": [
                "entrance_cues", "exit_fades", "crescendo_building",
                "dramatic_pauses", "emotional_punctuation", "seamless_transitions"
            ]
        }
    
    @staticmethod
    def get_dialogue_creator_specializations() -> Dict[str, Any]:
        """Specialized capabilities for Dialogue Creator Agent"""
        return {
            "conversation_types": [
                "character_introduction", "quest_giving", "information_gathering",
                "emotional_support", "conflict_resolution", "casual_chat",
                "dramatic_revelation", "comedic_exchange"
            ],
            "speech_styles": [
                "formal_eloquent", "casual_friendly", "wise_cryptic",
                "playful_mischievous", "gruff_straightforward", "poetic_flowery",
                "ancient_formal", "modern_colloquial"
            ],
            "dialogue_functions": [
                "plot_advancement", "character_development", "world_building",
                "exposition_delivery", "emotional_connection", "humor_injection",
                "tension_building", "relationship_building"
            ],
            "cultural_voices": [
                "royal_court", "common_folk", "scholarly_academic",
                "warrior_culture", "magical_community", "merchant_class",
                "rural_communities", "urban_societies"
            ]
        }


if __name__ == "__main__":
    # Demo the agent creation
    print("🎭 Magic Adventure Agents Demo")
    print("=" * 50)
    
    # Create agent factory
    factory = MagicAdventureAgents()
    
    # Create all agents
    agents = factory.create_all_agents()
    
    # Display agent information
    for name, agent in agents.items():
        print(f"\n🤖 {name.upper().replace('_', ' ')} AGENT")
        print(f"Role: {agent.role}")
        print(f"Goal: {agent.goal}")
        print(f"Backstory (first 100 chars): {agent.backstory[:100]}...")
    
    print(f"\n✨ All {len(agents)} agents created successfully!")
    print("🎮 Ready for magical adventures!")