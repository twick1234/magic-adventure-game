/**
 * Quest and Trading System
 * Handles quest management, trading mechanics, and character interactions
 */

class QuestSystem {
    constructor(gameWorld) {
        this.gameWorld = gameWorld;
        this.activeQuests = new Map();
        this.completedQuests = new Set();
        this.questHistory = [];
        this.questUI = null;
        
        this.initializeSystem();
    }

    initializeSystem() {
        this.createQuestUI();
        this.bindEvents();
    }

    createQuestUI() {
        if (document.getElementById('quest-container')) {
            return; // UI already exists
        }

        const questHTML = `
            <div id="quest-container" class="quest-container hidden">
                <div class="quest-panel">
                    <div class="quest-header">
                        <h3>📜 Quests</h3>
                        <button class="close-btn" id="quest-close">×</button>
                    </div>
                    
                    <div class="quest-tabs">
                        <button class="quest-tab active" data-tab="available">Available</button>
                        <button class="quest-tab" data-tab="active">Active</button>
                        <button class="quest-tab" data-tab="completed">Completed</button>
                    </div>
                    
                    <div class="quest-content">
                        <div class="quest-list" id="quest-list">
                            <!-- Quest items will be populated here -->
                        </div>
                        
                        <div class="quest-details" id="quest-details">
                            <div class="quest-detail-content">
                                <h4>Select a quest to view details</h4>
                                <p>Click on any quest from the list to see more information.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', questHTML);
    }

    bindEvents() {
        // Close button
        const closeBtn = document.getElementById('quest-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeQuestUI());
        }

        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quest-tab')) {
                this.switchQuestTab(e.target.dataset.tab);
            }
        });

        // Quest selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quest-item')) {
                const questId = e.target.closest('.quest-item').dataset.questId;
                this.selectQuest(questId);
            }
        });

        // Quest action buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quest-accept-btn')) {
                const questId = e.target.dataset.questId;
                this.acceptQuest(questId);
            }
            if (e.target.classList.contains('quest-abandon-btn')) {
                const questId = e.target.dataset.questId;
                this.abandonQuest(questId);
            }
        });

        // ESC to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isQuestUIOpen()) {
                this.closeQuestUI();
            }
        });
    }

    showQuestsFrom(character) {
        this.currentQuestGiver = character;
        this.openQuestUI();
        this.switchQuestTab('available');
        this.populateAvailableQuests(character);
    }

    openQuestUI() {
        document.getElementById('quest-container').classList.remove('hidden');
        document.body.classList.add('quest-ui-open');
    }

    closeQuestUI() {
        document.getElementById('quest-container').classList.add('hidden');
        document.body.classList.remove('quest-ui-open');
        this.currentQuestGiver = null;
    }

    isQuestUIOpen() {
        return !document.getElementById('quest-container').classList.contains('hidden');
    }

    switchQuestTab(tabName) {
        // Update tab appearance
        document.querySelectorAll('.quest-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Populate content based on tab
        switch (tabName) {
            case 'available':
                this.populateAvailableQuests(this.currentQuestGiver);
                break;
            case 'active':
                this.populateActiveQuests();
                break;
            case 'completed':
                this.populateCompletedQuests();
                break;
        }
    }

    populateAvailableQuests(questGiver) {
        const questList = document.getElementById('quest-list');
        questList.innerHTML = '';

        if (!questGiver || !questGiver.quests) {
            questList.innerHTML = '<div class="no-quests">No quests available from this character.</div>';
            return;
        }

        questGiver.quests.forEach(quest => {
            if (!this.activeQuests.has(quest.id) && !this.completedQuests.has(quest.id)) {
                const questItem = this.createQuestItem(quest, 'available', questGiver);
                questList.appendChild(questItem);
            }
        });

        if (questList.children.length === 0) {
            questList.innerHTML = '<div class="no-quests">No new quests available.</div>';
        }
    }

    populateActiveQuests() {
        const questList = document.getElementById('quest-list');
        questList.innerHTML = '';

        if (this.activeQuests.size === 0) {
            questList.innerHTML = '<div class="no-quests">No active quests.</div>';
            return;
        }

        for (const quest of this.activeQuests.values()) {
            const questItem = this.createQuestItem(quest, 'active');
            questList.appendChild(questItem);
        }
    }

    populateCompletedQuests() {
        const questList = document.getElementById('quest-list');
        questList.innerHTML = '';

        if (this.completedQuests.size === 0) {
            questList.innerHTML = '<div class="no-quests">No completed quests.</div>';
            return;
        }

        this.questHistory.forEach(quest => {
            if (this.completedQuests.has(quest.id)) {
                const questItem = this.createQuestItem(quest, 'completed');
                questList.appendChild(questItem);
            }
        });
    }

    createQuestItem(quest, status, questGiver = null) {
        const item = document.createElement('div');
        item.className = `quest-item quest-${status}`;
        item.dataset.questId = quest.id;

        const difficultyClass = this.getQuestDifficultyClass(quest);
        const progressText = status === 'active' ? this.getQuestProgressText(quest) : '';
        const statusIcon = this.getQuestStatusIcon(status);

        item.innerHTML = `
            <div class="quest-item-header">
                <div class="quest-title">
                    <span class="quest-icon">${statusIcon}</span>
                    <span class="quest-name">${quest.title}</span>
                    <span class="quest-difficulty ${difficultyClass}">${this.getQuestDifficulty(quest)}</span>
                </div>
                ${questGiver ? `<div class="quest-giver">from ${questGiver.name}</div>` : ''}
            </div>
            
            <div class="quest-item-body">
                <div class="quest-description">${quest.description}</div>
                ${progressText}
                
                <div class="quest-rewards">
                    ${this.formatQuestRewards(quest.reward)}
                </div>
            </div>
        `;

        return item;
    }

    getQuestStatusIcon(status) {
        switch (status) {
            case 'available': return '❗';
            case 'active': return '⏳';
            case 'completed': return '✅';
            default: return '📜';
        }
    }

    getQuestDifficulty(quest) {
        if (quest.requirements && quest.requirements.level) {
            const level = quest.requirements.level;
            if (level <= 5) return 'Easy';
            if (level <= 15) return 'Medium';
            if (level <= 30) return 'Hard';
            return 'Expert';
        }
        return 'Unknown';
    }

    getQuestDifficultyClass(quest) {
        const difficulty = this.getQuestDifficulty(quest);
        return `difficulty-${difficulty.toLowerCase()}`;
    }

    getQuestProgressText(quest) {
        // This would track actual progress - simplified for now
        return '<div class="quest-progress">Progress: In Progress...</div>';
    }

    formatQuestRewards(reward) {
        if (!reward) return '<div class="no-rewards">No rewards</div>';

        let rewardText = '<div class="reward-list">';
        
        if (reward.gold) {
            rewardText += `<span class="reward-item gold">💰 ${reward.gold} gold</span>`;
        }
        
        if (reward.xp) {
            rewardText += `<span class="reward-item xp">⭐ ${reward.xp} XP</span>`;
        }
        
        if (reward.item) {
            rewardText += `<span class="reward-item item">🎁 ${reward.item}</span>`;
        }
        
        rewardText += '</div>';
        return rewardText;
    }

    selectQuest(questId) {
        // Find the quest from available sources
        let quest = this.activeQuests.get(questId);
        
        if (!quest && this.currentQuestGiver) {
            quest = this.currentQuestGiver.quests?.find(q => q.id === questId);
        }
        
        if (!quest) {
            quest = this.questHistory.find(q => q.id === questId);
        }

        if (!quest) return;

        this.displayQuestDetails(quest);
    }

    displayQuestDetails(quest) {
        const details = document.getElementById('quest-details');
        const isActive = this.activeQuests.has(quest.id);
        const isCompleted = this.completedQuests.has(quest.id);
        const isAvailable = !isActive && !isCompleted;

        details.innerHTML = `
            <div class="quest-detail-content">
                <div class="quest-detail-header">
                    <h4>${quest.title}</h4>
                    <div class="quest-meta">
                        <span class="quest-difficulty ${this.getQuestDifficultyClass(quest)}">
                            ${this.getQuestDifficulty(quest)}
                        </span>
                        ${quest.requirements ? `<span class="quest-req">Req. Level ${quest.requirements.level}</span>` : ''}
                    </div>
                </div>
                
                <div class="quest-detail-body">
                    <div class="quest-full-description">
                        ${quest.description}
                    </div>
                    
                    ${quest.objectives ? this.formatQuestObjectives(quest.objectives) : ''}
                    
                    <div class="quest-rewards-detail">
                        <h5>Rewards:</h5>
                        ${this.formatQuestRewards(quest.reward)}
                    </div>
                    
                    ${this.getQuestNotes(quest)}
                </div>
                
                <div class="quest-detail-actions">
                    ${this.getQuestActionButtons(quest, isActive, isCompleted, isAvailable)}
                </div>
            </div>
        `;
    }

    formatQuestObjectives(objectives) {
        if (!objectives || objectives.length === 0) return '';

        let html = '<div class="quest-objectives"><h5>Objectives:</h5><ul>';
        objectives.forEach(objective => {
            html += `<li class="objective ${objective.completed ? 'completed' : ''}">${objective.description}</li>`;
        });
        html += '</ul></div>';
        
        return html;
    }

    getQuestNotes(quest) {
        const notes = [];
        
        if (quest.timeLimit) {
            notes.push(`⏰ Time limit: ${quest.timeLimit}`);
        }
        
        if (quest.location) {
            notes.push(`📍 Location: ${quest.location}`);
        }
        
        if (quest.warning) {
            notes.push(`⚠️ Warning: ${quest.warning}`);
        }
        
        if (notes.length === 0) return '';
        
        return `<div class="quest-notes">${notes.map(note => `<div class="quest-note">${note}</div>`).join('')}</div>`;
    }

    getQuestActionButtons(quest, isActive, isCompleted, isAvailable) {
        if (isCompleted) {
            return '<div class="quest-completed-msg">✅ Quest Completed!</div>';
        }
        
        if (isActive) {
            return `
                <button class="quest-abandon-btn btn-danger" data-quest-id="${quest.id}">
                    Abandon Quest
                </button>
                <div class="quest-hint">Complete the objectives to finish this quest.</div>
            `;
        }
        
        if (isAvailable) {
            const canAccept = this.canAcceptQuest(quest);
            
            return `
                <button class="quest-accept-btn btn-primary ${!canAccept ? 'disabled' : ''}" 
                        data-quest-id="${quest.id}" 
                        ${!canAccept ? 'disabled' : ''}>
                    Accept Quest
                </button>
                ${!canAccept ? '<div class="quest-requirement-error">Requirements not met!</div>' : ''}
            `;
        }
        
        return '';
    }

    canAcceptQuest(quest) {
        // Check if player meets quest requirements
        const player = this.gameWorld.player || { level: 1 };
        
        if (quest.requirements) {
            if (quest.requirements.level && player.level < quest.requirements.level) {
                return false;
            }
            
            if (quest.requirements.items) {
                // Check if player has required items
                // This would integrate with inventory system
                return true; // Simplified for now
            }
            
            if (quest.requirements.completedQuests) {
                // Check if prerequisite quests are completed
                return quest.requirements.completedQuests.every(reqQuestId => 
                    this.completedQuests.has(reqQuestId)
                );
            }
        }
        
        return true;
    }

    acceptQuest(questId) {
        if (!this.currentQuestGiver) return;
        
        const quest = this.currentQuestGiver.quests?.find(q => q.id === questId);
        if (!quest) return;
        
        if (!this.canAcceptQuest(quest)) {
            this.showQuestMessage('You do not meet the requirements for this quest.', 'error');
            return;
        }
        
        // Add to active quests
        const activeQuest = {
            ...quest,
            acceptedAt: Date.now(),
            giver: this.currentQuestGiver.id,
            progress: {},
            objectives: quest.objectives ? quest.objectives.map(obj => ({
                ...obj,
                completed: false
            })) : []
        };
        
        this.activeQuests.set(questId, activeQuest);
        
        this.showQuestMessage(`Quest "${quest.title}" accepted!`, 'success');
        
        // Update UI
        this.switchQuestTab('active');
        
        // Emit quest accepted event
        if (this.gameWorld && this.gameWorld.eventManager) {
            this.gameWorld.eventManager.emit('quest_accepted', activeQuest);
        }
    }

    abandonQuest(questId) {
        if (!this.activeQuests.has(questId)) return;
        
        const quest = this.activeQuests.get(questId);
        
        if (confirm(`Are you sure you want to abandon "${quest.title}"?`)) {
            this.activeQuests.delete(questId);
            this.showQuestMessage(`Quest "${quest.title}" abandoned.`, 'warning');
            
            // Update UI
            this.switchQuestTab('active');
            
            // Emit quest abandoned event
            if (this.gameWorld && this.gameWorld.eventManager) {
                this.gameWorld.eventManager.emit('quest_abandoned', quest);
            }
        }
    }

    completeQuest(questId, giveRewards = true) {
        const quest = this.activeQuests.get(questId);
        if (!quest) return false;
        
        // Move to completed
        this.activeQuests.delete(questId);
        this.completedQuests.add(questId);
        this.questHistory.push({
            ...quest,
            completedAt: Date.now()
        });
        
        if (giveRewards && quest.reward) {
            this.giveQuestRewards(quest.reward);
        }
        
        this.showQuestMessage(`Quest "${quest.title}" completed!`, 'success');
        
        // Emit quest completed event
        if (this.gameWorld && this.gameWorld.eventManager) {
            this.gameWorld.eventManager.emit('quest_completed', quest);
        }
        
        return true;
    }

    giveQuestRewards(reward) {
        // This would integrate with player inventory and stats
        // For now, just show what rewards were given
        
        let rewardMessages = [];
        
        if (reward.gold) {
            rewardMessages.push(`Received ${reward.gold} gold`);
        }
        
        if (reward.xp) {
            rewardMessages.push(`Gained ${reward.xp} experience`);
        }
        
        if (reward.item) {
            rewardMessages.push(`Received ${reward.item}`);
        }
        
        if (rewardMessages.length > 0) {
            this.showQuestMessage(rewardMessages.join(', '), 'reward');
        }
    }

    showQuestMessage(message, type = 'info') {
        // Create temporary message display
        const messageEl = document.createElement('div');
        messageEl.className = `quest-message quest-message-${type}`;
        messageEl.textContent = message;
        messageEl.style.position = 'fixed';
        messageEl.style.top = '20px';
        messageEl.style.left = '50%';
        messageEl.style.transform = 'translateX(-50%)';
        messageEl.style.zIndex = '1000';
        messageEl.style.padding = '10px 20px';
        messageEl.style.borderRadius = '5px';
        messageEl.style.fontWeight = 'bold';
        
        // Style based on type
        switch (type) {
            case 'success':
                messageEl.style.background = '#10b981';
                messageEl.style.color = 'white';
                break;
            case 'error':
                messageEl.style.background = '#ef4444';
                messageEl.style.color = 'white';
                break;
            case 'warning':
                messageEl.style.background = '#f59e0b';
                messageEl.style.color = 'white';
                break;
            case 'reward':
                messageEl.style.background = '#8b5cf6';
                messageEl.style.color = 'white';
                break;
            default:
                messageEl.style.background = '#6b7280';
                messageEl.style.color = 'white';
        }
        
        document.body.appendChild(messageEl);
        
        // Animate in
        messageEl.animate([
            { opacity: 0, transform: 'translateX(-50%) translateY(-20px)' },
            { opacity: 1, transform: 'translateX(-50%) translateY(0px)' }
        ], { duration: 300, easing: 'ease-out' });
        
        // Remove after delay
        setTimeout(() => {
            messageEl.animate([
                { opacity: 1, transform: 'translateX(-50%) translateY(0px)' },
                { opacity: 0, transform: 'translateX(-50%) translateY(-20px)' }
            ], { duration: 300, easing: 'ease-in' }).onfinish = () => {
                messageEl.remove();
            };
        }, 3000);
    }

    updateQuestProgress(questId, objectiveId, completed = true) {
        const quest = this.activeQuests.get(questId);
        if (!quest) return;
        
        if (quest.objectives) {
            const objective = quest.objectives.find(obj => obj.id === objectiveId);
            if (objective) {
                objective.completed = completed;
                
                // Check if all objectives are completed
                const allCompleted = quest.objectives.every(obj => obj.completed);
                if (allCompleted) {
                    this.completeQuest(questId);
                }
            }
        }
    }

    // Method to check quest completion conditions
    checkQuestConditions(event, data) {
        for (const quest of this.activeQuests.values()) {
            // This would contain complex logic to check various quest conditions
            // based on game events like killing monsters, collecting items, etc.
            
            // Example: Check if quest is completed by game event
            if (quest.completionCondition && quest.completionCondition.event === event) {
                if (this.evaluateCondition(quest.completionCondition, data)) {
                    this.completeQuest(quest.id);
                }
            }
        }
    }

    evaluateCondition(condition, data) {
        // Simplified condition evaluation
        switch (condition.type) {
            case 'kill_monster':
                return data.monsterId === condition.target;
            case 'collect_item':
                return data.itemId === condition.item && data.quantity >= condition.amount;
            case 'reach_location':
                return data.location === condition.location;
            default:
                return false;
        }
    }

    // Get active quest count
    getActiveQuestCount() {
        return this.activeQuests.size;
    }

    // Get completed quest count
    getCompletedQuestCount() {
        return this.completedQuests.size;
    }

    // Export quest data for save system
    exportQuestData() {
        return {
            activeQuests: Array.from(this.activeQuests.entries()),
            completedQuests: Array.from(this.completedQuests),
            questHistory: this.questHistory
        };
    }

    // Import quest data from save system
    importQuestData(data) {
        if (data.activeQuests) {
            this.activeQuests = new Map(data.activeQuests);
        }
        
        if (data.completedQuests) {
            this.completedQuests = new Set(data.completedQuests);
        }
        
        if (data.questHistory) {
            this.questHistory = data.questHistory;
        }
    }
}

// Trading System
class TradingSystem {
    constructor(gameWorld) {
        this.gameWorld = gameWorld;
        this.currentTrader = null;
        this.playerInventory = new Map(); // Simple inventory simulation
        this.playerGold = 1000; // Starting gold
        
        this.initializeSystem();
    }

    initializeSystem() {
        this.createTradeUI();
        this.bindEvents();
    }

    createTradeUI() {
        if (document.getElementById('trade-container')) {
            return; // UI already exists
        }

        const tradeHTML = `
            <div id="trade-container" class="trade-container hidden">
                <div class="trade-panel">
                    <div class="trade-header">
                        <h3>🛒 Trade</h3>
                        <div class="player-gold">Gold: <span id="player-gold">${this.playerGold}</span></div>
                        <button class="close-btn" id="trade-close">×</button>
                    </div>
                    
                    <div class="trade-content">
                        <div class="merchant-inventory">
                            <h4 id="merchant-name">Merchant</h4>
                            <div class="inventory-grid" id="merchant-items">
                                <!-- Merchant items will be populated here -->
                            </div>
                        </div>
                        
                        <div class="trade-actions">
                            <div class="selected-item" id="selected-item">
                                Select an item to trade
                            </div>
                            <button class="trade-btn btn-primary" id="buy-item" disabled>Buy Item</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', tradeHTML);
    }

    bindEvents() {
        // Close button
        document.getElementById('trade-close')?.addEventListener('click', () => this.closeTradeUI());

        // Buy button
        document.getElementById('buy-item')?.addEventListener('click', () => this.buySelectedItem());

        // Item selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.trade-item')) {
                this.selectTradeItem(e.target.closest('.trade-item'));
            }
        });

        // ESC to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isTradeUIOpen()) {
                this.closeTradeUI();
            }
        });
    }

    openTradeWith(merchant) {
        this.currentTrader = merchant;
        this.populateMerchantInventory();
        this.openTradeUI();
    }

    openTradeUI() {
        document.getElementById('trade-container').classList.remove('hidden');
        document.body.classList.add('trade-ui-open');
    }

    closeTradeUI() {
        document.getElementById('trade-container').classList.add('hidden');
        document.body.classList.remove('trade-ui-open');
        this.currentTrader = null;
        this.selectedItem = null;
    }

    isTradeUIOpen() {
        return !document.getElementById('trade-container').classList.contains('hidden');
    }

    populateMerchantInventory() {
        if (!this.currentTrader || !this.currentTrader.inventory) return;

        document.getElementById('merchant-name').textContent = this.currentTrader.name;
        document.getElementById('player-gold').textContent = this.playerGold;

        const inventoryGrid = document.getElementById('merchant-items');
        inventoryGrid.innerHTML = '';

        this.currentTrader.inventory.forEach((item, index) => {
            const itemElement = this.createTradeItemElement(item, index);
            inventoryGrid.appendChild(itemElement);
        });
    }

    createTradeItemElement(item, index) {
        const element = document.createElement('div');
        element.className = 'trade-item';
        element.dataset.itemIndex = index;

        const canAfford = this.playerGold >= item.price;
        const affordClass = canAfford ? 'affordable' : 'too-expensive';

        element.innerHTML = `
            <div class="item-icon">${this.getItemIcon(item.type)}</div>
            <div class="item-details">
                <div class="item-name">${item.name}</div>
                <div class="item-price ${affordClass}">💰 ${item.price}</div>
                <div class="item-type">${item.type}</div>
            </div>
        `;

        return element;
    }

    getItemIcon(type) {
        const icons = {
            weapon: '⚔️',
            armor: '🛡️',
            consumable: '🧪',
            accessory: '💍',
            tool: '🔧',
            misc: '📦'
        };
        return icons[type] || '📦';
    }

    selectTradeItem(itemElement) {
        // Remove previous selection
        document.querySelectorAll('.trade-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Select new item
        itemElement.classList.add('selected');
        const itemIndex = parseInt(itemElement.dataset.itemIndex);
        const item = this.currentTrader.inventory[itemIndex];
        
        this.selectedItem = { item, index: itemIndex };
        this.updateSelectedItemDisplay();
    }

    updateSelectedItemDisplay() {
        const selectedDisplay = document.getElementById('selected-item');
        const buyButton = document.getElementById('buy-item');

        if (!this.selectedItem) {
            selectedDisplay.innerHTML = 'Select an item to trade';
            buyButton.disabled = true;
            return;
        }

        const { item } = this.selectedItem;
        const canAfford = this.playerGold >= item.price;

        selectedDisplay.innerHTML = `
            <div class="selected-item-details">
                <h4>${item.name}</h4>
                <p>Type: ${item.type}</p>
                <p>Price: 💰 ${item.price}</p>
                ${this.getItemDescription(item)}
            </div>
        `;

        buyButton.disabled = !canAfford;
        buyButton.textContent = canAfford ? 'Buy Item' : 'Not Enough Gold';
    }

    getItemDescription(item) {
        // Add item descriptions based on type and name
        const descriptions = {
            'Iron Sword': 'A sturdy blade forged from iron. +15 Attack',
            'Health Potion': 'Restores 50 health points when consumed.',
            'Leather Armor': 'Basic protection for adventurers. +10 Defense',
            'Magic Ring': 'Enchanted ring that boosts magical abilities. +5 Mana',
            'Rope': 'Useful for climbing and various adventures.'
        };

        return descriptions[item.name] ? `<p class="item-description">${descriptions[item.name]}</p>` : '';
    }

    buySelectedItem() {
        if (!this.selectedItem || !this.currentTrader) return;

        const { item, index } = this.selectedItem;
        
        if (this.playerGold < item.price) {
            this.showTradeMessage('Not enough gold!', 'error');
            return;
        }

        // Complete the purchase
        this.playerGold -= item.price;
        this.addToPlayerInventory(item);
        
        // Remove item from merchant (optional - some merchants have infinite stock)
        // this.currentTrader.inventory.splice(index, 1);
        
        this.showTradeMessage(`Purchased ${item.name} for ${item.price} gold!`, 'success');
        
        // Update UI
        document.getElementById('player-gold').textContent = this.playerGold;
        this.selectedItem = null;
        this.updateSelectedItemDisplay();
        // this.populateMerchantInventory(); // Uncomment if items should be removed
        
        // Emit trade event
        if (this.gameWorld && this.gameWorld.eventManager) {
            this.gameWorld.eventManager.emit('item_purchased', { item, merchant: this.currentTrader });
        }
    }

    addToPlayerInventory(item) {
        // Simple inventory management
        const itemKey = item.name;
        const currentAmount = this.playerInventory.get(itemKey) || 0;
        this.playerInventory.set(itemKey, currentAmount + 1);
    }

    showTradeMessage(message, type = 'info') {
        // Reuse the quest message system
        const messageEl = document.createElement('div');
        messageEl.className = `trade-message trade-message-${type}`;
        messageEl.textContent = message;
        messageEl.style.position = 'fixed';
        messageEl.style.top = '20px';
        messageEl.style.left = '50%';
        messageEl.style.transform = 'translateX(-50%)';
        messageEl.style.zIndex = '1000';
        messageEl.style.padding = '10px 20px';
        messageEl.style.borderRadius = '5px';
        messageEl.style.fontWeight = 'bold';
        
        switch (type) {
            case 'success':
                messageEl.style.background = '#10b981';
                messageEl.style.color = 'white';
                break;
            case 'error':
                messageEl.style.background = '#ef4444';
                messageEl.style.color = 'white';
                break;
            default:
                messageEl.style.background = '#6b7280';
                messageEl.style.color = 'white';
        }
        
        document.body.appendChild(messageEl);
        
        setTimeout(() => {
            messageEl.animate([
                { opacity: 1 },
                { opacity: 0 }
            ], { duration: 300 }).onfinish = () => messageEl.remove();
        }, 2000);
    }

    // Get player's current gold
    getPlayerGold() {
        return this.playerGold;
    }

    // Get player's inventory
    getPlayerInventory() {
        return Array.from(this.playerInventory.entries()).map(([name, quantity]) => ({
            name,
            quantity
        }));
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QuestSystem, TradingSystem };
}