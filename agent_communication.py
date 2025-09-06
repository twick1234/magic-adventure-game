#!/usr/bin/env python3
"""
🔗 Agent Communication & Context Management System

This module implements sophisticated communication and context sharing between
CrewAI agents to maintain story consistency and enable collaborative storytelling.

Features:
- Inter-agent message passing and coordination
- Shared context database with version control  
- Story consistency validation and conflict resolution
- Memory management for long-term continuity
- Event-driven communication patterns
- Context synchronization across agent sessions

The system ensures all agents stay coordinated and maintain a consistent
view of the game world, characters, and ongoing storylines.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can send to each other"""
    STORY_UPDATE = "story_update"
    CHARACTER_CHANGE = "character_change" 
    LOCATION_CHANGE = "location_change"
    QUEST_UPDATE = "quest_update"
    DIALOGUE_REQUEST = "dialogue_request"
    AUDIO_CUE = "audio_cue"
    CONTEXT_SYNC = "context_sync"
    VALIDATION_REQUEST = "validation_request"
    ERROR_REPORT = "error_report"
    COLLABORATION_REQUEST = "collaboration_request"


class Priority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    id: str = field(default_factory=lambda: hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8])
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.CONTEXT_SYNC
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    processed: bool = False
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class ContextVersion:
    """Versioned context snapshot for consistency tracking"""
    version: int
    timestamp: datetime
    context_data: Dict[str, Any]
    changed_by: str
    change_summary: str
    checksum: str = field(default="")
    
    def __post_init__(self):
        # Generate checksum for data integrity
        self.checksum = hashlib.sha256(
            json.dumps(self.context_data, sort_keys=True).encode()
        ).hexdigest()[:16]


class SharedContextDB:
    """
    Centralized context database that all agents can access
    Maintains versioned history and handles concurrent access
    """
    
    def __init__(self):
        self._context_data = {}
        self._versions = []
        self._current_version = 0
        self._lock = threading.RLock()
        self._subscribers = defaultdict(list)
        self._change_log = []
        
        logger.info("🗄️ Initialized Shared Context Database")
    
    def get_context(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get current context data, optionally filtered by keys"""
        with self._lock:
            if keys:
                return {k: self._context_data.get(k) for k in keys if k in self._context_data}
            return self._context_data.copy()
    
    def update_context(self, updates: Dict[str, Any], changed_by: str, 
                      change_summary: str = "Context update") -> int:
        """
        Update context data and create new version
        
        Returns the new version number
        """
        with self._lock:
            # Apply updates
            old_data = self._context_data.copy()
            self._context_data.update(updates)
            
            # Create version snapshot
            self._current_version += 1
            version = ContextVersion(
                version=self._current_version,
                timestamp=datetime.now(),
                context_data=self._context_data.copy(),
                changed_by=changed_by,
                change_summary=change_summary
            )
            self._versions.append(version)
            
            # Log changes
            self._change_log.append({
                "version": self._current_version,
                "timestamp": datetime.now(),
                "changed_by": changed_by,
                "changes": self._get_change_diff(old_data, self._context_data),
                "summary": change_summary
            })
            
            # Notify subscribers
            self._notify_subscribers(updates, changed_by)
            
            logger.info(f"📝 Context updated to version {self._current_version} by {changed_by}")
            return self._current_version
    
    def get_version(self, version_number: int) -> Optional[ContextVersion]:
        """Get a specific version of the context"""
        with self._lock:
            for version in self._versions:
                if version.version == version_number:
                    return version
            return None
    
    def get_version_history(self, limit: int = 10) -> List[ContextVersion]:
        """Get recent version history"""
        with self._lock:
            return self._versions[-limit:] if self._versions else []
    
    def subscribe_to_changes(self, subscriber: str, callback: Callable):
        """Subscribe to context changes"""
        with self._lock:
            self._subscribers[subscriber].append(callback)
            logger.info(f"📡 {subscriber} subscribed to context changes")
    
    def validate_consistency(self) -> Dict[str, Any]:
        """Validate context consistency and detect conflicts"""
        with self._lock:
            issues = []
            
            # Check for required fields
            required_fields = ["player_name", "current_location", "game_state"]
            for field in required_fields:
                if field not in self._context_data:
                    issues.append(f"Missing required field: {field}")
            
            # Check for logical consistency
            if "player_health" in self._context_data:
                health = self._context_data["player_health"]
                if health < 0 or health > 100:
                    issues.append(f"Invalid player health: {health}")
            
            # Check story consistency
            if "story_progress" in self._context_data:
                progress = self._context_data["story_progress"]
                if progress < 0 or progress > 100:
                    issues.append(f"Invalid story progress: {progress}")
            
            return {
                "is_consistent": len(issues) == 0,
                "issues": issues,
                "last_check": datetime.now(),
                "version": self._current_version
            }
    
    def _get_change_diff(self, old_data: Dict, new_data: Dict) -> Dict[str, Any]:
        """Calculate the difference between two context versions"""
        changes = {
            "added": {},
            "modified": {},
            "removed": {}
        }
        
        # Find added and modified keys
        for key, value in new_data.items():
            if key not in old_data:
                changes["added"][key] = value
            elif old_data[key] != value:
                changes["modified"][key] = {
                    "old": old_data[key],
                    "new": value
                }
        
        # Find removed keys
        for key in old_data:
            if key not in new_data:
                changes["removed"][key] = old_data[key]
        
        return changes
    
    def _notify_subscribers(self, changes: Dict[str, Any], changed_by: str):
        """Notify all subscribers of context changes"""
        for subscriber, callbacks in self._subscribers.items():
            if subscriber != changed_by:  # Don't notify the agent that made the change
                for callback in callbacks:
                    try:
                        callback(changes, changed_by)
                    except Exception as e:
                        logger.error(f"❌ Error notifying subscriber {subscriber}: {e}")


class AgentCommunicationHub:
    """
    Central hub for agent-to-agent communication
    Handles message routing, queuing, and coordination
    """
    
    def __init__(self, context_db: SharedContextDB):
        self.context_db = context_db
        self._message_queue = []
        self._message_handlers = defaultdict(list)
        self._active_conversations = {}
        self._agent_status = {}
        self._lock = threading.RLock()
        
        logger.info("💬 Initialized Agent Communication Hub")
    
    def register_agent(self, agent_name: str, message_handler: Optional[Callable] = None):
        """Register an agent with the communication hub"""
        with self._lock:
            self._agent_status[agent_name] = {
                "registered_at": datetime.now(),
                "last_active": datetime.now(),
                "status": "active",
                "messages_sent": 0,
                "messages_received": 0
            }
            
            if message_handler:
                self._message_handlers[agent_name].append(message_handler)
            
            logger.info(f"🤖 Registered agent: {agent_name}")
    
    def send_message(self, message: AgentMessage) -> bool:
        """Send a message from one agent to another"""
        with self._lock:
            try:
                # Validate sender and recipient
                if message.sender not in self._agent_status:
                    logger.warning(f"⚠️ Unknown sender: {message.sender}")
                    return False
                
                if message.recipient not in self._agent_status and message.recipient != "broadcast":
                    logger.warning(f"⚠️ Unknown recipient: {message.recipient}")
                    return False
                
                # Add to queue
                self._message_queue.append(message)
                
                # Update sender stats
                self._agent_status[message.sender]["messages_sent"] += 1
                self._agent_status[message.sender]["last_active"] = datetime.now()
                
                # Process message immediately if not broadcast
                if message.recipient != "broadcast":
                    self._process_message(message)
                
                logger.debug(f"📨 Message sent from {message.sender} to {message.recipient}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to send message: {e}")
                return False
    
    def get_messages_for_agent(self, agent_name: str, 
                              message_types: Optional[List[MessageType]] = None) -> List[AgentMessage]:
        """Get pending messages for a specific agent"""
        with self._lock:
            messages = []
            for message in self._message_queue:
                if (message.recipient == agent_name or message.recipient == "broadcast") and not message.processed:
                    if not message_types or message.message_type in message_types:
                        messages.append(message)
            
            # Mark as processed
            for message in messages:
                message.processed = True
                if message.recipient != "broadcast":
                    self._agent_status[agent_name]["messages_received"] += 1
            
            return messages
    
    def start_conversation(self, initiator: str, participants: List[str], 
                          topic: str) -> str:
        """Start a multi-agent conversation"""
        conversation_id = hashlib.md5(f"{initiator}_{topic}_{datetime.now()}".encode()).hexdigest()[:8]
        
        with self._lock:
            self._active_conversations[conversation_id] = {
                "id": conversation_id,
                "initiator": initiator,
                "participants": participants,
                "topic": topic,
                "started_at": datetime.now(),
                "messages": [],
                "status": "active"
            }
            
            # Notify participants
            for participant in participants:
                if participant != initiator:
                    invite_message = AgentMessage(
                        sender="communication_hub",
                        recipient=participant,
                        message_type=MessageType.COLLABORATION_REQUEST,
                        content={
                            "conversation_id": conversation_id,
                            "initiator": initiator,
                            "topic": topic,
                            "participants": participants
                        },
                        priority=Priority.HIGH
                    )
                    self.send_message(invite_message)
            
            logger.info(f"🗣️ Started conversation '{topic}' with {len(participants)} participants")
            return conversation_id
    
    def add_to_conversation(self, conversation_id: str, sender: str, 
                           content: Dict[str, Any]) -> bool:
        """Add a message to an active conversation"""
        with self._lock:
            if conversation_id not in self._active_conversations:
                return False
            
            conversation = self._active_conversations[conversation_id]
            if sender not in conversation["participants"]:
                return False
            
            message = {
                "sender": sender,
                "content": content,
                "timestamp": datetime.now()
            }
            conversation["messages"].append(message)
            
            # Notify other participants
            for participant in conversation["participants"]:
                if participant != sender:
                    notify_message = AgentMessage(
                        sender=sender,
                        recipient=participant,
                        message_type=MessageType.COLLABORATION_REQUEST,
                        content={
                            "conversation_id": conversation_id,
                            "message": content,
                            "from": sender
                        }
                    )
                    self.send_message(notify_message)
            
            return True
    
    def request_collaboration(self, requester: str, target_agents: List[str], 
                            task_description: str, context: Dict[str, Any]) -> List[str]:
        """Request collaboration from multiple agents"""
        collaboration_id = hashlib.md5(f"{requester}_{task_description}_{datetime.now()}".encode()).hexdigest()[:8]
        responses = []
        
        for agent in target_agents:
            message = AgentMessage(
                sender=requester,
                recipient=agent,
                message_type=MessageType.COLLABORATION_REQUEST,
                content={
                    "collaboration_id": collaboration_id,
                    "task": task_description,
                    "context": context,
                    "deadline": datetime.now() + timedelta(minutes=5)
                },
                priority=Priority.HIGH,
                requires_response=True,
                response_deadline=datetime.now() + timedelta(minutes=5)
            )
            
            if self.send_message(message):
                responses.append(agent)
        
        logger.info(f"🤝 Collaboration request sent to {len(responses)} agents")
        return responses
    
    def validate_story_consistency(self, proposed_changes: Dict[str, Any], 
                                 requesting_agent: str) -> Dict[str, Any]:
        """
        Validate proposed story changes against current context
        Returns validation result and any conflicts
        """
        current_context = self.context_db.get_context()
        conflicts = []
        warnings = []
        
        # Check for logical consistency
        if "current_location" in proposed_changes:
            new_location = proposed_changes["current_location"]
            current_location = current_context.get("current_location", "")
            
            # Simple validation - could be made much more sophisticated
            if new_location == current_location:
                warnings.append("Location change to same location")
        
        if "player_health" in proposed_changes:
            new_health = proposed_changes["player_health"]
            current_health = current_context.get("player_health", 100)
            
            if new_health > current_health + 50:  # Arbitrary healing limit
                conflicts.append("Excessive health increase without explanation")
            
            if new_health < 0:
                conflicts.append("Player health cannot be negative")
        
        # Check story progress consistency
        if "story_progress" in proposed_changes:
            new_progress = proposed_changes["story_progress"]
            current_progress = current_context.get("story_progress", 0)
            
            if new_progress < current_progress:
                conflicts.append("Story progress cannot go backwards")
        
        return {
            "is_valid": len(conflicts) == 0,
            "conflicts": conflicts,
            "warnings": warnings,
            "validated_by": "communication_hub",
            "timestamp": datetime.now()
        }
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get communication statistics for all agents"""
        with self._lock:
            stats = {
                "total_agents": len(self._agent_status),
                "total_messages": len(self._message_queue),
                "active_conversations": len([c for c in self._active_conversations.values() if c["status"] == "active"]),
                "agent_details": self._agent_status.copy()
            }
            return stats
    
    def _process_message(self, message: AgentMessage):
        """Process a message and call appropriate handlers"""
        handlers = self._message_handlers.get(message.recipient, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"❌ Error processing message in handler: {e}")


class StoryConsistencyManager:
    """
    Manages story consistency across all agent interactions
    Validates changes and resolves conflicts
    """
    
    def __init__(self, context_db: SharedContextDB):
        self.context_db = context_db
        self._consistency_rules = []
        self._conflict_resolvers = {}
        
        logger.info("📚 Initialized Story Consistency Manager")
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default consistency rules"""
        self._consistency_rules = [
            {
                "name": "health_bounds",
                "check": lambda ctx: 0 <= ctx.get("player_health", 100) <= 100,
                "message": "Player health must be between 0 and 100"
            },
            {
                "name": "progress_monotonic",
                "check": lambda ctx: ctx.get("story_progress", 0) >= 0,
                "message": "Story progress cannot be negative"
            },
            {
                "name": "required_fields",
                "check": lambda ctx: all(field in ctx for field in ["player_name", "current_location"]),
                "message": "Required fields must be present"
            }
        ]
    
    def validate_changes(self, proposed_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Validate proposed changes against consistency rules"""
        current_context = self.context_db.get_context()
        test_context = current_context.copy()
        test_context.update(proposed_changes)
        
        violations = []
        for rule in self._consistency_rules:
            if not rule["check"](test_context):
                violations.append({
                    "rule": rule["name"],
                    "message": rule["message"]
                })
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "timestamp": datetime.now()
        }
    
    def resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Attempt to resolve conflicts automatically"""
        resolved = []
        unresolved = []
        
        for conflict in conflicts:
            conflict_type = conflict.get("type", "unknown")
            if conflict_type in self._conflict_resolvers:
                try:
                    resolution = self._conflict_resolvers[conflict_type](conflict)
                    resolved.append(resolution)
                except Exception as e:
                    logger.error(f"❌ Failed to resolve conflict: {e}")
                    unresolved.append(conflict)
            else:
                unresolved.append(conflict)
        
        return {
            "resolved": resolved,
            "unresolved": unresolved,
            "timestamp": datetime.now()
        }


if __name__ == "__main__":
    # Demo the communication system
    print("🔗 Agent Communication System Demo")
    print("=" * 50)
    
    # Initialize components
    context_db = SharedContextDB()
    comm_hub = AgentCommunicationHub(context_db)
    consistency_manager = StoryConsistencyManager(context_db)
    
    # Register some agents
    comm_hub.register_agent("story_generator")
    comm_hub.register_agent("character_behavior") 
    comm_hub.register_agent("world_builder")
    
    # Update context
    context_db.update_context({
        "player_name": "Test Hero",
        "current_location": "Forest",
        "player_health": 100,
        "story_progress": 10
    }, "system", "Initial setup")
    
    # Send a message
    message = AgentMessage(
        sender="story_generator",
        recipient="character_behavior",
        message_type=MessageType.CHARACTER_CHANGE,
        content={"character": "Wise Owl", "mood": "helpful"}
    )
    comm_hub.send_message(message)
    
    # Get statistics
    stats = comm_hub.get_agent_statistics()
    print(f"📊 System Statistics:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Total Messages: {stats['total_messages']}")
    
    # Validate consistency
    validation = context_db.validate_consistency()
    print(f"📝 Context Consistency: {validation['is_consistent']}")
    
    print("✨ Demo completed successfully!")