"""Add performance indexes

Revision ID: 002_add_indexes
Revises: 001_initial_schema
Create Date: 2025-09-04 22:24:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User authentication and sessions indexes
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_user_sessions_token', 'user_sessions', ['session_token'])
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'], 
                   postgresql_where=sa.text('is_active = true'))

    # World chunk retrieval (most critical for performance)
    op.create_index('idx_world_chunks_coords', 'world_chunks', 
                   ['world_id', 'chunk_x', 'chunk_y', 'chunk_z'])
    op.create_index('idx_world_chunks_modified', 'world_chunks', ['last_modified'])

    # Character positioning and relationships
    op.create_index('idx_characters_world', 'characters', ['world_id'], 
                   postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_characters_user', 'characters', ['user_id'], 
                   postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_characters_position', 'characters', ['position'], 
                   postgresql_using='gin')
    op.create_index('idx_character_relationships_character', 'character_relationships', 
                   ['character_id'])
    op.create_index('idx_character_relationships_target', 'character_relationships', 
                   ['target_character_id'])

    # Story and quest systems
    op.create_index('idx_stories_world', 'stories', ['world_id'], 
                   postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_story_choices_story', 'story_choices', ['story_id'])
    op.create_index('idx_story_choices_character', 'story_choices', ['character_id'])
    op.create_index('idx_quests_world', 'quests', ['world_id'])
    op.create_index('idx_quest_progress_character', 'quest_progress', ['character_id'])

    # AI agent activities (for monitoring and debugging)
    op.create_index('idx_ai_activities_agent', 'ai_agent_activities', ['agent_id'])
    op.create_index('idx_ai_activities_world', 'ai_agent_activities', ['world_id'])
    op.create_index('idx_ai_activities_executed', 'ai_agent_activities', ['executed_at'])

    # World events and evolution
    op.create_index('idx_world_events_scheduled', 'world_events', 
                   ['world_id', 'scheduled_at'], 
                   postgresql_where=sa.text("status = 'scheduled'"))
    op.create_index('idx_world_evolution_world', 'world_evolution_log', ['world_id'])
    op.create_index('idx_world_evolution_executed', 'world_evolution_log', ['executed_at'])

    # Inventory and achievements
    op.create_index('idx_inventory_character', 'inventory_items', ['character_id'])
    op.create_index('idx_achievements_user', 'user_achievements', ['user_id'])

    # JSONB indexes for complex queries
    op.create_index('idx_characters_position_x', 'characters', 
                   [sa.text("(position->>'x')::integer")])
    op.create_index('idx_characters_position_y', 'characters', 
                   [sa.text("(position->>'y')::integer")])
    op.create_index('idx_characters_position_z', 'characters', 
                   [sa.text("(position->>'z')::integer")])

    # Story branching queries
    op.create_index('idx_stories_narrative_threads', 'stories', ['narrative_threads'], 
                   postgresql_using='gin')
    op.create_index('idx_story_choices_consequences', 'story_choices', ['consequences'], 
                   postgresql_using='gin')

    # AI memory and configuration
    op.create_index('idx_npcs_personality', 'npcs', ['personality'], postgresql_using='gin')
    op.create_index('idx_ai_agents_config', 'ai_agents', ['configuration'], 
                   postgresql_using='gin')

    # World chunk block data
    op.create_index('idx_world_chunks_blocks', 'world_chunks', ['block_data'], 
                   postgresql_using='gin')

    # NPC and structure positioning
    op.create_index('idx_npcs_world', 'npcs', ['world_id'], 
                   postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_world_structures_position', 'world_structures', ['position'], 
                   postgresql_using='gin')

    # Agent type filtering
    op.create_index('idx_ai_agents_type', 'ai_agents', ['agent_type'], 
                   postgresql_where=sa.text('is_enabled = true'))

    # Quest status filtering
    op.create_index('idx_quests_status', 'quests', ['world_id', 'status'])

    # Seasonal events
    op.create_index('idx_world_events_seasonal', 'world_events', ['world_id'], 
                   postgresql_where=sa.text('is_seasonal = true'))

    # Achievement type filtering
    op.create_index('idx_achievements_type', 'user_achievements', ['achievement_type'])

    # Inventory type filtering
    op.create_index('idx_inventory_type', 'inventory_items', ['character_id', 'item_type'])

    # World evolution impact scoring
    op.create_index('idx_world_evolution_impact', 'world_evolution_log', ['impact_score'])


def downgrade() -> None:
    # Drop all indexes in reverse order
    op.drop_index('idx_world_evolution_impact')
    op.drop_index('idx_inventory_type')
    op.drop_index('idx_achievements_type')
    op.drop_index('idx_world_events_seasonal')
    op.drop_index('idx_quests_status')
    op.drop_index('idx_ai_agents_type')
    op.drop_index('idx_world_structures_position')
    op.drop_index('idx_npcs_world')
    op.drop_index('idx_world_chunks_blocks')
    op.drop_index('idx_ai_agents_config')
    op.drop_index('idx_npcs_personality')
    op.drop_index('idx_story_choices_consequences')
    op.drop_index('idx_stories_narrative_threads')
    op.drop_index('idx_characters_position_z')
    op.drop_index('idx_characters_position_y')
    op.drop_index('idx_characters_position_x')
    op.drop_index('idx_achievements_user')
    op.drop_index('idx_inventory_character')
    op.drop_index('idx_world_evolution_executed')
    op.drop_index('idx_world_evolution_world')
    op.drop_index('idx_world_events_scheduled')
    op.drop_index('idx_ai_activities_executed')
    op.drop_index('idx_ai_activities_world')
    op.drop_index('idx_ai_activities_agent')
    op.drop_index('idx_quest_progress_character')
    op.drop_index('idx_quests_world')
    op.drop_index('idx_story_choices_character')
    op.drop_index('idx_story_choices_story')
    op.drop_index('idx_stories_world')
    op.drop_index('idx_character_relationships_target')
    op.drop_index('idx_character_relationships_character')
    op.drop_index('idx_characters_position')
    op.drop_index('idx_characters_user')
    op.drop_index('idx_characters_world')
    op.drop_index('idx_world_chunks_modified')
    op.drop_index('idx_world_chunks_coords')
    op.drop_index('idx_user_sessions_expires')
    op.drop_index('idx_user_sessions_user_id')
    op.drop_index('idx_user_sessions_token')
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_username')