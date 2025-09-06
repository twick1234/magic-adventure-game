/**
 * Minecraft-style World Generation System
 * Includes procedural terrain generation, biomes, and resource placement
 */

class WorldGenerator {
    constructor(width = 40, height = 25) {
        this.width = width;
        this.height = height;
        this.world = [];
        this.biomes = [];
        this.resources = [];
        this.seed = Math.random() * 1000;
        
        // Terrain types
        this.terrainTypes = {
            GRASS: 'grass',
            DIRT: 'dirt',
            STONE: 'stone',
            WATER: 'water',
            SAND: 'sand',
            MOUNTAIN: 'mountain',
            SNOW: 'snow',
            ICE: 'ice'
        };
        
        // Resource types
        this.resourceTypes = {
            TREE: 'tree',
            PINE_TREE: 'tree-pine',
            ROCK: 'rock',
            CRYSTAL: 'crystal'
        };
        
        // Biome definitions
        this.biomeTypes = {
            GRASSLAND: {
                name: 'grassland',
                primaryTerrain: this.terrainTypes.GRASS,
                secondaryTerrain: [this.terrainTypes.DIRT, this.terrainTypes.STONE],
                resources: [this.resourceTypes.TREE, this.resourceTypes.ROCK],
                resourceDensity: 0.15,
                waterChance: 0.1
            },
            FOREST: {
                name: 'forest',
                primaryTerrain: this.terrainTypes.GRASS,
                secondaryTerrain: [this.terrainTypes.DIRT],
                resources: [this.resourceTypes.TREE, this.resourceTypes.PINE_TREE],
                resourceDensity: 0.35,
                waterChance: 0.05
            },
            DESERT: {
                name: 'desert',
                primaryTerrain: this.terrainTypes.SAND,
                secondaryTerrain: [this.terrainTypes.STONE],
                resources: [this.resourceTypes.ROCK, this.resourceTypes.CRYSTAL],
                resourceDensity: 0.08,
                waterChance: 0.02
            },
            MOUNTAINS: {
                name: 'mountains',
                primaryTerrain: this.terrainTypes.MOUNTAIN,
                secondaryTerrain: [this.terrainTypes.STONE, this.terrainTypes.DIRT],
                resources: [this.resourceTypes.ROCK, this.resourceTypes.CRYSTAL],
                resourceDensity: 0.12,
                waterChance: 0.03
            },
            TUNDRA: {
                name: 'tundra',
                primaryTerrain: this.terrainTypes.SNOW,
                secondaryTerrain: [this.terrainTypes.ICE, this.terrainTypes.STONE],
                resources: [this.resourceTypes.PINE_TREE, this.resourceTypes.CRYSTAL],
                resourceDensity: 0.10,
                waterChance: 0.08
            }
        };
    }
    
    // Simplex noise implementation for terrain generation
    noise(x, y) {
        const n = Math.sin(x * 12.9898 + y * 78.233 + this.seed) * 43758.5453;
        return (n - Math.floor(n)) * 2 - 1;
    }
    
    // Octaved noise for more complex terrain
    octaveNoise(x, y, octaves = 4, persistence = 0.5) {
        let value = 0;
        let amplitude = 1;
        let frequency = 1;
        let maxValue = 0;
        
        for (let i = 0; i < octaves; i++) {
            value += this.noise(x * frequency, y * frequency) * amplitude;
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2;
        }
        
        return value / maxValue;
    }
    
    // Generate biome map
    generateBiomes() {
        const biomes = Object.values(this.biomeTypes);
        const biomeMap = [];
        
        for (let y = 0; y < this.height; y++) {
            biomeMap[y] = [];
            for (let x = 0; x < this.width; x++) {
                // Use noise to determine biome
                const temperature = this.octaveNoise(x * 0.05, y * 0.05, 3);
                const humidity = this.octaveNoise((x + 100) * 0.05, (y + 100) * 0.05, 3);
                
                let selectedBiome;
                
                if (temperature < -0.4) {
                    selectedBiome = this.biomeTypes.TUNDRA;
                } else if (temperature > 0.4 && humidity < -0.2) {
                    selectedBiome = this.biomeTypes.DESERT;
                } else if (humidity > 0.3) {
                    selectedBiome = this.biomeTypes.FOREST;
                } else if (temperature > 0.2 && Math.abs(humidity) < 0.2) {
                    selectedBiome = this.biomeTypes.MOUNTAINS;
                } else {
                    selectedBiome = this.biomeTypes.GRASSLAND;
                }
                
                biomeMap[y][x] = selectedBiome;
            }
        }
        
        return biomeMap;
    }
    
    // Generate base terrain
    generateTerrain() {
        const terrain = [];
        this.biomes = this.generateBiomes();
        
        for (let y = 0; y < this.height; y++) {
            terrain[y] = [];
            for (let x = 0; x < this.width; x++) {
                const biome = this.biomes[y][x];
                const elevation = this.octaveNoise(x * 0.1, y * 0.1, 4);
                const moisture = this.octaveNoise((x + 200) * 0.08, (y + 200) * 0.08, 3);
                
                let terrainType = biome.primaryTerrain;
                
                // Water generation
                if (elevation < -0.3 && Math.random() < biome.waterChance * 10) {
                    terrainType = this.terrainTypes.WATER;
                }
                // Secondary terrain variation
                else if (Math.random() < 0.3 && biome.secondaryTerrain.length > 0) {
                    const randomSecondary = Math.floor(Math.random() * biome.secondaryTerrain.length);
                    terrainType = biome.secondaryTerrain[randomSecondary];
                }
                
                terrain[y][x] = {
                    type: terrainType,
                    biome: biome.name,
                    elevation: elevation,
                    moisture: moisture,
                    resource: null,
                    harvestable: false,
                    harvested: false
                };
            }
        }
        
        return terrain;
    }
    
    // Place resources based on biome rules
    placeResources() {
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const tile = this.world[y][x];
                const biome = this.biomes[y][x];
                
                // Don't place resources on water
                if (tile.type === this.terrainTypes.WATER) continue;
                
                // Check if we should place a resource
                if (Math.random() < biome.resourceDensity) {
                    const availableResources = biome.resources;
                    const resourceType = availableResources[Math.floor(Math.random() * availableResources.length)];
                    
                    tile.resource = resourceType;
                    tile.harvestable = true;
                    
                    // Store resource location for easy access
                    this.resources.push({
                        x: x,
                        y: y,
                        type: resourceType,
                        respawnTime: this.getResourceRespawnTime(resourceType)
                    });
                }
            }
        }
    }
    
    // Get respawn time for different resource types
    getResourceRespawnTime(resourceType) {
        const respawnTimes = {
            [this.resourceTypes.TREE]: 30000, // 30 seconds
            [this.resourceTypes.PINE_TREE]: 45000, // 45 seconds
            [this.resourceTypes.ROCK]: 60000, // 60 seconds
            [this.resourceTypes.CRYSTAL]: 120000 // 2 minutes
        };
        return respawnTimes[resourceType] || 30000;
    }
    
    // Generate rivers and water bodies
    generateWaterBodies() {
        // Add some larger water bodies
        const numLakes = Math.floor(Math.random() * 3) + 1;
        
        for (let i = 0; i < numLakes; i++) {
            const centerX = Math.floor(Math.random() * (this.width - 6)) + 3;
            const centerY = Math.floor(Math.random() * (this.height - 6)) + 3;
            const radius = Math.floor(Math.random() * 3) + 2;
            
            for (let dy = -radius; dy <= radius; dy++) {
                for (let dx = -radius; dx <= radius; dx++) {
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance <= radius && Math.random() < 0.7) {
                        const x = centerX + dx;
                        const y = centerY + dy;
                        
                        if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
                            this.world[y][x].type = this.terrainTypes.WATER;
                            this.world[y][x].resource = null;
                            this.world[y][x].harvestable = false;
                        }
                    }
                }
            }
        }
    }
    
    // Generate the complete world
    generateWorld() {
        console.log('Generating world...');
        
        // Generate base terrain
        this.world = this.generateTerrain();
        
        // Add water bodies
        this.generateWaterBodies();
        
        // Place resources
        this.placeResources();
        
        console.log(`World generated: ${this.width}x${this.height} with ${this.resources.length} resources`);
        return this.world;
    }
    
    // Get world data for rendering
    getWorldData() {
        return {
            world: this.world,
            width: this.width,
            height: this.height,
            resources: this.resources,
            biomes: this.biomes
        };
    }
    
    // Regenerate world with new seed
    regenerateWorld() {
        this.seed = Math.random() * 1000;
        this.resources = [];
        return this.generateWorld();
    }
}

class WorldRenderer {
    constructor(containerId, worldGenerator) {
        this.container = document.getElementById(containerId);
        this.worldGenerator = worldGenerator;
        this.blocks = [];
        this.selectedBlock = null;
        this.onBlockClick = null;
        this.onResourceHarvest = null;
        this.playerPosition = { x: 0, y: 0 };
        
        // Resource harvest rewards
        this.harvestRewards = {
            'tree': { name: 'Wood', emoji: '🪵', amount: 3 },
            'tree-pine': { name: 'Pine Wood', emoji: '🌲', amount: 2 },
            'rock': { name: 'Stone', emoji: '🪨', amount: 5 },
            'crystal': { name: 'Crystal', emoji: '💎', amount: 1 }
        };
    }
    
    // Render the world grid
    renderWorld() {
        const worldData = this.worldGenerator.getWorldData();
        
        // Clear container
        this.container.innerHTML = '';
        this.blocks = [];
        
        // Set CSS variables for grid
        this.container.style.setProperty('--world-width', worldData.width);
        this.container.style.setProperty('--world-height', worldData.height);
        this.container.className = 'world-container';
        
        // Create blocks
        for (let y = 0; y < worldData.height; y++) {
            this.blocks[y] = [];
            for (let x = 0; x < worldData.width; x++) {
                const tile = worldData.world[y][x];
                const blockElement = this.createBlockElement(tile, x, y);
                this.container.appendChild(blockElement);
                this.blocks[y][x] = blockElement;
            }
        }
        
        console.log('World rendered successfully');
    }
    
    // Create individual block element
    createBlockElement(tile, x, y) {
        const block = document.createElement('div');
        block.className = `world-block block-${tile.type}`;
        block.dataset.x = x;
        block.dataset.y = y;
        block.dataset.biome = tile.biome;
        
        // Add biome class
        block.classList.add(`biome-${tile.biome}`);
        
        // Add resource if present
        if (tile.resource && !tile.harvested) {
            block.classList.add(`block-${tile.resource}`);
            if (tile.harvestable) {
                block.classList.add('block-interactive');
            }
        }
        
        // Add click handler
        block.addEventListener('click', (e) => this.handleBlockClick(e, tile, x, y));
        
        // Add hover effects for interactive blocks
        if (tile.harvestable && !tile.harvested) {
            block.addEventListener('mouseenter', () => {
                block.style.cursor = 'pointer';
            });
        }
        
        return block;
    }
    
    // Handle block click events
    handleBlockClick(event, tile, x, y) {
        event.stopPropagation();
        
        // Clear previous selection
        if (this.selectedBlock) {
            this.selectedBlock.classList.remove('block-selected');
        }
        
        // Select new block
        const blockElement = this.blocks[y][x];
        blockElement.classList.add('block-selected');
        this.selectedBlock = blockElement;
        
        // Handle resource harvesting
        if (tile.harvestable && tile.resource && !tile.harvested) {
            this.harvestResource(tile, blockElement, x, y);
        }
        
        // Call custom click handler if provided
        if (this.onBlockClick) {
            this.onBlockClick(tile, x, y);
        }
    }
    
    // Handle resource harvesting
    harvestResource(tile, blockElement, x, y) {
        if (tile.harvested) return;
        
        tile.harvested = true;
        const reward = this.harvestRewards[tile.resource];
        
        // Visual feedback
        blockElement.classList.add('block-harvested');
        blockElement.classList.remove('block-interactive');
        
        // Show harvest effect
        this.showHarvestEffect(blockElement, reward);
        
        // Schedule respawn
        const resource = this.worldGenerator.resources.find(r => r.x === x && r.y === y);
        if (resource) {
            setTimeout(() => {
                this.respawnResource(tile, blockElement, x, y);
            }, resource.respawnTime);
        }
        
        // Call custom harvest handler if provided
        if (this.onResourceHarvest) {
            this.onResourceHarvest(reward, x, y);
        }
        
        console.log(`Harvested ${reward.name} x${reward.amount} at (${x}, ${y})`);
    }
    
    // Show harvest animation effect
    showHarvestEffect(blockElement, reward) {
        const effect = document.createElement('div');
        effect.className = 'harvest-effect';
        effect.innerHTML = `+${reward.amount} ${reward.emoji}`;
        effect.style.color = '#4CAF50';
        effect.style.fontWeight = 'bold';
        
        blockElement.appendChild(effect);
        
        // Remove effect after animation
        setTimeout(() => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        }, 1000);
    }
    
    // Respawn harvested resource
    respawnResource(tile, blockElement, x, y) {
        tile.harvested = false;
        blockElement.classList.remove('block-harvested');
        blockElement.classList.add('block-interactive');
        
        console.log(`Resource respawned at (${x}, ${y})`);
    }
    
    // Update player position on the world
    updatePlayerPosition(x, y) {
        // Convert percentage to grid coordinates
        const gridX = Math.floor((x / 100) * this.worldGenerator.width);
        const gridY = Math.floor((y / 100) * this.worldGenerator.height);
        
        this.playerPosition = { x: gridX, y: gridY };
        
        // Get current tile information
        if (gridX >= 0 && gridX < this.worldGenerator.width && 
            gridY >= 0 && gridY < this.worldGenerator.height) {
            const currentTile = this.worldGenerator.world[gridY][gridX];
            return {
                tile: currentTile,
                biome: currentTile.biome,
                terrain: currentTile.type,
                coordinates: { x: gridX, y: gridY }
            };
        }
        
        return null;
    }
    
    // Apply weather effects
    applyWeatherEffect(weather) {
        this.container.classList.remove('weather-rain', 'weather-snow');
        
        if (weather === 'rain') {
            this.container.classList.add('weather-rain');
        } else if (weather === 'snow') {
            this.container.classList.add('weather-snow');
        }
    }
    
    // Apply day/night cycle
    applyTimeOfDay(isNight) {
        this.container.classList.toggle('world-night', isNight);
    }
    
    // Get block at specific coordinates
    getBlockAt(x, y) {
        if (x >= 0 && x < this.worldGenerator.width && 
            y >= 0 && y < this.worldGenerator.height) {
            return this.worldGenerator.world[y][x];
        }
        return null;
    }
    
    // Clear block selection
    clearSelection() {
        if (this.selectedBlock) {
            this.selectedBlock.classList.remove('block-selected');
            this.selectedBlock = null;
        }
    }
}

// Minimap renderer
class MinimapRenderer {
    constructor(containerId, worldGenerator) {
        this.container = document.getElementById(containerId);
        this.worldGenerator = worldGenerator;
        this.playerMarker = null;
        this.scale = 0.2; // How much to scale down the world
    }
    
    render() {
        const worldData = this.worldGenerator.getWorldData();
        const minimapWidth = Math.max(1, Math.floor(worldData.width * this.scale));
        const minimapHeight = Math.max(1, Math.floor(worldData.height * this.scale));
        
        // Clear and setup container
        this.container.innerHTML = '';
        this.container.className = 'world-minimap';
        this.container.style.setProperty('--minimap-width', minimapWidth);
        this.container.style.setProperty('--minimap-height', minimapHeight);
        
        // Create minimap blocks (simplified view)
        for (let y = 0; y < minimapHeight; y++) {
            for (let x = 0; x < minimapWidth; x++) {
                // Sample the world at this position
                const worldX = Math.floor((x / minimapWidth) * worldData.width);
                const worldY = Math.floor((y / minimapHeight) * worldData.height);
                const tile = worldData.world[worldY][worldX];
                
                const block = document.createElement('div');
                block.className = `minimap-block block-${tile.type}`;
                this.container.appendChild(block);
            }
        }
        
        // Add player marker
        this.playerMarker = document.createElement('div');
        this.playerMarker.className = 'minimap-player';
        this.container.appendChild(this.playerMarker);
    }
    
    updatePlayerPosition(worldX, worldY) {
        if (this.playerMarker) {
            const minimapX = (worldX / this.worldGenerator.width) * 100;
            const minimapY = (worldY / this.worldGenerator.height) * 100;
            
            this.playerMarker.style.left = minimapX + '%';
            this.playerMarker.style.top = minimapY + '%';
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WorldGenerator, WorldRenderer, MinimapRenderer };
}