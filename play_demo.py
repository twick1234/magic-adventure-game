#!/usr/bin/env python3
"""Demo version that shows how the interactive game works"""

import sys
import os

# Add the current directory to Python path so we can import the game
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_interactive_game():
    print("🎮 DEMO: How the Magic Adventure Game Works Locally")
    print("="*60)
    print("When you run: python3 kids_adventure_game.py")
    print("Here's what happens:\n")
    
    # Simulate the game flow
    print("🚀 Loading Magical Adventure Game...")
    print("🎮 Powered by CrewAI - Multi-Agent Storytelling!")
    print("📖 Perfect for kids who love magic and friendship!")
    print()
    
    print("🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟")
    print("🏰✨ MAGICAL ADVENTURE GAME ✨🏰")
    print("🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟")
    print()
    
    print("🎭 Welcome to a world of friendship and magic!")
    print("📚 Your Story Creator builds magical worlds")
    print("🎲 Your Game Master guides your choices")
    print("💫 Your Adventure Helper cheers you on!")
    print()
    print("="*60)
    print()
    
    # Simulate name input
    print("🌟 Let's start your magical journey!")
    print("✨ What's your adventurer name? [You would type: Alex]")
    player_name = "Alex"
    print(f"✨ What's your adventurer name? {player_name}")
    print()
    print(f"🎉 Welcome, {player_name}! Your adventure begins now...")
    print()
    
    # Show first adventure scene
    print("🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟")
    print("ADVENTURE CHAPTER 1")
    print("🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟")
    print()
    
    print("📚 Story Creator says:")
    print("🎭 You enter the Enchanted Forest where magical butterflies dance around ancient trees that sparkle with golden light. A friendly fox with a shimmering collar approaches you with bright, hopeful eyes!")
    print()
    
    print("🎲 Game Master asks Alex:")
    print("The fox speaks in a gentle voice: 'Brave adventurer, the Crystal of Friendship has been stolen by a sad, lonely dragon. Will you help me get it back so all the forest creatures can be friends again?'")
    print()
    print("Your choices:")
    print("1. Yes! Let's help the dragon feel less lonely")
    print("2. Follow the fox to learn more about the dragon")
    print("3. Ask other forest animals what they know")
    print()
    
    print("💫 Adventure Helper whispers:")
    print("You're showing such a kind heart! 💛")
    print()
    
    # Simulate choice
    print("🎯 Choose 1, 2, or 3 (or 'quit' to exit): [You would type: 1]")
    choice = "1"
    print(f"🎯 Choose 1, 2, or 3 (or 'quit' to exit): {choice}")
    print()
    
    print("✨ You chose: Yes! Let's help the dragon feel less lonely")
    print()
    print("🎉 What happens next:")
    print("🌟 Your kind heart fills the fox with joy! 'You truly are a hero!' the fox exclaims. Together you head toward the dragon's mountain home.")
    print()
    
    print("🎮 Press Enter to continue your adventure... [You would press Enter]")
    print()
    
    print("🎊 And the adventure continues for 2 more magical chapters!")
    print("🏆 At the end, you help the dragon learn about friendship!")
    print()
    print("="*60)
    print("🎮 TO PLAY INTERACTIVELY:")
    print("Run: python3 kids_adventure_game.py")
    print("Then type your responses and press Enter!")
    print("="*60)

if __name__ == "__main__":
    simulate_interactive_game()