import random
import logging
from config import CONFIG
from utils import (
    distance, manhattan_distance, is_adjacent, 
    get_adjacent_positions, get_direction_to, 
    get_line_positions, get_positions_in_range,
    weighted_choice
)

# Import the DEBUG logger
from logger import DEBUG

class MovementSystem:
    """Handles all aspects of goblin movement in the game"""
    
    def __init__(self, game):
        self.game = game
        self.logger = logging.getLogger("goblinball.movement")
    
    def reset_movement_points(self, goblin):
        """Reset a goblin's movement points for a new turn
        
        Args:
            goblin: The goblin to reset movement points for
        """
        if not goblin.knocked_down and not goblin.unavailable:
            goblin.movement = goblin.max_movement
    
    def reset_all_movement_points(self):
        """Reset movement points for all goblins in the game"""
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                self.reset_movement_points(goblin)
    
    def move_goblin(self, goblin, target_pos):
        """Move a goblin to a new position if possible
        
        Args:
            goblin: The goblin to move
            target_pos: The target position (x, y) tuple
            
        Returns:
            bool: True if the goblin moved successfully, False otherwise
        """
        # Check if the goblin can move
        if goblin.knocked_down or goblin.unavailable:
            return False
            
        x, y = target_pos
        
        # Check if the target position is on the grid
        if not self.game.grid.is_valid_position(target_pos):
            return False
            
        # Check if the target position is empty
        occupied = self.game.grid.get_entity_at_position(target_pos)
        if occupied:
            # If attempting to move into an occupied square, try to block instead
            if hasattr(occupied, 'team') and occupied.team != goblin.team:
                return self.attempt_block(goblin, occupied)
            return False
        
        # Calculate movement distance (using Manhattan distance)
        move_distance = manhattan_distance(goblin.position, target_pos)
        
        # Check if goblin has enough movement points
        if move_distance > goblin.movement:
            return False
            
        # First check if the goblin is currently in any opponent's zone of control
        # This handles the case of leaving a zone of control
        current_blockers = self.get_adjacent_blockers(goblin.position, goblin.team)
        if current_blockers:
            # Need to make DUKE check to leave ZoC
            duke_result = self.perform_duke_check(goblin, current_blockers)
            
            if not duke_result["success"]:
                # Failed to leave ZoC
                return False
        
        # Now check for zone of control along the path
        path = self.calculate_path(goblin.position, target_pos)
        
        for pos in path[1:]:  # Skip starting position
            blockers = self.get_adjacent_blockers(pos, goblin.team)
            
            if blockers and pos != target_pos:  # If not the final position
                # Need to make DUKE check to move through ZoC
                duke_result = self.perform_duke_check(goblin, blockers)
                
                if not duke_result["success"]:
                    # Failed to move through ZoC
                    return False
            
        # Move the goblin to the new position and update the game state
        old_pos = goblin.position
        self.game.grid.move_entity(goblin, target_pos)
        goblin.position = target_pos
        
        # Update movement trail - ensure we're tracking this move correctly
        # First check if this goblin has a trail
        if goblin.id not in self.game.movement_trails:
            self.game.movement_trails[goblin.id] = []
            
        # Make sure we store the original position (start of the move)
        # For better visualization, we'll add the previous position first if it's not already there
        # This ensures we track the "from -> to" path for each move
        if not self.game.movement_trails[goblin.id] or self.game.movement_trails[goblin.id][-1] != old_pos:
            self.game.movement_trails[goblin.id].append(old_pos)
            
        # Now add the new position
        self.game.movement_trails[goblin.id].append(target_pos)
        
        # Keep only the last N positions
        while len(self.game.movement_trails[goblin.id]) > self.game.trail_length:
            self.game.movement_trails[goblin.id].pop(0)
        
        # Log the movement for debugging
        DEBUG.log(f"Goblin {goblin.name} moved from {old_pos} to {target_pos}")
        DEBUG.log(f"Movement trail: {self.game.movement_trails[goblin.id]}")
        
        # Reduce movement points
        goblin.movement -= move_distance
        
        # Update stats
        goblin.stats["moves_made"] += 1
        
        # Check for scoring
        if goblin.has_ball:
            # Check for touchdown (reaching end zone)
            if (goblin.team == self.game.team1 and target_pos[1] == 0) or \
               (goblin.team == self.game.team2 and target_pos[1] == self.game.grid_size - 1):
                self.game.score_touchdown(goblin)
                
        return True
    
    def calculate_path(self, start_pos, end_pos):
        """Calculate a path between two positions using Manhattan distance
        
        Returns:
            list: List of positions (x,y) tuples representing the path
        """
        path = [start_pos]
        current = start_pos
        
        # Simple implementation - move in straight lines 
        # First horizontally, then vertically
        x_diff = end_pos[0] - start_pos[0]
        y_diff = end_pos[1] - start_pos[1]
        
        # Move horizontally first
        x_dir = 1 if x_diff > 0 else -1 if x_diff < 0 else 0
        for _ in range(abs(x_diff)):
            current = (current[0] + x_dir, current[1])
            path.append(current)
        
        # Then move vertically
        y_dir = 1 if y_diff > 0 else -1 if y_diff < 0 else 0
        for _ in range(abs(y_diff)):
            current = (current[0], current[1] + y_dir)
            path.append(current)
        
        return path
    
    def get_adjacent_blockers(self, position, team):
        """Get all enemy goblins adjacent to a position
        
        Args:
            position: Tuple (x, y) of the position to check
            team: The team to check against (find enemies of this team)
            
        Returns:
            list: List of enemy goblins adjacent to the position
        """
        blockers = []
        x, y = position
        
        # Check all adjacent squares
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the center position
                
                check_pos = (x + dx, y + dy)
                # Ensure the position is on the grid
                if not (0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height):
                    continue
                
                entity = self.game.grid.get_entity_at_position(check_pos)
                if entity and hasattr(entity, 'team') and entity.team != team and not entity.knocked_down:
                    blockers.append(entity)
        
        return blockers
    
    def perform_duke_check(self, goblin, blockers):
        """Perform a DUKE (Dodge Under Killer Enemies) check
        
        Args:
            goblin: The goblin attempting to dodge
            blockers: List of enemy goblins in zone of control
            
        Returns:
            dict: Result of the DUKE check
        """
        # Base success chance
        success_chance = 0.5
        
        # Adjust for number of blockers (-10% per additional blocker)
        success_chance -= (len(blockers) - 1) * 0.1
        
        # Adjust for goblin's agility (+10% per point)
        success_chance += goblin.agility * 0.1
        
        # Ball carrier penalty (-20%)
        if goblin.has_ball:
            success_chance -= 0.2
        
        # Ensure chance is between 0.1 and 0.9
        success_chance = max(0.1, min(0.9, success_chance))
        
        # Roll for success
        success = random.random() < success_chance
        
        if success:
            goblin.stats["successful_dukes"] += 1
        else:
            # If DUKE check fails, goblin is knocked down and must make an injury roll
            goblin.knocked_down = True
            
            # Create knockdown event
            self.game.event_manager.create_and_dispatch("knockdown", {
                "goblin_id": goblin.id,
                "goblin_name": goblin.name,
                "goblin": goblin,
                "cause": "failed_duke"
            })
            
            # If the goblin had the ball, it's dropped and the play ends
            if goblin.has_ball:
                goblin.has_ball = False
                
                # Log ball dropped event
                self.game.event_manager.create_and_dispatch("ball_dropped", {
                    "goblin_id": goblin.id,
                    "goblin_name": goblin.name,
                    "goblin": goblin,
                    "position": goblin.position
                })
                
                # End the play since the ball carrier was knocked down
                self.game.end_play()
        
        # Create event for DUKE check
        self.game.event_manager.create_and_dispatch("duke_check", {
            "goblin_id": goblin.id,
            "goblin_name": goblin.name,
            "goblin": goblin,
            "blockers": blockers,
            "success": success,
            "chance": success_chance
        })
        
        # Add visualization if renderer exists
        if hasattr(self.game, 'renderer') and self.game.renderer:
            self.game.renderer.ui_renderer.add_duke_visualization(
                goblin, blockers, success, success_chance
            )
        
        return {
            "success": success,
            "chance": success_chance,
            "num_blockers": len(blockers),
            "goblin": goblin,
            "blockers": blockers
        }
    
    def attempt_block(self, goblin, target):
        """Attempt to block another goblin
        
        Args:
            goblin: The goblin attempting the block
            target: The goblin being blocked
            
        Returns:
            bool: True if the block was successful, False otherwise
        """
        # Check if either goblin is None 
        if not goblin or not target:
            return False
            
        # Check if goblin has enough movement points for a block
        block_cost = self.game.config.get("blocking_cost", 2)
        if goblin.movement < block_cost:
            return False
            
        # Check if the two goblins are adjacent
        if not is_adjacent(goblin.position, target.position):
            return False
            
        # Check if the target can be blocked (not knocked down already)
        if target.knocked_down:
            return False
            
        # Perform the block
        # Blocker: Strength + d10
        # Defender: Agility + d10 (-3 if carrying ball)
        blocker_roll = goblin.strength + random.randint(1, 10)
        defender_penalty = self.game.config.get("carrier_penalty", -3) if target.has_ball else 0
        defender_roll = target.agility + random.randint(1, 10) + defender_penalty
        
        # Calculate the difference
        diff = blocker_roll - defender_roll
        
        # Determine the result
        push_threshold = self.game.config.get("push_threshold", 3)
        knockdown_threshold = self.game.config.get("knockdown_threshold", 6)
        
        # The block happens regardless of result
        goblin.movement -= block_cost
        goblin.stats["blocks_attempted"] += 1
        
        result = "fail"
        
        if diff >= knockdown_threshold:
            # Knock down the target
            target.knocked_down = True
            result = "knockdown"
            goblin.stats["blocks_successful"] += 1
            goblin.stats["knockdowns_caused"] += 1
            goblin.stats["career_blocks"] += 1
            
            # Create event for knockdown
            self.game.event_manager.create_and_dispatch("knockdown", {
                "goblin_id": target.id,
                "goblin_name": target.name,
                "goblin": target
            })
            
            # If the target had the ball, it's dropped and the play ends
            if target.has_ball:
                target.has_ball = False
                
                # Log ball dropped event
                self.game.event_manager.create_and_dispatch("ball_dropped", {
                    "goblin_id": target.id,
                    "goblin_name": target.name,
                    "goblin": target,
                    "position": target.position
                })
                
                # End the play since the ball carrier was knocked down
                self.game.end_play()
            
        elif diff >= push_threshold:
            # Push the target back
            result = "push"
            goblin.stats["blocks_successful"] += 1
            goblin.stats["career_blocks"] += 1
            
            # Get direction from blocker to target
            dx = target.position[0] - goblin.position[0]
            dy = target.position[1] - goblin.position[1]
            
            # Normalize direction
            if dx != 0:
                dx = dx // abs(dx)
            if dy != 0:
                dy = dy // abs(dy)
                
            # Calculate push destination
            push_x = target.position[0] + dx
            push_y = target.position[1] + dy
            push_pos = (push_x, push_y)
            
            # Check if the push position is valid
            if 0 <= push_x < self.game.grid.width and 0 <= push_y < self.game.grid.height:
                # Check if the push position is empty
                if self.game.grid.get_entity_at_position(push_pos) is None:
                    # Move the target to the push position
                    self.game.grid.move_entity(target, push_pos)
                    target.position = push_pos
                    
                    # Create event for push
                    self.game.event_manager.create_and_dispatch("push", {
                        "pusher_id": goblin.id,
                        "pusher_name": goblin.name,
                        "pusher": goblin,
                        "target_id": target.id,
                        "target_name": target.name,
                        "target": target,
                        "from_pos": target.position,
                        "to_pos": push_pos
                    })
        
        # Log the block event
        self.game.event_manager.create_and_dispatch("block", {
            "blocker_id": goblin.id,
            "blocker_name": goblin.name,
            "blocker": goblin,
            "target_id": target.id,
            "target_name": target.name,
            "target": target,
            "result": result,
            "blocker_roll": blocker_roll,
            "defender_roll": defender_roll,
            "diff": diff,
            "target_knocked_down": target.knocked_down
        })
        
        # Add visualization if renderer exists
        if hasattr(self.game, 'renderer') and self.game.renderer:
            self.game.renderer.ui_renderer.add_block_visualization(
                goblin, target, result, blocker_roll, defender_roll
            )
        
        return result != "fail"
    
    def get_possible_moves(self, goblin):
        """Get all possible valid move positions for a goblin
        
        Args:
            goblin: The goblin to get moves for
            
        Returns:
            list: List of valid (x, y) positions the goblin can move to
        """
        if goblin.movement <= 0 or goblin.knocked_down or goblin.unavailable:
            return []
            
        current_x, current_y = goblin.position
        possible_moves = []
        
        # Check if the goblin is currently in any opponent's zone of control
        current_blockers = self.get_adjacent_blockers(goblin.position, goblin.team)
        current_duke_risk = len(current_blockers)
        
        # Determine if this is a defensive blocker trying to get to the carrier
        is_defensive_blocker = False
        carrier = None
        if goblin.team == self.game.defense_team and not goblin.has_ball:
            is_defensive_blocker = True
            carrier = self.game.offense_team.get_carrier()
        
        # Check all positions within movement range
        for dx in range(-goblin.movement, goblin.movement + 1):
            for dy in range(-goblin.movement, goblin.movement + 1):
                # Skip the current position
                if dx == 0 and dy == 0:
                    continue
                    
                # Skip positions beyond movement range (using Manhattan distance)
                if abs(dx) + abs(dy) > goblin.movement:
                    continue
                    
                new_x = current_x + dx
                new_y = current_y + dy
                new_pos = (new_x, new_y)
                
                # Ensure the position is on the grid
                if not (0 <= new_x < self.game.grid.width and 0 <= new_y < self.game.grid.height):
                    continue
                    
                # Ensure the position is empty
                if self.game.grid.get_entity_at_position(new_pos) is not None:
                    continue
                
                # Check for zone of control along the path
                path = self.calculate_path(goblin.position, new_pos)
                can_reach = True
                
                # First check if the goblin has to leave a zone of control
                if current_blockers:
                    # The success chance calculation should match perform_duke_check
                    success_chance = 0.5
                    success_chance -= (len(current_blockers) - 1) * 0.1
                    success_chance += goblin.agility * 0.1
                    if goblin.has_ball:
                        success_chance -= 0.2
                    
                    # If chance is very low, don't consider this move
                    # Use a lower threshold for defensive blockers trying to reach the carrier
                    risk_threshold = 0.2 if (is_defensive_blocker and carrier and manhattan_distance(new_pos, carrier.position) <= 2) else 0.3
                    
                    if success_chance < risk_threshold:  # Threshold for "too risky"
                        continue
                
                # Check path for zone control issues
                for pos in path[1:]:  # Skip starting position
                    blockers = self.get_adjacent_blockers(pos, goblin.team)
                    
                    if blockers and pos != new_pos:  # If not the final position
                        # Calculate DUKE success chance
                        success_chance = 0.5
                        success_chance -= (len(blockers) - 1) * 0.1
                        success_chance += goblin.agility * 0.1
                        if goblin.has_ball:
                            success_chance -= 0.2
                        
                        # If chance is very low, don't consider this move
                        # Again, use a lower threshold for defensive blockers
                        risk_threshold = 0.2 if (is_defensive_blocker and carrier and manhattan_distance(new_pos, carrier.position) <= 2) else 0.3
                        
                        if success_chance < risk_threshold:  # Threshold for "too risky"
                            can_reach = False
                            break
                
                if can_reach:
                    possible_moves.append(new_pos)
                    
        # If current position is surrounded by lots of blockers, 
        # and moving is very risky, consider staying put
        if current_duke_risk > 0:
            # Check if there are any good blocking targets from current position
            for adj_pos in get_adjacent_positions(goblin.position, self.game.grid.width):
                entity = self.game.grid.get_entity_at_position(adj_pos)
                if entity and hasattr(entity, 'team') and entity.team != goblin.team and not entity.knocked_down:
                    # Found a potential blocking target
                    # Add current position as a valid "move" to indicate blocking might be better
                    possible_moves.append(goblin.position)
                    break
        
        return possible_moves
        
    def is_blocking_position(self, goblin, position):
        """Check if a goblin can block from a given position
        
        Args:
            goblin: The goblin to check
            position: The position to check for blocking from
            
        Returns:
            tuple: (bool, target) where bool is True if can block, and target is the goblin to block
        """
        # Check all adjacent positions for enemies
        for adj_pos in get_adjacent_positions(position, self.game.grid.width):
            entity = self.game.grid.get_entity_at_position(adj_pos)
            if entity and hasattr(entity, 'team') and entity.team != goblin.team and not entity.knocked_down:
                return True, entity
                
        return False, None
        
    def can_pick_up_ball(self, goblin):
        """Check if a goblin can pick up the ball
        
        Args:
            goblin: The goblin to check
            
        Returns:
            bool: True if the goblin can pick up the ball, False otherwise
        """
        # For now, just a simple check - later we could add more conditions
        return not goblin.has_ball and not goblin.knocked_down and not goblin.unavailable 