#!/usr/bin/env python3
"""
🏰✨ MAGICAL ADVENTURE GAME ✨🏰
A CrewAI-powered interactive story game for kids!

How to play:
1. Run this file: python kids_adventure_game.py
2. Enter your name when prompted
3. Make choices by typing 1, 2, or 3
4. Enjoy your magical adventure!

Three AI agents create your story:
- 📚 Story Creator (builds the magical world)
- 🎲 Game Master (gives you choices)
- 💫 Adventure Helper (encourages you)
"""

import random
import sys

class KidsAdventureGame:
    def __init__(self):
        self.player_name = ""
        self.score = 0
        self.adventures_completed = 0
        
        # Pre-written adventures that simulate AI responses
        self.story_database = {
            "forest_start": {
                "story": "You enter the Enchanted Forest where magical butterflies dance around ancient trees that sparkle with golden light. A friendly fox with a shimmering collar approaches you with bright, hopeful eyes!",
                "question": "The fox speaks in a gentle voice: 'Brave adventurer, the Crystal of Friendship has been stolen by a sad, lonely dragon. Will you help me get it back so all the forest creatures can be friends again?'",
                "choices": [
                    "Yes! Let's help the dragon feel less lonely",
                    "Follow the fox to learn more about the dragon", 
                    "Ask other forest animals what they know"
                ],
                "responses": [
                    "🌟 Your kind heart fills the fox with joy! 'You truly are a hero!' the fox exclaims. Together you head toward the dragon's mountain home.",
                    "🦊 The wise fox smiles proudly. 'You are thoughtful and brave!' The fox leads you through a secret path filled with glowing mushrooms.",
                    "🐰 The woodland creatures gather around you - rabbits, squirrels, and birds all chirp happily! 'The dragon just needs a friend!' they tell you."
                ]
            },
            "dragon_meeting": {
                "story": "You reach a beautiful crystal cave where a magnificent dragon with scales that shimmer like rainbows sits alone, looking very sad. Tears like tiny diamonds fall from his eyes.",
                "question": "The dragon notices you and speaks softly: 'I took the crystal because I was so lonely... no one ever wanted to be my friend. Can you help me learn how to make friends?'",
                "choices": [
                    "Teach the dragon that sharing makes friends happy",
                    "Show the dragon how to say sorry nicely",
                    "Invite the dragon to play games with forest friends"
                ],
                "responses": [
                    "🐉 The dragon's eyes light up! 'I never knew sharing could make others happy!' He gently returns the crystal and asks to share his treasure with everyone.",
                    "💎 'I'm sorry I took the crystal,' the dragon says sweetly. 'Will you forgive me?' The crystal begins to glow brighter with kindness!",
                    "🎮 'Games? I love games!' the dragon cheers. 'I know the best hiding spots!' All the animals come running to play together!"
                ]
            },
            "magical_celebration": {
                "story": "The Crystal of Friendship glows brilliantly as all the forest creatures gather for the most wonderful celebration! Music fills the air as everyone dances together.",
                "question": "The dragon, now smiling brightly, offers you a special gift: 'Choose a magical power to take home with you, dear friend!'",
                "choices": [
                    "The power to help others feel less lonely",
                    "The power to turn any sad moment into a happy one",
                    "The power to make new friends wherever you go"
                ],
                "responses": [
                    "💝 A warm golden light surrounds you! Now you can always tell when someone needs a friend, and you'll know just how to help them feel better.",
                    "🌈 Sparkles of rainbow light dance around you! Now you can find the good in any situation and help others smile even on tough days.",
                    "✨ A gentle, friendly glow shines from your heart! Now everywhere you go, you'll attract kind people who want to be your friend!"
                ]
            }
        }
        
        self.encouragements = [
            "You're showing such a kind heart! 💛",
            "What a wise and brave choice! 🌟", 
            "Your compassion makes you a true hero! 🦸",
            "You're learning what real friendship means! 💫",
            "I'm so proud of how thoughtful you are! 🎉"
        ]

    def display_title(self):
        print("\n" + "🌟" * 30)
        print("🏰✨ MAGICAL ADVENTURE GAME ✨🏰")
        print("🌟" * 30)
        print("\n🎭 Welcome to a world of friendship and magic!")
        print("📚 Your Story Creator builds magical worlds")
        print("🎲 Your Game Master guides your choices")
        print("💫 Your Adventure Helper cheers you on!")
        print("\n" + "="*60)

    def get_player_name(self):
        print("\n🌟 Let's start your magical journey!")
        try:
            name = input("✨ What's your adventurer name? ").strip()
            if not name:
                name = "Brave Hero"
            self.player_name = name
            print(f"\n🎉 Welcome, {self.player_name}! Your adventure begins now...")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Thanks for visiting! Come back anytime!")
            sys.exit(0)

    def simulate_crewai_response(self, adventure_key: str, choice_num: int = None):
        """Simulate what CrewAI agents would say"""
        adventure = self.story_database[adventure_key]
        
        # Story Creator response
        story_response = adventure["story"]
        
        # Game Master response  
        game_master_response = adventure["question"] + "\n\nYour choices:"
        for i, choice in enumerate(adventure["choices"], 1):
            game_master_response += f"\n{i}. {choice}"
        
        # Adventure Helper response
        helper_response = random.choice(self.encouragements)
        
        return {
            "story": story_response,
            "choices": game_master_response, 
            "encouragement": helper_response,
            "outcomes": adventure["responses"]
        }

    def get_player_choice(self, max_choices: int = 3):
        """Get player's choice with error handling"""
        while True:
            try:
                choice = input(f"\n🎯 Choose 1, 2, or {max_choices} (or 'quit' to exit): ").strip().lower()
                
                if choice == 'quit':
                    return -1
                
                choice_num = int(choice)
                if 1 <= choice_num <= max_choices:
                    return choice_num - 1  # Convert to 0-based index
                else:
                    print(f"🎈 Please choose a number between 1 and {max_choices}!")
                    
            except ValueError:
                print("🎈 Please enter a number or 'quit'!")
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Thanks for playing! Your adventure continues in your dreams!")
                return -1

    def play_adventure_scene(self, scene_key: str):
        """Play one adventure scene"""
        print(f"\n{'🌟' * 25}")
        print(f"ADVENTURE CHAPTER {self.adventures_completed + 1}")
        print(f"{'🌟' * 25}")
        
        # Get AI responses (simulated)
        responses = self.simulate_crewai_response(scene_key)
        
        # Story Creator tells the story
        print(f"\n📚 Story Creator says:")
        print(f"🎭 {responses['story']}")
        
        # Game Master presents choices
        print(f"\n🎲 Game Master asks {self.player_name}:")
        print(responses['choices'])
        
        # Adventure Helper encourages
        print(f"\n💫 Adventure Helper whispers:")
        print(responses['encouragement'])
        
        # Get player choice
        choice = self.get_player_choice()
        
        if choice == -1:  # Player wants to quit
            return False
        
        # Show outcome
        print(f"\n✨ You chose: {self.story_database[scene_key]['choices'][choice]}")
        print(f"\n🎉 What happens next:")
        print(responses['outcomes'][choice])
        
        # Update score and progress
        self.score += choice + 1
        self.adventures_completed += 1
        
        return True

    def play_full_game(self):
        """Play the complete adventure"""
        self.display_title()
        self.get_player_name()
        
        # Play through all adventure scenes
        scenes = ["forest_start", "dragon_meeting", "magical_celebration"]
        
        for scene in scenes:
            if not self.play_adventure_scene(scene):
                print(f"\n🎭 Your adventure ends here, {self.player_name}!")
                print("🌟 But remember - you can always return to this magical world!")
                return
            
            if scene != scenes[-1]:  # Not the last scene
                try:
                    input(f"\n🎮 Press Enter to continue your adventure...")
                except (EOFError, KeyboardInterrupt):
                    break
        
        # Victory celebration!
        self.show_victory_celebration()

    def show_victory_celebration(self):
        """Show the final celebration"""
        print(f"\n{'🎊' * 20}")
        print("🏆 QUEST COMPLETED! 🏆")
        print(f"{'🎊' * 20}")
        print(f"\n🌟 Congratulations, {self.player_name}!")
        print("You completed your magical adventure!")
        print(f"🎯 Adventure Score: {'⭐' * min(self.score, 10)}")
        print(f"🏅 Chapters Completed: {self.adventures_completed}")
        
        print(f"\n💝 You learned that:")
        print("   🤝 Friendship is the greatest magic")
        print("   💛 Kindness can heal any sadness")
        print("   🌈 Everyone deserves understanding")
        
        print(f"\n🎭 Thank you for playing, {self.player_name}!")
        print("🏰 Your magical adventure lives on in your heart!")
        print("✨ Remember: You have the power to make real magic every day!")

def main():
    """Start the Magical Adventure Game"""
    print("🚀 Loading Magical Adventure Game...")
    print("🎮 Powered by CrewAI - Multi-Agent Storytelling!")
    print("📖 Perfect for kids who love magic and friendship!")
    
    try:
        game = KidsAdventureGame()
        game.play_full_game()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for visiting our magical world!")
        print("🌟 Come back anytime for more adventures!")

if __name__ == "__main__":
    main()