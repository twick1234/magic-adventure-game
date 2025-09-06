/**
 * AI Character Movement and Behavior System
 * Handles all character AI behaviors, pathfinding, and autonomous actions
 */

class CharacterAI {
    constructor(character, gameWorld) {
        this.character = character;
        this.gameWorld = gameWorld;
        this.lastUpdate = Date.now();
        this.behaviorState = 'idle';
        this.targetPosition = null;
        this.pathIndex = 0;
        this.lastInteraction = 0;
        this.behaviorTimer = 0;
        this.alertness = 0; // 0-100, affects behavior intensity
        
        this.initializeBehavior();
    }

    initializeBehavior() {
        // Set up movement pattern based on character type
        this.setupMovementPattern();
        
        // Initialize behavior timers
        this.nextBehaviorChange = Date.now() + Math.random() * 10000 + 5000; // 5-15 seconds
        this.nextDialogue = 0;
        this.lastPlayerInteraction = 0;
    }

    setupMovementPattern() {
        const patterns = this.character.movementPattern;
        
        switch (patterns) {
            case 'stationary':
                this.targetPosition = { ...this.character.position };
                break;
                
            case 'small_area':
                this.setupSmallAreaPatrol();
                break;
                
            case 'patrol':
                this.setupPatrolRoute();
                break;
                
            case 'wide_patrol':
                this.setupWidePatrolRoute();
                break;
                
            case 'random':
                this.setupRandomMovement();
                break;
                
            case 'aggressive_patrol':
                this.setupAggressivePatrol();
                break;
                
            case 'guard_area':
                this.setupGuardBehavior();
                break;
                
            case 'follow_player':
                this.setupFollowBehavior();
                break;
                
            case 'traveling':
                this.setupTravelingBehavior();
                break;
                
            case 'work_area':
                this.setupWorkAreaBehavior();
                break;
        }
    }

    setupSmallAreaPatrol() {
        const baseX = this.character.position.x;
        const baseY = this.character.position.y;
        
        this.patrolPoints = [
            { x: baseX, y: baseY },
            { x: baseX + Math.random() * 10 - 5, y: baseY + Math.random() * 10 - 5 },
            { x: baseX + Math.random() * 10 - 5, y: baseY + Math.random() * 10 - 5 },
            { x: baseX + Math.random() * 10 - 5, y: baseY + Math.random() * 10 - 5 }
        ];
        
        this.currentPatrolIndex = 0;
        this.targetPosition = this.patrolPoints[0];
    }

    setupPatrolRoute() {
        if (this.character.patrolPoints) {
            this.patrolPoints = [...this.character.patrolPoints];
        } else {
            this.setupSmallAreaPatrol(); // Fallback
        }
        this.currentPatrolIndex = 0;
        this.targetPosition = this.patrolPoints[0];
    }

    setupWidePatrolRoute() {
        if (this.character.patrolPoints) {
            this.patrolPoints = [...this.character.patrolPoints];
        } else {
            // Create wider patrol area
            const baseX = this.character.position.x;
            const baseY = this.character.position.y;
            
            this.patrolPoints = [
                { x: baseX - 15, y: baseY - 15 },
                { x: baseX + 15, y: baseY - 15 },
                { x: baseX + 15, y: baseY + 15 },
                { x: baseX - 15, y: baseY + 15 }
            ];
        }
        this.currentPatrolIndex = 0;
        this.targetPosition = this.patrolPoints[0];
    }

    setupRandomMovement() {
        this.randomMoveTimer = Date.now() + Math.random() * 8000 + 2000; // 2-10 seconds
        this.generateRandomTarget();
    }

    setupAggressivePatrol() {
        const territoryRadius = this.character.territoryRadius || 10;
        const centerX = this.character.position.x;
        const centerY = this.character.position.y;
        
        this.territoryCenter = { x: centerX, y: centerY };
        this.territoryRadius = territoryRadius;
        this.aggressionLevel = 0;
        this.generateRandomTarget();
    }

    setupGuardBehavior() {
        this.guardPosition = { ...this.character.position };
        this.guardRadius = 5;
        this.targetPosition = { ...this.guardPosition };
    }

    setupFollowBehavior() {
        this.followDistance = 3;
        this.maxFollowDistance = 15;
    }

    setupTravelingBehavior() {
        if (this.character.schedule) {
            this.schedule = this.character.schedule;
            this.updateScheduleTarget();
        } else {
            this.setupRandomMovement();
        }
    }

    setupWorkAreaBehavior() {
        const workArea = {
            x: this.character.position.x,
            y: this.character.position.y,
            width: 8,
            height: 8
        };
        
        this.workPoints = [
            { x: workArea.x - 2, y: workArea.y },
            { x: workArea.x + 2, y: workArea.y },
            { x: workArea.x, y: workArea.y - 2 },
            { x: workArea.x, y: workArea.y + 2 }
        ];
        
        this.currentWorkIndex = 0;
        this.targetPosition = this.workPoints[0];
    }

    update(deltaTime, playerPosition, allCharacters) {
        const now = Date.now();
        
        // Update timers
        this.behaviorTimer += deltaTime;
        
        // Check for player proximity and update alertness
        this.updateAlertness(playerPosition);
        
        // Update behavior based on character type and current state
        this.updateBehavior(deltaTime, playerPosition, allCharacters);
        
        // Move towards target position
        this.updateMovement(deltaTime);
        
        // Update behavior state changes
        if (now > this.nextBehaviorChange) {
            this.changeBehavior();
            this.nextBehaviorChange = now + Math.random() * 15000 + 5000;
        }
        
        this.lastUpdate = now;
    }

    updateAlertness(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        const interactionRadius = this.character.interactionRadius * 2;
        
        if (distance <= interactionRadius) {
            this.alertness = Math.min(100, this.alertness + 5);
            this.lastPlayerInteraction = Date.now();
        } else {
            this.alertness = Math.max(0, this.alertness - 1);
        }
    }

    updateBehavior(deltaTime, playerPosition, allCharacters) {
        switch (this.character.type) {
            case 'monster':
                this.updateMonsterBehavior(playerPosition, allCharacters);
                break;
                
            case 'companion':
                this.updateCompanionBehavior(playerPosition);
                break;
                
            case 'merchant':
                this.updateMerchantBehavior(playerPosition);
                break;
                
            case 'villager':
                this.updateVillagerBehavior(playerPosition);
                break;
                
            default:
                this.updateGenericBehavior(playerPosition);
                break;
        }
    }

    updateMonsterBehavior(playerPosition, allCharacters) {
        const distance = this.distanceTo(playerPosition);
        const detectionRadius = this.character.interactionRadius * 2;
        const attackRadius = this.character.interactionRadius;
        
        if (distance <= attackRadius) {
            this.behaviorState = 'attacking';
            this.targetPosition = { ...playerPosition };
        } else if (distance <= detectionRadius) {
            this.behaviorState = 'pursuing';
            this.targetPosition = { ...playerPosition };
            this.aggressionLevel = Math.min(100, this.aggressionLevel + 2);
        } else if (this.aggressionLevel > 0) {
            this.behaviorState = 'searching';
            this.aggressionLevel = Math.max(0, this.aggressionLevel - 1);
            
            // Search pattern - move towards last known player position
            if (!this.targetPosition || this.hasReachedTarget()) {
                this.generateSearchTarget();
            }
        } else {
            this.behaviorState = 'patrolling';
            this.updatePatrolBehavior();
        }
    }

    updateCompanionBehavior(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        
        if (distance > this.maxFollowDistance) {
            // Teleport if too far away
            this.character.position = {
                x: playerPosition.x + (Math.random() - 0.5) * 6,
                y: playerPosition.y + (Math.random() - 0.5) * 6
            };
            this.behaviorState = 'following';
        } else if (distance > this.followDistance) {
            this.behaviorState = 'following';
            this.targetPosition = {
                x: playerPosition.x + (Math.random() - 0.5) * this.followDistance,
                y: playerPosition.y + (Math.random() - 0.5) * this.followDistance
            };
        } else {
            this.behaviorState = 'idle';
            if (Math.random() < 0.01) { // Occasionally explore nearby
                this.targetPosition = {
                    x: this.character.position.x + (Math.random() - 0.5) * 10,
                    y: this.character.position.y + (Math.random() - 0.5) * 10
                };
            }
        }
    }

    updateMerchantBehavior(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        
        if (distance <= this.character.interactionRadius * 1.5) {
            this.behaviorState = 'interested';
            // Face the player
            this.faceTarget(playerPosition);
        } else {
            this.behaviorState = 'working';
            this.updatePatrolBehavior(); // Merchants move around their area
        }
    }

    updateVillagerBehavior(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        
        if (distance <= this.character.interactionRadius) {
            this.behaviorState = 'social';
            this.faceTarget(playerPosition);
        } else {
            this.behaviorState = 'daily_routine';
            
            if (this.character.schedule) {
                this.updateScheduleTarget();
            } else {
                this.updatePatrolBehavior();
            }
        }
    }

    updateGenericBehavior(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        
        if (distance <= this.character.interactionRadius) {
            this.behaviorState = 'attentive';
            this.faceTarget(playerPosition);
        } else {
            this.behaviorState = 'idle';
            this.updatePatrolBehavior();
        }
    }

    updatePatrolBehavior() {
        if (!this.patrolPoints || this.patrolPoints.length === 0) {
            return;
        }
        
        if (this.hasReachedTarget()) {
            this.currentPatrolIndex = (this.currentPatrolIndex + 1) % this.patrolPoints.length;
            this.targetPosition = { ...this.patrolPoints[this.currentPatrolIndex] };
        }
    }

    updateScheduleTarget() {
        const hour = new Date().getHours();
        let scheduleKey = 'morning';
        
        if (hour >= 12 && hour < 18) {
            scheduleKey = 'afternoon';
        } else if (hour >= 18) {
            scheduleKey = 'evening';
        }
        
        if (this.schedule[scheduleKey]) {
            this.targetPosition = { ...this.schedule[scheduleKey] };
        }
    }

    updateMovement(deltaTime) {
        if (!this.targetPosition) return;
        
        const speed = this.getMovementSpeed();
        const dx = this.targetPosition.x - this.character.position.x;
        const dy = this.targetPosition.y - this.character.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance > 1) {
            const moveDistance = speed * deltaTime / 1000;
            const ratio = Math.min(moveDistance / distance, 1);
            
            this.character.position.x += dx * ratio;
            this.character.position.y += dy * ratio;
            
            // Keep within game boundaries
            this.character.position.x = Math.max(5, Math.min(95, this.character.position.x));
            this.character.position.y = Math.max(5, Math.min(95, this.character.position.y));
        }
    }

    generateRandomTarget() {
        const range = 20;
        this.targetPosition = {
            x: Math.max(5, Math.min(95, this.character.position.x + (Math.random() - 0.5) * range)),
            y: Math.max(5, Math.min(95, this.character.position.y + (Math.random() - 0.5) * range))
        };
    }

    generateSearchTarget() {
        const searchRadius = 15;
        this.targetPosition = {
            x: Math.max(5, Math.min(95, this.character.position.x + (Math.random() - 0.5) * searchRadius)),
            y: Math.max(5, Math.min(95, this.character.position.y + (Math.random() - 0.5) * searchRadius))
        };
    }

    changeBehavior() {
        // Random behavior changes to make NPCs feel more alive
        if (Math.random() < 0.3) {
            this.generateRandomTarget();
        }
        
        // Emit behavior change event for dialogue system
        if (this.gameWorld && this.gameWorld.eventManager) {
            this.gameWorld.eventManager.emit('character_behavior_change', {
                character: this.character,
                newBehavior: this.behaviorState,
                alertness: this.alertness
            });
        }
    }

    getMovementSpeed() {
        let baseSpeed = 15; // pixels per second
        
        // Adjust speed based on character type
        switch (this.character.type) {
            case 'monster':
                baseSpeed = 20;
                break;
            case 'companion':
                baseSpeed = 25;
                break;
            case 'elder':
                baseSpeed = 8;
                break;
        }
        
        // Adjust speed based on behavior state
        switch (this.behaviorState) {
            case 'pursuing':
            case 'attacking':
                baseSpeed *= 1.5;
                break;
            case 'following':
                baseSpeed *= 1.2;
                break;
            case 'idle':
                baseSpeed *= 0.7;
                break;
        }
        
        return baseSpeed;
    }

    distanceTo(position) {
        if (!position) return Infinity;
        
        const dx = this.character.position.x - position.x;
        const dy = this.character.position.y - position.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    hasReachedTarget() {
        if (!this.targetPosition) return true;
        
        return this.distanceTo(this.targetPosition) < 2;
    }

    faceTarget(targetPosition) {
        // Store facing direction for visual updates
        const dx = targetPosition.x - this.character.position.x;
        this.character.facingDirection = dx >= 0 ? 'right' : 'left';
    }

    canInteractWith(playerPosition) {
        const distance = this.distanceTo(playerPosition);
        return distance <= this.character.interactionRadius;
    }

    onPlayerInteraction(player) {
        this.lastPlayerInteraction = Date.now();
        this.alertness = Math.min(100, this.alertness + 20);
        
        // Face the player during interaction
        this.faceTarget(player.position);
        
        // Set behavior state for interaction
        this.behaviorState = 'interacting';
        
        // Stop moving during interaction
        this.targetPosition = { ...this.character.position };
        
        // Return interaction response
        return this.generateInteractionResponse(player);
    }

    generateInteractionResponse(player) {
        // This will be handled by the dialogue system
        return {
            characterId: this.character.id,
            behaviorState: this.behaviorState,
            alertness: this.alertness,
            canTrade: this.character.type === 'merchant',
            hasQuests: this.character.quests && this.character.quests.length > 0,
            mood: this.getCurrentMood()
        };
    }

    getCurrentMood() {
        if (this.alertness > 70) return 'excited';
        if (this.alertness > 40) return 'interested';
        if (this.behaviorState === 'attacking') return 'hostile';
        if (this.behaviorState === 'following') return 'loyal';
        return 'calm';
    }

    // Method to get current action for display
    getCurrentAction() {
        const now = Date.now();
        
        // Return idle action based on behavior state
        if (this.character.dialogue && this.character.dialogue.idle) {
            const idleActions = this.character.dialogue.idle;
            const index = Math.floor((now / 5000) % idleActions.length);
            return idleActions[index];
        }
        
        return '*stands quietly*';
    }

    // Debug info for development
    getDebugInfo() {
        return {
            id: this.character.id,
            position: this.character.position,
            behaviorState: this.behaviorState,
            alertness: this.alertness,
            targetPosition: this.targetPosition,
            movementPattern: this.character.movementPattern
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CharacterAI;
}