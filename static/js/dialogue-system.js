/**
 * Dialogue and Interaction System
 * Handles all character interactions, dialogue trees, and conversation management
 */

class DialogueSystem {
    constructor(gameWorld) {
        this.gameWorld = gameWorld;
        this.currentDialogue = null;
        this.activeCharacter = null;
        this.dialogueHistory = [];
        this.playerChoices = [];
        
        this.initializeUI();
    }

    initializeUI() {
        // Create dialogue UI elements if they don't exist
        this.createDialogueUI();
        this.bindEvents();
    }

    createDialogueUI() {
        // Check if dialogue UI already exists
        if (document.getElementById('dialogue-container')) {
            return;
        }

        const dialogueHTML = `
            <div id="dialogue-container" class="dialogue-container hidden">
                <div class="dialogue-box">
                    <div class="character-info">
                        <div class="character-avatar" id="dialogue-avatar">🧙‍♂️</div>
                        <div class="character-details">
                            <div class="character-name" id="dialogue-name">Character Name</div>
                            <div class="character-mood" id="dialogue-mood">Neutral</div>
                        </div>
                    </div>
                    
                    <div class="dialogue-content">
                        <div class="dialogue-text" id="dialogue-text">
                            Welcome to the dialogue system!
                        </div>
                        
                        <div class="dialogue-choices" id="dialogue-choices">
                            <!-- Dynamic choice buttons will be inserted here -->
                        </div>
                    </div>
                    
                    <div class="dialogue-controls">
                        <button class="dialogue-btn" id="dialogue-continue">Continue</button>
                        <button class="dialogue-btn dialogue-btn-secondary" id="dialogue-close">Close</button>
                    </div>
                </div>
            </div>
            
            <!-- Quick interaction popup -->
            <div id="interaction-popup" class="interaction-popup hidden">
                <div class="popup-content">
                    <div class="popup-character" id="popup-avatar">🧙‍♂️</div>
                    <div class="popup-text" id="popup-text">Hello, traveler!</div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogueHTML);
    }

    bindEvents() {
        const continueBtn = document.getElementById('dialogue-continue');
        const closeBtn = document.getElementById('dialogue-close');

        if (continueBtn) {
            continueBtn.addEventListener('click', () => this.continueDialogue());
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeDialogue());
        }

        // ESC key to close dialogue
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isDialogueOpen()) {
                this.closeDialogue();
            }
        });
    }

    startInteraction(character, player) {
        this.activeCharacter = character;
        
        // Determine interaction type
        const interactionType = this.determineInteractionType(character, player);
        
        switch (interactionType) {
            case 'combat':
                return this.startCombatInteraction(character, player);
            
            case 'trade':
                return this.startTradeInteraction(character, player);
            
            case 'quest':
                return this.startQuestInteraction(character, player);
                
            case 'dialogue':
            default:
                return this.startDialogue(character, player);
        }
    }

    determineInteractionType(character, player) {
        // Hostile characters initiate combat
        if (character.type === 'monster' && character.personality.aggression > 70) {
            return 'combat';
        }
        
        // Merchants can trade
        if (character.type === 'merchant') {
            return 'trade';
        }
        
        // Quest givers with available quests
        if (character.quests && character.quests.length > 0) {
            return 'quest';
        }
        
        return 'dialogue';
    }

    startDialogue(character, player) {
        this.currentDialogue = {
            character: character,
            player: player,
            state: 'greeting',
            context: {}
        };

        const greeting = this.selectDialogueLine(character, 'greeting');
        this.displayDialogue(character, greeting);
        this.showDialogueUI();
        
        return { type: 'dialogue', message: greeting };
    }

    startCombatInteraction(character, player) {
        const hostileMessage = this.selectDialogueLine(character, 'hostile');
        this.showQuickPopup(character, hostileMessage);
        
        return { 
            type: 'combat', 
            message: hostileMessage,
            combat: {
                enemy: character,
                canFlee: true,
                initiative: character.combat ? character.combat.speed : 5
            }
        };
    }

    startTradeInteraction(character, player) {
        const tradeMessage = this.selectDialogueLine(character, 'trading');
        this.displayTradeInterface(character, player);
        
        return { 
            type: 'trade', 
            message: tradeMessage,
            inventory: character.inventory || []
        };
    }

    startQuestInteraction(character, player) {
        const questMessage = this.selectDialogueLine(character, 'quest_available');
        this.displayQuestInterface(character, player);
        
        return { 
            type: 'quest', 
            message: questMessage,
            quests: character.quests || []
        };
    }

    selectDialogueLine(character, category) {
        if (!character.dialogue || !character.dialogue[category]) {
            return "..."; // Default silent response
        }

        const lines = character.dialogue[category];
        if (Array.isArray(lines)) {
            // Select based on character mood and history
            return this.selectContextualLine(lines, character);
        }
        
        return lines;
    }

    selectContextualLine(lines, character) {
        // Simple selection - can be enhanced with context awareness
        let index = Math.floor(Math.random() * lines.length);
        
        // Avoid repeating the same line too frequently
        const recentLines = this.dialogueHistory
            .filter(entry => entry.characterId === character.id)
            .slice(-3)
            .map(entry => entry.line);
            
        let attempts = 0;
        while (recentLines.includes(lines[index]) && attempts < lines.length) {
            index = (index + 1) % lines.length;
            attempts++;
        }
        
        return lines[index];
    }

    displayDialogue(character, text) {
        document.getElementById('dialogue-avatar').textContent = character.emoji;
        document.getElementById('dialogue-name').textContent = character.name;
        document.getElementById('dialogue-text').innerHTML = this.formatDialogueText(text);
        
        // Update mood display
        const mood = this.getMoodFromText(text, character);
        document.getElementById('dialogue-mood').textContent = mood;
        
        // Generate response choices
        this.generateDialogueChoices(character);
        
        // Record in history
        this.dialogueHistory.push({
            characterId: character.id,
            line: text,
            timestamp: Date.now()
        });
    }

    formatDialogueText(text) {
        // Handle special formatting in dialogue text
        return text
            .replace(/\*(.*?)\*/g, '<em class="action-text">$1</em>') // *actions*
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **emphasis**
            .replace(/🎵(.*?)🎵/g, '<span class="music-text">♪ $1 ♪</span>'); // 🎵music🎵
    }

    getMoodFromText(text, character) {
        // Determine mood from dialogue content and character state
        if (text.includes('*growl') || text.includes('*snarl')) return 'Hostile';
        if (text.includes('*laugh') || text.includes('*chuckle')) return 'Amused';
        if (text.includes('*whisper') || text.includes('*mysterious')) return 'Mysterious';
        if (text.includes('*excited') || text.includes('!')) return 'Excited';
        if (text.includes('*sad') || text.includes('*sigh')) return 'Melancholy';
        
        // Based on character personality
        if (character.personality) {
            if (character.personality.friendliness > 80) return 'Friendly';
            if (character.personality.wisdom > 80) return 'Wise';
            if (character.personality.mysteriousness > 80) return 'Enigmatic';
        }
        
        return 'Neutral';
    }

    generateDialogueChoices(character) {
        const choicesContainer = document.getElementById('dialogue-choices');
        choicesContainer.innerHTML = '';
        
        const choices = this.getAvailableChoices(character);
        
        choices.forEach((choice, index) => {
            const button = document.createElement('button');
            button.className = 'dialogue-choice-btn';
            button.textContent = choice.text;
            button.addEventListener('click', () => this.selectChoice(choice, index));
            choicesContainer.appendChild(button);
        });
    }

    getAvailableChoices(character) {
        const choices = [];
        
        // Standard conversation choices
        choices.push({ text: "Tell me about yourself", action: 'learn_about' });
        choices.push({ text: "What's happening around here?", action: 'local_info' });
        
        // Context-specific choices
        if (character.type === 'merchant') {
            choices.push({ text: "What do you have for sale?", action: 'show_wares' });
        }
        
        if (character.quests && character.quests.length > 0) {
            choices.push({ text: "Do you have any work for me?", action: 'show_quests' });
        }
        
        if (character.type === 'elder' || character.personality.wisdom > 70) {
            choices.push({ text: "Share your wisdom with me", action: 'request_wisdom' });
        }
        
        if (character.type === 'companion') {
            choices.push({ text: "Would you like to join me?", action: 'recruit' });
        }
        
        // Always include goodbye option
        choices.push({ text: "Farewell", action: 'goodbye' });
        
        return choices;
    }

    selectChoice(choice, index) {
        const character = this.activeCharacter;
        let response = "";
        
        switch (choice.action) {
            case 'learn_about':
                response = this.generatePersonalityResponse(character);
                break;
                
            case 'local_info':
                response = this.generateLocalInfoResponse(character);
                break;
                
            case 'show_wares':
                this.showTradeInterface();
                return;
                
            case 'show_quests':
                this.showQuestInterface();
                return;
                
            case 'request_wisdom':
                response = this.selectDialogueLine(character, 'wisdom') || 
                          this.selectDialogueLine(character, 'advice') ||
                          "I have lived long and seen much, young one.";
                break;
                
            case 'recruit':
                response = this.handleRecruitAttempt(character);
                break;
                
            case 'goodbye':
                this.handleGoodbye(character);
                return;
                
            default:
                response = "I'm not sure how to respond to that.";
        }
        
        this.displayDialogue(character, response);
    }

    generatePersonalityResponse(character) {
        const personality = character.personality;
        const responses = [];
        
        if (personality.wisdom > 80) {
            responses.push("I have spent many years studying the ancient ways...");
        }
        
        if (personality.friendliness > 80) {
            responses.push("I've always enjoyed meeting new people and hearing their stories!");
        }
        
        if (personality.mysteriousness > 80) {
            responses.push("There are some things about me that are better left unknown...");
        }
        
        if (personality.greed > 70) {
            responses.push("I've worked hard for everything I have, and I value a good deal!");
        }
        
        return responses.length > 0 ? responses[Math.floor(Math.random() * responses.length)] :
               "I'm just a simple person trying to make my way in this world.";
    }

    generateLocalInfoResponse(character) {
        const localInfo = [
            "Strange lights have been seen in the eastern forest lately...",
            "The harvest this year has been surprisingly good!",
            "There are rumors of bandits on the northern roads.",
            "The old ruins to the south are said to be cursed.",
            "Trade has been slow, but adventurers like yourself bring excitement!",
            "The weather-witch says a storm is coming from the mountains.",
            "Children have been reporting seeing fairies in the moonlight."
        ];
        
        // Character-specific information
        if (character.type === 'ranger') {
            return "The wildlife has been restless lately. Something has them spooked in the deep woods.";
        }
        
        if (character.type === 'merchant') {
            return "Business has been good, but I worry about the increasing number of monster sightings.";
        }
        
        return localInfo[Math.floor(Math.random() * localInfo.length)];
    }

    handleRecruitAttempt(character) {
        if (character.type === 'companion') {
            // Add companion logic here
            this.gameWorld.eventManager.emit('companion_recruited', character);
            return "I would be honored to accompany you on your adventures!";
        } else if (character.personality.friendliness > 70) {
            return "I appreciate the offer, but I have responsibilities here.";
        } else {
            return "I prefer to stay where I am, thank you.";
        }
    }

    handleGoodbye(character) {
        const goodbyes = [
            "Safe travels, adventurer!",
            "May fortune smile upon you!",
            "Farewell, and may we meet again!",
            "Take care of yourself out there!",
            "Until next time, friend!"
        ];
        
        const goodbye = goodbyes[Math.floor(Math.random() * goodbyes.length)];
        this.showQuickPopup(character, goodbye);
        
        setTimeout(() => {
            this.closeDialogue();
        }, 2000);
    }

    showDialogueUI() {
        document.getElementById('dialogue-container').classList.remove('hidden');
        document.body.classList.add('dialogue-active');
    }

    closeDialogue() {
        document.getElementById('dialogue-container').classList.add('hidden');
        document.body.classList.remove('dialogue-active');
        
        this.currentDialogue = null;
        this.activeCharacter = null;
        
        // Emit dialogue end event
        if (this.gameWorld && this.gameWorld.eventManager) {
            this.gameWorld.eventManager.emit('dialogue_ended');
        }
    }

    isDialogueOpen() {
        return !document.getElementById('dialogue-container').classList.contains('hidden');
    }

    continueDialogue() {
        if (!this.activeCharacter) return;
        
        // Generate random idle dialogue
        const idleResponse = this.selectDialogueLine(this.activeCharacter, 'idle') ||
                           this.selectDialogueLine(this.activeCharacter, 'greeting');
        
        this.displayDialogue(this.activeCharacter, idleResponse);
    }

    showQuickPopup(character, message, duration = 3000) {
        const popup = document.getElementById('interaction-popup');
        document.getElementById('popup-avatar').textContent = character.emoji;
        document.getElementById('popup-text').innerHTML = this.formatDialogueText(message);
        
        popup.classList.remove('hidden');
        
        setTimeout(() => {
            popup.classList.add('hidden');
        }, duration);
    }

    showTradeInterface() {
        // This would open a separate trade UI
        this.closeDialogue();
        
        if (this.gameWorld && this.gameWorld.tradeSystem) {
            this.gameWorld.tradeSystem.openTradeWith(this.activeCharacter);
        } else {
            this.showQuickPopup(this.activeCharacter, "Trading system not yet implemented!", 2000);
        }
    }

    showQuestInterface() {
        // This would open a separate quest UI
        this.closeDialogue();
        
        if (this.gameWorld && this.gameWorld.questSystem) {
            this.gameWorld.questSystem.showQuestsFrom(this.activeCharacter);
        } else {
            this.showQuickPopup(this.activeCharacter, "Quest system not yet implemented!", 2000);
        }
    }

    displayTradeInterface(character, player) {
        this.showQuickPopup(character, "Welcome to my shop! *rummages through wares*");
        
        // For now, just show a message - full trade system would be separate
        setTimeout(() => {
            this.startDialogue(character, player);
        }, 2000);
    }

    displayQuestInterface(character, player) {
        this.showQuickPopup(character, "I have important tasks for brave souls like yourself!");
        
        // For now, just show a message - full quest system would be separate
        setTimeout(() => {
            this.startDialogue(character, player);
        }, 2000);
    }

    // Utility method to trigger dialogue from external systems
    triggerCharacterDialogue(character, category, customMessage = null) {
        const message = customMessage || this.selectDialogueLine(character, category);
        this.showQuickPopup(character, message);
    }

    // Method to check if a character can be interacted with
    canInteractWith(character, playerPosition) {
        const dx = character.position.x - playerPosition.x;
        const dy = character.position.y - playerPosition.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        return distance <= character.interactionRadius;
    }

    // Get interaction preview (for UI hints)
    getInteractionPreview(character) {
        let type = 'Talk';
        let icon = '💬';
        
        if (character.type === 'monster' && character.personality.aggression > 70) {
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
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DialogueSystem;
}