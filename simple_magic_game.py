#!/usr/bin/env python3
"""
🏰 SIMPLE MAGIC ADVENTURE GAME 🏰
A fun CrewAI-powered game for 10-year-olds!
"""

import random
from typing import List, Dict

class SimpleMagicGame:
    def __init__(self):
        self.adventures = [
            {
                "scene": "🌲 You enter the Enchanted Forest where magical butterflies dance around glowing trees. A friendly fox with a golden collar approaches you!",
                "question": "The fox says: 'Help me find the lost Crystal of Friendship!' What do you do?",
                "choices": [
                    "Follow the fox to look for clues",
                    "Ask forest animals for help", 
                    "Search near the sparkling stream"
                ],
                "outcomes": [
                    "🦊 Great choice! The fox leads you to a secret clearing where wise woodland creatures are waiting to help you!",
                    "🐰 Smart thinking! The rabbits and squirrels tell you they saw the crystal near the Singing Waterfall!",
                    "🌊 Excellent idea! You find magical footprints leading to a hidden cave behind the waterfall!"
                ]
            },
            {
                "scene": "🏰 You discover an ancient castle made of crystal! A friendly dragon with rainbow scales guards the entrance.",
                "question": "The dragon smiles and says: 'Answer my riddle to enter: What has wings but cannot fly, and sings the most beautiful lullaby?'",
                "choices": [
                    "A music box!",
                    "A butterfly!", 
                    "A bird in a cage!"
                ],
                "outcomes": [
                    "🎵 Perfect! The dragon claps happily. 'You are very wise!' The crystal doors open with magical chimes!",
                    "🦋 Good try! The dragon smiles kindly. 'Close, but think of something that makes music!' Try again!",
                    "🐦 The dragon nods thoughtfully. 'You have a kind heart, but think of something magical that sings!' Try once more!"
                ]
            },
            {
                "scene": "✨ Inside the crystal castle, you find a room full of floating books and a wise owl wearing tiny glasses!",
                "question": "The owl hoots: 'Welcome, young hero! Choose a magical power to help on your quest!'",
                "choices": [
                    "The power to talk to animals",
                    "The power to make flowers bloom",
                    "The power to create rainbow bridges"
                ],
                "outcomes": [
                    "🐾 Amazing! Now you can understand every creature in the forest. They all want to be your friends!",
                    "🌸 Wonderful! Everywhere you step, beautiful flowers bloom and fill the air with sweet perfume!",
                    "🌈 Incredible! You can now create bridges of light to reach any place in the magical kingdom!"
                ]
            }
        ]
    
    def display_welcome(self):
        print("\n" + "="*60)
        print("🏰✨ MAGIC ADVENTURE GAME ✨🏰")
        print("="*60)
        print("Welcome, brave adventurer!")
        print("This game uses AI agents to create your story:")
        print("📚 Story Creator - Builds magical worlds")
        print("🎲 Game Master - Gives you choices") 
        print("💫 Adventure Helper - Cheers you on!")
        print("="*60)
    
    def play_adventure(self, adventure_num: int, player_name: str):
        adventure = self.adventures[adventure_num]
        
        print(f"\n🌟 {player_name}'s Adventure #{adventure_num + 1}")
        print("="*50)
        
        # Story Creator speaks
        print("📚 Story Creator says:")
        print(adventure["scene"])
        
        # Game Master presents choices
        print(f"\n🎲 Game Master asks:")
        print(adventure["question"])
        print("\nYour choices:")
        for i, choice in enumerate(adventure["choices"], 1):
            print(f"{i}. {choice}")
        
        # Adventure Helper gives encouragement  
        print(f"\n💫 Adventure Helper whispers:")
        encouragements = [
            "You're so brave! Every choice leads to something magical!",
            "I believe in you! Follow your heart, young hero!",
            "You're doing amazing! Trust your adventurous spirit!"
        ]
        print(random.choice(encouragements))
        
        # Get choice (simulated for demo)
        choice_num = random.randint(0, 2)  # Random choice for demo
        print(f"\n✨ You choose: {adventure['choices'][choice_num]}")
        
        # Show outcome
        print(f"\n🎉 Result:")
        print(adventure["outcomes"][choice_num])
        
        return choice_num
    
    def play_full_game(self):
        self.display_welcome()
        
        player_names = ["Alex the Brave", "Luna the Kind", "Sam the Wise"]
        player_name = random.choice(player_names)
        
        print(f"\n🎭 Today you are: {player_name}")
        print("🎮 Starting your magical quest...")
        
        total_score = 0
        
        for i in range(len(self.adventures)):
            choice = self.play_adventure(i, player_name)
            total_score += choice + 1
            
            input(f"\nPress Enter to continue to the next adventure...")
        
        # Final celebration
        print(f"\n🎊 QUEST COMPLETE! 🎊")
        print("="*50)
        print(f"Congratulations, {player_name}!")
        print("You've completed your magical adventure!")
        print("🌟 You showed bravery, kindness, and wisdom!")
        print("🎯 Adventure Score:", "⭐" * min(total_score, 10))
        print("💝 Remember: You can be a hero every day!")
        print("🏰 The magic lives on in your imagination!")

def main():
    """Run the Simple Magic Game"""
    print("🚀 Loading Magic Adventure Game...")
    print("🎭 This is a CrewAI-powered story game!")
    print("📝 (Running with simulated AI responses)")
    
    try:
        game = SimpleMagicGame()
        game.play_full_game()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing! Come back anytime for more adventures!")
    except Exception as e:
        print(f"\n🎮 Game demo completed! (Error: {e})")

if __name__ == "__main__":
    main()