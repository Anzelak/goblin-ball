import pygame
import random
import sys
import os

# Make sure we're in the right directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    os.chdir(os.path.dirname(sys.executable))
else:
    # Running as script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from goblin import Goblin
from team import Team
from event import EventManager
from renderer import GameRenderer

class Game:
    def __init__(self, team1, team2, config=None):
        """Initialize a new game between two teams"""
        # Teams
        self.team1 = team1
        self.team2 = team2
        
        # Field
        self.grid_size = CONFIG.get("grid_size", 10)
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Game state
        self.current_play = 0
        self.max_plays = CONFIG.get("plays_per_game", 20)
        self.turn = 0
        self.play_complete = False
        self.game_complete = False
        
        # Role assignment
        self.offense_team = team1
        self.defense_team = team2
        self.offense_team.is_offense = True
        
        # Events and logs
        self.event_manager = EventManager()
        
        # Game-specific stats that don't persist to team/goblin records
        self.game_stats = {
            "longest_play_turns": 0,
            "most_blocks_in_play": 0,
            "injuries_this_game": 0
        }
        
        # For each new game, reset team scores but preserve stats
        self.team1.score = 0
        self.team2.score = 0
        
        # Reset carrier tracking for new game
        self.team1.carrier_rotation_counter = 0
        self.team2.carrier_rotation_counter = 0
        self.team1.carrier_history = []
        self.team2.carrier_history = []
        
        # Position the teams on the field
        self.position_teams()
        
    def position_teams(self):
        """Position the teams on the field for the start of a play"""
        # Clear the grid
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Position team1 in bottom half (for now, later we'll make this more sophisticated)
        for i, goblin in enumerate(self.team1.goblins):
            if goblin.out_of_game:
                continue
                
            # Simple row formation at the bottom
            y = 8  # Second-to-last row
            x = 2 + i * 2  # Spread out across the row
            
            # Ensure we're within grid bounds
            x = min(x, self.grid_size - 1)
            
            goblin.position = (x, y)
            self.grid[y][x] = goblin
            
        # Position team2 in top half
        for i, goblin in enumerate(self.team2.goblins):
            if goblin.out_of_game:
                continue
                
            # Simple row formation at the top
            y = 1  # Second row
            x = 2 + i * 2  # Spread out across the row
            
            # Ensure we're within grid bounds
            x = min(x, self.grid_size - 1)
            
            goblin.position = (x, y)
            self.grid[y][x] = goblin
            
        # Select carrier for offense team
        self.offense_team.select_next_carrier()
        
    def start_play(self):
        """Start a new play"""
        self.current_play += 1
        self.turn = 0
        self.play_complete = False
        
        # Reset goblin movement points
        for team in [self.team1, self.team2]:
            for goblin in team.goblins:
                goblin.movement = goblin.max_movement
                
        # Position teams
        self.position_teams()
        
        # Log the play start
        self.event_manager.create_and_dispatch("play_start", {
            "play_number": self.current_play,
            "offense_team": self.offense_team.name,
            "carrier": self.offense_team.get_carrier().name
        })
        
    def end_play(self):
        """End the current play"""
        self.play_complete = True
        
        # Log the play end
        self.event_manager.create_and_dispatch("play_end", {
            "play_number": self.current_play,
            "turns": self.turn
        })
        
        # Update stats
        self.game_stats["longest_play_turns"] = max(self.game_stats["longest_play_turns"], self.turn)
        
        # Check if game is complete
        if self.current_play >= self.max_plays:
            self.end_game()
            
    def end_game(self):
        """End the game"""
        self.game_complete = True
        
        # Determine winner
        if self.team1.score > self.team2.score:
            winner = self.team1
        elif self.team2.score > self.team1.score:
            winner = self.team2
        else:
            winner = None  # Tie
            
        # Log the game end
        self.event_manager.create_and_dispatch("game_end", {
            "winner": winner.name if winner else "Tie",
            "score": {
                self.team1.name: self.team1.score,
                self.team2.name: self.team2.score
            },
            "plays": self.current_play
        })
        
        # Update team stats
        self.team1.update_stats(self.team2.score)
        self.team2.update_stats(self.team1.score)

def main():
    """Main entry point for the Goblinball simulation"""
    # Create teams
    team1 = Team("Mudcrushers", (200, 50, 50))  # Red team
    team2 = Team("Skullsmashers", (50, 50, 200))  # Blue team
    
    # Add goblins to teams
    team1.create_team(5)
    team2.create_team(5)
    
    # Print out the created teams
    print("Team 1:", team1.name)
    for goblin in team1.goblins:
        print(f"  {goblin.name}: STR={goblin.strength}, TOU={goblin.toughness}, MOV={goblin.movement}")
        
    print("\nTeam 2:", team2.name)
    for goblin in team2.goblins:
        print(f"  {goblin.name}: STR={goblin.strength}, TOU={goblin.toughness}, MOV={goblin.movement}")
    
    # Create a game
    game = Game(team1, team2)
    
    # Start first play
    game.start_play()
    
    # Create renderer
    renderer = GameRenderer(game)
    
    # Run visualization
    renderer.run()

if __name__ == "__main__":
    main() 