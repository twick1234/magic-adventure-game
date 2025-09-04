#!/usr/bin/env python3
"""
🏰 MAGIC ADVENTURE GAME 🏰
A CrewAI-powered interactive adventure for kids!

Three AI agents work together to create an amazing adventure:
- Story Creator: Builds the magical world and scenarios  
- Game Master: Manages the game and responds to choices
- Adventure Helper: Gives hints and encouragement
"""

from crewai import Agent, Task, Crew, Process
import os
import random
from typing import Dict, List

class MagicAdventureGame:
    def __init__(self):
        self.player_name = ""
        self.player_health = 100
        self.player_items = []
        self.current_location = "Enchanted Forest"
        self.game_state = "beginning"
        
    def display_header(self):
        print("\n" + "="*60)
        print("🏰✨ WELCOME TO THE MAGIC ADVENTURE GAME ✨🏰")
        print("="*60)
        print("A magical world awaits you, young adventurer!")
        print("Three wise AI companions will guide your journey:")
        print("📚 Story Weaver - Creates your magical world")
        print("🎲 Game Master - Guides your adventure") 
        print("💫 Helper Spirit - Gives you hints and courage")
        print("="*60)

    def get_player_info(self):
        print("\n🌟 Let's begin your magical journey!")
        self.player_name = input("What's your adventurer name? ").strip()
        if not self.player_name:
            self.player_name = "Brave Explorer"
        print(f"\nWelcome, {self.player_name}! Your adventure begins...")

    def create_story_crew(self) -> Crew:
        """Create the AI crew that will run the game"""
        
        # Story Creator - Builds the world and scenarios
        story_creator = Agent(
            role="Magical Story Weaver",
            goal="Create exciting, age-appropriate adventures for young heroes",
            backstory="You're a wise storyteller who has seen countless magical realms. You love creating fun, safe adventures that spark imagination and teach good values. You always include friendly characters, magical creatures, and positive choices.",
            verbose=False,
            allow_delegation=False
        )
        
        # Game Master - Manages gameplay and responds to choices  
        game_master = Agent(
            role="Adventure Game Master",
            goal="Guide players through exciting choices and manage the game flow",
            backstory="You're a friendly guide who helps young adventurers navigate their quests. You present clear choices, celebrate good decisions, and always keep things fun and encouraging. You never let players get truly stuck or scared.",
            verbose=False,
            allow_delegation=False
        )
        
        # Helper - Provides hints and encouragement
        adventure_helper = Agent(
            role="Magical Adventure Helper",
            goal="Provide helpful hints and encouragement to young adventurers",
            backstory="You're a cheerful companion spirit who believes every child can be a hero. You offer gentle guidance, celebrate victories, and help when things get challenging. You're always positive and supportive.",
            verbose=False,
            allow_delegation=False
        )
        
        return story_creator, game_master, adventure_helper

    def create_game_tasks(self, story_creator, game_master, adventure_helper, player_input: str = "") -> List[Task]:
        """Create tasks for the current game situation"""
        
        context = f"""
        Player Name: {self.player_name}
        Current Location: {self.current_location}
        Health: {self.player_health}/100
        Items: {', '.join(self.player_items) if self.player_items else 'None'}
        Game State: {self.game_state}
        Player Input: {player_input}
        """
        
        if self.game_state == "beginning":
            # Starting the adventure
            story_task = Task(
                description=f"""Create the opening of a magical adventure for a 10-year-old named {self.player_name}. 
                Set the scene in an Enchanted Forest with:
                - A magical, welcoming atmosphere
                - An interesting quest or mystery to solve
                - Friendly magical creatures they might meet
                - A clear, simple goal
                Keep it exciting but not scary. Make it 3-4 sentences.""",
                expected_output="An engaging opening scene that sets up the adventure",
                agent=story_creator
            )
            
            choice_task = Task(
                description=f"""Based on the story opening, present {self.player_name} with 3 simple, fun choices for what to do first. 
                Make sure each choice:
                - Sounds adventurous and fun
                - Is appropriate for a 10-year-old  
                - Could lead to something interesting
                - Is clearly numbered (1, 2, 3)
                Format: Present the choices clearly with numbers.""",
                expected_output="Three numbered adventure choices",
                agent=game_master
            )
            
        else:
            # Responding to player choice
            story_task = Task(
                description=f"""Continue the adventure story based on {self.player_name}'s choice: "{player_input}"
                Current situation: {context}
                
                Create what happens next:
                - Make their choice lead to something exciting
                - Include friendly characters or magical discoveries
                - Keep it positive and fun
                - 2-3 sentences describing the outcome""",
                expected_output="A continuation of the adventure based on the player's choice",
                agent=story_creator
            )
            
            choice_task = Task(
                description=f"""Based on the new story development, give {self.player_name} 3 new choices for what to do next.
                Consider their current situation: {context}
                
                Make each choice:
                - Lead to different types of adventures
                - Be appropriate and fun for kids
                - Be clearly numbered (1, 2, 3)""",
                expected_output="Three new numbered choices for continuing the adventure",
                agent=game_master
            )
        
        hint_task = Task(
            description=f"""Provide a helpful hint or encouraging message for {self.player_name}.
            Current situation: {context}
            
            Give them:
            - A gentle hint about what each choice might lead to
            - Encouragement about their adventure
            - Remind them they're doing great
            Keep it short and positive!""",
            expected_output="An encouraging hint or tip",
            agent=adventure_helper
        )
        
        return [story_task, choice_task, hint_task]

    def run_game_round(self, story_creator, game_master, adventure_helper, player_input: str = ""):
        """Run one round of the game"""
        
        tasks = self.create_game_tasks(story_creator, game_master, adventure_helper, player_input)
        
        crew = Crew(
            agents=[story_creator, game_master, adventure_helper],
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )
        
        try:
            # This would normally run the AI crew, but without API keys it will fail
            # For demo purposes, we'll simulate the responses
            return self.simulate_ai_responses(player_input)
        except Exception as e:
            return self.simulate_ai_responses(player_input)
    
    def simulate_ai_responses(self, player_input: str = "") -> Dict[str, str]:
        """Simulate AI responses for demo without API keys"""
        
        adventures = [
            {
                "story": f"🌲 {self.player_name} steps into the Enchanted Forest where glittering butterflies dance around ancient oak trees. A friendly fox with a golden collar approaches and whispers, 'The Crystal of Friendship has been lost! The forest creatures need a brave hero like you to find it.' The fox's eyes sparkle with hope.",
                "choices": """
1. Follow the golden fox deeper into the magical forest
2. Look for clues near the sparkling stream you hear nearby  
3. Climb the tall oak tree to get a better view of the forest""",
                "hint": "💫 Remember, young hero - sometimes the best adventures start by helping others! Each path will show you something magical. Trust your brave heart!"
            },
            {
                "story": f"🦋 {self.player_name} follows the golden fox to a clearing where woodland creatures have gathered - rabbits wearing tiny hats, squirrels with acorn backpacks, and a wise old owl with spectacles. 'Welcome, brave one!' they cheer. The owl hoots softly, 'The Crystal was last seen near the Singing Waterfall, but beware - it's guarded by riddles!'",
                "choices": """
1. Head to the Singing Waterfall with your new animal friends
2. Ask the wise owl to teach you about solving riddles first
3. Search the clearing for more clues about the Crystal""",
                "hint": "🦉 Wise choice! The forest animals want to help you succeed. Learning about riddles might be very useful for your quest!"
            },
            {
                "story": f"🌊 {self.player_name} and the animal friends reach the beautiful Singing Waterfall, where water droplets create tiny rainbows. Behind the waterfall, they spot a glowing cave! But a friendly dragon with rainbow scales appears and smiles. 'To enter my crystal cave, solve this riddle: I am round and bright, I light up the night, children wish on me with all their might. What am I?'",
                "choices": """
1. Answer 'A star!' with confidence
2. Answer 'The moon!' thoughtfully  
3. Ask your animal friends to help you think""",
                "hint": "⭐ You're so close to solving this! Think about what shines in the night sky that children make wishes on. Your animal friends believe in you!"
            }
        ]
        
        # Cycle through adventures based on game state
        if self.game_state == "beginning":
            adventure = adventures[0]
            self.game_state = "exploring"
        elif len(player_input) > 0 and "1" in player_input:
            adventure = adventures[1] 
        else:
            adventure = adventures[2]
            
        return {
            "story": adventure["story"],
            "choices": adventure["choices"], 
            "hint": adventure["hint"]
        }

    def play_game(self):
        """Main game loop"""
        self.display_header()
        self.get_player_info()
        
        print(f"\n🎮 Creating your magical adventure crew...")
        story_creator, game_master, adventure_helper = self.create_story_crew()
        print("✨ Your AI companions are ready!")
        
        game_running = True
        turn_count = 0
        
        while game_running and turn_count < 5:  # Limit turns for demo
            print(f"\n{'='*50}")
            print(f"🏰 ADVENTURE TURN {turn_count + 1} 🏰")
            print("="*50)
            
            if turn_count == 0:
                # First turn - start the adventure
                responses = self.run_game_round(story_creator, game_master, adventure_helper)
            else:
                # Get player choice
                print(f"\n{self.player_name}, what do you choose?")
                choice = input("Enter 1, 2, or 3 (or 'quit' to end): ").strip().lower()
                
                if choice == 'quit':
                    break
                    
                responses = self.run_game_round(story_creator, game_master, adventure_helper, choice)
            
            # Display the responses
            print(f"\n📚 Story Weaver says:")
            print(responses["story"])
            
            print(f"\n🎲 Game Master presents your choices:")
            print(responses["choices"])
            
            print(f"\n💫 Helper Spirit whispers:")
            print(responses["hint"])
            
            turn_count += 1
        
        print(f"\n🌟 Thank you for playing, {self.player_name}!")
        print("🎉 You are a true hero! The adventure continues in your imagination...")
        print("💝 Remember: You can be brave, kind, and magical every day!")

def main():
    """Start the Magic Adventure Game"""
    print("🎮 Initializing Magic Adventure Game...")
    print("📝 Note: This game works best with OpenAI API key in .env file")
    print("🎭 Running in demo mode with simulated responses...")
    
    game = MagicAdventureGame()
    game.play_game()

if __name__ == "__main__":
    main()