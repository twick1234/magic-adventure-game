#!/usr/bin/env python3
"""
🗄️ Magic Adventure Game - Database Models

SQLAlchemy models for the persistent, evolving Minecraft-style fantasy adventure game.
Provides comprehensive data models for users, worlds, characters, stories, AI agents,
and all game systems with optimized relationships and constraints.

This module implements:
- User management and authentication
- World persistence with chunk-based storage
- Character progression and relationships
- Story evolution and branching narratives
- AI agent activity tracking
- Quest and achievement systems
- Inventory and crafting mechanics
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, Text, 
    DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid
import bcrypt
import json

# Database base class
Base = declarative_base()

# Database configuration
DATABASE_URL = "postgresql://username:password@localhost/magic_adventure_game"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TimestampMixin:
    """Mixin for adding timestamp columns to models"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    profile_data = Column(JSONB, default=dict)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    timezone = Column(String(50), default='UTC')
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    story_evolutions = relationship("StoryEvolution", back_populates="triggered_by_user")
    
    def set_password(self, password: str) -> None:
        """Hash and set user password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'profile_data': self.profile_data,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'timezone': self.timezone
        }


class UserSession(Base, TimestampMixin):
    """User session management for authentication"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    session_data = Column(JSONB, default=dict)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_sessions_expires', expires_at, postgresql_where=(is_active == True)),
    )
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now(timezone.utc) > self.expires_at


class World(Base, TimestampMixin):
    """World container for game environments"""
    __tablename__ = "worlds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    world_settings = Column(JSONB, default=dict)
    last_evolved = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chunks = relationship("WorldChunk", back_populates="world", cascade="all, delete-orphan")
    structures = relationship("WorldStructure", back_populates="world", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")
    npcs = relationship("NPC", back_populates="world", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="world", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="world", cascade="all, delete-orphan")
    events = relationship("WorldEvent", back_populates="world", cascade="all, delete-orphan")
    agent_activities = relationship("AIAgentActivity", back_populates="world")
    evolution_logs = relationship("WorldEvolutionLog", back_populates="world", cascade="all, delete-orphan")
    
    def get_active_characters_count(self) -> int:
        """Get count of active characters in this world"""
        return len([c for c in self.characters if c.is_active])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'world_settings': self.world_settings,
            'created_at': self.created_at.isoformat(),
            'last_evolved': self.last_evolved.isoformat(),
            'version': self.version,
            'is_active': self.is_active,
            'active_characters': self.get_active_characters_count()
        }


class WorldChunk(Base, TimestampMixin):
    """Minecraft-style world chunks for infinite world generation"""
    __tablename__ = "world_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    chunk_x = Column(Integer, nullable=False)
    chunk_y = Column(Integer, nullable=False)
    chunk_z = Column(Integer, nullable=False)
    block_data = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, default=dict)
    last_modified = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)
    
    # Relationships
    world = relationship("World", back_populates="chunks")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('world_id', 'chunk_x', 'chunk_y', 'chunk_z'),
        Index('idx_world_chunks_coords', world_id, chunk_x, chunk_y, chunk_z),
        Index('idx_world_chunks_modified', last_modified),
        Index('idx_world_chunks_blocks', block_data, postgresql_using='gin'),
    )
    
    def get_block_at(self, x: int, y: int, z: int) -> Dict[str, Any]:
        """Get block data at specific coordinates within chunk"""
        block_key = f"{x},{y},{z}"
        return self.block_data.get('blocks', {}).get(block_key, {'type': 'air'})
    
    def set_block_at(self, x: int, y: int, z: int, block_data: Dict[str, Any]) -> None:
        """Set block data at specific coordinates within chunk"""
        if 'blocks' not in self.block_data:
            self.block_data['blocks'] = {}
        block_key = f"{x},{y},{z}"
        self.block_data['blocks'][block_key] = block_data
        self.last_modified = datetime.now(timezone.utc)
        self.version += 1


class WorldStructure(Base, TimestampMixin):
    """Persistent structures in the world like buildings, dungeons"""
    __tablename__ = "world_structures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    structure_type = Column(String(50), nullable=False)
    position = Column(JSONB, nullable=False)
    structure_data = Column(JSONB, nullable=False, default=dict)
    created_by_user = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    world = relationship("World", back_populates="structures")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_world_structures_position', position, postgresql_using='gin'),
    )


class Character(Base, TimestampMixin):
    """Player characters with stats, progression, and inventory"""
    __tablename__ = "characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    character_class = Column(String(50), nullable=False)
    stats = Column(JSONB, nullable=False, default=dict)
    position = Column(JSONB, nullable=False, default={'x': 0, 'y': 0, 'z': 0})
    inventory = Column(JSONB, default=dict)
    skills = Column(JSONB, default=dict)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="characters")
    world = relationship("World", back_populates="characters")
    relationships = relationship("CharacterRelationship", 
                               foreign_keys="CharacterRelationship.character_id",
                               back_populates="character",
                               cascade="all, delete-orphan")
    target_relationships = relationship("CharacterRelationship",
                                      foreign_keys="CharacterRelationship.target_character_id",
                                      back_populates="target_character")
    story_choices = relationship("StoryChoice", back_populates="character", cascade="all, delete-orphan")
    quest_progress = relationship("QuestProgress", back_populates="character", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="character", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_characters_world', world_id, postgresql_where=(is_active == True)),
        Index('idx_characters_user', user_id, postgresql_where=(is_active == True)),
        Index('idx_characters_position', position, postgresql_using='gin'),
        Index('idx_characters_position_x', func.cast(position['x'], Integer)),
        Index('idx_characters_position_y', func.cast(position['y'], Integer)),
        Index('idx_characters_position_z', func.cast(position['z'], Integer)),
    )
    
    def get_position_tuple(self) -> tuple:
        """Get position as tuple (x, y, z)"""
        pos = self.position or {'x': 0, 'y': 0, 'z': 0}
        return (pos['x'], pos['y'], pos['z'])
    
    def set_position(self, x: int, y: int, z: int) -> None:
        """Set character position"""
        self.position = {'x': x, 'y': y, 'z': z}
        self.last_active = datetime.now(timezone.utc)
    
    def add_experience(self, amount: int) -> bool:
        """Add experience and handle level ups"""
        self.experience += amount
        required_exp = self.level * 1000  # Simple level formula
        
        if self.experience >= required_exp:
            self.level += 1
            return True  # Level up occurred
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'world_id': str(self.world_id),
            'name': self.name,
            'character_class': self.character_class,
            'stats': self.stats,
            'position': self.position,
            'level': self.level,
            'experience': self.experience,
            'last_active': self.last_active.isoformat(),
            'is_active': self.is_active
        }


class CharacterRelationship(Base, TimestampMixin):
    """Relationships and social dynamics between characters"""
    __tablename__ = "character_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    target_character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # friend, enemy, neutral, romantic, rival
    affinity_score = Column(Float, default=0.0)  # -100.0 to +100.0
    interaction_history = Column(JSONB, default=list)
    
    # Relationships
    character = relationship("Character", foreign_keys=[character_id], back_populates="relationships")
    target_character = relationship("Character", foreign_keys=[target_character_id], back_populates="target_relationships")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('character_id', 'target_character_id'),
        CheckConstraint('character_id != target_character_id'),
        CheckConstraint('affinity_score >= -100.0 AND affinity_score <= 100.0'),
        Index('idx_character_relationships_character', character_id),
        Index('idx_character_relationships_target', target_character_id),
    )
    
    def add_interaction(self, interaction_type: str, details: Dict[str, Any]) -> None:
        """Add an interaction to the history"""
        interaction = {
            'type': interaction_type,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if not isinstance(self.interaction_history, list):
            self.interaction_history = []
        
        self.interaction_history.append(interaction)
        
        # Keep only last 50 interactions
        if len(self.interaction_history) > 50:
            self.interaction_history = self.interaction_history[-50:]


class NPC(Base, TimestampMixin):
    """AI-powered non-player characters"""
    __tablename__ = "npcs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    npc_type = Column(String(50), nullable=False)  # merchant, guard, sage, quest_giver, etc.
    personality = Column(JSONB, nullable=False, default=dict)
    position = Column(JSONB, nullable=False, default={'x': 0, 'y': 0, 'z': 0})
    dialogue_tree = Column(JSONB, default=dict)
    ai_memory = Column(JSONB, default=dict)  # AI agent memory for this NPC
    last_interaction = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    world = relationship("World", back_populates="npcs")
    
    # Indexes
    __table_args__ = (
        Index('idx_npcs_world', world_id, postgresql_where=(is_active == True)),
        Index('idx_npcs_personality', personality, postgresql_using='gin'),
    )
    
    def interact_with_character(self, character: Character, message: str) -> Dict[str, Any]:
        """Handle interaction with a character"""
        # Update last interaction time
        self.last_interaction = datetime.now(timezone.utc)
        
        # Store interaction in AI memory
        if 'interactions' not in self.ai_memory:
            self.ai_memory['interactions'] = []
        
        interaction = {
            'character_id': str(character.id),
            'character_name': character.name,
            'message': message,
            'timestamp': self.last_interaction.isoformat()
        }
        
        self.ai_memory['interactions'].append(interaction)
        
        # Keep only last 20 interactions
        if len(self.ai_memory['interactions']) > 20:
            self.ai_memory['interactions'] = self.ai_memory['interactions'][-20:]
        
        return {
            'npc_id': str(self.id),
            'npc_name': self.name,
            'response': "I remember our conversation...",  # This would be generated by AI agent
            'personality': self.personality,
            'relationship_change': 0.0
        }


class Story(Base, TimestampMixin):
    """Dynamic narrative threads that evolve with player choices"""
    __tablename__ = "stories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    story_type = Column(String(50), nullable=False)  # main, side, emergent, seasonal
    narrative_threads = Column(JSONB, default=dict)
    branching_data = Column(JSONB, default=dict)
    priority = Column(Integer, default=0)
    last_evolved = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    world = relationship("World", back_populates="stories")
    choices = relationship("StoryChoice", back_populates="story", cascade="all, delete-orphan")
    evolution_history = relationship("StoryEvolution", back_populates="story", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="story")
    
    # Indexes
    __table_args__ = (
        Index('idx_stories_world', world_id, postgresql_where=(is_active == True)),
        Index('idx_stories_narrative_threads', narrative_threads, postgresql_using='gin'),
    )
    
    def create_branch(self, branch_name: str, branch_data: Dict[str, Any]) -> None:
        """Create a new story branch"""
        if 'branches' not in self.branching_data:
            self.branching_data['branches'] = {}
        
        self.branching_data['branches'][branch_name] = {
            'data': branch_data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_active': True
        }
        
        self.last_evolved = datetime.now(timezone.utc)


class StoryChoice(Base):
    """Player choices that affect story progression"""
    __tablename__ = "story_choices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey('stories.id', ondelete='CASCADE'), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    choice_text = Column(Text, nullable=False)
    choice_data = Column(JSONB, default=dict)
    consequences = Column(JSONB, default=dict)
    made_at = Column(DateTime(timezone=True), server_default=func.now())
    choice_order = Column(Integer, nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="choices")
    character = relationship("Character", back_populates="story_choices")
    
    # Indexes
    __table_args__ = (
        Index('idx_story_choices_story', story_id),
        Index('idx_story_choices_character', character_id),
        Index('idx_story_choices_consequences', consequences, postgresql_using='gin'),
    )


class StoryEvolution(Base):
    """Tracks how stories evolve through AI and player actions"""
    __tablename__ = "story_evolution"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid=True), ForeignKey('stories.id', ondelete='CASCADE'), nullable=False)
    triggered_by_user = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    evolution_type = Column(String(50), nullable=False)  # player_choice, ai_evolution, world_event
    before_state = Column(JSONB, nullable=False)
    after_state = Column(JSONB, nullable=False)
    ai_reasoning = Column(Text)
    evolved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="evolution_history")
    triggered_by_user = relationship("User", back_populates="story_evolutions")


class Quest(Base, TimestampMixin):
    """Dynamic quests generated by AI and player actions"""
    __tablename__ = "quests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    story_id = Column(UUID(as_uuid=True), ForeignKey('stories.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    quest_type = Column(String(50), nullable=False)  # main, side, daily, seasonal, emergency
    objectives = Column(JSONB, nullable=False, default=list)
    rewards = Column(JSONB, default=dict)
    status = Column(String(20), default='available')  # available, active, completed, failed, expired
    completed_at = Column(DateTime(timezone=True))
    is_repeatable = Column(Boolean, default=False)
    
    # Relationships
    world = relationship("World", back_populates="quests")
    story = relationship("Story", back_populates="quests")
    progress_records = relationship("QuestProgress", back_populates="quest", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_quests_world', world_id),
        Index('idx_quests_status', world_id, status),
    )


class QuestProgress(Base, TimestampMixin):
    """Individual character progress on quests"""
    __tablename__ = "quest_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quest_id = Column(UUID(as_uuid=True), ForeignKey('quests.id', ondelete='CASCADE'), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    progress_data = Column(JSONB, default=dict)
    status = Column(String(20), default='not_started')  # not_started, active, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    quest = relationship("Quest", back_populates="progress_records")
    character = relationship("Character", back_populates="quest_progress")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('quest_id', 'character_id'),
        Index('idx_quest_progress_character', character_id),
    )


class AIAgent(Base, TimestampMixin):
    """AI agents that manage various aspects of the game"""
    __tablename__ = "ai_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(100), unique=True, nullable=False)
    agent_type = Column(String(50), nullable=False)  # story_generator, world_builder, npc_controller, etc.
    configuration = Column(JSONB, nullable=False, default=dict)
    memory_state = Column(JSONB, default=dict)
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    is_enabled = Column(Boolean, default=True)
    
    # Relationships
    activities = relationship("AIAgentActivity", back_populates="agent", cascade="all, delete-orphan")
    evolution_logs = relationship("WorldEvolutionLog", back_populates="agent")
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_agents_type', agent_type, postgresql_where=(is_enabled == True)),
        Index('idx_ai_agents_config', configuration, postgresql_using='gin'),
    )


class AIAgentActivity(Base):
    """Log of AI agent activities for monitoring and debugging"""
    __tablename__ = "ai_agent_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('ai_agents.id', ondelete='CASCADE'), nullable=False)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'))
    activity_type = Column(String(50), nullable=False)
    activity_data = Column(JSONB, default=dict)
    results = Column(JSONB, default=dict)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    execution_time_ms = Column(Float)
    
    # Relationships
    agent = relationship("AIAgent", back_populates="activities")
    world = relationship("World", back_populates="agent_activities")
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_activities_agent', agent_id),
        Index('idx_ai_activities_world', world_id),
        Index('idx_ai_activities_executed', executed_at),
    )


class WorldEvent(Base, TimestampMixin):
    """World events including seasonal changes and emergent events"""
    __tablename__ = "world_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String(50), nullable=False)  # seasonal, emergency, celebration, disaster
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_data = Column(JSONB, default=dict)
    scheduled_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    status = Column(String(20), default='scheduled')  # scheduled, active, completed, cancelled
    is_seasonal = Column(Boolean, default=False)
    
    # Relationships
    world = relationship("World", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index('idx_world_events_scheduled', world_id, scheduled_at, postgresql_where=(status == 'scheduled')),
        Index('idx_world_events_seasonal', world_id, postgresql_where=(is_seasonal == True)),
    )


class WorldEvolutionLog(Base):
    """Comprehensive log of world evolution by AI agents"""
    __tablename__ = "world_evolution_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(UUID(as_uuid=True), ForeignKey('worlds.id', ondelete='CASCADE'), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('ai_agents.id'), nullable=False)
    evolution_type = Column(String(50), nullable=False)  # terrain_change, structure_added, story_evolution
    changes_made = Column(JSONB, nullable=False)
    ai_reasoning = Column(Text)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    impact_score = Column(Float, default=0.0)  # Measure of change magnitude
    
    # Relationships
    world = relationship("World", back_populates="evolution_logs")
    agent = relationship("AIAgent", back_populates="evolution_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_world_evolution_world', world_id),
        Index('idx_world_evolution_executed', executed_at),
        Index('idx_world_evolution_impact', impact_score),
    )


class UserAchievement(Base):
    """Player achievements and progression milestones"""
    __tablename__ = "user_achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_type = Column(String(50), nullable=False)  # exploration, combat, social, building, story
    title = Column(String(200), nullable=False)
    description = Column(Text)
    achievement_data = Column(JSONB, default=dict)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    points_awarded = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    
    # Indexes
    __table_args__ = (
        Index('idx_achievements_user', user_id),
        Index('idx_achievements_type', achievement_type),
    )


class InventoryItem(Base, TimestampMixin):
    """Character inventory items with stacking support"""
    __tablename__ = "inventory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    item_type = Column(String(50), nullable=False)  # weapon, armor, consumable, material, tool
    item_name = Column(String(100), nullable=False)
    item_properties = Column(JSONB, default=dict)
    quantity = Column(Integer, default=1)
    stack_position = Column(Integer)  # Position in inventory grid
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True))
    
    # Relationships
    character = relationship("Character", back_populates="inventory_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_inventory_character', character_id),
        Index('idx_inventory_type', character_id, item_type),
    )
    
    def use_item(self, amount: int = 1) -> bool:
        """Use item and update quantity"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.last_used = datetime.now(timezone.utc)
            return True
        return False


class CraftingRecipe(Base, TimestampMixin):
    """Available crafting recipes"""
    __tablename__ = "crafting_recipes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_name = Column(String(100), unique=True, nullable=False)
    ingredients = Column(JSONB, nullable=False)  # Required materials and quantities
    result_item = Column(JSONB, nullable=False)  # Item created by recipe
    crafting_level_required = Column(Integer, default=1)
    is_discoverable = Column(Boolean, default=True)
    
    def can_craft(self, character: Character) -> bool:
        """Check if character can craft this recipe"""
        character_level = character.skills.get('crafting', 0)
        return character_level >= self.crafting_level_required
    
    def check_materials(self, character: Character) -> Dict[str, bool]:
        """Check if character has required materials"""
        inventory = {item.item_name: item.quantity for item in character.inventory_items}
        requirements_met = {}
        
        for ingredient, required_amount in self.ingredients.items():
            available_amount = inventory.get(ingredient, 0)
            requirements_met[ingredient] = available_amount >= required_amount
        
        return requirements_met


# Database utility functions
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_sample_data(db: Session):
    """Initialize database with sample data"""
    # Create sample world
    sample_world = World(
        name="Mystical Realms",
        description="A world of magic, mystery, and endless adventure",
        world_settings={
            'difficulty': 'normal',
            'pvp_enabled': False,
            'seasonal_events': True,
            'ai_evolution_rate': 'daily',
            'max_players': 100
        }
    )
    db.add(sample_world)
    db.commit()
    
    # Create sample AI agents
    agents = [
        AIAgent(
            agent_name="story_weaver",
            agent_type="narrative_generator",
            configuration={
                'creativity_level': 0.8,
                'story_coherence': 0.9,
                'response_length': 'medium',
                'preferred_genres': ['fantasy', 'adventure', 'mystery']
            }
        ),
        AIAgent(
            agent_name="world_sculptor",
            agent_type="environment_builder",
            configuration={
                'terrain_complexity': 0.7,
                'structure_frequency': 0.5,
                'biome_diversity': 0.8,
                'seasonal_adaptation': True
            }
        )
    ]
    
    for agent in agents:
        db.add(agent)
    
    db.commit()


if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")
    
    # Initialize sample data
    db = next(get_db())
    try:
        init_sample_data(db)
        print("Sample data initialized successfully!")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
    finally:
        db.close()