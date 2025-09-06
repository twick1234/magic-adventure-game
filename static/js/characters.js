/**
 * AI Character System for Magic Adventure Game
 * Complete character data structure with personalities, dialogue, and behaviors
 */

// Character types and base configurations
const CHARACTER_TYPES = {
    VILLAGER: 'villager',
    MERCHANT: 'merchant',
    QUEST_GIVER: 'quest_giver',
    COMPANION: 'companion',
    MONSTER: 'monster',
    ELDER: 'elder',
    RANGER: 'ranger',
    STRANGER: 'stranger'
};

// Character data structure with 12 unique NPCs
const CHARACTER_DATA = {
    // Quest Giver - Wise Wizard
    'eldric_the_wise': {
        id: 'eldric_the_wise',
        name: 'Eldric the Wise',
        type: CHARACTER_TYPES.QUEST_GIVER,
        emoji: '🧙‍♂️',
        level: 50,
        health: 200,
        position: { x: 20, y: 30 },
        personality: {
            wisdom: 95,
            friendliness: 80,
            helpfulness: 90,
            mysticism: 100
        },
        dialogue: {
            greeting: [
                "Ah, young adventurer! The ancient prophecies foretold of your arrival.",
                "Welcome, brave soul. The realm has need of heroes like yourself.",
                "I sense great potential within you, traveler. Are you ready for adventure?"
            ],
            quest_available: [
                "I have an urgent quest for one of your caliber. Will you hear me out?",
                "Dark forces stir in the eastern caves. Someone must investigate...",
                "The Crystal of Eternal Light has been stolen. Can you retrieve it?"
            ],
            quest_complete: [
                "Magnificent work! Your bravery has saved our realm once again.",
                "The prophecy comes to pass through your noble deeds. Well done!",
                "Accept this reward, champion. You have earned it a hundred times over."
            ],
            idle: [
                "*studies ancient tomes*",
                "*gazes mysteriously into the distance*",
                "*whispers incantations under his breath*"
            ]
        },
        quests: [
            {
                id: 'crystal_quest',
                title: 'The Stolen Crystal',
                description: 'Retrieve the Crystal of Eternal Light from the Shadow Caves',
                reward: { gold: 500, xp: 1000, item: 'Crystal Pendant' },
                requirements: { level: 5 }
            },
            {
                id: 'herb_gathering',
                title: 'Magical Herbs',
                description: 'Collect 10 Moonflower petals from the Enchanted Forest',
                reward: { gold: 200, xp: 400, item: 'Health Potion' },
                requirements: { level: 1 }
            }
        ],
        movementPattern: 'stationary',
        interactionRadius: 3
    },

    // Merchant Trader
    'gorin_goldbeard': {
        id: 'gorin_goldbeard',
        name: 'Gorin Goldbeard',
        type: CHARACTER_TYPES.MERCHANT,
        emoji: '👨‍💼',
        level: 25,
        health: 120,
        position: { x: 60, y: 40 },
        personality: {
            greediness: 70,
            friendliness: 60,
            trustworthiness: 75,
            shrewdness: 85
        },
        dialogue: {
            greeting: [
                "Welcome to Gorin's Goods! Finest wares in all the lands!",
                "Looking for something special, friend? I've got just the thing!",
                "Step right up! Everything must go... for the right price, of course!"
            ],
            trading: [
                "Ah, you have excellent taste! This item is quite rare...",
                "I could part with this for the right offer. What say you?",
                "Business is business, but for you, I might make a special deal."
            ],
            no_money: [
                "Come back when your purse is heavier, friend!",
                "These items aren't charity, you know!",
                "Gold talks, and yours is staying awfully quiet..."
            ],
            idle: [
                "*polishes his wares*",
                "*counts gold coins*",
                "*arranges merchandise*"
            ]
        },
        inventory: [
            { name: 'Iron Sword', price: 150, type: 'weapon' },
            { name: 'Health Potion', price: 50, type: 'consumable' },
            { name: 'Leather Armor', price: 100, type: 'armor' },
            { name: 'Magic Ring', price: 300, type: 'accessory' },
            { name: 'Rope', price: 20, type: 'tool' }
        ],
        movementPattern: 'small_area',
        interactionRadius: 2
    },

    // Friendly Villager
    'maya_brightsmile': {
        id: 'maya_brightsmile',
        name: 'Maya Brightsmile',
        type: CHARACTER_TYPES.VILLAGER,
        emoji: '👩‍🌾',
        level: 8,
        health: 80,
        position: { x: 45, y: 60 },
        personality: {
            friendliness: 95,
            helpfulness: 85,
            curiosity: 70,
            optimism: 90
        },
        dialogue: {
            greeting: [
                "Oh hello there! What a lovely day for an adventure!",
                "Welcome to our village! I hope you'll stay a while!",
                "A new face! How exciting! Are you here to help with the harvest?"
            ],
            helpful: [
                "If you need directions, I know every path in these parts!",
                "The baker makes the most delicious bread - you should try some!",
                "Be careful in the northern woods, strange sounds have been heard..."
            ],
            gossip: [
                "Did you hear? Old Tom found a mysterious chest in his garden!",
                "The merchant's prices have gone up again, if you ask me...",
                "There are rumors of treasure hidden beneath the old oak tree!"
            ],
            idle: [
                "*tends to her garden*",
                "*hums a cheerful tune*",
                "*waves at passersby*"
            ]
        },
        movementPattern: 'patrol',
        patrolPoints: [
            { x: 40, y: 55 },
            { x: 50, y: 60 },
            { x: 45, y: 65 }
        ],
        interactionRadius: 2
    },

    // Forest Ranger
    'thorin_swiftarrow': {
        id: 'thorin_swiftarrow',
        name: 'Thorin Swiftarrow',
        type: CHARACTER_TYPES.RANGER,
        emoji: '🏹',
        level: 30,
        health: 150,
        position: { x: 80, y: 25 },
        personality: {
            independence: 90,
            nature_love: 95,
            vigilance: 85,
            stoicism: 80
        },
        dialogue: {
            greeting: [
                "Well met, traveler. The forest spirits watch over you.",
                "Another soul seeking adventure in these ancient woods?",
                "Stay on the marked paths - these forests hold many secrets."
            ],
            warning: [
                "Dark creatures have been spotted near the old ruins lately.",
                "The weather changes quickly here. Best be prepared.",
                "Some trails lead to wonder, others to peril. Choose wisely."
            ],
            knowledge: [
                "I've tracked these lands for twenty years. Ask me anything.",
                "The old growth trees remember stories from ages past.",
                "Follow the stream north to find the hidden waterfall grotto."
            ],
            idle: [
                "*scans the treeline carefully*",
                "*adjusts his bow and quiver*",
                "*tracks animal footprints*"
            ]
        },
        movementPattern: 'wide_patrol',
        patrolPoints: [
            { x: 75, y: 20 },
            { x: 85, y: 25 },
            { x: 80, y: 35 },
            { x: 70, y: 30 }
        ],
        interactionRadius: 4
    },

    // Mysterious Stranger
    'shadow_enigma': {
        id: 'shadow_enigma',
        name: 'The Shadow',
        type: CHARACTER_TYPES.STRANGER,
        emoji: '🕵️‍♂️',
        level: 40,
        health: 180,
        position: { x: 15, y: 80 },
        personality: {
            mysteriousness: 100,
            suspicion: 75,
            knowledge: 90,
            secrecy: 95
        },
        dialogue: {
            greeting: [
                "...*steps from the shadows*... You seek knowledge, don't you?",
                "Not many venture to this forgotten corner. What brings you here?",
                "Shhh... walls have ears. Speak quietly if you wish to speak at all."
            ],
            cryptic: [
                "The answer you seek lies where the sun never shines...",
                "Three keys open the door, but only one opens the heart.",
                "When the moon is dark, the true path reveals itself."
            ],
            secrets: [
                "I know things... things others would kill to learn.",
                "The merchant isn't who he appears to be. Trust no one completely.",
                "There's a hidden passage beneath the village well..."
            ],
            idle: [
                "*melts back into shadows*",
                "*watches from the corner of their eye*",
                "*whispers to unseen companions*"
            ]
        },
        movementPattern: 'random',
        interactionRadius: 1
    },

    // Friendly Animal Companion
    'patches_the_fox': {
        id: 'patches_the_fox',
        name: 'Patches',
        type: CHARACTER_TYPES.COMPANION,
        emoji: '🦊',
        level: 15,
        health: 60,
        position: { x: 70, y: 55 },
        personality: {
            loyalty: 100,
            playfulness: 95,
            intelligence: 70,
            energy: 90
        },
        dialogue: {
            greeting: [
                "*yips excitedly and wags tail*",
                "*tilts head curiously at you*",
                "*bounds over with obvious joy*"
            ],
            following: [
                "*follows close behind, tail wagging*",
                "*occasionally runs ahead to scout*",
                "*stops to sniff interesting scents*"
            ],
            helpful: [
                "*scratches at the ground, revealing something shiny*",
                "*barks and points toward a hidden path*",
                "*brings you a small healing herb in its mouth*"
            ],
            idle: [
                "*chases its own tail*",
                "*pounces at falling leaves*",
                "*curls up for a quick nap*"
            ]
        },
        abilities: ['treasure_sense', 'path_finding', 'herb_gathering'],
        movementPattern: 'follow_player',
        interactionRadius: 2
    },

    // Village Elder
    'grandmother_willow': {
        id: 'grandmother_willow',
        name: 'Grandmother Willow',
        type: CHARACTER_TYPES.ELDER,
        emoji: '👵',
        level: 60,
        health: 100,
        position: { x: 35, y: 45 },
        personality: {
            wisdom: 100,
            patience: 95,
            kindness: 90,
            memory: 85
        },
        dialogue: {
            greeting: [
                "Come closer, child. These old eyes have seen much in their time.",
                "Ah, a young adventurer! Reminds me of my dear departed husband...",
                "Sit a while, dear one. The old stories are worth hearing."
            ],
            stories: [
                "Long ago, when the world was young, dragons soared these very skies...",
                "The ancient oak remembers when this was all farmland, before the magic came.",
                "Your grandfather once saved this village, you know. You have his eyes."
            ],
            advice: [
                "Patience, young one. The greatest treasures take time to find.",
                "Listen to your heart, but don't ignore your head entirely.",
                "Sometimes the longest path leads to the most beautiful destinations."
            ],
            idle: [
                "*knits quietly by the window*",
                "*feeds breadcrumbs to birds*",
                "*rocks gently in her chair*"
            ]
        },
        movementPattern: 'stationary',
        interactionRadius: 2
    },

    // Hostile Creature - Shadow Wolf
    'grimfang': {
        id: 'grimfang',
        name: 'Grimfang',
        type: CHARACTER_TYPES.MONSTER,
        emoji: '🐺',
        level: 20,
        health: 100,
        position: { x: 90, y: 15 },
        personality: {
            aggression: 90,
            cunning: 70,
            pack_instinct: 80,
            territoriality: 95
        },
        dialogue: {
            hostile: [
                "*growls menacingly, baring sharp fangs*",
                "*circles you with predatory intent*",
                "*howls to summon the pack*"
            ],
            attacking: [
                "*lunges forward with claws extended*",
                "*snaps viciously at your heels*",
                "*eyes glow red with primal rage*"
            ],
            retreat: [
                "*whimpers and backs away slowly*",
                "*limps into the undergrowth*",
                "*howls mournfully before fleeing*"
            ],
            idle: [
                "*prowls through tall grass*",
                "*sniffs the air for prey*",
                "*marks territory*"
            ]
        },
        combat: {
            damage: 25,
            defense: 15,
            speed: 8,
            special_attacks: ['pounce', 'howl', 'bite']
        },
        movementPattern: 'aggressive_patrol',
        territoryRadius: 5,
        interactionRadius: 3
    },

    // Hostile Creature - Goblin Raider
    'skarr_the_mean': {
        id: 'skarr_the_mean',
        name: 'Skarr the Mean',
        type: CHARACTER_TYPES.MONSTER,
        emoji: '👹',
        level: 18,
        health: 80,
        position: { x: 25, y: 90 },
        personality: {
            aggression: 85,
            greed: 95,
            cowardice: 60,
            cunning: 75
        },
        dialogue: {
            hostile: [
                "Grrr! Give Skarr your shiny things or get bonked!",
                "*brandishes a rusty club menacingly*",
                "No pass! Skarr's territory! Pay toll or fight!"
            ],
            attacking: [
                "Bonk bonk BONK! Skarr smash good!",
                "Shiny things will be MINE!",
                "*swings club wildly in all directions*"
            ],
            retreat: [
                "Skarr remember this! Next time bring bigger club!",
                "*runs away clutching precious belongings*",
                "Not fair! You cheat somehow!"
            ],
            idle: [
                "*counts stolen trinkets*",
                "*sharpens rusty weapons*",
                "*mutters about revenge plots*"
            ]
        },
        combat: {
            damage: 20,
            defense: 10,
            speed: 6,
            special_attacks: ['club_smash', 'steal', 'intimidate']
        },
        movementPattern: 'guard_area',
        treasureHoard: [
            { name: 'Rusty Coins', value: 10 },
            { name: 'Broken Jewelry', value: 25 },
            { name: 'Shiny Button', value: 5 }
        ],
        interactionRadius: 2
    },

    // Mystical Creature - Ancient Tree Spirit
    'oakenheart': {
        id: 'oakenheart',
        name: 'Oakenheart',
        type: CHARACTER_TYPES.ELDER,
        emoji: '🌳',
        level: 80,
        health: 300,
        position: { x: 50, y: 20 },
        personality: {
            wisdom: 100,
            patience: 100,
            nature_connection: 100,
            ancient_memory: 95
        },
        dialogue: {
            greeting: [
                "Young seedling... your roots run deep. I sense great potential.",
                "*ancient voice creaks like wind through branches*",
                "The forest speaks of your coming, small one. What do you seek?"
            ],
            wisdom: [
                "Time moves differently for my kind. What seems urgent may simply need patience.",
                "Every creature has its season. Every ending births a beginning.",
                "The deepest magic flows not from spells, but from understanding."
            ],
            nature_lore: [
                "These roots have drunk from streams older than kingdoms...",
                "The mushroom circle nearby is a gateway, but only for the pure of heart.",
                "When the forest is in danger, all who love it feel the pain."
            ],
            idle: [
                "*leaves rustle without wind*",
                "*small creatures nest in protective branches*",
                "*ancient bark glows softly with inner light*"
            ]
        },
        abilities: ['forest_blessing', 'nature_healing', 'ancient_knowledge'],
        movementPattern: 'stationary',
        interactionRadius: 4
    },

    // Traveling Bard
    'melody_songweaver': {
        id: 'melody_songweaver',
        name: 'Melody Songweaver',
        type: CHARACTER_TYPES.VILLAGER,
        emoji: '🎵',
        level: 22,
        health: 90,
        position: { x: 65, y: 70 },
        personality: {
            creativity: 95,
            charisma: 90,
            wanderlust: 85,
            optimism: 88
        },
        dialogue: {
            greeting: [
                "🎶 Oh, a new face to grace this humble stage! 🎶",
                "Welcome, friend! Care to hear a tale of distant lands?",
                "*strums lute cheerfully* The road has brought me another audience!"
            ],
            stories: [
                "I once played for a king who wept at my ballad of lost love...",
                "Beyond the mountains lies a city of pure crystal and singing stones!",
                "The dragons of old loved music most of all - it soothed their fiery hearts."
            ],
            performance: [
                "🎵 *plays an enchanting melody that seems to heal your spirit* 🎵",
                "*tells an epic tale with dramatic gestures*",
                "Would you like to learn a traveling song? It lightens any journey!"
            ],
            idle: [
                "*practices intricate finger patterns*",
                "*composes new verses*",
                "*tunes instruments carefully*"
            ]
        },
        abilities: ['inspire_courage', 'heal_with_music', 'share_knowledge'],
        movementPattern: 'traveling',
        schedule: {
            morning: { x: 40, y: 50 },
            afternoon: { x: 65, y: 70 },
            evening: { x: 30, y: 40 }
        },
        interactionRadius: 3
    },

    // Blacksmith
    'iron_magnus': {
        id: 'iron_magnus',
        name: 'Iron Magnus',
        type: CHARACTER_TYPES.MERCHANT,
        emoji: '🔨',
        level: 35,
        health: 160,
        position: { x: 55, y: 35 },
        personality: {
            craftsmanship: 95,
            strength: 85,
            dedication: 90,
            gruffness: 70
        },
        dialogue: {
            greeting: [
                "*wipes sweat from brow* What do ye need, traveler?",
                "Quality steel doesn't forge itself! What brings ye to my smithy?",
                "*hammering stops* Ah, a customer! Or just another time-waster?"
            ],
            crafting: [
                "This blade will serve ye well, but treat it with respect!",
                "Good steel is like a loyal friend - care for it and it'll never fail ye.",
                "I can upgrade that weapon, but it'll cost ye extra for the fine work."
            ],
            busy: [
                "Can't ye see I'm working? Come back when the forge cools!",
                "*continues hammering rhythmically*",
                "Art takes time, friend! These hands don't rush perfection."
            ],
            idle: [
                "*shapes glowing metal on anvil*",
                "*stokes the forge fire*",
                "*examines finished weapons critically*"
            ]
        },
        services: ['weapon_upgrade', 'armor_repair', 'custom_crafting'],
        inventory: [
            { name: 'Steel Sword', price: 250, type: 'weapon' },
            { name: 'Iron Shield', price: 180, type: 'armor' },
            { name: 'Weapon Upgrade Kit', price: 100, type: 'service' }
        ],
        movementPattern: 'work_area',
        interactionRadius: 2
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CHARACTER_DATA, CHARACTER_TYPES };
}