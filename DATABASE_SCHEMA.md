# 🎮 Magic Adventure Game - Database Schema
**Document Version:** v1.0.0  
**Created:** September 4, 2025 - 2:15 PM UTC  
**Last Updated:** September 4, 2025 - 2:15 PM UTC  
**Author:** Database Architect Agent  

## Overview
Comprehensive database schema for a persistent, evolving Minecraft-style fantasy adventure game with AI-driven world evolution, user authentication, and real-time story branching.

## Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Character : creates
    User ||--o{ Session : has
    User ||--o{ Achievement : earns
    
    World ||--o{ WorldChunk : contains
    World ||--o{ Character : hosts
    World ||--o{ Story : has
    World ||--o{ WorldEvent : experiences
    World ||--o{ WorldEvolutionLog : evolves
    
    Character ||--o{ Inventory : owns
    Character ||--o{ CharacterRelationship : has
    Character ||--o{ QuestProgress : tracks
    Character ||--o{ CharacterSkill : develops
    
    Story ||--o{ StoryBranch : branches
    Story ||--o{ PlayerChoice : records
    
    Quest ||--o{ QuestProgress : tracked_by
    Quest ||--o{ QuestObjective : contains
    
    AIAgent ||--o{ WorldEvolutionLog : creates
    AIAgent ||--o{ AgentMemory : stores
    
    CraftingRecipe ||--o{ Inventory : creates
    
    User {
        bigint id PK
        string username UK
        string email UK
        string password_hash
        jsonb profile
        timestamp created_at
        timestamp updated_at
        boolean is_active
        timestamp last_login
    }
    
    Character {
        bigint id PK
        bigint user_id FK
        bigint world_id FK
        string name
        string character_class
        int level
        int experience
        jsonb stats
        jsonb appearance
        float position_x
        float position_y
        float position_z
        timestamp created_at
        timestamp updated_at
    }
    
    World {
        bigint id PK
        string name UK
        jsonb settings
        string world_type
        bigint seed
        timestamp created_at
        timestamp updated_at
        boolean is_active
        jsonb metadata
    }
    
    WorldChunk {
        bigint id PK
        bigint world_id FK
        int chunk_x
        int chunk_y
        int chunk_z
        jsonb block_data
        jsonb structures
        timestamp created_at
        timestamp updated_at
        int version
    }
    
    Story {
        bigint id PK
        bigint world_id FK
        string title
        text description
        string story_type
        jsonb metadata
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    StoryBranch {
        bigint id PK
        bigint story_id FK
        bigint parent_branch_id FK
        string branch_name
        text content
        jsonb conditions
        jsonb consequences
        int branch_order
        timestamp created_at
    }
    
    PlayerChoice {
        bigint id PK
        bigint character_id FK
        bigint story_branch_id FK
        string choice_text
        jsonb choice_data
        jsonb consequences
        timestamp made_at
    }
    
    Quest {
        bigint id PK
        bigint world_id FK
        string title
        text description
        string quest_type
        jsonb requirements
        jsonb rewards
        int difficulty_level
        boolean is_active
        timestamp created_at
        timestamp expires_at
    }
    
    QuestObjective {
        bigint id PK
        bigint quest_id FK
        string objective_text
        jsonb requirements
        jsonb progress_data
        boolean is_completed
        int order_index
    }
    
    QuestProgress {
        bigint id PK
        bigint character_id FK
        bigint quest_id FK
        string status
        jsonb progress_data
        timestamp started_at
        timestamp completed_at
        jsonb rewards_earned
    }
    
    Inventory {
        bigint id PK
        bigint character_id FK
        string item_type
        string item_name
        int quantity
        jsonb item_data
        int slot_position
        timestamp acquired_at
        timestamp updated_at
    }
    
    CharacterRelationship {
        bigint id PK
        bigint character_id FK
        bigint target_character_id FK
        string relationship_type
        int relationship_value
        jsonb interaction_history
        timestamp created_at
        timestamp updated_at
    }
    
    CharacterSkill {
        bigint id PK
        bigint character_id FK
        string skill_name
        int skill_level
        int experience_points
        jsonb skill_data
        timestamp updated_at
    }
    
    Achievement {
        bigint id PK
        bigint user_id FK
        string achievement_name
        text description
        int points
        jsonb unlock_data
        timestamp unlocked_at
    }
    
    AIAgent {
        bigint id PK
        string agent_name UK
        string agent_type
        jsonb configuration
        jsonb current_state
        boolean is_active
        timestamp created_at
        timestamp last_activity
    }
    
    AgentMemory {
        bigint id PK
        bigint agent_id FK
        bigint world_id FK
        string memory_type
        jsonb memory_data
        timestamp created_at
        timestamp expires_at
    }
    
    WorldEvolutionLog {
        bigint id PK
        bigint world_id FK
        bigint agent_id FK
        string evolution_type
        jsonb changes_made
        jsonb reasoning
        timestamp applied_at
        boolean is_active
    }
    
    WorldEvent {
        bigint id PK
        bigint world_id FK
        string event_type
        string event_name
        text description
        jsonb event_data
        timestamp start_time
        timestamp end_time
        boolean is_active
    }
    
    CraftingRecipe {
        bigint id PK
        string recipe_name UK
        jsonb ingredients
        jsonb result_item
        int required_level
        string recipe_type
        jsonb unlock_conditions
        timestamp created_at
    }
    
    Session {
        bigint id PK
        bigint user_id FK
        string session_token UK
        jsonb session_data
        timestamp created_at
        timestamp expires_at
        boolean is_active
    }
```

## Table Specifications

### User Management

#### Users Table
**Primary Key:** `id` (bigint, auto-increment)
**Unique Constraints:** `username`, `email`
**Indexes:** 
- `idx_users_username` on `username`
- `idx_users_email` on `email`
- `idx_users_last_login` on `last_login`

**Security Features:**
- Password hashing using bcrypt with salt rounds
- Account lockout after failed attempts
- Session token management
- Profile data stored in JSONB for flexibility

#### Sessions Table
**Primary Key:** `id` (bigint, auto-increment)
**Foreign Keys:** `user_id` → Users.id
**Unique Constraints:** `session_token`
**TTL:** Sessions automatically expire after configured timeout

### World Persistence System

#### Worlds Table
**Primary Key:** `id` (bigint, auto-increment)
**Unique Constraints:** `name`
**Features:**
- Seed-based world generation for reproducibility
- JSONB settings for world configuration
- Version tracking for world schema evolution
- Metadata storage for AI agent context

#### WorldChunks Table
**Primary Key:** `id` (bigint, auto-increment)
**Foreign Keys:** `world_id` → Worlds.id
**Composite Index:** `idx_world_chunks_coordinates` on `(world_id, chunk_x, chunk_y, chunk_z)`
**Features:**
- Minecraft-style chunk-based storage (16x16x16 blocks)
- JSONB block data for efficient storage
- Structure metadata for landmarks and buildings
- Version control for chunk modifications

**Block Data Format:**
```json
{
  "blocks": {
    "0,0,0": {"type": "grass", "metadata": {}},
    "0,1,0": {"type": "air", "metadata": {}}
  },
  "entities": [
    {"type": "npc", "id": "villager_001", "position": [8, 1, 8]}
  ]
}
```

### Character System

#### Characters Table
**Primary Key:** `id` (bigint, auto-increment)
**Foreign Keys:** 
- `user_id` → Users.id
- `world_id` → Worlds.id
**Indexes:**
- `idx_characters_user_world` on `(user_id, world_id)`
- `idx_characters_position` on `(position_x, position_y, position_z)`

**Stats Format:**
```json
{
  "health": 100,
  "mana": 50,
  "strength": 15,
  "intelligence": 12,
  "dexterity": 18,
  "constitution": 14,
  "charisma": 10
}
```

#### CharacterRelationships Table
**Features:**
- Bidirectional relationship tracking
- Relationship values (-100 to +100)
- Interaction history logging
- AI-driven relationship evolution

#### CharacterSkills Table
**Features:**
- Multiple skill trees per character
- Experience-based progression
- Skill unlock dependencies
- Mastery levels and specializations

### Story Evolution System

#### Stories Table
**Primary Key:** `id` (bigint, auto-increment)
**Foreign Keys:** `world_id` → Worlds.id
**Features:**
- Multiple concurrent storylines
- AI-generated narrative threads
- Player choice impact tracking
- Story state persistence

#### StoryBranches Table
**Features:**
- Tree-structured branching narratives
- Conditional content based on character stats
- Dynamic consequence system
- AI-generated branch extensions

#### PlayerChoices Table
**Features:**
- Complete choice history tracking
- Consequence prediction and tracking
- Choice impact on world state
- Retroactive story modification support

### Quest System

#### Quests Table
**Features:**
- Dynamic quest generation by AI agents
- Difficulty scaling based on character level
- Time-limited and permanent quests
- Multi-objective quest support

#### QuestObjectives Table
**Features:**
- Ordered objective sequences
- Progress tracking with metrics
- Conditional objective unlocking
- Dynamic objective modification

#### QuestProgress Table
**Features:**
- Individual character progress tracking
- Reward distribution system
- Quest sharing between characters
- Achievement integration

### AI Agent System

#### AIAgents Table
**Features:**
- Multiple specialized agent types
- Configuration management
- State persistence between runs
- Activity monitoring and logging

**Agent Types:**
- `story_weaver`: Narrative generation and evolution
- `world_builder`: Environmental changes and additions
- `character_master`: NPC behavior and relationships
- `quest_generator`: Dynamic quest creation
- `event_coordinator`: World events and seasonal changes
- `balance_keeper`: Game balance monitoring

#### AgentMemory Table
**Features:**
- Persistent agent memory across sessions
- Memory expiration and cleanup
- Context sharing between agents
- Memory priority and importance scoring

#### WorldEvolutionLog Table
**Features:**
- Complete audit trail of world changes
- AI reasoning documentation
- Change rollback capability
- Evolution pattern analysis

### Inventory and Crafting

#### Inventory Table
**Features:**
- Stack-based item management
- Position-based storage (bags, equipment slots)
- Item durability and enchantment support
- Trade and transfer logging

#### CraftingRecipes Table
**Features:**
- Level-gated recipe unlocking
- Multi-ingredient complex recipes
- Success probability based on skill
- Recipe discovery system

### Events and Achievements

#### WorldEvents Table
**Features:**
- Seasonal event cycles
- Player-triggered events
- AI-generated emergent events
- Cross-world event propagation

#### Achievements Table
**Features:**
- Progressive achievement chains
- Hidden achievement discovery
- Point-based reward system
- Social achievement sharing

## Performance Optimization

### Critical Indexes

```sql
-- World chunk retrieval optimization
CREATE INDEX idx_world_chunks_coordinates ON world_chunks (world_id, chunk_x, chunk_y, chunk_z);
CREATE INDEX idx_world_chunks_updated ON world_chunks (updated_at);

-- Character position queries
CREATE INDEX idx_characters_position ON characters (world_id, position_x, position_y, position_z);
CREATE INDEX idx_characters_user ON characters (user_id, world_id);

-- Story and quest lookups
CREATE INDEX idx_story_branches_parent ON story_branches (parent_branch_id);
CREATE INDEX idx_player_choices_character ON player_choices (character_id, made_at);
CREATE INDEX idx_quest_progress_character ON quest_progress (character_id, status);

-- AI agent activity
CREATE INDEX idx_world_evolution_world ON world_evolution_log (world_id, applied_at);
CREATE INDEX idx_agent_memory_world ON agent_memory (world_id, agent_id);

-- JSONB optimization
CREATE INDEX idx_characters_stats ON characters USING GIN (stats);
CREATE INDEX idx_world_chunks_blocks ON world_chunks USING GIN (block_data);
CREATE INDEX idx_users_profile ON users USING GIN (profile);
```

### Query Optimization Strategies

1. **Chunk Loading:** Spatial indexing for efficient area-based chunk retrieval
2. **Story Branching:** Recursive CTE for branch traversal
3. **Character Relationships:** Graph-based queries with path optimization
4. **AI Agent Coordination:** Message queue integration for async processing

## Migration Scripts

### Initial Schema Creation
```sql
-- See migrations/001_initial_schema.py for complete DDL
-- Includes all table creation, constraints, and initial indexes
```

### Performance Enhancement Migration
```sql
-- See migrations/002_add_indexes.py for performance indexes
-- Includes JSONB indexes and spatial optimization
```

## Backup and Recovery

### Automated Backup Strategy
- **Full Backup:** Daily at 2 AM UTC
- **Incremental Backup:** Every 4 hours
- **Transaction Log Backup:** Every 15 minutes
- **Retention:** 30 days full, 7 days incremental

### Recovery Procedures
1. **Point-in-time Recovery:** Within 15-minute granularity
2. **World Rollback:** Individual world state restoration
3. **Character Recovery:** Individual character data restoration
4. **Story State Recovery:** Narrative thread restoration

## Development and Testing

### Sample Data Generation
The system includes comprehensive sample data generators for:
- Realistic user profiles and characters
- Diverse world chunks with various biomes
- Complex story branches and player choices
- AI agent activity simulation
- Quest and achievement data

### Testing Utilities
- **Load Testing:** Concurrent user simulation
- **Data Integrity:** Referential integrity verification
- **Performance Profiling:** Query execution analysis
- **Migration Testing:** Schema evolution validation

## Configuration

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/magic_adventure
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
REDIS_URL=redis://localhost:6379/0
BACKUP_RETENTION_DAYS=30
```

### Database Tuning
- **Shared Buffers:** 25% of available RAM
- **Work Memory:** 4MB per connection
- **Maintenance Work Memory:** 256MB
- **WAL Buffers:** 16MB
- **Checkpoint Segments:** 32

This database schema provides a solid foundation for a persistent, evolving game world where AI agents can continuously modify and expand the environment while maintaining data integrity and performance.