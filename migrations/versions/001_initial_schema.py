"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-09-04 22:23:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100)),
        sa.Column('profile_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('session_token', sa.String(255), nullable=False),
        sa.Column('session_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create worlds table
    op.create_table(
        'worlds',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('world_settings', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_evolved', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create world_chunks table
    op.create_table(
        'world_chunks',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('chunk_x', sa.Integer(), nullable=False),
        sa.Column('chunk_y', sa.Integer(), nullable=False),
        sa.Column('chunk_z', sa.Integer(), nullable=False),
        sa.Column('block_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_modified', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('world_id', 'chunk_x', 'chunk_y', 'chunk_z')
    )
    
    # Create world_structures table
    op.create_table(
        'world_structures',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('structure_type', sa.String(50), nullable=False),
        sa.Column('position', postgresql.JSONB(), nullable=False),
        sa.Column('structure_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_by_user', postgresql.UUID()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user'], ['users.id'])
    )
    
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('character_class', sa.String(50), nullable=False),
        sa.Column('stats', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('position', postgresql.JSONB(), nullable=False, server_default='{"x": 0, "y": 0, "z": 0}'),
        sa.Column('inventory', postgresql.JSONB(), server_default='{}'),
        sa.Column('skills', postgresql.JSONB(), server_default='{}'),
        sa.Column('level', sa.Integer(), server_default='1'),
        sa.Column('experience', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_active', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    
    # Create character_relationships table
    op.create_table(
        'character_relationships',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('character_id', postgresql.UUID(), nullable=False),
        sa.Column('target_character_id', postgresql.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('affinity_score', sa.Float(), server_default='0.0'),
        sa.Column('interaction_history', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('character_id', 'target_character_id'),
        sa.CheckConstraint('character_id != target_character_id'),
        sa.CheckConstraint('affinity_score >= -100.0 AND affinity_score <= 100.0')
    )
    
    # Create npcs table
    op.create_table(
        'npcs',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('npc_type', sa.String(50), nullable=False),
        sa.Column('personality', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('position', postgresql.JSONB(), nullable=False, server_default='{"x": 0, "y": 0, "z": 0}'),
        sa.Column('dialogue_tree', postgresql.JSONB(), server_default='{}'),
        sa.Column('ai_memory', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_interaction', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    
    # Create stories table
    op.create_table(
        'stories',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('story_type', sa.String(50), nullable=False),
        sa.Column('narrative_threads', postgresql.JSONB(), server_default='{}'),
        sa.Column('branching_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_evolved', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    
    # Create ai_agents table
    op.create_table(
        'ai_agents',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('configuration', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('memory_state', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_active', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_enabled', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_name')
    )
    
    # Create story_choices table
    op.create_table(
        'story_choices',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('story_id', postgresql.UUID(), nullable=False),
        sa.Column('character_id', postgresql.UUID(), nullable=False),
        sa.Column('choice_text', sa.Text(), nullable=False),
        sa.Column('choice_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('consequences', postgresql.JSONB(), server_default='{}'),
        sa.Column('made_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('choice_order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE')
    )
    
    # Create story_evolution table
    op.create_table(
        'story_evolution',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('story_id', postgresql.UUID(), nullable=False),
        sa.Column('triggered_by_user', postgresql.UUID()),
        sa.Column('evolution_type', sa.String(50), nullable=False),
        sa.Column('before_state', postgresql.JSONB(), nullable=False),
        sa.Column('after_state', postgresql.JSONB(), nullable=False),
        sa.Column('ai_reasoning', sa.Text()),
        sa.Column('evolved_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by_user'], ['users.id'])
    )
    
    # Create quests table
    op.create_table(
        'quests',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('story_id', postgresql.UUID()),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('quest_type', sa.String(50), nullable=False),
        sa.Column('objectives', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('rewards', postgresql.JSONB(), server_default='{}'),
        sa.Column('status', sa.String(20), server_default='available'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_repeatable', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'])
    )
    
    # Create quest_progress table
    op.create_table(
        'quest_progress',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('quest_id', postgresql.UUID(), nullable=False),
        sa.Column('character_id', postgresql.UUID(), nullable=False),
        sa.Column('progress_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('status', sa.String(20), server_default='not_started'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('quest_id', 'character_id')
    )
    
    # Create ai_agent_activities table
    op.create_table(
        'ai_agent_activities',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_id', postgresql.UUID(), nullable=False),
        sa.Column('world_id', postgresql.UUID()),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('activity_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('results', postgresql.JSONB(), server_default='{}'),
        sa.Column('executed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('execution_time_ms', sa.Float()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    
    # Create world_events table
    op.create_table(
        'world_events',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('event_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('executed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('status', sa.String(20), server_default='scheduled'),
        sa.Column('is_seasonal', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    
    # Create world_evolution_log table
    op.create_table(
        'world_evolution_log',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('world_id', postgresql.UUID(), nullable=False),
        sa.Column('agent_id', postgresql.UUID(), nullable=False),
        sa.Column('evolution_type', sa.String(50), nullable=False),
        sa.Column('changes_made', postgresql.JSONB(), nullable=False),
        sa.Column('ai_reasoning', sa.Text()),
        sa.Column('executed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('impact_score', sa.Float(), server_default='0.0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.id'])
    )
    
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('achievement_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('achievement_data', postgresql.JSONB(), server_default='{}'),
        sa.Column('unlocked_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('points_awarded', sa.Integer(), server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('character_id', postgresql.UUID(), nullable=False),
        sa.Column('item_type', sa.String(50), nullable=False),
        sa.Column('item_name', sa.String(100), nullable=False),
        sa.Column('item_properties', postgresql.JSONB(), server_default='{}'),
        sa.Column('quantity', sa.Integer(), server_default='1'),
        sa.Column('stack_position', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('acquired_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_used', sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE')
    )
    
    # Create crafting_recipes table
    op.create_table(
        'crafting_recipes',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('recipe_name', sa.String(100), nullable=False),
        sa.Column('ingredients', postgresql.JSONB(), nullable=False),
        sa.Column('result_item', postgresql.JSONB(), nullable=False),
        sa.Column('crafting_level_required', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_discoverable', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recipe_name')
    )


def downgrade() -> None:
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('crafting_recipes')
    op.drop_table('inventory_items')
    op.drop_table('user_achievements')
    op.drop_table('world_evolution_log')
    op.drop_table('world_events')
    op.drop_table('ai_agent_activities')
    op.drop_table('quest_progress')
    op.drop_table('quests')
    op.drop_table('story_evolution')
    op.drop_table('story_choices')
    op.drop_table('ai_agents')
    op.drop_table('stories')
    op.drop_table('npcs')
    op.drop_table('character_relationships')
    op.drop_table('characters')
    op.drop_table('world_structures')
    op.drop_table('world_chunks')
    op.drop_table('worlds')
    op.drop_table('user_sessions')
    op.drop_table('users')
    
    # Drop UUID extension
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')