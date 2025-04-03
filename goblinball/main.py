import pygame
import random
import sys
import os
import time
import datetime
import logging
import traceback
import importlib

# Make sure we're in the right directory and setup proper import paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    os.chdir(os.path.dirname(sys.executable))
else:
    # Running as script - adjust path based on how we're run
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the current directory to sys.path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # If we're running as a module (python -m goblinball.main), go up one level
    if script_dir.endswith('goblinball') and os.path.basename(script_dir) == 'goblinball':
        # Check if we're being run as a module
        if __name__ != '__main__' or any(arg.endswith('goblinball.main') for arg in sys.argv):
            parent_dir = os.path.dirname(script_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
    
    # Change to the script directory
    os.chdir(script_dir)

# Setup logging to file and console
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'goblinball_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("goblinball")

# Log start with detailed environment info
logger.info("=" * 50)
logger.info("Starting Goblinball")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Sys path: {sys.path}")
logger.info("=" * 50)

def validate_imports():
    """Validate all required modules exist before starting the game"""
    required_modules = [
        'config',
        'goblin',
        'team',
        'event',
        'renderer',
        'logger',
        'animation',
        'movement_system',
        'carrier_movement',
        'blocker_movement',
        'ai_goals',
        'utils',
        'grid',
        'game_controller',
        'grid_renderer',
        'goblin_renderer',
        'ui_renderer',
        'animation_renderer'
    ]
    
    missing_modules = []
    for module_name in required_modules:
        try:
            # Try importing the module
            importlib.import_module(module_name)
        except ImportError:
            # If import fails, add to missing list
            missing_modules.append(module_name)
    
    if missing_modules:
        logger.critical(f"Cannot start game. Missing required modules: {', '.join(missing_modules)}")
        logger.critical("Current directory: " + os.getcwd())
        logger.critical("Sys path: " + str(sys.path))
        
        # Add detailed troubleshooting info
        if 'animation_renderer' in missing_modules:
            logger.critical("Missing animation_renderer.py. This file should be in the same directory as renderer.py.")
            
        # Suggest solutions based on common problems
        logger.critical("\nPossible solutions:")
        logger.critical("1. Run from parent directory: python -m goblinball.main")
        logger.critical("2. Ensure all required files exist in the project structure")
        logger.critical("3. Check for circular imports")
        
        return False
    
    logger.info("All required modules validated successfully")
    return True

# Make sure we can find our modules
try:
    if not validate_imports():
        print("\n=== GOBLINBALL LAUNCH FAILED ===")
        print("Missing required modules. Check logs for details.")
        print(f"Log file: {log_file}")
        sys.exit(1)
        
    from config import CONFIG
    from goblin import Goblin
    from team import Team
    from event import EventManager
    from renderer import GameRenderer
    from logger import DEBUG, DebugLogger
    from animation import AnimationManager
    from movement_system import MovementSystem
    from carrier_movement import CarrierMovement
    from blocker_movement import BlockerMovement
    from ai_goals import AIGoalSystem, MovementStyleSelector
    from utils import is_adjacent, manhattan_distance
    from grid import Grid
    from game_controller import GameController
except ImportError as e:
    logger.critical(f"Could not import required modules: {e}")
    logger.critical("Make sure you're running the game from the correct directory.")
    logger.critical("See README.md for instructions on how to run the game.")
    logger.critical(f"Current directory: {os.getcwd()}")
    logger.critical(f"Sys path: {sys.path}")
    sys.exit(1)

class Game:
    def __init__(self, team1, team2, config=None):
        """Initialize a new game between two teams"""
        # Configuration
        self.config = CONFIG
        
        # Teams
        self.team1 = team1
        self.team2 = team2
        
        # Field
        self.grid_size = CONFIG.get("grid_size", 10)
        self.grid = Grid(self.grid_size, self.grid_size)
        
        # Game state
        self.current_play = 0
        self.max_plays = CONFIG.get("plays_per_game", 20)
        self.turn = 0
        self.play_complete = False
        self.game_complete = False
        self.auto_advance = False
        self.turn_delay = 0.5  # Seconds between automatic turns
        self.last_turn_time = time.time()
        
        # Turn history for Previous Turn functionality
        self.turn_history = []
        self.max_history = 20  # Maximum number of turns to keep in history
        self.current_history_index = -1  # -1 means we're at the current state
        
        # Role assignment
        self.offense_team = team1
        self.defense_team = team2
        self.offense_team.is_offense = True
        
        # Events and logs
        self.event_manager = EventManager()
        
        # Animation system
        self.animation_manager = AnimationManager()
        
        # Movement systems
        self.movement_system = MovementSystem(self)
        self.carrier_movement = CarrierMovement(self, self.movement_system)
        self.blocker_movement = BlockerMovement(self, self.movement_system)
        
        # AI systems
        self.goal_system = AIGoalSystem(self)
        self.style_selector = MovementStyleSelector(self)
        
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
        
        # Movement trail tracking
        self.movement_trails = {}  # Dictionary to store recent positions of goblins
        self.trail_length = 5  # Number of previous positions to track
        self.max_turn_movement = 3  # Maximum number of moves a goblin can make in a turn
        
        # Create the game controller
        self.controller = GameController(self)
        
        DEBUG.log(f"Game initialized with teams: {team1.name} vs {team2.name}")
        
        # Position the teams on the field
        self.controller.position_teams()
    
    def update_movement_trail(self, goblin, new_position):
        """Update the movement trail for a goblin after it moves"""
        if goblin.id not in self.movement_trails:
            self.movement_trails[goblin.id] = []
            
        # Add new position to the trail
        self.movement_trails[goblin.id].append(new_position)
        
        # Keep only the most recent positions
        if len(self.movement_trails[goblin.id]) > self.trail_length:
            self.movement_trails[goblin.id].pop(0)
            
    def get_movement_trail(self, goblin):
        """Get the movement trail for a goblin"""
        return self.movement_trails.get(goblin.id, [])
    
    def score_touchdown(self, carrier):
        """Score a touchdown
        
        Args:
            carrier: The carrier goblin who scored
        """
        if not carrier or not carrier.has_ball:
            return
            
        # Award points to the carrier's team
        touchdown_points = self.config.get("touchdown_points", 3)
        carrier.team.score += touchdown_points
        
        # Update stats
        carrier.stats["touchdowns"] += 1
        carrier.stats["career_touchdowns"] += 1
        carrier.team.stats["touchdowns"] += 1
        
        # Log the event
        self.event_manager.create_and_dispatch("touchdown", {
            "carrier_id": carrier.id,
            "carrier_name": carrier.name,
            "team_id": carrier.team.id,
            "team_name": carrier.team.name,
            "points": touchdown_points,
            "position": carrier.position,
            "goblin": carrier  # Store reference to the goblin
        })
        
        # End the play
        self.end_play()
        
    def score_field_goal(self, carrier):
        """Score a field goal
        
        Args:
            carrier: The carrier goblin who scored
        """
        if not carrier or not carrier.has_ball:
            return
            
        # Award points to the carrier's team
        field_goal_points = self.config.get("field_goal_points", 1)
        carrier.team.score += field_goal_points
        
        # Update stats
        carrier.stats["field_goals"] += 1
        carrier.team.stats["field_goals"] += 1
        
        # Log the event
        self.event_manager.create_and_dispatch("field_goal", {
            "carrier_id": carrier.id,
            "carrier_name": carrier.name,
            "team_id": carrier.team.id,
            "team_name": carrier.team.name,
            "points": field_goal_points,
            "position": carrier.position
        })
        
        # End the play
        self.end_play()
    
    def start_play(self):
        """Start a new play"""
        self.controller.start_play()
    
    def process_turn(self):
        """Process a single turn of the game"""
        return self.controller.process_turn()
    
    def end_play(self):
        """End the current play and swap offense/defense"""
        self.controller.end_play()
        
        # After each play is over, swap offense and defense
        # for the next play if the game isn't over
        if not self.game_complete:
            temp = self.offense_team
            self.offense_team = self.defense_team
            self.defense_team = temp
            
            # Update is_offense flags
            self.offense_team.is_offense = True
            self.defense_team.is_offense = False
    
    def end_game(self):
        """End the game"""
        self.controller.end_game()
    
    def auto_advance_turns(self):
        """Auto-advance turns if enough time has passed"""
        return self.controller.auto_advance_turns()
        
    def get_ball_carrier(self):
        """Get the current ball carrier from the offense team
        
        Returns:
            Goblin or None: The current ball carrier, or None if no carrier
        """
        return self.offense_team.get_carrier()
        
    def turn_movement_count(self, goblin):
        """Get the number of moves a goblin has made in the current turn
        
        Args:
            goblin: The goblin to check
            
        Returns:
            int: Number of moves in the current turn
        """
        # Default to 1 move per turn if not tracking
        return 1
    
    def next_turn(self):
        """Process the next turn"""
        # If we're viewing history, move forward in history
        if self.current_history_index >= 0:
            self.current_history_index -= 1
            if self.current_history_index >= 0:
                # Restore state from history
                self.restore_state_from_history(self.current_history_index)
            else:
                # Back to current state
                self.restore_current_state()
            return True
            
        # Save current state to history before processing next turn
        self.save_state_to_history()
        
        # Process the turn
        return self.process_turn()
    
    def previous_turn(self):
        """Go back to the previous turn"""
        # If we're already at the earliest saved turn, do nothing
        if self.current_history_index >= len(self.turn_history) - 1:
            return False
            
        # If we're at current state, save it first
        if self.current_history_index == -1:
            self.save_current_state()
            
        # Move back in history
        self.current_history_index += 1
        
        # Restore state from history
        self.restore_state_from_history(self.current_history_index)
        return True
    
    def save_state_to_history(self):
        """Save the current game state to history"""
        # Limit the size of history
        while len(self.turn_history) >= self.max_history:
            self.turn_history.pop()
            
        # Create a state snapshot
        state = {
            'turn': self.turn,
            'play': self.current_play,
            'goblin_positions': {},
            'goblin_states': {},
            'trails': {},
            'ball_carrier': self.get_ball_carrier().id if self.get_ball_carrier() else None
        }
        
        # Save goblin positions and states
        for team in [self.team1, self.team2]:
            for goblin in team.goblins:
                state['goblin_positions'][goblin.id] = goblin.position
                state['goblin_states'][goblin.id] = {
                    'knocked_down': goblin.knocked_down,
                    'movement': goblin.movement,
                    'has_ball': goblin.has_ball
                }
                
        # Save movement trails
        for goblin_id, trail in self.movement_trails.items():
            state['trails'][goblin_id] = trail.copy()
            
        # Insert at the beginning (newest first)
        self.turn_history.insert(0, state)
    
    def save_current_state(self):
        """Save the current state for returning to it later"""
        self.current_state = {
            'turn': self.turn,
            'play': self.current_play,
            'goblin_positions': {},
            'goblin_states': {},
            'trails': {},
            'ball_carrier': self.get_ball_carrier().id if self.get_ball_carrier() else None
        }
        
        # Save goblin positions and states
        for team in [self.team1, self.team2]:
            for goblin in team.goblins:
                self.current_state['goblin_positions'][goblin.id] = goblin.position
                self.current_state['goblin_states'][goblin.id] = {
                    'knocked_down': goblin.knocked_down,
                    'movement': goblin.movement,
                    'has_ball': goblin.has_ball
                }
                
        # Save movement trails
        for goblin_id, trail in self.movement_trails.items():
            self.current_state['trails'][goblin_id] = trail.copy()
    
    def restore_state_from_history(self, index):
        """Restore a game state from history
        
        Args:
            index: The index in history to restore from
        """
        if index < 0 or index >= len(self.turn_history):
            return
            
        state = self.turn_history[index]
        
        # Restore turn and play
        self.turn = state['turn']
        self.current_play = state['play']
        
        # Clear the grid
        self.grid.clear()
        
        # Restore goblin positions and states
        for team in [self.team1, self.team2]:
            for goblin in team.goblins:
                if goblin.id in state['goblin_positions']:
                    # Restore position
                    goblin.position = state['goblin_positions'][goblin.id]
                    
                    # Place on grid
                    self.grid.place_entity(goblin, goblin.position)
                    
                    # Restore state
                    if goblin.id in state['goblin_states']:
                        goblin_state = state['goblin_states'][goblin.id]
                        goblin.knocked_down = goblin_state['knocked_down']
                        goblin.movement = goblin_state['movement']
                        goblin.has_ball = goblin_state['has_ball']
                        
        # Restore movement trails
        self.movement_trails = {}
        for goblin_id, trail in state['trails'].items():
            self.movement_trails[goblin_id] = trail.copy()
    
    def restore_current_state(self):
        """Restore the current game state"""
        if not hasattr(self, 'current_state'):
            return
            
        state = self.current_state
        
        # Restore turn and play
        self.turn = state['turn']
        self.current_play = state['play']
        
        # Clear the grid
        self.grid.clear()
        
        # Restore goblin positions and states
        for team in [self.team1, self.team2]:
            for goblin in team.goblins:
                if goblin.id in state['goblin_positions']:
                    # Restore position
                    goblin.position = state['goblin_positions'][goblin.id]
                    
                    # Place on grid
                    self.grid.place_entity(goblin, goblin.position)
                    
                    # Restore state
                    if goblin.id in state['goblin_states']:
                        goblin_state = state['goblin_states'][goblin.id]
                        goblin.knocked_down = goblin_state['knocked_down']
                        goblin.movement = goblin_state['movement']
                        goblin.has_ball = goblin_state['has_ball']
                        
        # Restore movement trails
        self.movement_trails = {}
        for goblin_id, trail in state['trails'].items():
            self.movement_trails[goblin_id] = trail.copy()
            
        # Reset history index
        self.current_history_index = -1

def main():
    """Main entry point for the Goblinball simulation"""
    try:
        logger.info("Starting Goblinball")
        logger.info(f"Running from directory: {os.getcwd()}")
        
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
        game.renderer = renderer  # Store reference to renderer in game
        
        # Run visualization
        renderer.run()
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(traceback.format_exc())
        print("\n=== GOBLINBALL CRASHED ===")
        print(f"Error: {e}")
        print("Please check the logs for details.")
        print(f"Log file: {log_file}")
        sys.exit(1)
    finally:
        # Close debug logger
        DEBUG.close()
        logger.info("Goblinball ended")

if __name__ == "__main__":
    main() 