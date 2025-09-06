# 🗄️ Magic Adventure Game - Database System

## Overview

This database system provides comprehensive data persistence for the Magic Adventure Game, supporting:

- **Multi-user gameplay** with secure authentication
- **World persistence** using Minecraft-style chunk-based storage
- **Story evolution** with AI-driven narrative branching
- **Character progression** and complex social relationships
- **AI agent automation** with activity tracking and world evolution
- **Real-time updates** and performance optimization

## Quick Start

### 1. Install Dependencies

```bash
# Install database dependencies
pip install -r requirements_database.txt

# Or install specific packages
pip install sqlalchemy alembic psycopg2-binary bcrypt redis
```

### 2. Setup PostgreSQL

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create database and user
createdb magic_adventure_game
psql magic_adventure_game -c "CREATE USER game_user WITH PASSWORD 'your_password';"
psql magic_adventure_game -c "GRANT ALL PRIVILEGES ON DATABASE magic_adventure_game TO game_user;"
```

### 3. Configure Database Connection

Create a `.env` file:

```bash
DATABASE_URL=postgresql://game_user:your_password@localhost/magic_adventure_game
REDIS_URL=redis://localhost:6379/0
```

### 4. Initialize Database

```bash
# Full setup with sample data
python database_setup.py --full-setup

# Or step by step
python database_setup.py --create-tables
python database_setup.py --sample-data
```

### 5. Run Migrations (Optional)

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Database Schema

### Core Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `users` | User authentication & profiles | Encrypted passwords, JSONB profiles |
| `worlds` | Game world containers | Settings, versioning, evolution tracking |
| `world_chunks` | Minecraft-style terrain storage | Coordinates, block data, metadata |
| `characters` | Player characters | Stats, position, inventory, relationships |
| `stories` | Dynamic narratives | Branching data, AI evolution |
| `ai_agents` | AI system management | Configuration, memory state |

### Relationship Examples

```python
# Get user's characters in a world
user = session.query(User).filter_by(username='wizard_adventurer').first()
characters = user.characters.filter(Character.world_id == world_id).all()

# Load world chunks around position
chunks = session.query(WorldChunk).filter(
    WorldChunk.world_id == world_id,
    WorldChunk.chunk_x.between(x-2, x+2),
    WorldChunk.chunk_z.between(z-2, z+2)
).all()

# Get character relationships
relationships = session.query(CharacterRelationship).filter(
    or_(
        CharacterRelationship.character_id == character.id,
        CharacterRelationship.target_character_id == character.id
    )
).all()
```

## Usage Examples

### 1. User Management

```python
from database_models import User, SessionLocal

# Create new user
def create_user(username: str, email: str, password: str):
    with SessionLocal() as session:
        user = User(username=username, email=email)
        user.set_password(password)
        session.add(user)
        session.commit()
        return user

# Authenticate user
def authenticate_user(username: str, password: str):
    with SessionLocal() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
```

### 2. World Management

```python
from database_models import World, WorldChunk

# Create new world
def create_world(name: str, settings: dict):
    with SessionLocal() as session:
        world = World(name=name, world_settings=settings)
        session.add(world)
        session.commit()
        return world

# Load chunk data
def get_chunk(world_id: str, x: int, y: int, z: int):
    with SessionLocal() as session:
        return session.query(WorldChunk).filter(
            WorldChunk.world_id == world_id,
            WorldChunk.chunk_x == x,
            WorldChunk.chunk_y == y,
            WorldChunk.chunk_z == z
        ).first()

# Set block in chunk
def set_block(world_id: str, x: int, y: int, z: int, block_data: dict):
    chunk_x, chunk_z = x // 16, z // 16
    local_x, local_z = x % 16, z % 16
    
    with SessionLocal() as session:
        chunk = get_chunk(world_id, chunk_x, 0, chunk_z)
        if chunk:
            chunk.set_block_at(local_x, y, local_z, block_data)
            session.commit()
```

### 3. Character Operations

```python
from database_models import Character, InventoryItem

# Create character
def create_character(user_id: str, world_id: str, name: str, char_class: str):
    with SessionLocal() as session:
        character = Character(
            user_id=user_id,
            world_id=world_id,
            name=name,
            character_class=char_class,
            stats={'strength': 10, 'intelligence': 10, 'dexterity': 10},
            position={'x': 0, 'y': 64, 'z': 0}
        )
        session.add(character)
        session.commit()
        return character

# Add item to inventory
def add_item(character_id: str, item_name: str, quantity: int = 1):
    with SessionLocal() as session:
        item = InventoryItem(
            character_id=character_id,
            item_type='material',
            item_name=item_name,
            quantity=quantity
        )
        session.add(item)
        session.commit()
```

### 4. Story System

```python
from database_models import Story, StoryChoice

# Create story arc
def create_story(world_id: str, title: str, story_type: str):
    with SessionLocal() as session:
        story = Story(
            world_id=world_id,
            title=title,
            story_type=story_type,
            narrative_threads={'main': 'The adventure begins...'}
        )
        session.add(story)
        session.commit()
        return story

# Record player choice
def make_choice(story_id: str, character_id: str, choice_text: str):
    with SessionLocal() as session:
        choice = StoryChoice(
            story_id=story_id,
            character_id=character_id,
            choice_text=choice_text,
            choice_order=1
        )
        session.add(choice)
        session.commit()
```

### 5. AI Agent Integration

```python
from database_models import AIAgent, AIAgentActivity, WorldEvolutionLog

# Execute AI agent activity
def run_agent_activity(agent_name: str, world_id: str, activity_type: str, data: dict):
    with SessionLocal() as session:
        agent = session.query(AIAgent).filter_by(agent_name=agent_name).first()
        
        # Record activity
        activity = AIAgentActivity(
            agent_id=agent.id,
            world_id=world_id,
            activity_type=activity_type,
            activity_data=data,
            results={'status': 'completed'}
        )
        session.add(activity)
        
        # Log world evolution
        evolution = WorldEvolutionLog(
            world_id=world_id,
            agent_id=agent.id,
            evolution_type=activity_type,
            changes_made=data,
            impact_score=0.5
        )
        session.add(evolution)
        session.commit()
```

## Performance Optimization

### 1. Indexing Strategy

The database includes comprehensive indexes for:

- **User authentication**: Username, email, session tokens
- **World chunks**: Coordinate-based retrieval
- **Character positioning**: Spatial queries
- **Story branching**: JSONB field queries
- **AI activities**: Time-based filtering

### 2. Caching Layer

```python
import redis
from functools import lru_cache

redis_client = redis.Redis.from_url('redis://localhost:6379/0')

@lru_cache(maxsize=1000)
def get_world_settings(world_id: str):
    """Cache world settings with LRU"""
    cached = redis_client.get(f"world:{world_id}:settings")
    if cached:
        return json.loads(cached)
    
    # Fetch from database and cache
    with SessionLocal() as session:
        world = session.query(World).get(world_id)
        if world:
            redis_client.setex(f"world:{world_id}:settings", 3600, 
                             json.dumps(world.world_settings))
            return world.world_settings
    return {}
```

### 3. Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Backup and Recovery

### 1. Automated Backups

```bash
#!/bin/bash
# Daily backup script
pg_dump -h localhost -U game_user magic_adventure_game | gzip > backup_$(date +%Y%m%d).sql.gz

# Keep last 7 days
find /backup -name "backup_*.sql.gz" -mtime +7 -delete
```

### 2. Point-in-time Recovery

```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

### 3. World State Snapshots

```python
from database_setup import DatabaseSetup

# Create world snapshot
setup = DatabaseSetup()
snapshot_path = setup.create_world_snapshot(world_id)

# Restore from snapshot
setup.restore_world_snapshot(snapshot_path)
```

## Monitoring and Debugging

### 1. Query Performance

```python
# Enable SQL logging for debugging
engine = create_engine(DATABASE_URL, echo=True)

# Profile slow queries
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log queries taking > 100ms
        logger.warning(f"Slow query: {total:.3f}s - {statement[:100]}...")
```

### 2. Database Health Monitoring

```python
def check_database_health():
    with SessionLocal() as session:
        try:
            # Test connection
            session.execute(text("SELECT 1"))
            
            # Check table sizes
            result = session.execute(text("""
                SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
                FROM pg_tables WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(tablename::regclass) DESC
            """))
            
            return {"status": "healthy", "tables": result.fetchall()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
```

## Development Workflow

### 1. Schema Changes

```bash
# Create migration for schema changes
alembic revision --autogenerate -m "Add new feature"

# Review generated migration
# Edit if necessary

# Apply migration
alembic upgrade head
```

### 2. Testing

```python
import pytest
from database_models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine("postgresql://test:test@localhost/test_magic_game")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(engine)

def test_user_creation(test_db):
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    test_db.add(user)
    test_db.commit()
    
    assert user.id is not None
    assert user.check_password("password123")
```

### 3. Data Migration

```python
def migrate_old_data():
    """Migrate data from old format to new schema"""
    with SessionLocal() as session:
        # Migration logic here
        pass
```

## Security Considerations

### 1. Password Security

- Uses bcrypt for password hashing
- Configurable salt rounds
- Password strength validation

### 2. SQL Injection Prevention

- All queries use SQLAlchemy ORM
- Parameterized queries only
- Input validation with Pydantic

### 3. Data Access Control

```python
def check_user_permission(user_id: str, character_id: str) -> bool:
    """Verify user owns character"""
    with SessionLocal() as session:
        character = session.query(Character).get(character_id)
        return character and str(character.user_id) == user_id
```

## Troubleshooting

### Common Issues

1. **Connection timeouts**
   - Check connection pool settings
   - Monitor database connections
   - Verify network connectivity

2. **Slow queries**
   - Check query plans with EXPLAIN
   - Review indexes
   - Consider query optimization

3. **Memory usage**
   - Monitor session lifecycle
   - Check for query result caching
   - Review connection pool size

### Performance Tuning

```sql
-- Analyze table statistics
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats WHERE schemaname = 'public';

-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC;
```

## Contributing

When contributing to the database system:

1. **Always create migrations** for schema changes
2. **Update documentation** for new models or relationships
3. **Add tests** for new database functionality
4. **Consider performance impact** of new queries
5. **Follow naming conventions** for tables and columns

## Support

For database-related issues:

1. Check the logs: `tail -f /var/log/postgresql/postgresql.log`
2. Monitor performance: `python -c "from database_models import check_database_health; print(check_database_health())"`
3. Review slow queries with SQL profiling tools
4. Check the GitHub issues for known problems

The database system is designed to scale with your game's growth while maintaining performance and data integrity.