"""
Game Controller for Goblinball
This module provides the main game controller logic, handling gameplay flow, scoring, and turn management.
"""

import random
import time
import logging
from utils import manhattan_distance

logger = logging.getLogger("goblinball.controller")

class GameController:
    """Handles game logic, turn management, and scoring"""
    
    def __init__(self, game):
        """Initialize the game controller
        
        Args:
            game: The main Game instance to control
        """
        self.game = game
        self.last_turn_time = time.time()
        
    def start_play(self):
        """Start a new play"""
        self.game.current_play += 1
        self.game.turn = 0
        self.game.play_complete = False
        
        logger.info(f"===== Starting Play {self.game.current_play} =====")
        
        # Reset goblin movement points
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                goblin.movement = goblin.max_movement
                goblin.knocked_down = False
                
                # Check for injuries from previous plays
                if goblin.misses_plays > 0:
                    goblin.misses_plays -= 1
                    goblin.unavailable = goblin.misses_plays > 0
                else:
                    goblin.unavailable = False
                
        # Position teams
        self.position_teams()
        
        # Log the play start
        self.game.event_manager.create_and_dispatch("play_start", {
            "play_number": self.game.current_play,
            "offense_team": self.game.offense_team.name,
            "carrier": self.game.offense_team.get_carrier().name
        })
    
    def position_teams(self):
        """Position the teams on the field for the start of a play"""
        # Clear the grid
        self.game.grid.clear()
        
        # Clear movement trails
        self.game.movement_trails = {}
        
        # Position team1 in bottom half
        for i, goblin in enumerate(self.game.team1.goblins):
            if goblin.out_of_game:
                continue
                
            # Simple row formation at the bottom
            y = 8  # Second-to-last row
            x = 2 + i * 2  # Spread out across the row
            
            # Ensure we're within grid bounds
            x = min(x, self.game.grid.width - 1)
            
            self.game.grid.place_entity(goblin, (x, y))
            goblin.position = (x, y)
            
            # Initialize movement trail for this goblin
            self.game.movement_trails[goblin.id] = [goblin.position]
            
            logger.debug(f"Positioned {goblin.name} at ({x}, {y})")
            
        # Position team2 in top half
        for i, goblin in enumerate(self.game.team2.goblins):
            if goblin.out_of_game:
                continue
                
            # Simple row formation at the top
            y = 1  # Second row
            x = 2 + i * 2  # Spread out across the row
            
            # Ensure we're within grid bounds
            x = min(x, self.game.grid.width - 1)
            
            self.game.grid.place_entity(goblin, (x, y))
            goblin.position = (x, y)
            
            # Initialize movement trail for this goblin
            self.game.movement_trails[goblin.id] = [goblin.position]
            
            logger.debug(f"Positioned {goblin.name} at ({x}, {y})")
            
        # Select carrier for offense team
        self.game.offense_team.select_next_carrier()
        carrier = self.game.offense_team.get_carrier()
        logger.info(f"Selected carrier: {carrier.name} from team {self.game.offense_team.name}")
    
    def process_turn(self):
        """Process a single turn of the game
        
        Returns:
            bool: True if the turn was processed, False if the play is already complete
        """
        if self.game.play_complete or self.game.game_complete:
            return False
            
        # Increment turn counter
        self.game.turn += 1
        max_turns = self.game.config.get("max_turns_per_play", 30)
        
        logger.info(f"==== Processing Turn {self.game.turn} ====")
        logger.info(f"Offense Team: {self.game.offense_team.name}, Defense Team: {self.game.defense_team.name}")
        
        # Log turn start
        self.game.event_manager.create_and_dispatch("turn_start", {
            "turn": self.game.turn,
            "play": self.game.current_play
        })
        
        # Reset movement points for all goblins at the start of each turn
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                if not goblin.knocked_down and not goblin.unavailable:
                    goblin.movement = goblin.max_movement
        
        # Check for turn limit
        if self.game.turn > max_turns:
            self.game.event_manager.create_and_dispatch("turn_limit_reached", {
                "max_turns": max_turns
            })
            logger.info(f"Turn limit of {max_turns} reached. Ending play.")
            self.end_play()
            return True
        
        # Process goblin actions in order:
        # 1. Move the carrier first
        carrier = self.game.offense_team.get_carrier()
        if carrier and not carrier.knocked_down and not carrier.unavailable:
            # Move the carrier
            logger.info(f"Attempting to move carrier {carrier.name}")
            carrier_moved = self.game.carrier_movement.move_carrier(carrier)
            
            # Check for scoring
            if self.check_scoring(carrier):
                logger.info(f"Carrier {carrier.name} scored! Ending play.")
                self.end_play()
                return True
        
        # 2. Move offensive blockers
        logger.info(f"Moving offensive blockers for team {self.game.offense_team.name}")
        for goblin in self.game.offense_team.goblins:
            if goblin != carrier and not goblin.knocked_down and not goblin.unavailable:
                self.game.blocker_movement.move_blocker(goblin)
                
        # 3. Move defensive blockers
        logger.info(f"Moving defensive blockers for team {self.game.defense_team.name}")
        for goblin in self.game.defense_team.goblins:
            if not goblin.knocked_down and not goblin.unavailable:
                self.game.blocker_movement.move_blocker(goblin)
                
        # Log turn end
        self.game.event_manager.create_and_dispatch("turn_end", {
            "turn": self.game.turn,
            "play": self.game.current_play
        })
        
        return True
    
    def check_scoring(self, carrier):
        """Check if a carrier has scored
        
        Args:
            carrier: The carrier goblin to check
            
        Returns:
            bool: True if the carrier scored, False otherwise
        """
        if not carrier.has_ball:
            return False
            
        # Check for touchdown (reaching end zone)
        x, y = carrier.position
        
        # Team 1 scores at top (y=0), Team 2 scores at bottom (y=grid_height-1)
        if (carrier.team == self.game.team1 and y == 0) or \
           (carrier.team == self.game.team2 and y == self.game.grid.height - 1):
            # Score touchdown!
            self.game.score_touchdown(carrier)
            return True
            
        return False
    
    def score_touchdown(self, carrier):
        """Score a touchdown
        
        Args:
            carrier: The carrier goblin who scored
            
        NOTE: This method should be moved to the Game class
        """
        if not carrier or not carrier.has_ball:
            return
            
        # Award points to the carrier's team
        touchdown_points = self.game.config.get("touchdown_points", 3)
        carrier.team.score += touchdown_points
        
        # Update stats
        carrier.stats["touchdowns"] += 1
        carrier.stats["career_touchdowns"] += 1
        carrier.team.stats["touchdowns"] += 1
        
        # Log the event
        self.game.event_manager.create_and_dispatch("touchdown", {
            "carrier_id": carrier.id,
            "carrier_name": carrier.name,
            "team_id": carrier.team.id,
            "team_name": carrier.team.name,
            "points": touchdown_points,
            "position": carrier.position
        })
        
        # End the play
        self.end_play()
        
    def score_field_goal(self, carrier):
        """Score a field goal
        
        Args:
            carrier: The carrier goblin who scored
            
        NOTE: This method should be moved to the Game class
        """
        if not carrier or not carrier.has_ball:
            return
            
        # Award points to the carrier's team
        field_goal_points = self.game.config.get("field_goal_points", 1)
        carrier.team.score += field_goal_points
        
        # Update stats
        carrier.stats["field_goals"] += 1
        carrier.team.stats["field_goals"] += 1
        
        # Log the event
        self.game.event_manager.create_and_dispatch("field_goal", {
            "carrier_id": carrier.id,
            "carrier_name": carrier.name,
            "team_id": carrier.team.id,
            "team_name": carrier.team.name,
            "points": field_goal_points,
            "position": carrier.position
        })
        
        # End the play
        self.end_play()
    
    def swap_offense_defense(self):
        """Swap offense and defense roles"""
        # Swap roles
        temp = self.game.offense_team
        self.game.offense_team = self.game.defense_team
        self.game.defense_team = temp
        
        # Update is_offense flags
        self.game.offense_team.is_offense = True
        self.game.defense_team.is_offense = False
        
        logger.info(f"Teams swapped: {self.game.offense_team.name} now on offense, {self.game.defense_team.name} on defense")
        
    def end_play(self):
        """End the current play"""
        self.game.play_complete = True
        
        logger.info(f"===== Ending Play {self.game.current_play} after {self.game.turn} turns =====")
        logger.info(f"Score: {self.game.team1.name} {self.game.team1.score} - {self.game.team2.score} {self.game.team2.name}")
        
        # Log the play end
        self.game.event_manager.create_and_dispatch("play_end", {
            "play_number": self.game.current_play,
            "turns": self.game.turn,
            "score": {
                self.game.team1.name: self.game.team1.score,
                self.game.team2.name: self.game.team2.score
            }
        })
        
        # Update stats
        self.game.game_stats["longest_play_turns"] = max(self.game.game_stats["longest_play_turns"], self.game.turn)
        
        # Check if game is complete
        if self.game.current_play >= self.game.max_plays:
            self.end_game()
            
    def end_game(self):
        """End the game"""
        self.game.game_complete = True
        
        # Determine winner
        if self.game.team1.score > self.game.team2.score:
            winner = self.game.team1
            winner_name = self.game.team1.name
        elif self.game.team2.score > self.game.team1.score:
            winner = self.game.team2
            winner_name = self.game.team2.name
        else:
            winner = None  # Tie
            winner_name = "Tie"
            
        logger.info("===== GAME OVER =====")
        logger.info(f"Final Score: {self.game.team1.name} {self.game.team1.score} - {self.game.team2.score} {self.game.team2.name}")
        logger.info(f"Winner: {winner_name}")
        
        # Log the game end
        self.game.event_manager.create_and_dispatch("game_end", {
            "winner": winner_name,
            "winner_team": winner,
            "score": {
                self.game.team1.name: self.game.team1.score,
                self.game.team2.name: self.game.team2.score
            },
            "plays": self.game.current_play
        })
        
        # Update team stats
        self.game.team1.update_stats(self.game.team2.score)
        self.game.team2.update_stats(self.game.team1.score)
        
        # Update career stats for all goblins
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                goblin.add_game_stats_to_career()
    
    def auto_advance_turns(self):
        """Auto-advance turns if enough time has passed
        
        Returns:
            bool: True if a turn was advanced, False otherwise
        """
        if self.game.auto_advance and time.time() - self.last_turn_time > self.game.turn_delay:
            self.last_turn_time = time.time()
            
            if self.game.play_complete:
                if not self.game.game_complete:
                    self.start_play()
                    return True
            else:
                self.process_turn()
                return True
                
        return False 