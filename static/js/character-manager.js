/**
 * Character Manager - Main Integration System
 * Coordinates all character systems and provides unified interface
 */

// Import character data and systems
// Note: In a real implementation, these would be proper ES6 imports
// For now, they're loaded via script tags

class CharacterManager {
    constructor(gameCanvas, gameWorld) {
        this.gameCanvas = gameCanvas;
        this.gameWorld = gameWorld;
        this.characters = new Map();
        this.characterAIs = new Map();
        this.lastUpdate = Date.now();
        this.isRunning = false;
        
        // System components
        this.renderer = null;
        this.dialogueSystem = null;
        this.questSystem = null;
        this.tradingSystem = null;
        this.eventManager = null;
        
        this.initializeSystems();
    }

    async initializeSystems() {
        try {
            // Initialize event manager
            this.eventManager = new SimpleEventManager();
            
            // Initialize renderer
            this.renderer = new CharacterRenderer(this.gameCanvas, this);
            
            // Initialize dialogue system
            this.dialogueSystem = new DialogueSystem(this);
            
            // Initialize quest and trading systems
            this.questSystem = new QuestSystem(this);
            this.tradingSystem = new TradingSystem(this);
            
            // Load and spawn characters
            this.loadCharacters();
            
            // Start the main update loop
            this.startUpdateLoop();
            
            console.log('Character Manager initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize Character Manager:', error);
        }
    }

    loadCharacters() {
        // Check if CHARACTER_DATA is available
        if (typeof CHARACTER_DATA === 'undefined') {
            console.error('CHARACTER_DATA not found. Make sure characters.js is loaded.');
            return;
        }

        // Load all characters from the data file
        for (const [characterId, characterData] of Object.entries(CHARACTER_DATA)) {
            this.spawnCharacter(characterData);
        }

        console.log(`Loaded ${this.characters.size} characters`);
    }

    spawnCharacter(characterData) {
        // Create a copy of character data
        const character = {
            ...characterData,
            health: characterData.health || 100,
            spawnTime: Date.now(),
            lastInteraction: 0
        };

        // Create AI for the character
        if (typeof CharacterAI !== 'undefined') {
            const ai = new CharacterAI(character, this);
            this.characterAIs.set(character.id, ai);
            character.ai = ai;
        } else {
            console.warn('CharacterAI not available for character:', character.id);
        }

        // Store character
        this.characters.set(character.id, character);

        // Create visual representation
        if (this.renderer) {
            this.renderer.createCharacterElement(character);
        }

        console.log(`Spawned character: ${character.name} (${character.id})`);
        
        return character;
    }

    removeCharacter(characterId) {
        const character = this.characters.get(characterId);
        if (!character) return false;

        // Remove AI
        if (this.characterAIs.has(characterId)) {
            this.characterAIs.delete(characterId);
        }

        // Remove visual representation
        if (this.renderer) {
            this.renderer.removeCharacterElement(characterId);
        }

        // Remove from characters map
        this.characters.delete(characterId);

        console.log(`Removed character: ${characterId}`);
        return true;
    }

    startUpdateLoop() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        
        const updateLoop = () => {
            if (!this.isRunning) return;
            
            const now = Date.now();
            const deltaTime = now - this.lastUpdate;
            
            this.update(deltaTime);
            this.lastUpdate = now;
            
            // Schedule next update
            requestAnimationFrame(updateLoop);
        };
        
        updateLoop();
        console.log('Character update loop started');
    }

    stopUpdateLoop() {
        this.isRunning = false;
        console.log('Character update loop stopped');
    }

    update(deltaTime) {
        const playerPosition = this.getPlayerPosition();
        const allCharacters = Array.from(this.characters.values());

        // Update all character AIs
        for (const character of allCharacters) {
            if (character.ai) {
                character.ai.update(deltaTime, playerPosition, allCharacters);
            }
        }

        // Update renderer with all characters
        if (this.renderer) {
            this.renderer.renderAllCharacters(allCharacters);
        }

        // Update character actions and dialogue
        this.updateCharacterActions();
    }

    updateCharacterActions() {
        const now = Date.now();
        
        for (const character of this.characters.values()) {
            // Show random idle actions occasionally
            if (character.ai && Math.random() < 0.001) { // 0.1% chance per frame
                const action = character.ai.getCurrentAction();
                if (action && this.renderer) {
                    this.renderer.showCharacterAction(character, action, 3000);
                }
            }
        }
    }

    handleCharacterInteraction(character) {
        if (!character || !this.dialogueSystem) return;

        // Check if character can be interacted with
        const playerPosition = this.getPlayerPosition();
        const canInteract = this.canInteractWithCharacter(character, playerPosition);
        
        if (!canInteract) {
            if (this.renderer) {
                this.renderer.showFloatingText(character, "Too far away!", 'warning');
            }
            return;
        }

        // Trigger AI interaction response
        if (character.ai) {
            const aiResponse = character.ai.onPlayerInteraction({ position: playerPosition });
            console.log('AI Response:', aiResponse);
        }

        // Handle interaction through dialogue system
        const player = { position: playerPosition };
        const result = this.dialogueSystem.startInteraction(character, player);
        
        // Update character's last interaction time
        character.lastInteraction = Date.now();
        
        // Emit interaction event
        this.eventManager.emit('character_interaction', {
            character,
            player,
            result,
            timestamp: Date.now()
        });

        return result;
    }

    canInteractWithCharacter(character, playerPosition) {
        if (!character || !playerPosition) return false;
        
        const distance = this.calculateDistance(character.position, playerPosition);
        return distance <= character.interactionRadius + 1; // Add small tolerance
    }

    calculateDistance(pos1, pos2) {
        if (!pos1 || !pos2) return Infinity;
        
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    getPlayerPosition() {
        // Get player position from game world
        if (this.gameWorld && this.gameWorld.player) {
            return this.gameWorld.player.position;
        }
        
        // Fallback: try to get from character element in DOM
        const playerElement = document.getElementById('character');
        if (playerElement) {
            const canvas = this.gameCanvas;
            const canvasRect = canvas.getBoundingClientRect();
            const playerRect = playerElement.getBoundingClientRect();
            
            return {
                x: ((playerRect.left - canvasRect.left) / canvasRect.width) * 100,
                y: ((playerRect.top - canvasRect.top) / canvasRect.height) * 100
            };
        }
        
        // Default fallback position
        return { x: 50, y: 70 };
    }

    // Character query methods
    getCharacterById(characterId) {
        return this.characters.get(characterId);
    }

    getCharactersByType(characterType) {
        return Array.from(this.characters.values()).filter(
            character => character.type === characterType
        );
    }

    getCharactersInRange(position, range) {
        return Array.from(this.characters.values()).filter(character => {
            const distance = this.calculateDistance(character.position, position);
            return distance <= range;
        });
    }

    getNearestCharacter(position, characterType = null) {
        let nearest = null;
        let nearestDistance = Infinity;
        
        for (const character of this.characters.values()) {
            if (characterType && character.type !== characterType) continue;
            
            const distance = this.calculateDistance(character.position, position);
            if (distance < nearestDistance) {
                nearest = character;
                nearestDistance = distance;
            }
        }
        
        return nearest;
    }

    // Quest-related methods
    getQuestGivers() {
        return Array.from(this.characters.values()).filter(
            character => character.quests && character.quests.length > 0
        );
    }

    getMerchants() {
        return this.getCharactersByType('merchant');
    }

    // Combat-related methods
    getHostileCharacters() {
        return Array.from(this.characters.values()).filter(
            character => character.type === 'monster' && 
                        character.personality && 
                        character.personality.aggression > 70
        );
    }

    // Character state management
    setCharacterHealth(characterId, health) {
        const character = this.characters.get(characterId);
        if (character) {
            character.health = Math.max(0, health);
            
            if (this.renderer) {
                this.renderer.updateCharacterElement(character);
            }
            
            if (character.health === 0) {
                this.handleCharacterDeath(character);
            }
        }
    }

    handleCharacterDeath(character) {
        console.log(`Character died: ${character.name}`);
        
        // Show death effect
        if (this.renderer) {
            this.renderer.createParticleEffect(character, 'damage', 3000);
            this.renderer.showFloatingText(character, 'Defeated!', 'warning');
        }
        
        // For monsters, remove them after a delay
        if (character.type === 'monster') {
            setTimeout(() => {
                this.removeCharacter(character.id);
            }, 5000);
        } else {
            // For NPCs, just mark as unconscious temporarily
            character.health = 1;
            character.isUnconscious = true;
            
            setTimeout(() => {
                character.isUnconscious = false;
                character.health = Math.floor(character.health * 0.5) + 50;
            }, 30000); // Recover after 30 seconds
        }
        
        // Emit death event
        this.eventManager.emit('character_death', character);
    }

    // Player interaction helpers
    getInteractionHints(playerPosition) {
        const hints = [];
        const nearbyRange = 8;
        
        const nearbyCharacters = this.getCharactersInRange(playerPosition, nearbyRange);
        
        for (const character of nearbyCharacters) {
            const distance = this.calculateDistance(character.position, playerPosition);
            const canInteract = distance <= character.interactionRadius;
            
            if (canInteract) {
                const preview = this.dialogueSystem ? 
                    this.dialogueSystem.getInteractionPreview(character) :
                    { type: 'Talk', icon: '💬' };
                
                hints.push({
                    character,
                    distance,
                    ...preview
                });
            }
        }
        
        return hints.sort((a, b) => a.distance - b.distance);
    }

    // Debug methods
    enableDebugMode(enabled = true) {
        this.debugMode = enabled;
        
        if (this.renderer) {
            for (const character of this.characters.values()) {
                this.renderer.showDebugInfo(character, enabled);
            }
        }
        
        console.log(`Debug mode ${enabled ? 'enabled' : 'disabled'}`);
    }

    getDebugInfo() {
        return {
            characterCount: this.characters.size,
            characters: Array.from(this.characters.values()).map(char => ({
                id: char.id,
                name: char.name,
                type: char.type,
                position: char.position,
                health: char.health,
                ai: char.ai ? char.ai.getDebugInfo() : null
            }))
        };
    }

    // Save/Load functionality
    exportCharacterData() {
        const data = {
            characters: {},
            timestamp: Date.now()
        };
        
        for (const [id, character] of this.characters) {
            data.characters[id] = {
                position: character.position,
                health: character.health,
                lastInteraction: character.lastInteraction,
                // Don't save AI state - it will be recreated
            };
        }
        
        // Include quest data
        if (this.questSystem) {
            data.quests = this.questSystem.exportQuestData();
        }
        
        return data;
    }

    importCharacterData(data) {
        if (!data || !data.characters) return;
        
        // Update character states
        for (const [id, savedData] of Object.entries(data.characters)) {
            const character = this.characters.get(id);
            if (character) {
                if (savedData.position) character.position = savedData.position;
                if (savedData.health !== undefined) character.health = savedData.health;
                if (savedData.lastInteraction) character.lastInteraction = savedData.lastInteraction;
            }
        }
        
        // Import quest data
        if (data.quests && this.questSystem) {
            this.questSystem.importQuestData(data.quests);
        }
        
        console.log('Character data imported successfully');
    }

    // Cleanup method
    destroy() {
        this.stopUpdateLoop();
        
        // Clean up all systems
        if (this.renderer) {
            this.renderer.destroy();
        }
        
        // Clear all data
        this.characters.clear();
        this.characterAIs.clear();
        
        console.log('Character Manager destroyed');
    }
}

// Simple Event Manager for internal communication
class SimpleEventManager {
    constructor() {
        this.listeners = new Map();
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
}

// Global initialization function
function initializeCharacterSystem(gameCanvas, gameWorld = null) {
    console.log('Initializing Character System...');
    
    // Create character manager
    const characterManager = new CharacterManager(gameCanvas, gameWorld);
    
    // Make it globally available
    window.characterManager = characterManager;
    
    // Set up global interaction handler
    window.handleCharacterClick = function(characterId) {
        const character = characterManager.getCharacterById(characterId);
        if (character) {
            characterManager.handleCharacterInteraction(character);
        }
    };
    
    console.log('Character System initialized and ready!');
    return characterManager;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CharacterManager, SimpleEventManager, initializeCharacterSystem };
}

// Auto-initialize if DOM is ready and we're in a browser environment
if (typeof window !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Auto-initialize with default game canvas
        const gameCanvas = document.getElementById('gameCanvas');
        if (gameCanvas && typeof CHARACTER_DATA !== 'undefined') {
            setTimeout(() => initializeCharacterSystem(gameCanvas), 1000);
        }
    });
}