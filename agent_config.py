#!/usr/bin/env python3
"""
⚙️ Agent Configuration & Specialization System

This module provides comprehensive configuration management for all CrewAI agents,
including specialized knowledge domains, personality settings, behavioral parameters,
and dynamic configuration updates.

Features:
- Agent personality and behavior configuration
- Specialized knowledge domain management
- Dynamic parameter adjustment based on game state
- Configuration validation and error checking
- Profile templates for different game scenarios
- Performance tuning and optimization settings

Each agent can be fine-tuned for specific scenarios while maintaining
consistency with their core role and personality.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Enumeration of agent roles"""
    STORY_GENERATOR = "story_generator"
    CHARACTER_BEHAVIOR = "character_behavior"
    WORLD_BUILDER = "world_builder"
    QUEST_MASTER = "quest_master"
    AUDIO_COORDINATOR = "audio_coordinator"
    DIALOGUE_CREATOR = "dialogue_creator"


class PersonalityTrait(Enum):
    """Personality traits that can be assigned to agents"""
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    LOGICAL = "logical"
    WHIMSICAL = "whimsical"
    DRAMATIC = "dramatic"
    METHODICAL = "methodical"
    SPONTANEOUS = "spontaneous"
    WISE = "wise"
    PLAYFUL = "playful"


class DifficultyLevel(Enum):
    """Game difficulty levels that affect agent behavior"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ADAPTIVE = "adaptive"


@dataclass
class AgentPersonality:
    """Personality configuration for an agent"""
    primary_traits: List[PersonalityTrait] = field(default_factory=list)
    creativity_level: float = 0.7  # 0.0 to 1.0
    verbosity: float = 0.6  # 0.0 to 1.0
    formality: float = 0.5  # 0.0 (casual) to 1.0 (formal)
    humor_level: float = 0.4  # 0.0 to 1.0
    risk_tolerance: float = 0.5  # 0.0 (conservative) to 1.0 (bold)
    collaboration_preference: float = 0.8  # 0.0 (independent) to 1.0 (collaborative)
    
    def to_backstory_elements(self) -> List[str]:
        """Convert personality to backstory elements"""
        elements = []
        
        if PersonalityTrait.CREATIVE in self.primary_traits:
            elements.append("You have an incredibly creative mind that sees possibilities everywhere.")
        
        if PersonalityTrait.WISE in self.primary_traits:
            elements.append("Your wisdom comes from countless experiences across many realms.")
        
        if PersonalityTrait.PLAYFUL in self.primary_traits:
            elements.append("You approach everything with a sense of wonder and playfulness.")
        
        if self.creativity_level > 0.8:
            elements.append("You excel at thinking outside conventional boundaries.")
        
        if self.collaboration_preference > 0.7:
            elements.append("You work best when collaborating with others and value teamwork.")
        
        return elements


@dataclass
class PerformanceSettings:
    """Performance and behavior settings for an agent"""
    max_response_length: int = 500
    response_time_target: float = 3.0  # seconds
    creativity_temperature: float = 0.7
    consistency_weight: float = 0.8
    innovation_weight: float = 0.6
    detail_level: float = 0.7  # 0.0 (minimal) to 1.0 (highly detailed)
    memory_retention: int = 10  # number of previous interactions to remember
    context_window: int = 2000  # tokens
    
    def adjust_for_difficulty(self, difficulty: DifficultyLevel):
        """Adjust settings based on game difficulty"""
        if difficulty == DifficultyLevel.BEGINNER:
            self.detail_level = 0.5
            self.creativity_temperature = 0.6
            self.max_response_length = 300
        elif difficulty == DifficultyLevel.EXPERT:
            self.detail_level = 0.9
            self.creativity_temperature = 0.8
            self.max_response_length = 800


@dataclass
class KnowledgeDomain:
    """Specialized knowledge domain for an agent"""
    domain_name: str
    expertise_areas: List[str] = field(default_factory=list)
    knowledge_depth: float = 0.7  # 0.0 (basic) to 1.0 (expert)
    preferred_styles: List[str] = field(default_factory=list)
    avoid_topics: List[str] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)


@dataclass
class AgentConfiguration:
    """Complete configuration for a single agent"""
    role: AgentRole
    name: str
    display_name: str
    description: str
    personality: AgentPersonality = field(default_factory=AgentPersonality)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    knowledge_domains: List[KnowledgeDomain] = field(default_factory=list)
    collaboration_preferences: Dict[AgentRole, float] = field(default_factory=dict)
    
    # CrewAI specific settings
    backstory_template: str = ""
    goal_template: str = ""
    allow_delegation: bool = True
    verbose: bool = True
    max_iter: int = 3
    memory: bool = True
    
    # Dynamic settings
    active: bool = True
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    def generate_backstory(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate dynamic backstory based on personality and context"""
        base_backstory = self.backstory_template
        
        # Add personality elements
        personality_elements = self.personality.to_backstory_elements()
        if personality_elements:
            base_backstory += " " + " ".join(personality_elements)
        
        # Add context-specific elements
        if context:
            if context.get("game_difficulty") == "beginner":
                base_backstory += " You are particularly patient and helpful with new adventurers."
            elif context.get("player_experience") == "expert":
                base_backstory += " You enjoy engaging with experienced players who appreciate complexity."
        
        return base_backstory
    
    def generate_goal(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate dynamic goal based on current context"""
        base_goal = self.goal_template
        
        if context:
            difficulty = context.get("game_difficulty", "intermediate")
            if difficulty == "beginner":
                base_goal = base_goal.replace("challenging", "accessible and fun")
            elif difficulty == "expert":
                base_goal = base_goal.replace("fun", "sophisticated and challenging")
        
        return base_goal


class AgentConfigurationManager:
    """
    Manages configurations for all agents in the Magic Adventure Game
    """
    
    def __init__(self, config_directory: Optional[str] = None):
        self.config_directory = Path(config_directory or "config")
        self.configurations = {}
        self.templates = {}
        self.game_scenarios = {}
        
        logger.info("⚙️ Initializing Agent Configuration Manager")
        self._load_default_configurations()
        self._load_templates()
        self._load_game_scenarios()
    
    def get_configuration(self, role: AgentRole, 
                         scenario: Optional[str] = None) -> AgentConfiguration:
        """
        Get configuration for a specific agent role
        
        Args:
            role: The agent role
            scenario: Optional scenario name for specialized configs
            
        Returns:
            AgentConfiguration object
        """
        config_key = f"{role.value}_{scenario}" if scenario else role.value
        
        if config_key in self.configurations:
            return self.configurations[config_key].copy()
        elif role.value in self.configurations:
            return self.configurations[role.value].copy()
        else:
            logger.warning(f"⚠️ No configuration found for {role.value}, using default")
            return self._create_default_configuration(role)
    
    def update_configuration(self, role: AgentRole, updates: Dict[str, Any], 
                           scenario: Optional[str] = None) -> bool:
        """
        Update configuration for a specific agent
        
        Args:
            role: The agent role
            updates: Dictionary of updates to apply
            scenario: Optional scenario name
            
        Returns:
            Boolean indicating success
        """
        try:
            config_key = f"{role.value}_{scenario}" if scenario else role.value
            
            if config_key not in self.configurations:
                self.configurations[config_key] = self._create_default_configuration(role)
            
            config = self.configurations[config_key]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                else:
                    logger.warning(f"⚠️ Unknown configuration key: {key}")
            
            config.last_updated = datetime.now()
            logger.info(f"✅ Updated configuration for {role.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update configuration: {e}")
            return False
    
    def create_scenario_configuration(self, scenario_name: str, 
                                    base_configs: Dict[AgentRole, Dict[str, Any]]) -> bool:
        """
        Create a new scenario configuration set
        
        Args:
            scenario_name: Name of the scenario
            base_configs: Base configurations for each agent role
            
        Returns:
            Boolean indicating success
        """
        try:
            for role, config_updates in base_configs.items():
                base_config = self.get_configuration(role)
                
                # Apply scenario-specific updates
                for key, value in config_updates.items():
                    if hasattr(base_config, key):
                        setattr(base_config, key, value)
                
                # Store scenario configuration
                scenario_key = f"{role.value}_{scenario_name}"
                self.configurations[scenario_key] = base_config
            
            # Store scenario metadata
            self.game_scenarios[scenario_name] = {
                "name": scenario_name,
                "created_at": datetime.now(),
                "roles": list(base_configs.keys())
            }
            
            logger.info(f"🎭 Created scenario configuration: {scenario_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create scenario configuration: {e}")
            return False
    
    def validate_configuration(self, config: AgentConfiguration) -> Dict[str, Any]:
        """Validate agent configuration for correctness"""
        issues = []
        warnings = []
        
        # Check required fields
        if not config.name:
            issues.append("Agent name is required")
        
        if not config.backstory_template:
            warnings.append("No backstory template provided")
        
        # Validate personality settings
        if config.personality.creativity_level < 0 or config.personality.creativity_level > 1:
            issues.append("Creativity level must be between 0 and 1")
        
        # Validate performance settings
        if config.performance.response_time_target <= 0:
            issues.append("Response time target must be positive")
        
        if config.performance.max_response_length <= 0:
            issues.append("Max response length must be positive")
        
        # Check knowledge domains
        if not config.knowledge_domains:
            warnings.append("No knowledge domains specified")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "timestamp": datetime.now()
        }
    
    def export_configuration(self, role: AgentRole, 
                           filename: Optional[str] = None) -> bool:
        """Export agent configuration to file"""
        try:
            config = self.get_configuration(role)
            filename = filename or f"{role.value}_config.yaml"
            
            # Convert to serializable dict
            config_dict = {
                "role": config.role.value,
                "name": config.name,
                "display_name": config.display_name,
                "description": config.description,
                "personality": config.personality.__dict__,
                "performance": config.performance.__dict__,
                "knowledge_domains": [domain.__dict__ for domain in config.knowledge_domains],
                "backstory_template": config.backstory_template,
                "goal_template": config.goal_template,
                "version": config.version,
                "last_updated": config.last_updated.isoformat()
            }
            
            # Write to file
            filepath = self.config_directory / filename
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
            
            logger.info(f"📁 Exported configuration to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export configuration: {e}")
            return False
    
    def get_all_configurations(self) -> Dict[str, AgentConfiguration]:
        """Get all loaded configurations"""
        return self.configurations.copy()
    
    def get_scenario_list(self) -> List[str]:
        """Get list of available scenarios"""
        return list(self.game_scenarios.keys())
    
    def optimize_for_performance(self, target_response_time: float = 2.0):
        """Optimize all configurations for performance"""
        for config in self.configurations.values():
            if config.performance.response_time_target > target_response_time:
                # Reduce complexity for faster responses
                config.performance.response_time_target = target_response_time
                config.performance.max_response_length = min(
                    config.performance.max_response_length, 400
                )
                config.performance.detail_level *= 0.8
                config.performance.creativity_temperature *= 0.9
        
        logger.info(f"⚡ Optimized configurations for {target_response_time}s response time")
    
    def _load_default_configurations(self):
        """Load default configurations for all agent roles"""
        
        # Story Generator Configuration
        story_config = AgentConfiguration(
            role=AgentRole.STORY_GENERATOR,
            name="Master Story Weaver",
            display_name="Story Weaver",
            description="Creates compelling fantasy narratives and plot developments",
            backstory_template="You are an ancient and wise storyteller who has witnessed countless epic adventures across magical realms.",
            goal_template="Create compelling, dynamic fantasy narratives that adapt to player choices and maintain narrative coherence"
        )
        
        story_config.personality.primary_traits = [
            PersonalityTrait.CREATIVE, PersonalityTrait.DRAMATIC, PersonalityTrait.WISE
        ]
        story_config.personality.creativity_level = 0.9
        story_config.personality.verbosity = 0.7
        
        story_config.knowledge_domains = [
            KnowledgeDomain(
                domain_name="fantasy_literature",
                expertise_areas=["epic_fantasy", "fairy_tales", "mythology", "hero_journeys"],
                knowledge_depth=0.9,
                preferred_styles=["narrative", "descriptive", "atmospheric"]
            ),
            KnowledgeDomain(
                domain_name="plot_structures",
                expertise_areas=["three_act", "hero_journey", "branching_narrative"],
                knowledge_depth=0.8
            )
        ]
        
        # Character Behavior Configuration
        character_config = AgentConfiguration(
            role=AgentRole.CHARACTER_BEHAVIOR,
            name="Character Psychology Master",
            display_name="Character Master",
            description="Manages character personalities and behavioral consistency",
            backstory_template="You are a master of character psychology and behavior, having studied countless fantasy beings.",
            goal_template="Develop rich, consistent character personalities that evolve naturally throughout the adventure"
        )
        
        character_config.personality.primary_traits = [
            PersonalityTrait.EMPATHETIC, PersonalityTrait.ANALYTICAL, PersonalityTrait.WISE
        ]
        character_config.personality.creativity_level = 0.8
        character_config.personality.collaboration_preference = 0.9
        
        # World Builder Configuration
        world_config = AgentConfiguration(
            role=AgentRole.WORLD_BUILDER,
            name="Realm Architect",
            display_name="World Builder", 
            description="Creates immersive fantasy environments and locations",
            backstory_template="You are the grand architect of magical realms, able to visualize fantastic worlds in exquisite detail.",
            goal_template="Create vivid, immersive fantasy environments that feel alive and enhance the story"
        )
        
        world_config.personality.primary_traits = [
            PersonalityTrait.CREATIVE, PersonalityTrait.METHODICAL, PersonalityTrait.ANALYTICAL
        ]
        world_config.personality.detail_level = 0.8
        
        # Quest Master Configuration  
        quest_config = AgentConfiguration(
            role=AgentRole.QUEST_MASTER,
            name="Quest Architect",
            display_name="Quest Master",
            description="Designs engaging quests and manages game progression",
            backstory_template="You are a masterful quest designer who understands the art of adventure pacing and engagement.",
            goal_template="Design engaging quests and challenges that provide meaningful progression and perfect pacing"
        )
        
        quest_config.personality.primary_traits = [
            PersonalityTrait.METHODICAL, PersonalityTrait.LOGICAL, PersonalityTrait.CREATIVE
        ]
        quest_config.personality.risk_tolerance = 0.6
        
        # Audio Coordinator Configuration
        audio_config = AgentConfiguration(
            role=AgentRole.AUDIO_COORDINATOR,
            name="Sonic Enchanter",
            display_name="Audio Coordinator",
            description="Manages immersive audio experiences and sound design",
            backstory_template="You are a master of sonic magic, able to weave sounds that transport listeners to fantastical realms.",
            goal_template="Coordinate immersive audio experiences that perfectly complement the narrative and enhance emotions"
        )
        
        audio_config.personality.primary_traits = [
            PersonalityTrait.CREATIVE, PersonalityTrait.EMPATHETIC, PersonalityTrait.METHODICAL
        ]
        audio_config.personality.creativity_level = 0.8
        
        # Dialogue Creator Configuration
        dialogue_config = AgentConfiguration(
            role=AgentRole.DIALOGUE_CREATOR,
            name="Voice of All Beings",
            display_name="Dialogue Creator",
            description="Creates authentic dialogue and character conversations",
            backstory_template="You are the universal translator of hearts and minds, able to give voice to any fantasy being.",
            goal_template="Create authentic, engaging dialogue that brings characters to life and drives meaningful interactions"
        )
        
        dialogue_config.personality.primary_traits = [
            PersonalityTrait.EMPATHETIC, PersonalityTrait.CREATIVE, PersonalityTrait.PLAYFUL
        ]
        dialogue_config.personality.humor_level = 0.6
        dialogue_config.personality.collaboration_preference = 0.9
        
        # Store configurations
        self.configurations[AgentRole.STORY_GENERATOR.value] = story_config
        self.configurations[AgentRole.CHARACTER_BEHAVIOR.value] = character_config
        self.configurations[AgentRole.WORLD_BUILDER.value] = world_config
        self.configurations[AgentRole.QUEST_MASTER.value] = quest_config
        self.configurations[AgentRole.AUDIO_COORDINATOR.value] = audio_config
        self.configurations[AgentRole.DIALOGUE_CREATOR.value] = dialogue_config
        
        logger.info("✅ Loaded default configurations for all agents")
    
    def _load_templates(self):
        """Load configuration templates"""
        self.templates["beginner_friendly"] = {
            "creativity_level": 0.6,
            "verbosity": 0.5,
            "detail_level": 0.6,
            "max_response_length": 300
        }
        
        self.templates["expert_mode"] = {
            "creativity_level": 0.9,
            "verbosity": 0.8,
            "detail_level": 0.9,
            "max_response_length": 600
        }
        
        logger.info("📋 Loaded configuration templates")
    
    def _load_game_scenarios(self):
        """Load predefined game scenarios"""
        self.game_scenarios["children_adventure"] = {
            "name": "Children's Adventure",
            "description": "Gentle, educational adventure suitable for children",
            "difficulty": DifficultyLevel.BEGINNER,
            "themes": ["friendship", "courage", "learning"]
        }
        
        self.game_scenarios["epic_quest"] = {
            "name": "Epic Quest",
            "description": "Complex, challenging adventure for experienced players",
            "difficulty": DifficultyLevel.EXPERT,
            "themes": ["heroism", "sacrifice", "destiny"]
        }
        
        logger.info("🎭 Loaded game scenarios")
    
    def _create_default_configuration(self, role: AgentRole) -> AgentConfiguration:
        """Create a basic default configuration for any role"""
        return AgentConfiguration(
            role=role,
            name=f"Default {role.value.replace('_', ' ').title()}",
            display_name=role.value.replace('_', ' ').title(),
            description=f"Default configuration for {role.value}",
            backstory_template=f"You are a {role.value.replace('_', ' ')} in a magical adventure game.",
            goal_template=f"Assist with {role.value.replace('_', ' ')} tasks for the adventure game."
        )


if __name__ == "__main__":
    # Demo the configuration system
    print("⚙️ Agent Configuration System Demo")
    print("=" * 50)
    
    # Initialize configuration manager
    config_manager = AgentConfigurationManager()
    
    # Get configuration for story generator
    story_config = config_manager.get_configuration(AgentRole.STORY_GENERATOR)
    print(f"📚 Story Generator Config:")
    print(f"  Name: {story_config.name}")
    print(f"  Creativity Level: {story_config.personality.creativity_level}")
    print(f"  Primary Traits: {[trait.value for trait in story_config.personality.primary_traits]}")
    
    # Validate configuration
    validation = config_manager.validate_configuration(story_config)
    print(f"  Validation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
    
    # Create scenario
    scenario_configs = {
        AgentRole.STORY_GENERATOR: {"personality.creativity_level": 0.5},
        AgentRole.CHARACTER_BEHAVIOR: {"personality.empathy_level": 0.9}
    }
    
    success = config_manager.create_scenario_configuration("gentle_mode", scenario_configs)
    print(f"🎭 Created scenario: {'✅ Success' if success else '❌ Failed'}")
    
    # Get all scenarios
    scenarios = config_manager.get_scenario_list()
    print(f"📋 Available scenarios: {scenarios}")
    
    print("✨ Demo completed successfully!")