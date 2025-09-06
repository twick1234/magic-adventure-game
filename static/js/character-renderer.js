/**
 * Character Rendering and Visual System
 * Handles all character visualization, animations, and UI elements
 */

class CharacterRenderer {
    constructor(gameCanvas, gameWorld) {
        this.canvas = gameCanvas;
        this.gameWorld = gameWorld;
        this.characterElements = new Map();
        this.animationFrameId = null;
        this.isAnimating = false;
        
        this.initializeRenderer();
    }

    initializeRenderer() {
        // Create character layer container
        this.characterLayer = document.createElement('div');
        this.characterLayer.className = 'character-layer';
        this.characterLayer.style.position = 'absolute';
        this.characterLayer.style.top = '0';
        this.characterLayer.style.left = '0';
        this.characterLayer.style.width = '100%';
        this.characterLayer.style.height = '100%';
        this.characterLayer.style.pointerEvents = 'none';
        this.characterLayer.style.zIndex = '10';
        
        this.canvas.appendChild(this.characterLayer);
        
        // Start animation loop
        this.startAnimationLoop();
    }

    createCharacterElement(character) {
        const element = document.createElement('div');
        element.className = 'npc-character';
        element.id = `character-${character.id}`;
        element.style.position = 'absolute';
        element.style.pointerEvents = 'auto';
        element.style.cursor = 'pointer';
        element.style.zIndex = '15';
        
        // Create character visual structure
        element.innerHTML = `
            <div class="character-sprite">
                <div class="character-emoji">${character.emoji}</div>
                <div class="character-shadow"></div>
            </div>
            <div class="character-ui">
                <div class="character-name">${character.name}</div>
                <div class="character-status">
                    <div class="health-bar">
                        <div class="health-fill" style="width: ${(character.health / this.getMaxHealth(character)) * 100}%"></div>
                    </div>
                    <div class="character-level">Lv.${character.level}</div>
                </div>
                <div class="interaction-hint" style="display: none;">
                    <span class="interaction-icon">💬</span>
                    <span class="interaction-text">Talk</span>
                </div>
            </div>
        `;
        
        this.setupCharacterInteraction(element, character);
        this.updateCharacterPosition(element, character);
        this.updateCharacterVisualState(element, character);
        
        this.characterLayer.appendChild(element);
        this.characterElements.set(character.id, element);
        
        return element;
    }

    setupCharacterInteraction(element, character) {
        let interactionTimeout;
        
        // Click interaction
        element.addEventListener('click', (e) => {
            e.stopPropagation();
            this.handleCharacterClick(character);
        });
        
        // Hover effects
        element.addEventListener('mouseenter', () => {
            this.showInteractionHint(element, character);
            element.classList.add('character-hover');
        });
        
        element.addEventListener('mouseleave', () => {
            this.hideInteractionHint(element);
            element.classList.remove('character-hover');
        });
        
        // Touch support for mobile
        element.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.showInteractionHint(element, character);
            
            clearTimeout(interactionTimeout);
            interactionTimeout = setTimeout(() => {
                this.handleCharacterClick(character);
            }, 200);
        });
        
        element.addEventListener('touchend', (e) => {
            e.preventDefault();
            clearTimeout(interactionTimeout);
            this.hideInteractionHint(element);
        });
    }

    showInteractionHint(element, character) {
        const hint = element.querySelector('.interaction-hint');
        if (hint) {
            const preview = this.getInteractionPreview(character);
            hint.querySelector('.interaction-icon').textContent = preview.icon;
            hint.querySelector('.interaction-text').textContent = preview.type;
            hint.style.display = 'block';
        }
    }

    hideInteractionHint(element) {
        const hint = element.querySelector('.interaction-hint');
        if (hint) {
            hint.style.display = 'none';
        }
    }

    getInteractionPreview(character) {
        let type = 'Talk';
        let icon = '💬';
        
        if (character.type === 'monster' && character.personality && character.personality.aggression > 70) {
            type = 'Fight';
            icon = '⚔️';
        } else if (character.type === 'merchant') {
            type = 'Trade';
            icon = '💰';
        } else if (character.quests && character.quests.length > 0) {
            type = 'Quest';
            icon = '❗';
        }
        
        return { type, icon };
    }

    handleCharacterClick(character) {
        // Get player position for distance check
        const playerPosition = this.gameWorld.player ? this.gameWorld.player.position : { x: 50, y: 70 };
        
        // Check if player is close enough to interact
        const distance = this.calculateDistance(playerPosition, character.position);
        const maxInteractionDistance = character.interactionRadius + 2; // Add some tolerance
        
        if (distance <= maxInteractionDistance) {
            // Trigger interaction through game world
            if (this.gameWorld && this.gameWorld.handleCharacterInteraction) {
                this.gameWorld.handleCharacterInteraction(character);
            }
        } else {
            // Show "too far away" message
            this.showFloatingText(character, "Too far away!", 'warning');
        }
    }

    updateCharacterElement(character) {
        const element = this.characterElements.get(character.id);
        if (!element) {
            return this.createCharacterElement(character);
        }
        
        this.updateCharacterPosition(element, character);
        this.updateCharacterVisualState(element, character);
        
        return element;
    }

    updateCharacterPosition(element, character) {
        if (!element || !character.position) return;
        
        const canvasRect = this.canvas.getBoundingClientRect();
        const x = (character.position.x / 100) * canvasRect.width;
        const y = (character.position.y / 100) * canvasRect.height;
        
        // Apply smooth movement
        const currentX = parseFloat(element.style.left) || x;
        const currentY = parseFloat(element.style.top) || y;
        
        if (Math.abs(currentX - x) > 1 || Math.abs(currentY - y) > 1) {
            element.style.transition = 'left 0.3s ease, top 0.3s ease';
        } else {
            element.style.transition = 'none';
        }
        
        element.style.left = x + 'px';
        element.style.top = y + 'px';
        element.style.transform = 'translate(-50%, -100%)'; // Center bottom of sprite
    }

    updateCharacterVisualState(element, character) {
        if (!element) return;
        
        const sprite = element.querySelector('.character-sprite');
        const emoji = element.querySelector('.character-emoji');
        const healthBar = element.querySelector('.health-fill');
        
        // Update health bar
        if (healthBar) {
            const healthPercent = (character.health / this.getMaxHealth(character)) * 100;
            healthBar.style.width = healthPercent + '%';
            
            // Color based on health
            if (healthPercent > 70) {
                healthBar.style.backgroundColor = '#4ade80'; // Green
            } else if (healthPercent > 30) {
                healthBar.style.backgroundColor = '#fbbf24'; // Yellow
            } else {
                healthBar.style.backgroundColor = '#ef4444'; // Red
            }
        }
        
        // Update facing direction
        if (character.facingDirection === 'left') {
            emoji.style.transform = 'scaleX(-1)';
        } else {
            emoji.style.transform = 'scaleX(1)';
        }
        
        // Update visual state based on character AI state
        this.updateCharacterAnimationState(element, character);
    }

    updateCharacterAnimationState(element, character) {
        const sprite = element.querySelector('.character-sprite');
        
        // Remove existing state classes
        sprite.classList.remove('moving', 'idle', 'attacking', 'interacting', 'alert');
        
        // Add appropriate state class based on AI
        if (character.ai) {
            switch (character.ai.behaviorState) {
                case 'pursuing':
                case 'following':
                    sprite.classList.add('moving', 'alert');
                    break;
                    
                case 'attacking':
                    sprite.classList.add('attacking');
                    break;
                    
                case 'interacting':
                    sprite.classList.add('interacting');
                    break;
                    
                case 'patrolling':
                    sprite.classList.add('moving');
                    break;
                    
                default:
                    sprite.classList.add('idle');
            }
            
            // Add alertness indicator
            if (character.ai.alertness > 50) {
                sprite.classList.add('alert');
            }
        } else {
            sprite.classList.add('idle');
        }
    }

    removeCharacterElement(characterId) {
        const element = this.characterElements.get(characterId);
        if (element) {
            element.remove();
            this.characterElements.delete(characterId);
        }
    }

    renderAllCharacters(characters) {
        // Update existing characters and create new ones
        characters.forEach(character => {
            this.updateCharacterElement(character);
        });
        
        // Remove characters that no longer exist
        for (const [characterId, element] of this.characterElements) {
            if (!characters.find(char => char.id === characterId)) {
                this.removeCharacterElement(characterId);
            }
        }
    }

    showFloatingText(character, text, type = 'info', duration = 2000) {
        const element = this.characterElements.get(character.id);
        if (!element) return;
        
        const floatingText = document.createElement('div');
        floatingText.className = `floating-text floating-text-${type}`;
        floatingText.textContent = text;
        floatingText.style.position = 'absolute';
        floatingText.style.left = '50%';
        floatingText.style.top = '-20px';
        floatingText.style.transform = 'translateX(-50%)';
        floatingText.style.pointerEvents = 'none';
        floatingText.style.zIndex = '20';
        
        element.appendChild(floatingText);
        
        // Animate the floating text
        floatingText.animate([
            { opacity: 0, transform: 'translateX(-50%) translateY(0px)' },
            { opacity: 1, transform: 'translateX(-50%) translateY(-10px)' },
            { opacity: 1, transform: 'translateX(-50%) translateY(-20px)' },
            { opacity: 0, transform: 'translateX(-50%) translateY(-30px)' }
        ], {
            duration: duration,
            easing: 'ease-out'
        }).onfinish = () => {
            floatingText.remove();
        };
    }

    showCharacterAction(character, action, duration = 3000) {
        const element = this.characterElements.get(character.id);
        if (!element) return;
        
        // Create action bubble
        const actionBubble = document.createElement('div');
        actionBubble.className = 'action-bubble';
        actionBubble.textContent = action;
        actionBubble.style.position = 'absolute';
        actionBubble.style.left = '50%';
        actionBubble.style.top = '-40px';
        actionBubble.style.transform = 'translateX(-50%)';
        actionBubble.style.pointerEvents = 'none';
        actionBubble.style.zIndex = '18';
        
        element.appendChild(actionBubble);
        
        // Remove after duration
        setTimeout(() => {
            if (actionBubble.parentNode) {
                actionBubble.remove();
            }
        }, duration);
    }

    highlightCharacter(character, highlight = true) {
        const element = this.characterElements.get(character.id);
        if (element) {
            if (highlight) {
                element.classList.add('character-highlighted');
            } else {
                element.classList.remove('character-highlighted');
            }
        }
    }

    showCharacterPath(character, path) {
        // Create path visualization for debugging
        if (!path || path.length === 0) return;
        
        const pathElement = document.createElement('div');
        pathElement.className = 'character-path';
        pathElement.style.position = 'absolute';
        pathElement.style.pointerEvents = 'none';
        pathElement.style.zIndex = '5';
        
        // Draw path points
        path.forEach((point, index) => {
            const pathPoint = document.createElement('div');
            pathPoint.className = 'path-point';
            pathPoint.style.position = 'absolute';
            pathPoint.style.left = point.x + '%';
            pathPoint.style.top = point.y + '%';
            pathPoint.style.transform = 'translate(-50%, -50%)';
            pathPoint.textContent = index;
            
            pathElement.appendChild(pathPoint);
        });
        
        this.characterLayer.appendChild(pathElement);
        
        // Remove path after 5 seconds
        setTimeout(() => {
            if (pathElement.parentNode) {
                pathElement.remove();
            }
        }, 5000);
    }

    startAnimationLoop() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        const animate = () => {
            this.updateAnimations();
            this.animationFrameId = requestAnimationFrame(animate);
        };
        animate();
    }

    stopAnimationLoop() {
        this.isAnimating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }

    updateAnimations() {
        // Update character animations based on their states
        for (const [characterId, element] of this.characterElements) {
            const character = this.gameWorld.getCharacterById(characterId);
            if (character && character.ai) {
                this.updateCharacterAnimation(element, character);
            }
        }
    }

    updateCharacterAnimation(element, character) {
        const emoji = element.querySelector('.character-emoji');
        if (!emoji) return;
        
        // Simple bob animation for moving characters
        if (character.ai && character.ai.behaviorState === 'moving') {
            const time = Date.now() * 0.005;
            const bob = Math.sin(time) * 2;
            emoji.style.transform += ` translateY(${bob}px)`;
        }
    }

    getMaxHealth(character) {
        // Calculate max health based on character level and type
        let baseHealth = 100;
        
        switch (character.type) {
            case 'monster':
                baseHealth = 80 + (character.level * 5);
                break;
            case 'elder':
            case 'quest_giver':
                baseHealth = 150 + (character.level * 3);
                break;
            case 'companion':
                baseHealth = 60 + (character.level * 4);
                break;
            default:
                baseHealth = 80 + (character.level * 3);
        }
        
        return baseHealth;
    }

    calculateDistance(pos1, pos2) {
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Utility method to create particle effects
    createParticleEffect(character, effectType, duration = 2000) {
        const element = this.characterElements.get(character.id);
        if (!element) return;
        
        const particles = document.createElement('div');
        particles.className = `particle-effect particle-${effectType}`;
        particles.style.position = 'absolute';
        particles.style.left = '50%';
        particles.style.top = '50%';
        particles.style.transform = 'translate(-50%, -50%)';
        particles.style.pointerEvents = 'none';
        particles.style.zIndex = '25';
        
        // Create multiple particles
        for (let i = 0; i < 10; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.position = 'absolute';
            particle.style.left = (Math.random() - 0.5) * 40 + 'px';
            particle.style.top = (Math.random() - 0.5) * 40 + 'px';
            
            // Set particle content based on effect type
            switch (effectType) {
                case 'magic':
                    particle.textContent = '✨';
                    break;
                case 'damage':
                    particle.textContent = '💥';
                    break;
                case 'heal':
                    particle.textContent = '💚';
                    break;
                default:
                    particle.textContent = '⚡';
            }
            
            particles.appendChild(particle);
        }
        
        element.appendChild(particles);
        
        // Animate and remove particles
        setTimeout(() => {
            if (particles.parentNode) {
                particles.remove();
            }
        }, duration);
    }

    // Debug method to show character info
    showDebugInfo(character, show = true) {
        const element = this.characterElements.get(character.id);
        if (!element) return;
        
        let debugInfo = element.querySelector('.debug-info');
        
        if (show && !debugInfo) {
            debugInfo = document.createElement('div');
            debugInfo.className = 'debug-info';
            debugInfo.style.position = 'absolute';
            debugInfo.style.left = '100%';
            debugInfo.style.top = '0';
            debugInfo.style.background = 'rgba(0,0,0,0.8)';
            debugInfo.style.color = 'white';
            debugInfo.style.padding = '5px';
            debugInfo.style.fontSize = '10px';
            debugInfo.style.whiteSpace = 'nowrap';
            debugInfo.style.zIndex = '30';
            
            element.appendChild(debugInfo);
        }
        
        if (debugInfo) {
            if (show) {
                const ai = character.ai;
                debugInfo.innerHTML = `
                    ID: ${character.id}<br>
                    State: ${ai ? ai.behaviorState : 'none'}<br>
                    Alert: ${ai ? ai.alertness : 0}<br>
                    Pos: ${Math.round(character.position.x)}, ${Math.round(character.position.y)}
                `;
                debugInfo.style.display = 'block';
            } else {
                debugInfo.style.display = 'none';
            }
        }
    }

    // Clean up method
    destroy() {
        this.stopAnimationLoop();
        
        // Remove all character elements
        for (const element of this.characterElements.values()) {
            element.remove();
        }
        this.characterElements.clear();
        
        // Remove character layer
        if (this.characterLayer && this.characterLayer.parentNode) {
            this.characterLayer.remove();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CharacterRenderer;
}