#!/usr/bin/env python3
"""
🏰 Magic Adventure Game - Concurrent AI Agents System
**Version:** v1.0.0
**Created:** September 4, 2025 - 2:30 PM UTC
**Updated:** September 4, 2025 - 2:30 PM UTC

This system manages 8+ concurrent AI agents that continuously evolve the game world,
generate content, manage balance, and create engaging experiences for players.
Each agent runs independently and communicates through a central orchestrator.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from crewai import Agent, Task, Crew, Process
import psycopg2
import redis
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class AgentMetrics:
    tasks_completed: int = 0
    errors_encountered: int = 0
    last_activity: Optional[datetime] = None
    processing_time_avg: float = 0.0
    success_rate: float = 100.0

class ConcurrentAIAgentSystem:
    """
    Manages 8+ concurrent AI agents that continuously evolve the game world
    """
    
    def __init__(self, database_url: str, redis_url: str, max_workers: int = 8):
        self.database_url = database_url
        self.redis_url = redis_url
        self.max_workers = max_workers
        
        # Initialize connections
        self.engine = create_engine(database_url, pool_size=20, max_overflow=30)
        self.redis_client = redis.from_url(redis_url)
        
        # Agent tracking
        self.agents: Dict[str, Dict] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Coordination
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.shutdown_event = asyncio.Event()
        
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all AI agents with their configurations"""
        
        # 1. Terrain Sculptor Agent - Modifies landscapes and natural features
        self.agents['terrain_sculptor'] = {
            'agent': Agent(
                role="Master Terrain Sculptor",
                goal="Continuously evolve and shape the natural world with beautiful landscapes",
                backstory="You are an ancient earth spirit with millennia of experience shaping worlds. You love creating diverse biomes, dramatic mountain ranges, mysterious caves, and flowing rivers that tell stories of geological time.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 300,  # 5 minutes
            'priority': 1,
            'status': AgentStatus.IDLE
        }
        
        # 2. Structure Architect Agent - Builds ruins, dungeons, settlements
        self.agents['structure_architect'] = {
            'agent': Agent(
                role="Legendary Structure Architect",
                goal="Design and construct amazing buildings, ruins, and architectural wonders",
                backstory="You are a master builder who has designed countless castles, temples, and mysterious ruins. You understand how structures should integrate with the landscape and create atmospheric environments.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 600,  # 10 minutes
            'priority': 2,
            'status': AgentStatus.IDLE
        }
        
        # 3. Ecosystem Manager Agent - Manages wildlife and natural systems
        self.agents['ecosystem_manager'] = {
            'agent': Agent(
                role="Wise Ecosystem Guardian",
                goal="Maintain balanced and thriving ecosystems with diverse wildlife",
                backstory="You are a druid-like entity who understands the delicate balance of nature. You manage animal populations, plant growth, resource regeneration, and seasonal cycles.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 180,  # 3 minutes
            'priority': 1,
            'status': AgentStatus.IDLE
        }
        
        # 4. Weather Controller Agent - Dynamic weather and seasonal changes
        self.agents['weather_controller'] = {
            'agent': Agent(
                role="Elemental Weather Master",
                goal="Create dynamic weather patterns and beautiful seasonal changes",
                backstory="You control the winds, rain, snow, and sunshine. You understand how weather affects the world and its inhabitants, creating immersive atmospheric conditions.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 120,  # 2 minutes
            'priority': 3,
            'status': AgentStatus.IDLE
        }
        
        # 5. Story Weaver Agent - Creates dynamic storylines and quests
        self.agents['story_weaver'] = {
            'agent': Agent(
                role="Grand Story Weaver",
                goal="Craft compelling narratives that adapt to player choices and world events",
                backstory="You are an ancient storyteller with infinite creativity. You weave tales that respond to player actions, create meaningful choices, and develop rich lore for the world.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 240,  # 4 minutes
            'priority': 1,
            'status': AgentStatus.IDLE
        }
        
        # 6. Quest Master Agent - Generates and manages dynamic quests
        self.agents['quest_master'] = {
            'agent': Agent(
                role="Supreme Quest Master",
                goal="Design engaging quests that challenge and reward players appropriately",
                backstory="You understand what makes quests fun and meaningful. You create adventures that scale with player abilities and create memorable experiences.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 480,  # 8 minutes
            'priority': 2,
            'status': AgentStatus.IDLE
        }
        
        # 7. Balance Guardian Agent - Monitors and adjusts game balance
        self.agents['balance_guardian'] = {
            'agent': Agent(
                role="Eternal Balance Guardian",
                goal="Maintain perfect game balance and ensure fair, fun gameplay",
                backstory="You see the mathematical beauty in balanced systems. You monitor player progression, economic health, and gameplay metrics to maintain harmony.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 900,  # 15 minutes
            'priority': 1,
            'status': AgentStatus.IDLE
        }
        
        # 8. Event Coordinator Agent - Orchestrates world events
        self.agents['event_coordinator'] = {
            'agent': Agent(
                role="Master Event Coordinator",
                goal="Create memorable world events that bring the community together",
                backstory="You love organizing celebrations, festivals, and special events. You understand timing and community dynamics to create moments of shared wonder.",
                verbose=True,
                allow_delegation=False
            ),
            'interval': 1800,  # 30 minutes
            'priority': 2,
            'status': AgentStatus.IDLE
        }
        
        # Initialize metrics for all agents
        for agent_name in self.agents:
            self.agent_metrics[agent_name] = AgentMetrics()

    async def start_agent_system(self):
        """Start all AI agents and begin continuous operation"""
        logger.info("🚀 Starting Concurrent AI Agent System")
        logger.info(f"📊 Total Agents: {len(self.agents)}")
        
        # Start each agent in its own async task
        for agent_name, agent_config in self.agents.items():
            task = asyncio.create_task(self._run_agent_loop(agent_name, agent_config))
            self.running_tasks[agent_name] = task
            logger.info(f"✅ Started {agent_name} (interval: {agent_config['interval']}s)")
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self._monitor_agents())
        self.running_tasks['monitor'] = monitor_task
        
        # Start metrics reporting
        metrics_task = asyncio.create_task(self._report_metrics())
        self.running_tasks['metrics'] = metrics_task
        
        logger.info("🎮 AI Agent System is now running!")
        
        # Wait until shutdown
        await self.shutdown_event.wait()
        
        # Cleanup
        await self._shutdown_agents()

    async def _run_agent_loop(self, agent_name: str, agent_config: Dict):
        """Run an individual agent in its own loop"""
        interval = agent_config['interval']
        
        while not self.shutdown_event.is_set():
            try:
                # Mark agent as working
                agent_config['status'] = AgentStatus.WORKING
                self.agent_metrics[agent_name].last_activity = datetime.now()
                
                start_time = time.time()
                
                # Execute agent task
                await self._execute_agent_task(agent_name, agent_config)
                
                # Update metrics
                processing_time = time.time() - start_time
                metrics = self.agent_metrics[agent_name]
                metrics.tasks_completed += 1
                metrics.processing_time_avg = (
                    (metrics.processing_time_avg * (metrics.tasks_completed - 1) + processing_time) /
                    metrics.tasks_completed
                )
                metrics.success_rate = (
                    (metrics.tasks_completed - metrics.errors_encountered) /
                    metrics.tasks_completed * 100
                )
                
                # Mark agent as idle
                agent_config['status'] = AgentStatus.IDLE
                
                logger.info(f"✨ {agent_name} completed task in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Error in {agent_name}: {str(e)}")
                agent_config['status'] = AgentStatus.ERROR
                self.agent_metrics[agent_name].errors_encountered += 1
                
                # Wait before retrying on error
                await asyncio.sleep(60)
            
            # Wait for next interval
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=interval)
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Normal interval timeout, continue loop

    async def _execute_agent_task(self, agent_name: str, agent_config: Dict):
        """Execute a specific task for an agent"""
        agent = agent_config['agent']
        
        # Create tasks based on agent type
        if agent_name == 'terrain_sculptor':
            task = Task(
                description="Analyze the current world state and make 1-3 terrain modifications. Focus on adding natural beauty, creating interesting geographical features, or improving existing landscapes. Consider biome diversity and player exploration paths.",
                expected_output="A detailed description of terrain changes made, including coordinates, biome types, and reasoning for the modifications.",
                agent=agent
            )
        
        elif agent_name == 'structure_architect':
            task = Task(
                description="Design and place 1-2 new structures in the world. This could include ruins, temples, towers, bridges, or other architectural features. Consider the surrounding terrain and existing structures.",
                expected_output="Detailed architectural plans with coordinates, materials, and the story/purpose behind each structure.",
                agent=agent
            )
        
        elif agent_name == 'ecosystem_manager':
            task = Task(
                description="Monitor and adjust wildlife populations, resource spawning, and natural growth. Ensure balanced ecosystems and address any imbalances. Consider seasonal changes and player impact.",
                expected_output="A report on ecosystem health, population adjustments made, and resource regeneration updates.",
                agent=agent
            )
        
        elif agent_name == 'weather_controller':
            task = Task(
                description="Update weather patterns across different regions. Create atmospheric conditions that enhance gameplay and immersion. Consider seasonal progression and regional climate differences.",
                expected_output="Weather update report with current conditions, forecasts, and any special weather events planned.",
                agent=agent
            )
        
        elif agent_name == 'story_weaver':
            task = Task(
                description="Develop new story threads or advance existing ones based on recent player actions. Create meaningful narrative connections and set up interesting choice points for players.",
                expected_output="Story progression report with new plot threads, character developments, and player choice opportunities.",
                agent=agent
            )
        
        elif agent_name == 'quest_master':
            task = Task(
                description="Generate 2-3 new dynamic quests appropriate for current player levels and world state. Ensure variety in quest types and meaningful rewards.",
                expected_output="Quest specifications including objectives, requirements, rewards, and narrative context.",
                agent=agent
            )
        
        elif agent_name == 'balance_guardian':
            task = Task(
                description="Analyze game balance metrics including player progression rates, economic health, combat balance, and resource distribution. Recommend adjustments if needed.",
                expected_output="Balance analysis report with key metrics, identified issues, and recommended adjustments.",
                agent=agent
            )
        
        elif agent_name == 'event_coordinator':
            task = Task(
                description="Plan and potentially initiate world events, festivals, or special occasions. Consider community engagement and seasonal appropriateness.",
                expected_output="Event planning report with upcoming events, community activities, and special celebrations.",
                agent=agent
            )
        
        # Execute the task
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        # Simulate AI execution (in real implementation, this would call actual CrewAI)
        result = await self._simulate_agent_execution(agent_name, task)
        
        # Store result in database
        await self._store_agent_result(agent_name, result)
        
        return result

    async def _simulate_agent_execution(self, agent_name: str, task: Task) -> Dict[str, Any]:
        """Simulate agent execution (replace with actual CrewAI execution)"""
        
        # Simulate processing time
        await asyncio.sleep(1.0 + (hash(agent_name) % 3))
        
        # Generate simulated results based on agent type
        world_changes = []
        
        if agent_name == 'terrain_sculptor':
            world_changes = [
                {
                    'type': 'terrain_modification',
                    'coordinates': {'x': 1000 + (hash(agent_name) % 500), 'y': 64, 'z': 1000 + (hash(agent_name) % 500)},
                    'changes': ['added_river', 'created_valley', 'placed_trees'],
                    'biome': 'temperate_forest'
                }
            ]
        
        elif agent_name == 'structure_architect':
            world_changes = [
                {
                    'type': 'structure_creation',
                    'coordinates': {'x': 500 + (hash(agent_name) % 1000), 'y': 70, 'z': 500 + (hash(agent_name) % 1000)},
                    'structure_type': 'ancient_ruins',
                    'materials': ['weathered_stone', 'moss_covered_blocks'],
                    'story': 'Ruins of an ancient watchtower'
                }
            ]
        
        elif agent_name == 'ecosystem_manager':
            world_changes = [
                {
                    'type': 'ecosystem_update',
                    'region': 'forest_sector_3',
                    'changes': ['increased_wildlife', 'regenerated_resources'],
                    'balance_score': 8.5
                }
            ]
        
        elif agent_name == 'story_weaver':
            world_changes = [
                {
                    'type': 'story_development',
                    'thread_id': f'story_{hash(agent_name) % 100}',
                    'developments': ['character_introduction', 'plot_twist'],
                    'player_choice_points': 3
                }
            ]
        
        # Common result structure
        result = {
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat(),
            'world_changes': world_changes,
            'success': True,
            'processing_time': 2.5,
            'impact_score': 7.8
        }
        
        return result

    async def _store_agent_result(self, agent_name: str, result: Dict[str, Any]):
        """Store agent execution results in the database"""
        try:
            with self.engine.connect() as conn:
                # Store in world_evolution_log table
                query = text("""
                    INSERT INTO world_evolution_log 
                    (world_id, agent_id, evolution_type, changes_made, reasoning, applied_at, is_active)
                    VALUES (1, (SELECT id FROM ai_agents WHERE agent_name = :agent_name), 
                           :evolution_type, :changes_made, :reasoning, NOW(), true)
                """)
                
                conn.execute(query, {
                    'agent_name': agent_name,
                    'evolution_type': result.get('world_changes', [{}])[0].get('type', 'general_update'),
                    'changes_made': json.dumps(result['world_changes']),
                    'reasoning': f"Automated {agent_name} evolution task"
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store result for {agent_name}: {str(e)}")
            
        # Also cache in Redis for quick access
        try:
            cache_key = f"agent_result:{agent_name}:{int(time.time())}"
            self.redis_client.setex(cache_key, 3600, json.dumps(result))  # 1-hour expiry
        except Exception as e:
            logger.error(f"Failed to cache result for {agent_name}: {str(e)}")

    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while not self.shutdown_event.is_set():
            try:
                # Check agent status
                healthy_agents = 0
                total_agents = len(self.agents)
                
                for agent_name, agent_config in self.agents.items():
                    if agent_config['status'] in [AgentStatus.IDLE, AgentStatus.WORKING]:
                        healthy_agents += 1
                    elif agent_config['status'] == AgentStatus.ERROR:
                        logger.warning(f"⚠️ Agent {agent_name} is in error state")
                
                health_percentage = (healthy_agents / total_agents) * 100
                logger.info(f"🏥 System Health: {health_percentage:.1f}% ({healthy_agents}/{total_agents} agents healthy)")
                
                # Store health metrics
                self.redis_client.setex("system:health", 300, json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'healthy_agents': healthy_agents,
                    'total_agents': total_agents,
                    'health_percentage': health_percentage
                }))
                
            except Exception as e:
                logger.error(f"Error in agent monitoring: {str(e)}")
            
            await asyncio.sleep(60)  # Check every minute

    async def _report_metrics(self):
        """Report detailed metrics every 5 minutes"""
        while not self.shutdown_event.is_set():
            try:
                logger.info("📊 === AGENT SYSTEM METRICS ===")
                
                for agent_name, metrics in self.agent_metrics.items():
                    logger.info(
                        f"🤖 {agent_name}: "
                        f"Tasks: {metrics.tasks_completed}, "
                        f"Errors: {metrics.errors_encountered}, "
                        f"Success Rate: {metrics.success_rate:.1f}%, "
                        f"Avg Time: {metrics.processing_time_avg:.2f}s"
                    )
                
                # Store aggregated metrics
                total_tasks = sum(m.tasks_completed for m in self.agent_metrics.values())
                total_errors = sum(m.errors_encountered for m in self.agent_metrics.values())
                
                logger.info(f"🌍 WORLD EVOLUTION: {total_tasks} total changes made")
                logger.info(f"⚡ SYSTEM STATUS: {total_errors} errors encountered")
                
            except Exception as e:
                logger.error(f"Error reporting metrics: {str(e)}")
            
            await asyncio.sleep(300)  # Report every 5 minutes

    async def _shutdown_agents(self):
        """Gracefully shutdown all agents"""
        logger.info("🛑 Shutting down AI Agent System...")
        
        # Cancel all running tasks
        for task_name, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"✅ Cancelled {task_name} task")
        
        # Close connections
        self.executor.shutdown(wait=True)
        self.redis_client.close()
        
        logger.info("✅ AI Agent System shutdown complete")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        status = {}
        for agent_name, agent_config in self.agents.items():
            metrics = self.agent_metrics[agent_name]
            status[agent_name] = {
                'status': agent_config['status'].value,
                'interval': agent_config['interval'],
                'tasks_completed': metrics.tasks_completed,
                'success_rate': metrics.success_rate,
                'last_activity': metrics.last_activity.isoformat() if metrics.last_activity else None
            }
        return status

# CLI Interface
async def main():
    """Main entry point for the concurrent AI agent system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Magic Adventure Game - AI Agent System")
    parser.add_argument("--database-url", default="postgresql://user:pass@localhost:5432/magic_adventure")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--workers", type=int, default=8)
    
    args = parser.parse_args()
    
    # Initialize the system
    agent_system = ConcurrentAIAgentSystem(
        database_url=args.database_url,
        redis_url=args.redis_url,
        max_workers=args.workers
    )
    
    try:
        # Start the system
        await agent_system.start_agent_system()
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
        agent_system.shutdown_event.set()

if __name__ == "__main__":
    print("🏰 Magic Adventure Game - Concurrent AI Agents System v1.0.0")
    print("🚀 Starting 8 concurrent AI agents for world evolution...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AI Agent System stopped by user")
    except Exception as e:
        print(f"❌ System error: {str(e)}")
        exit(1)