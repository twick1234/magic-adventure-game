# 🏰 Magic Adventure Game - CrewAI Multi-Agent System

A comprehensive, production-ready CrewAI multi-agent system that creates dynamic, immersive fantasy adventure games through the collaboration of 6 specialized AI agents.

## 🎭 System Overview

This system brings together multiple AI agents, each with distinct personalities and specialized knowledge, to create a cohesive and engaging gaming experience:

### 🤖 The Six Specialized Agents

1. **📚 Story Generator Agent (Master Story Weaver)**
   - Creates dynamic fantasy narratives and plot twists
   - Maintains story consistency across sessions
   - Adapts storylines based on player choices

2. **🎭 Character Behavior Agent (Character Psychology Master)**
   - Manages NPC personalities and behaviors
   - Ensures character consistency and development
   - Handles character dialogue and interactions

3. **🌍 World Builder Agent (Realm Architect)**
   - Generates rich environmental descriptions
   - Creates immersive fantasy locations
   - Manages world-building elements and atmosphere

4. **⚔️ Quest Master Agent (Quest Architect)**
   - Designs engaging quests and challenges
   - Manages game progression and pacing
   - Creates meaningful objectives and rewards

5. **🎵 Audio Coordinator Agent (Sonic Enchanter)**
   - Manages audio cues and ambient sounds
   - Coordinates music selection and sound effects
   - Enhances emotional moments through audio

6. **💬 Dialogue Creator Agent (Voice of All Beings)**
   - Generates contextual conversations
   - Creates character-specific dialogue patterns
   - Manages player-NPC interactions

## 🏗️ Architecture

The system is built with a modular, scalable architecture:

```
┌─────────────────────────────────┐
│        Web Frontend             │
├─────────────────────────────────┤
│      FastAPI Web Layer         │
├─────────────────────────────────┤
│     Game Orchestrator           │
├─────────────────────────────────┤
│   Agent Communication Hub       │
├─────────────────────────────────┤
│  6 Specialized CrewAI Agents    │
├─────────────────────────────────┤
│   Context & Configuration       │
└─────────────────────────────────┘
```

### 🔧 Core Components

- **Game Orchestrator**: Coordinates all agents and manages game flow
- **Agent Communication Hub**: Handles inter-agent messaging and coordination
- **Shared Context Database**: Maintains game state and story consistency
- **Configuration Manager**: Handles agent personalities and settings
- **Error Handling System**: Comprehensive error management and recovery
- **Web Integration**: FastAPI server with WebSocket support

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd magic-adventure-game

# Install dependencies
pip install -r requirements_crewai.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

### 2. Basic Usage

```bash
# Interactive CLI mode
python magic_adventure_crewai.py --mode cli

# Web API server mode
python magic_adventure_crewai.py --mode web --port 8000

# Demo and testing mode
python magic_adventure_crewai.py --mode demo
```

### 3. Environment Configuration

Create a `.env` file with the following variables:

```env
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-4

# Optional: CrewAI Configuration
CREWAI_TELEMETRY_OPT_OUT=true

# Optional: Game Configuration
GAME_DIFFICULTY=intermediate
MAX_TURNS_PER_SESSION=50
SESSION_TIMEOUT_HOURS=24

# Optional: Web Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_DIRECTORY=logs
```

## 🎮 Usage Examples

### CLI Interactive Mode

```bash
python magic_adventure_crewai.py --mode cli
```

This starts an interactive command-line adventure where you can:
- Create a character (name and class)
- Choose difficulty level
- Make decisions and see how all 6 agents collaborate
- View game status and statistics

### Web API Mode

```bash
python magic_adventure_crewai.py --mode web --host 0.0.0.0 --port 8000
```

Starts a FastAPI web server providing:
- REST API endpoints for game interactions
- WebSocket support for real-time updates
- Interactive API documentation at `/docs`
- Demo web interface at `/demo.html`

### Programmatic Usage

```python
from magic_adventure_crewai import MagicAdventureSystem
from agent_config import DifficultyLevel

# Initialize the system
system = MagicAdventureSystem()

# Create a game session
session_id = system.create_game_session(
    player_name="Hero",
    character_class="Mage",
    difficulty=DifficultyLevel.INTERMEDIATE
)

# Get the orchestrator for this session
session = system.get_session(session_id)
orchestrator = session["orchestrator"]

# Start the game
start_response = orchestrator.start_new_game("Hero", "Mage")
print(start_response)

# Process player actions
action_response = orchestrator.process_player_action("explore the forest", "exploration")
print(action_response)
```

## 🔧 API Reference

### REST Endpoints

- `POST /api/game/start` - Start a new game session
- `POST /api/game/{session_id}/action` - Process a player action
- `GET /api/game/{session_id}/status` - Get current game status
- `GET /api/admin/stats` - Get system statistics (admin)

### WebSocket Endpoints

- `WS /api/ws/{session_id}` - Real-time game updates

### Example API Usage

```javascript
// Start a new game
const response = await fetch('/api/game/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Hero',
    character_class: 'Warrior'
  })
});

const gameData = await response.json();
const sessionId = gameData.data.session_id;

// Process an action
const actionResponse = await fetch(`/api/game/${sessionId}/action`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'explore the enchanted forest',
    action_type: 'exploration'
  })
});
```

## 🎨 Customization

### Agent Personalities

Each agent can be customized through the configuration system:

```python
from agent_config import AgentConfigurationManager, AgentRole

config_manager = AgentConfigurationManager()

# Get current configuration
story_config = config_manager.get_configuration(AgentRole.STORY_GENERATOR)

# Modify personality traits
story_config.personality.creativity_level = 0.9
story_config.personality.verbosity = 0.8

# Update configuration
config_manager.update_configuration(AgentRole.STORY_GENERATOR, {
    "personality": story_config.personality
})
```

### Game Scenarios

Create custom scenarios for different game types:

```python
# Create a children-friendly scenario
children_scenario = {
    AgentRole.STORY_GENERATOR: {
        "personality.creativity_level": 0.7,
        "performance.max_response_length": 200
    },
    AgentRole.CHARACTER_BEHAVIOR: {
        "personality.humor_level": 0.8
    }
}

config_manager.create_scenario_configuration("children_mode", children_scenario)
```

## 📊 Monitoring and Debugging

### Health Checks

The system includes comprehensive health monitoring:

```python
# Run health checks
health_report = system.health_monitor.run_health_checks()
print(f"System Status: {health_report['status']}")
```

### Performance Monitoring

```python
from error_handling import performance_monitor

# Monitor performance of operations
with performance_monitor("agent_response", "story_generator", logger) as metric:
    response = agent.process_request(request)
    
# View performance statistics
stats = logger.get_performance_stats()
print(f"Average response time: {stats['average_duration']:.2f}s")
```

### Error Handling

```python
# Custom error handling
try:
    result = orchestrator.process_player_action(action)
except Exception as e:
    error = error_handler.handle_error(e, ErrorCategory.AGENT_FAILURE, ErrorSeverity.HIGH)
    # System automatically attempts recovery
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python magic_adventure_crewai.py --mode demo

# Run specific component tests
python -m pytest tests/
```

### Test Coverage

The demo mode tests:
- ✅ Agent creation and initialization
- ✅ Configuration management
- ✅ Context database operations
- ✅ Agent communication
- ✅ Error handling and recovery
- ✅ Health monitoring
- ✅ Session management

## 🔒 Security Considerations

- **API Keys**: Store securely in environment variables
- **Input Validation**: All user inputs are validated through Pydantic models
- **Session Management**: Sessions have configurable timeouts
- **CORS**: Configure appropriately for production environments
- **Rate Limiting**: Implement in production deployments

## 🎛️ Configuration Options

### Agent Behavior

```yaml
# agent_config.yaml
story_generator:
  personality:
    creativity_level: 0.8
    verbosity: 0.7
    humor_level: 0.4
  performance:
    max_response_length: 500
    response_time_target: 3.0
```

### Game Settings

```python
# Difficulty-based configuration
if difficulty == DifficultyLevel.BEGINNER:
    config.performance.detail_level = 0.5
    config.personality.verbosity = 0.6
elif difficulty == DifficultyLevel.EXPERT:
    config.performance.detail_level = 0.9
    config.personality.creativity_level = 0.9
```

## 🚀 Production Deployment

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_crewai.txt .
RUN pip install -r requirements_crewai.txt

COPY . .
EXPOSE 8000

CMD ["python", "magic_adventure_crewai.py", "--mode", "web"]
```

### Environment Variables for Production

```env
# Production settings
OPENAI_API_KEY=your_production_key
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
SESSION_TIMEOUT_HOURS=4
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Submit a pull request

## 📖 Documentation

- **Architecture**: See `ARCHITECTURE.md` for detailed system design
- **API Documentation**: Available at `/docs` when running web mode
- **Agent Specifications**: See individual agent modules for detailed documentation
- **Business Requirements**: See `BRD.md` for complete requirements

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements_crewai.txt`

2. **API Key Issues**: Verify your `.env` file contains a valid `OPENAI_API_KEY`

3. **Port Already in Use**: Change the port with `--port 8001` or check for existing processes

4. **Agent Response Timeouts**: Increase timeout settings in agent configuration

5. **Memory Issues**: Reduce `context_window` and `memory_retention` in performance settings

### Debug Mode

Enable detailed logging:

```bash
python magic_adventure_crewai.py --mode cli --debug
```

### Health Diagnostics

```bash
# Check system health
python magic_adventure_crewai.py --mode demo
```

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI) framework
- Powered by [OpenAI GPT models](https://openai.com)
- Web framework by [FastAPI](https://fastapi.tiangolo.com)
- Inspired by classic text-based adventure games

---

**Created with ❤️ for interactive storytelling and AI collaboration**

For support, questions, or contributions, please open an issue or submit a pull request.