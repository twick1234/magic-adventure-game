#!/usr/bin/env python3
"""
🗄️ Magic Adventure Game - Database Setup and Sample Data

This script provides utilities for setting up the database, running migrations,
and populating it with comprehensive sample data for development and testing.

Usage:
    python database_setup.py --create-tables    # Create all tables
    python database_setup.py --sample-data      # Insert sample data
    python database_setup.py --full-setup       # Create tables and insert sample data
    python database_setup.py --reset-db         # Drop and recreate everything
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import uuid
import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_models import (
    Base, User, World, WorldChunk, WorldStructure, Character, CharacterRelationship,
    NPC, Story, StoryChoice, StoryEvolution, Quest, QuestProgress, AIAgent,
    AIAgentActivity, WorldEvent, WorldEvolutionLog, UserAchievement,
    InventoryItem, CraftingRecipe, get_db
)


# Database configuration
DATABASE_URL = "postgresql://username:password@localhost/magic_adventure_game"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseSetup:
    """Handles database initialization and sample data creation"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.sample_world_id = None
        self.sample_user_ids = []
        self.sample_character_ids = []
        self.sample_agent_ids = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def create_tables(self):
        """Create all database tables"""
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    
    def drop_tables(self):
        """Drop all database tables"""
        print("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
    
    def create_sample_users(self) -> List[User]:
        """Create sample users for testing"""
        print("Creating sample users...")
        
        users_data = [
            {
                'username': 'wizard_adventurer',
                'email': 'wizard@magic-game.com',
                'display_name': 'Gandalf the Code',
                'profile_data': {
                    'preferred_class': 'mage',
                    'play_style': 'explorer',
                    'achievements_count': 15,
                    'favorite_spells': ['fireball', 'teleport', 'heal'],
                    'timezone': 'UTC'
                }
            },
            {
                'username': 'brave_knight',
                'email': 'knight@magic-game.com',
                'display_name': 'Sir Codealot',
                'profile_data': {
                    'preferred_class': 'warrior',
                    'play_style': 'combat',
                    'achievements_count': 8,
                    'favorite_weapons': ['sword', 'shield', 'lance'],
                    'guild': 'Knights of the Round Table'
                }
            },
            {
                'username': 'sneaky_rogue',
                'email': 'rogue@magic-game.com',
                'display_name': 'Shadow Walker',
                'profile_data': {
                    'preferred_class': 'rogue',
                    'play_style': 'stealth',
                    'achievements_count': 12,
                    'skills': ['lockpicking', 'stealth', 'backstab'],
                    'reputation': 'neutral'
                }
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                profile_data=user_data['profile_data']
            )
            user.set_password('test_password_123')  # Same password for all test users
            self.session.add(user)
            users.append(user)
        
        self.session.commit()
        self.sample_user_ids = [str(user.id) for user in users]
        print(f"✅ Created {len(users)} sample users")
        return users
    
    def create_sample_world(self) -> World:
        """Create a sample game world"""
        print("Creating sample world...")
        
        world = World(
            name="Mystical Realms",
            description="A vast world of magic, mystery, and endless adventure where AI agents weave stories that evolve with player choices.",
            world_settings={
                'difficulty': 'normal',
                'pvp_enabled': False,
                'seasonal_events': True,
                'ai_evolution_rate': 'daily',
                'max_players': 100,
                'world_size': 'infinite',
                'biomes': ['forest', 'mountains', 'desert', 'ocean', 'underground'],
                'magic_level': 'high',
                'technology_level': 'medieval_fantasy'
            }
        )
        
        self.session.add(world)
        self.session.commit()
        self.sample_world_id = str(world.id)
        print(f"✅ Created sample world: {world.name}")
        return world
    
    def create_sample_chunks(self, world: World) -> List[WorldChunk]:
        """Create sample world chunks around spawn point"""
        print("Creating sample world chunks...")
        
        chunks = []
        # Create a 5x5 grid of chunks around spawn (0,0,0)
        for x in range(-2, 3):
            for z in range(-2, 3):
                # Generate different terrain based on position
                if x == 0 and z == 0:
                    # Spawn chunk - village
                    block_data = {
                        'blocks': {
                            '8,1,8': {'type': 'cobblestone', 'structure': 'village_center'},
                            '7,1,8': {'type': 'wood_planks', 'structure': 'house'},
                            '9,1,8': {'type': 'wood_planks', 'structure': 'house'},
                            '8,1,7': {'type': 'water', 'structure': 'well'},
                            '8,1,9': {'type': 'dirt', 'planted': 'wheat'}
                        },
                        'biome': 'village',
                        'structures': ['village_center', 'houses', 'well', 'farm']
                    }
                elif abs(x) + abs(z) == 1:
                    # Adjacent chunks - forest
                    block_data = {
                        'blocks': {
                            f'{i},{j},{k}': {'type': 'oak_log' if (i+k) % 3 == 0 else 'grass'}
                            for i in range(0, 16, 2) for j in range(1, 4) for k in range(0, 16, 2)
                        },
                        'biome': 'forest',
                        'structures': ['trees', 'forest_path']
                    }
                else:
                    # Outer chunks - mountains or plains
                    biome = 'mountains' if abs(x) == 2 or abs(z) == 2 else 'plains'
                    block_data = {
                        'blocks': {
                            f'{i},1,{k}': {'type': 'stone' if biome == 'mountains' else 'grass'}
                            for i in range(0, 16, 4) for k in range(0, 16, 4)
                        },
                        'biome': biome,
                        'structures': ['natural_formation']
                    }
                
                chunk = WorldChunk(
                    world_id=world.id,
                    chunk_x=x,
                    chunk_y=0,
                    chunk_z=z,
                    block_data=block_data,
                    metadata={
                        'generated_by': 'sample_data_script',
                        'generation_algorithm': 'simple_biome',
                        'last_player_visit': None
                    }
                )
                chunks.append(chunk)
                self.session.add(chunk)
        
        self.session.commit()
        print(f"✅ Created {len(chunks)} world chunks")
        return chunks
    
    def create_sample_characters(self, users: List[User], world: World) -> List[Character]:
        """Create sample characters for users"""
        print("Creating sample characters...")
        
        character_configs = [
            {
                'name': 'Elderan the Wise',
                'character_class': 'mage',
                'stats': {
                    'strength': 12, 'intelligence': 18, 'dexterity': 14,
                    'constitution': 13, 'wisdom': 16, 'charisma': 15,
                    'health': 100, 'mana': 150, 'stamina': 80
                },
                'position': {'x': 128, 'y': 64, 'z': 128},  # Spawn area
                'skills': {
                    'magic': 85, 'alchemy': 70, 'lore': 90,
                    'crafting': 45, 'combat': 30
                }
            },
            {
                'name': 'Sir Valiant',
                'character_class': 'warrior',
                'stats': {
                    'strength': 18, 'intelligence': 12, 'dexterity': 14,
                    'constitution': 16, 'wisdom': 13, 'charisma': 14,
                    'health': 150, 'mana': 50, 'stamina': 120
                },
                'position': {'x': 120, 'y': 64, 'z': 135},
                'skills': {
                    'combat': 90, 'smithing': 60, 'leadership': 70,
                    'crafting': 40, 'magic': 15
                }
            },
            {
                'name': 'Luna Shadowstep',
                'character_class': 'rogue',
                'stats': {
                    'strength': 14, 'intelligence': 15, 'dexterity': 18,
                    'constitution': 12, 'wisdom': 16, 'charisma': 13,
                    'health': 90, 'mana': 70, 'stamina': 110
                },
                'position': {'x': 135, 'y': 64, 'z': 120},
                'skills': {
                    'stealth': 95, 'lockpicking': 85, 'archery': 80,
                    'crafting': 55, 'magic': 25
                }
            }
        ]
        
        characters = []
        for i, (user, config) in enumerate(zip(users, character_configs)):
            character = Character(
                user_id=user.id,
                world_id=world.id,
                name=config['name'],
                character_class=config['character_class'],
                stats=config['stats'],
                position=config['position'],
                skills=config['skills'],
                level=5 + i,  # Different starting levels
                experience=1000 * (5 + i)
            )
            characters.append(character)
            self.session.add(character)
        
        self.session.commit()
        self.sample_character_ids = [str(char.id) for char in characters]
        print(f"✅ Created {len(characters)} characters")
        return characters
    
    def create_sample_npcs(self, world: World) -> List[NPC]:
        """Create sample NPCs with AI personalities"""
        print("Creating sample NPCs...")
        
        npc_configs = [
            {
                'name': 'Merchant Goldweaver',
                'npc_type': 'merchant',
                'personality': {
                    'traits': ['greedy', 'cunning', 'friendly'],
                    'mood': 'optimistic',
                    'speech_pattern': 'eloquent',
                    'interests': ['gold', 'rare_items', 'trade_routes'],
                    'relationships': {'players': 'friendly', 'guards': 'neutral'}
                },
                'position': {'x': 125, 'y': 64, 'z': 130},
                'dialogue_tree': {
                    'greetings': ['Welcome to my shop!', 'Looking for something special?'],
                    'trades': ['I have the finest wares!', 'Gold for goods, fair and square!'],
                    'gossip': ['Have you heard about the dragon sighting?']
                }
            },
            {
                'name': 'Guard Captain Ironhelm',
                'npc_type': 'guard',
                'personality': {
                    'traits': ['dutiful', 'stern', 'protective'],
                    'mood': 'serious',
                    'speech_pattern': 'formal',
                    'interests': ['law_and_order', 'village_safety', 'combat_training'],
                    'relationships': {'players': 'cautious', 'merchants': 'protective'}
                },
                'position': {'x': 130, 'y': 64, 'z': 125},
                'dialogue_tree': {
                    'greetings': ['State your business.', 'Keep the peace, traveler.'],
                    'quests': ['Strange things happening lately...'],
                    'warnings': ['Stay out of trouble.']
                }
            },
            {
                'name': 'Sage Moonwhisper',
                'npc_type': 'sage',
                'personality': {
                    'traits': ['wise', 'mysterious', 'patient'],
                    'mood': 'contemplative',
                    'speech_pattern': 'cryptic',
                    'interests': ['ancient_knowledge', 'magic', 'prophecies'],
                    'relationships': {'players': 'helpful', 'other_sages': 'respectful'}
                },
                'position': {'x': 132, 'y': 65, 'z': 132},
                'dialogue_tree': {
                    'greetings': ['The threads of fate bring you here.', 'Seek ye wisdom?'],
                    'lore': ['The old magic stirs again...'],
                    'prophecy': ['Dark times approach, but hope remains.']
                }
            }
        ]
        
        npcs = []
        for config in npc_configs:
            npc = NPC(
                world_id=world.id,
                name=config['name'],
                npc_type=config['npc_type'],
                personality=config['personality'],
                position=config['position'],
                dialogue_tree=config['dialogue_tree'],
                ai_memory={
                    'interactions': [],
                    'mood_history': [],
                    'learned_facts': [],
                    'relationships': {}
                }
            )
            npcs.append(npc)
            self.session.add(npc)
        
        self.session.commit()
        print(f"✅ Created {len(npcs)} NPCs")
        return npcs
    
    def create_sample_stories(self, world: World) -> List[Story]:
        """Create sample story arcs"""
        print("Creating sample stories...")
        
        story_configs = [
            {
                'title': 'The Awakening Dragon',
                'description': 'Ancient magic stirs as a dragon awakens in the nearby mountains, threatening the peaceful village.',
                'story_type': 'main',
                'narrative_threads': {
                    'main_plot': {
                        'act1': 'Strange tremors shake the village',
                        'act2': 'Discovery of dragon signs',
                        'act3': 'Confrontation or negotiation with dragon'
                    },
                    'subplots': {
                        'merchant_fear': 'Merchant loses trade routes',
                        'guard_preparation': 'Guards prepare defenses',
                        'sage_knowledge': 'Sage reveals ancient dragon lore'
                    }
                },
                'branching_data': {
                    'branches': {
                        'peaceful_resolution': {'probability': 0.3, 'requirements': ['high_charisma']},
                        'combat_victory': {'probability': 0.4, 'requirements': ['high_combat']},
                        'dragon_alliance': {'probability': 0.2, 'requirements': ['magical_knowledge']},
                        'village_evacuation': {'probability': 0.1, 'requirements': ['leadership']}
                    }
                },
                'priority': 10
            },
            {
                'title': 'The Mysterious Merchant',
                'description': 'A strange merchant arrives with impossible goods and cryptic warnings.',
                'story_type': 'side',
                'narrative_threads': {
                    'mystery': {
                        'clue1': 'Merchant sells items that shouldn\'t exist',
                        'clue2': 'Warnings about coming darkness',
                        'clue3': 'Connection to ancient prophecies'
                    }
                },
                'branching_data': {
                    'branches': {
                        'trust_merchant': {'probability': 0.5, 'requirements': ['wisdom']},
                        'investigate_suspicion': {'probability': 0.3, 'requirements': ['intelligence']},
                        'ignore_merchant': {'probability': 0.2, 'requirements': []}
                    }
                },
                'priority': 5
            }
        ]
        
        stories = []
        for config in story_configs:
            story = Story(
                world_id=world.id,
                title=config['title'],
                description=config['description'],
                story_type=config['story_type'],
                narrative_threads=config['narrative_threads'],
                branching_data=config['branching_data'],
                priority=config['priority']
            )
            stories.append(story)
            self.session.add(story)
        
        self.session.commit()
        print(f"✅ Created {len(stories)} stories")
        return stories
    
    def create_sample_ai_agents(self) -> List[AIAgent]:
        """Create sample AI agents"""
        print("Creating sample AI agents...")
        
        agent_configs = [
            {
                'agent_name': 'story_weaver',
                'agent_type': 'narrative_generator',
                'configuration': {
                    'creativity_level': 0.8,
                    'story_coherence': 0.9,
                    'response_length': 'medium',
                    'preferred_genres': ['fantasy', 'adventure', 'mystery'],
                    'update_frequency': 'daily',
                    'adaptation_rate': 0.7
                }
            },
            {
                'agent_name': 'world_sculptor',
                'agent_type': 'environment_builder',
                'configuration': {
                    'terrain_complexity': 0.7,
                    'structure_frequency': 0.5,
                    'biome_diversity': 0.8,
                    'seasonal_adaptation': True,
                    'player_influence': 0.6
                }
            },
            {
                'agent_name': 'character_director',
                'agent_type': 'npc_controller',
                'configuration': {
                    'personality_consistency': 0.9,
                    'memory_retention': 0.8,
                    'social_awareness': 0.7,
                    'emotional_range': 0.6
                }
            },
            {
                'agent_name': 'quest_master',
                'agent_type': 'quest_generator',
                'configuration': {
                    'difficulty_scaling': True,
                    'reward_balance': 0.8,
                    'narrative_integration': 0.9,
                    'emergent_content': 0.7
                }
            }
        ]
        
        agents = []
        for config in agent_configs:
            agent = AIAgent(
                agent_name=config['agent_name'],
                agent_type=config['agent_type'],
                configuration=config['configuration'],
                memory_state={
                    'initialization_time': datetime.now(timezone.utc).isoformat(),
                    'total_activations': 0,
                    'last_major_action': None,
                    'learned_patterns': []
                }
            )
            agents.append(agent)
            self.session.add(agent)
        
        self.session.commit()
        self.sample_agent_ids = [str(agent.id) for agent in agents]
        print(f"✅ Created {len(agents)} AI agents")
        return agents
    
    def create_sample_achievements(self, users: List[User]):
        """Create sample achievements for users"""
        print("Creating sample achievements...")
        
        achievement_configs = [
            {
                'achievement_type': 'exploration',
                'title': 'World Walker',
                'description': 'Visited 10 different biomes',
                'points_awarded': 50
            },
            {
                'achievement_type': 'combat',
                'title': 'Dragon Slayer',
                'description': 'Defeated a mighty dragon',
                'points_awarded': 100
            },
            {
                'achievement_type': 'social',
                'title': 'Friend of All',
                'description': 'Made friends with 5 different NPCs',
                'points_awarded': 75
            }
        ]
        
        achievements = []
        for user in users:
            for i, config in enumerate(achievement_configs):
                if i < len(users):  # Give different achievements to different users
                    achievement = UserAchievement(
                        user_id=user.id,
                        achievement_type=config['achievement_type'],
                        title=config['title'],
                        description=config['description'],
                        achievement_data={
                            'earned_date': datetime.now(timezone.utc).isoformat(),
                            'difficulty': 'normal',
                            'category': config['achievement_type']
                        },
                        points_awarded=config['points_awarded']
                    )
                    achievements.append(achievement)
                    self.session.add(achievement)
        
        self.session.commit()
        print(f"✅ Created {len(achievements)} achievements")
        return achievements
    
    def create_sample_recipes(self):
        """Create sample crafting recipes"""
        print("Creating sample crafting recipes...")
        
        recipe_configs = [
            {
                'recipe_name': 'Iron Sword',
                'ingredients': {'iron_ingot': 2, 'wood_stick': 1},
                'result_item': {
                    'name': 'Iron Sword',
                    'type': 'weapon',
                    'damage': 25,
                    'durability': 100,
                    'rarity': 'common'
                },
                'crafting_level_required': 15
            },
            {
                'recipe_name': 'Health Potion',
                'ingredients': {'red_herb': 3, 'spring_water': 1, 'glass_bottle': 1},
                'result_item': {
                    'name': 'Health Potion',
                    'type': 'consumable',
                    'effect': 'heal',
                    'potency': 50,
                    'rarity': 'common'
                },
                'crafting_level_required': 5
            },
            {
                'recipe_name': 'Enchanted Cloak',
                'ingredients': {'silk_fabric': 4, 'magic_thread': 2, 'sapphire': 1},
                'result_item': {
                    'name': 'Enchanted Cloak',
                    'type': 'armor',
                    'defense': 15,
                    'magic_resistance': 20,
                    'rarity': 'rare'
                },
                'crafting_level_required': 40
            }
        ]
        
        recipes = []
        for config in recipe_configs:
            recipe = CraftingRecipe(
                recipe_name=config['recipe_name'],
                ingredients=config['ingredients'],
                result_item=config['result_item'],
                crafting_level_required=config['crafting_level_required']
            )
            recipes.append(recipe)
            self.session.add(recipe)
        
        self.session.commit()
        print(f"✅ Created {len(recipes)} crafting recipes")
        return recipes
    
    def full_setup(self):
        """Complete database setup with sample data"""
        print("🚀 Starting full database setup...")
        
        # Create tables
        self.create_tables()
        
        # Create sample data in proper order
        users = self.create_sample_users()
        world = self.create_sample_world()
        chunks = self.create_sample_chunks(world)
        characters = self.create_sample_characters(users, world)
        npcs = self.create_sample_npcs(world)
        stories = self.create_sample_stories(world)
        agents = self.create_sample_ai_agents()
        achievements = self.create_sample_achievements(users)
        recipes = self.create_sample_recipes()
        
        print("\n🎉 Database setup complete!")
        print(f"📊 Summary:")
        print(f"   • {len(users)} Users created")
        print(f"   • 1 World created with {len(chunks)} chunks")
        print(f"   • {len(characters)} Characters created")
        print(f"   • {len(npcs)} NPCs created")
        print(f"   • {len(stories)} Stories created")
        print(f"   • {len(agents)} AI Agents created")
        print(f"   • {len(achievements)} Achievements created")
        print(f"   • {len(recipes)} Crafting Recipes created")
        
        return {
            'users': users,
            'world': world,
            'characters': characters,
            'npcs': npcs,
            'stories': stories,
            'agents': agents
        }


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Magic Adventure Game Database Setup')
    parser.add_argument('--create-tables', action='store_true',
                       help='Create all database tables')
    parser.add_argument('--sample-data', action='store_true',
                       help='Insert comprehensive sample data')
    parser.add_argument('--full-setup', action='store_true',
                       help='Create tables and insert sample data')
    parser.add_argument('--reset-db', action='store_true',
                       help='Drop and recreate everything (DESTRUCTIVE)')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    with DatabaseSetup() as db_setup:
        try:
            if args.reset_db:
                print("⚠️  WARNING: This will delete ALL data!")
                confirm = input("Type 'YES' to confirm: ")
                if confirm == 'YES':
                    db_setup.drop_tables()
                    db_setup.full_setup()
                else:
                    print("Operation cancelled.")
                    return
            
            elif args.full_setup:
                db_setup.full_setup()
            
            elif args.create_tables:
                db_setup.create_tables()
            
            elif args.sample_data:
                print("Creating sample data (assumes tables exist)...")
                users = db_setup.create_sample_users()
                world = db_setup.create_sample_world()
                db_setup.create_sample_chunks(world)
                db_setup.create_sample_characters(users, world)
                db_setup.create_sample_npcs(world)
                db_setup.create_sample_stories(world)
                db_setup.create_sample_ai_agents()
                db_setup.create_sample_achievements(users)
                db_setup.create_sample_recipes()
                print("✅ Sample data creation complete!")
        
        except Exception as e:
            print(f"❌ Error during database setup: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()