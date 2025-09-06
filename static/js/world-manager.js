/**
 * World Manager - Coordinates world generation, rendering, and game interactions
 */

class WorldManager {
    constructor() {
        this.worldGenerator = new WorldGenerator(40, 25);
        this.worldRenderer = null;
        this.minimapRenderer = null;
        this.inventory = new Map();
        this.playerStats = {
            x: 50,
            y: 70,
            level: 1,
            experience: 0,
            health: 100,
            maxHealth: 100
        };
        this.currentWeather = 'sunny';
        this.timeOfDay = 'day';
        this.lastWeatherUpdate = Date.now();
        
        this.init();
    }
    
    init() {
        // Initialize world generation and rendering
        this.generateNewWorld();
        
        // Setup renderers
        this.worldRenderer = new WorldRenderer('gameCanvas', this.worldGenerator);
        this.setupRendererCallbacks();
        
        // Setup minimap if container exists
        const minimapContainer = document.getElementById('worldMinimap');
        if (minimapContainer) {
            this.minimapRenderer = new MinimapRenderer('worldMinimap', this.worldGenerator);
        }
        
        // Setup game loops
        this.startGameLoops();
        
        console.log('World Manager initialized');
    }
    
    generateNewWorld() {
        console.log('Generating new world...');
        this.worldGenerator.generateWorld();
        
        // Reset inventory and stats
        this.inventory.clear();
        this.addChatMessage('🌍 World', 'A new world has been generated! Explore and gather resources.');
        
        // If renderer exists, re-render
        if (this.worldRenderer) {
            this.worldRenderer.renderWorld();
        }
        
        // Update minimap
        if (this.minimapRenderer) {
            this.minimapRenderer.render();
        }
    }
    
    setupRendererCallbacks() {
        // Handle block clicks
        this.worldRenderer.onBlockClick = (tile, x, y) => {
            this.handleBlockInteraction(tile, x, y);
        };
        
        // Handle resource harvesting
        this.worldRenderer.onResourceHarvest = (reward, x, y) => {
            this.handleResourceHarvest(reward, x, y);
        };
    }
    
    handleBlockInteraction(tile, x, y) {
        // Provide information about the clicked tile
        const biomeInfo = this.getBiomeInfo(tile.biome);
        let message = `🔍 ${biomeInfo.name} terrain (${tile.type}) at (${x}, ${y})`
        
        if (tile.resource && !tile.harvested) {
            const resourceInfo = this.getResourceInfo(tile.resource);
            message += ` - Contains ${resourceInfo.name} ${resourceInfo.emoji}`;
        } else if (tile.harvested) {
            message += ` - Resource harvested (will respawn)`;
        }
        
        this.addChatMessage('🔍 Explore', message);
        
        // Update world status
        this.updateLocationInfo(tile, x, y);
    }
    
    handleResourceHarvest(reward, x, y) {
        // Add to inventory
        const currentAmount = this.inventory.get(reward.name) || 0;
        this.inventory.set(reward.name, currentAmount + reward.amount);
        
        // Give experience
        const expGain = this.calculateExperienceGain(reward);
        this.playerStats.experience += expGain;
        this.checkLevelUp();
        
        // Show chat message
        this.addChatMessage('⛏️ Harvest', 
            `Collected ${reward.amount}x ${reward.name} ${reward.emoji} (+${expGain} XP)`);
        
        // Update UI
        this.updateInventoryDisplay();
        this.updatePlayerStatsDisplay();
    }
    
    calculateExperienceGain(reward) {
        const expValues = {
            'Wood': 5,
            'Pine Wood': 6,
            'Stone': 3,
            'Crystal': 15
        };
        return (expValues[reward.name] || 1) * reward.amount;
    }
    
    checkLevelUp() {
        const requiredExp = this.playerStats.level * 100;
        if (this.playerStats.experience >= requiredExp) {
            this.playerStats.level++;
            this.playerStats.experience = 0;
            this.playerStats.maxHealth += 10;
            this.playerStats.health = this.playerStats.maxHealth;
            
            this.addChatMessage('🎉 Level Up!', 
                `Congratulations! You reached level ${this.playerStats.level}! (+10 max health)`);
            
            this.updatePlayerStatsDisplay();
        }
    }
    
    getBiomeInfo(biomeName) {
        const biomeInfo = {
            'grassland': { name: 'Grassland', emoji: '🌾', description: 'Rolling hills with scattered resources' },
            'forest': { name: 'Forest', emoji: '🌲', description: 'Dense woodland rich in timber' },
            'desert': { name: 'Desert', emoji: '🏜️', description: 'Arid wasteland with precious gems' },
            'mountains': { name: 'Mountains', emoji: '⛰️', description: 'Rocky peaks with mineral deposits' },
            'tundra': { name: 'Tundra', emoji: '🌨️', description: 'Frozen landscape with rare resources' }
        };
        return biomeInfo[biomeName] || { name: 'Unknown', emoji: '❓', description: 'Mysterious terrain' };
    }
    
    getResourceInfo(resourceType) {
        const resourceInfo = {
            'tree': { name: 'Tree', emoji: '🌳', description: 'Source of wood for building' },
            'tree-pine': { name: 'Pine Tree', emoji: '🌲', description: 'Hardy conifer wood' },
            'rock': { name: 'Rock', emoji: '🪨', description: 'Stone for construction' },
            'crystal': { name: 'Crystal', emoji: '💎', description: 'Rare magical crystal' }
        };
        return resourceInfo[resourceType] || { name: 'Resource', emoji: '📦', description: 'Unknown resource' };
    }
    
    updateLocationInfo(tile, x, y) {
        const biomeInfo = this.getBiomeInfo(tile.biome);
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
            locationElement.innerHTML = `${biomeInfo.emoji} ${biomeInfo.name} (${x}, ${y})`;
        }
    }
    
    updateInventoryDisplay() {
        const inventoryElement = document.getElementById('inventory');
        if (inventoryElement) {
            let inventoryHtml = '<h4>📦 Inventory</h4>';
            if (this.inventory.size === 0) {
                inventoryHtml += '<p>Empty</p>';
            } else {
                this.inventory.forEach((amount, item) => {
                    const resourceInfo = this.getResourceInfo(item.toLowerCase().replace(' ', '-'));
                    inventoryHtml += `<div class="inventory-item">${resourceInfo.emoji} ${item}: ${amount}</div>`;
                });
            }
            inventoryElement.innerHTML = inventoryHtml;
        }
    }
    
    updatePlayerStatsDisplay() {
        // Update character level
        const levelElement = document.getElementById('characterLevel');
        if (levelElement) {
            levelElement.textContent = this.playerStats.level;
        }
        
        // Update health
        const healthElement = document.getElementById('characterHealth');
        if (healthElement) {
            healthElement.textContent = `${this.playerStats.health}/${this.playerStats.maxHealth}`;
        }
        
        // Update experience
        const expElement = document.getElementById('characterExp');
        if (expElement) {
            const requiredExp = this.playerStats.level * 100;
            expElement.textContent = `${this.playerStats.experience}/${requiredExp}`;
        }
    }
    
    // Handle character movement in the world
    updateCharacterPosition(x, y) {
        this.playerStats.x = x;
        this.playerStats.y = y;
        
        // Get world tile information
        const tileInfo = this.worldRenderer.updatePlayerPosition(x, y);
        if (tileInfo) {
            // Update minimap
            if (this.minimapRenderer) {
                this.minimapRenderer.updatePlayerPosition(tileInfo.coordinates.x, tileInfo.coordinates.y);
            }
            
            // Random events based on terrain
            this.triggerRandomEvents(tileInfo);
        }
        
        return tileInfo;
    }
    
    triggerRandomEvents(tileInfo) {
        // Random chance for events when moving
        if (Math.random() < 0.05) { // 5% chance
            const events = this.getRandomEventsForTerrain(tileInfo.terrain, tileInfo.biome);
            if (events.length > 0) {
                const event = events[Math.floor(Math.random() * events.length)];
                this.addChatMessage('🎲 Event', event.message);
                
                // Apply event effects
                if (event.healthChange) {
                    this.playerStats.health = Math.max(0, 
                        Math.min(this.playerStats.maxHealth, this.playerStats.health + event.healthChange));
                    this.updatePlayerStatsDisplay();
                }
                
                if (event.item) {
                    const currentAmount = this.inventory.get(event.item) || 0;
                    this.inventory.set(event.item, currentAmount + 1);
                    this.updateInventoryDisplay();
                }
            }
        }
    }
    
    getRandomEventsForTerrain(terrain, biome) {
        const events = [];
        
        switch (terrain) {
            case 'water':
                events.push(
                    { message: 'You found a crystal clear spring! (+5 health)', healthChange: 5 },
                    { message: 'A friendly fish splashes nearby!' }
                );
                break;
            case 'grass':
                events.push(
                    { message: 'You discovered some wild berries! (+3 health)', healthChange: 3 },
                    { message: 'A butterfly lands on your shoulder.' },
                    { message: 'You found an old coin buried in the grass!', item: 'Coin' }
                );
                break;
            case 'mountain':
                events.push(
                    { message: 'You slip on loose rocks... (-2 health)', healthChange: -2 },
                    { message: 'The view from here is breathtaking!' },
                    { message: 'You found a rare gem in the rocks!', item: 'Rare Gem' }
                );
                break;
            case 'desert':
                events.push(
                    { message: 'The heat is draining... (-1 health)', healthChange: -1 },
                    { message: 'You see a mirage in the distance.' },
                    { message: 'A hidden oasis! (+5 health)', healthChange: 5 }
                );
                break;
        }
        
        return events;
    }
    
    // Weather and time systems
    startGameLoops() {
        // Weather update loop (every 2 minutes)
        setInterval(() => {
            this.updateWeather();
        }, 120000);
        
        // Time of day loop (every 5 minutes)
        setInterval(() => {
            this.updateTimeOfDay();
        }, 300000);
        
        // Auto-save inventory (every 30 seconds)
        setInterval(() => {
            this.saveGameState();
        }, 30000);
    }
    
    updateWeather() {
        const weathers = ['sunny', 'cloudy', 'rain', 'storm', 'snow'];
        const newWeather = weathers[Math.floor(Math.random() * weathers.length)];
        
        if (newWeather !== this.currentWeather) {
            this.currentWeather = newWeather;
            this.addChatMessage('🌦️ Weather', `The weather changed to ${newWeather}!`);
            
            // Update weather display
            const weatherElement = document.getElementById('currentWeather');
            if (weatherElement) {
                weatherElement.textContent = newWeather.charAt(0).toUpperCase() + newWeather.slice(1);
            }
            
            // Apply visual effects
            if (this.worldRenderer) {
                this.worldRenderer.applyWeatherEffect(newWeather);
            }
        }
    }
    
    updateTimeOfDay() {
        this.timeOfDay = this.timeOfDay === 'day' ? 'night' : 'day';
        this.addChatMessage('🌅 Time', `It is now ${this.timeOfDay}time.`);
        
        // Apply visual effects
        if (this.worldRenderer) {
            this.worldRenderer.applyTimeOfDay(this.timeOfDay === 'night');
        }
    }
    
    // Save/Load system
    saveGameState() {
        const gameState = {
            inventory: Object.fromEntries(this.inventory),
            playerStats: this.playerStats,
            worldSeed: this.worldGenerator.seed,
            currentWeather: this.currentWeather,
            timeOfDay: this.timeOfDay,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem('magic-adventure-world-state', JSON.stringify(gameState));
        } catch (error) {
            console.warn('Could not save game state:', error);
        }
    }
    
    loadGameState() {
        try {
            const saved = localStorage.getItem('magic-adventure-world-state');
            if (saved) {
                const gameState = JSON.parse(saved);
                
                // Restore inventory
                this.inventory = new Map(Object.entries(gameState.inventory || {}));
                
                // Restore player stats
                if (gameState.playerStats) {
                    this.playerStats = { ...this.playerStats, ...gameState.playerStats };
                }
                
                // Restore weather and time
                this.currentWeather = gameState.currentWeather || 'sunny';
                this.timeOfDay = gameState.timeOfDay || 'day';
                
                // Update displays
                this.updateInventoryDisplay();
                this.updatePlayerStatsDisplay();
                
                const weatherElement = document.getElementById('currentWeather');
                if (weatherElement) {
                    weatherElement.textContent = this.currentWeather.charAt(0).toUpperCase() + this.currentWeather.slice(1);
                }
                
                this.addChatMessage('💾 System', 'Game state loaded successfully!');
                return true;
            }
        } catch (error) {
            console.warn('Could not load game state:', error);
        }
        return false;
    }
    
    // Helper method to add chat messages
    addChatMessage(sender, message) {
        if (typeof addChatMessage === 'function') {
            addChatMessage(sender, message);
        } else {
            console.log(`[${sender}] ${message}`);
        }
    }
    
    // Public methods for external use
    regenerateWorld() {
        this.generateNewWorld();
    }
    
    getInventorySummary() {
        const summary = {};
        this.inventory.forEach((amount, item) => {
            summary[item] = amount;
        });
        return summary;
    }
    
    getPlayerStats() {
        return { ...this.playerStats };
    }
    
    getCurrentWorldInfo() {
        return {
            weather: this.currentWeather,
            timeOfDay: this.timeOfDay,
            worldSize: {
                width: this.worldGenerator.width,
                height: this.worldGenerator.height
            },
            resourceCount: this.worldGenerator.resources.length,
            playerLevel: this.playerStats.level
        };
    }
}

// Global instance for easy access
let worldManager = null;

// Initialize when DOM is ready
function initializeWorldSystem() {
    if (!worldManager) {
        worldManager = new WorldManager();
        console.log('World system initialized');
        
        // Try to load saved game state
        worldManager.loadGameState();
        
        // Expose to global scope for debugging
        window.worldManager = worldManager;
    }
    return worldManager;
}

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWorldSystem);
} else {
    initializeWorldSystem();
}