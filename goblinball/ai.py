import random
import logging
import time
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
        """Reset a goblin's movement points for a new turn"""
        goblin.movement = goblin.max_movement
    
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
            
        # Check if the goblin is currently in any opponent's zone of control
        # DUKE check is only needed when LEAVING a zone of control
        current_blockers = self.get_adjacent_blockers(goblin.position, goblin.team)
        
        if current_blockers:
            # Need to make DUKE check to leave ZoC
            duke_result = self.perform_duke_check(goblin, current_blockers)
            
            if not duke_result["success"]:
                # Failed to leave ZoC
                return False
            
        # Move the goblin to the new position and update the game state
        old_pos = goblin.position
        self.game.grid.move_entity(goblin, target_pos)
        goblin.position = target_pos
        
        # Update movement trail
        self.game.update_movement_trail(goblin, target_pos)
        
        # Reduce movement points
        goblin.movement -= move_distance
        
        # Update stats
        goblin.stats["moves_made"] += 1
        
        # Check for scoring
        if goblin.has_ball:
            # Check for touchdown (reaching end zone)
            if (goblin.team == self.game.team1 and target_pos[1] == 0) or \
               (goblin.team == self.game.team2 and target_pos[1] == self.game.grid_size - 1):
                self.game.controller.score_touchdown(goblin)
                
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
        
        # Adjust for goblin's dodge skill (+10% per point)
        success_chance += goblin.dodge_skill * 0.1
        
        # Ball carrier penalty (-20%)
        if goblin.has_ball:
            success_chance -= 0.2
        
        # Ensure chance is between 0.1 and 0.9
        success_chance = max(0.1, min(0.9, success_chance))
        
        # Roll for success
        success = random.random() < success_chance
        
        if success:
            goblin.stats["successful_dukes"] += 1
        
        return {
            "success": success,
            "chance": success_chance,
            "num_blockers": len(blockers),
            "goblin": goblin,
            "blockers": blockers
        }
    
    def attempt_block(self, goblin, target):
        """Attempt to block an enemy goblin
        
        Args:
            goblin: The goblin attempting to block
            target: The enemy goblin to block
            
        Returns:
            dict: Result of the block attempt
        """
        # Check if goblin has at least 1 movement point
        if goblin.movement < 1:
            return {"success": False, "reason": "Not enough movement points to block"}
        
        # Perform the block
        block_result = goblin.block(target)
        
        # Use 1 movement point regardless of success
        goblin.movement -= 1
        
        events = [{
            "type": "block_attempt",
            "blocker": goblin,
            "target": target,
            "result": block_result["result"],
            "margin": block_result["margin"]
        }]
        
        # Handle knockdown
        if block_result["result"] in ["knockdown", "knockdown_with_injury"]:
            events.append({
                "type": "knockdown",
                "goblin": target,
                "blocker": goblin
            })
            
            # If the target had the ball, it's dropped
            if target.has_ball:
                target.has_ball = False
                # Calculate scatter direction and distance
                scatter_direction = (random.randint(-1, 1), random.randint(-1, 1))
                scatter_distance = random.randint(1, 3)
                
                # Calculate final position
                scatter_pos = (
                    target.position[0] + scatter_direction[0] * scatter_distance,
                    target.position[1] + scatter_direction[1] * scatter_distance
                )
                
                # Ensure the ball stays on the grid
                scatter_pos = (
                    max(0, min(scatter_pos[0], self.game.grid.width - 1)),
                    max(0, min(scatter_pos[1], self.game.grid.height - 1))
                )
                
                # Place the ball at the scatter position
                self.game.ball_position = scatter_pos
                events.append({
                    "type": "ball_dropped",
                    "previous_carrier": target,
                    "new_position": scatter_pos
                })
        
        # Handle injury
        if block_result["result"] == "knockdown_with_injury":
            # Check what kind of injury
            injury_type = "minor_injury"  # Assume minor by default
            
            # Check if goblin is out of game
            if target.out_of_game:
                injury_type = "career_ending_injury"
            elif target.misses_plays > 1:
                injury_type = "major_injury"
            
            events.append({
                "type": "injury",
                "goblin": target,
                "injury_type": injury_type,
                "plays_missed": target.misses_plays
            })
        
        return {
            "success": True,
            "block_result": block_result["result"],
            "events": events
        }
    
    def can_pick_up_ball(self, goblin):
        """Check if a goblin can pick up the ball
        
        Args:
            goblin: The goblin to check
            
        Returns:
            bool: True if the goblin can pick up the ball, False otherwise
        """
        # Check if goblin is at the ball's position
        if goblin.position != self.game.ball_position:
            return False
        
        # Check if goblin is knocked down or unavailable
        if goblin.knocked_down or goblin.unavailable:
            return False
        
        # Check if goblin has enough movement points to pick up the ball (costs 1)
        if goblin.movement < 1:
            return False
        
        return True
    
    def pick_up_ball(self, goblin):
        """Attempt to pick up the ball
        
        Args:
            goblin: The goblin attempting to pick up the ball
            
        Returns:
            dict: Result of the attempt
        """
        if not self.can_pick_up_ball(goblin):
            return {"success": False, "reason": "Cannot pick up ball"}
        
        # Roll for success - base 70% chance
        success_chance = 0.7
        
        # Adjust for adjacent enemies (-10% per enemy)
        adjacent_enemies = self.get_adjacent_blockers(goblin.position, goblin.team)
        success_chance -= len(adjacent_enemies) * 0.1
        
        # Ensure chance is between 0.2 and 0.9
        success_chance = max(0.2, min(0.9, success_chance))
        
        # Roll for success
        success = random.random() < success_chance
        
        if success:
            # Ball is picked up
            goblin.has_ball = True
            self.game.ball_position = None  # Ball is now with the goblin
            
            # Use 1 movement point
            goblin.movement -= 1
            
            return {
                "success": True,
                "events": [{
                    "type": "ball_pickup",
                    "goblin": goblin,
                    "position": goblin.position
                }]
            }
        else:
            # Failed to pick up, ball remains where it is
            # Use 1 movement point anyway
            goblin.movement -= 1
            
            # Calculate scatter
            scatter_direction = (random.randint(-1, 1), random.randint(-1, 1))
            scatter_distance = 1  # Short scatter for failed pickup
            
            # Calculate final position
            scatter_pos = (
                goblin.position[0] + scatter_direction[0] * scatter_distance,
                goblin.position[1] + scatter_direction[1] * scatter_distance
            )
            
            # Ensure the ball stays on the grid
            scatter_pos = (
                max(0, min(scatter_pos[0], self.game.grid.width - 1)),
                max(0, min(scatter_pos[1], self.game.grid.height - 1))
            )
            
            # Place the ball at the scatter position
            self.game.ball_position = scatter_pos
            
            return {
                "success": False,
                "reason": "Failed to pick up ball",
                "events": [{
                    "type": "ball_pickup_failed",
                    "goblin": goblin,
                    "new_position": scatter_pos
                }]
            }

    def get_possible_moves(self, goblin):
        """Get all valid positions the goblin can move to with current movement points
        
        Args:
            goblin: The goblin to check
            
        Returns:
            list: List of (x, y) tuples representing valid move positions
        """
        if goblin.knocked_down or goblin.unavailable or goblin.movement <= 0:
            return []
            
        # Get all positions within movement range
        valid_positions = []
        current_x, current_y = goblin.position
        
        # Check if goblin is currently in a zone of control
        current_blockers = self.get_adjacent_blockers(goblin.position, goblin.team)
        needs_duke_check = len(current_blockers) > 0
        
        # Check all positions within manhattan distance of movement points
        for dx in range(-goblin.movement, goblin.movement + 1):
            for dy in range(-goblin.movement, goblin.movement + 1):
                # Skip if total movement would exceed movement points
                if abs(dx) + abs(dy) > goblin.movement:
                    continue
                    
                # Skip current position
                if dx == 0 and dy == 0:
                    continue
                    
                # Calculate potential position
                pos_x = current_x + dx
                pos_y = current_y + dy
                pos = (pos_x, pos_y)
                
                # Check if position is valid
                if not (0 <= pos_x < self.game.grid.width and 0 <= pos_y < self.game.grid.height):
                    continue
                    
                # Check if position is empty
                if self.game.grid.get_entity_at_position(pos) is not None:
                    # If occupied by an enemy, we can try to block
                    entity = self.game.grid.get_entity_at_position(pos)
                    if hasattr(entity, 'team') and entity.team != goblin.team:
                        valid_positions.append(pos)
                    continue
                
                # Calculate the movement cost to reach this position
                move_distance = manhattan_distance(goblin.position, pos)
                
                # If the goblin needs to make a DUKE check to leave its current position,
                # verify that it would likely succeed
                if needs_duke_check:
                    # Estimate DUKE success chance
                    duke_chance = self.estimate_duke_success_chance(goblin, current_blockers)
                    
                    # If DUKE chance is very low, don't consider this move valid
                    if duke_chance < 0.3:  # Only consider moves with at least 30% chance
                        continue
                
                # If we can reach the position with our movement points, add it
                if move_distance <= goblin.movement:
                    valid_positions.append(pos)
        
        return valid_positions
        
    def estimate_duke_success_chance(self, goblin, blockers):
        """Estimate the chance of a successful DUKE check without actually performing it
        
        Args:
            goblin: The goblin attempting to dodge
            blockers: List of enemy goblins in zone of control
            
        Returns:
            float: Estimated success chance (0.0-1.0)
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
        return max(0.1, min(0.9, success_chance))

    def find_path_to(self, goblin, target_pos):
        """Find a path for the goblin to the target position
        
        Args:
            goblin: The goblin to move
            target_pos: Tuple (x, y) of the target position
            
        Returns:
            list: List of positions to move through, or empty list if no path
        """
        if goblin.knocked_down or goblin.unavailable or goblin.movement <= 0:
            return []
            
        # If target is not valid, return empty path
        if not self.game.grid.is_valid_position(target_pos):
            return []
            
        # If target is occupied, check if it's an enemy (for blocking)
        entity = self.game.grid.get_entity_at_position(target_pos)
        if entity and not (hasattr(entity, 'team') and entity.team != goblin.team):
            return []
            
        # Get all valid moves
        valid_moves = self.get_possible_moves(goblin)
        
        # If target is in valid moves, return direct path
        if target_pos in valid_moves:
            return [target_pos]
            
        # Otherwise, find the move that gets us closest to the target
        if valid_moves:
            closest_move = min(valid_moves, key=lambda pos: manhattan_distance(pos, target_pos))
            return [closest_move]
            
        return []


class CarrierMovement:
    """Specialized movement logic for the ball carrier"""
    
    def __init__(self, game, movement_system):
        self.game = game
        self.movement_system = movement_system
        
    def move_carrier(self, carrier):
        """Move the ball carrier based on the current game state"""
        if carrier.knocked_down or carrier.unavailable or carrier.movement <= 0:
            DEBUG.log(f"Carrier {carrier.name} cannot move")
            return False
            
        DEBUG.log(f"Moving carrier {carrier.name} with {carrier.movement} movement points")
        
        # Get current position
        current_x, current_y = carrier.position
        
        # Set a base goal based on offense direction
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        target_x = self.game.grid.width // 2  # Center of the field
        
        # Use different strategies for finding movement targets
        # 1. First try to move directly toward the end zone
        # 2. If blocked, look for alternate routes
        # 3. As a last resort, move laterally
        
        # Calculate path options with different priorities
        direct_path = self.get_direct_path(carrier, (target_x, target_y))
        flanking_paths = self.get_flanking_paths(carrier, target_y)
        safe_paths = self.get_safe_paths(carrier)
        
        # Merge and prioritize paths
        all_paths = []
        all_paths.extend([(p, 3) for p in direct_path])  # Direct path - highest priority
        all_paths.extend([(p, 2) for p in flanking_paths])  # Flanking - medium priority
        all_paths.extend([(p, 1) for p in safe_paths])  # Safe - lowest priority
        
        # Sort by priority (highest first) and distance (closest first)
        all_paths.sort(key=lambda x: (-x[1], manhattan_distance(carrier.position, x[0])))
        
        # Filter out moves that are beyond movement range or blocked
        valid_moves = []
        for move, priority in all_paths:
            # Check if we have enough movement points
            distance = manhattan_distance(carrier.position, move)
            if distance <= carrier.movement:
                # Check if the move is valid (empty space, on grid)
                if self.is_valid_move(carrier, move):
                    valid_moves.append(move)
                    
        # If we have valid moves, try to execute the best one
        if valid_moves:
            for move in valid_moves:
                # Try to move the carrier
                if self.movement_system.move_goblin(carrier, move):
                    DEBUG.log(f"Carrier {carrier.name} moved to {move}")
                    return True
                
        # If we get here, no valid moves found or all moves failed
        DEBUG.log(f"Carrier {carrier.name} couldn't find valid move")
        return False


class BlockerMovement:
    """Specialized movement logic for blockers"""
    
    def __init__(self, game, movement_system):
        self.game = game
        self.movement_system = movement_system
        self.formation_offsets = [
            (-1, -1),  # Up-left
            (0, -1),   # Up
            (1, -1),   # Up-right
            (-1, 0),   # Left
            (1, 0),    # Right
            (-1, 1),   # Down-left
            (0, 1),    # Down
            (1, 1),    # Down-right
        ]
        
    def move_blocker(self, blocker):
        """Move the blocker according to their team's strategy"""
        if blocker.knocked_down or blocker.unavailable or blocker.movement <= 0:
            return False
            
        # Different behavior for offense and defense
        if blocker.team == self.game.offense_team:
            return self.move_offensive_blocker(blocker)
        else:
            return self.move_defensive_blocker(blocker)
            
    def move_offensive_blocker(self, blocker):
        """Move an offensive blocker
        
        Args:
            blocker: The blocker goblin to move
            
        Returns:
            bool: True if the blocker moved successfully, False otherwise
        """
        # If no movement points left, can't move
        if blocker.movement <= 0 or blocker.knocked_down or blocker.unavailable:
            return False
            
        DEBUG.log(f"Moving offensive blocker {blocker.name} with {blocker.movement} movement points")
        
        # Get carrier and current positions
        carrier = blocker.team.get_carrier()
        if not carrier:
            DEBUG.log(f"No carrier found for team {blocker.team.name}!")
            return False
            
        blocker_x, blocker_y = blocker.position
        carrier_x, carrier_y = carrier.position
        
        # Identify defensive blockers near carrier
        enemies_near_carrier = []
        
        for x in range(self.game.grid.width):
            for y in range(self.game.grid.height):
                goblin = self.game.grid.get_entity_at_position((x, y))
                if goblin and goblin.team != blocker.team and not goblin.knocked_down:
                    dist_to_carrier = manhattan_distance((x, y), carrier.position)
                    if dist_to_carrier <= 3:  # Within threatening range
                        enemies_near_carrier.append((goblin, dist_to_carrier))
        
        # Sort enemies by distance to carrier (closest first)
        enemies_near_carrier.sort(key=lambda x: x[1])
        
        # 1. Try to find a blocking target first
        if blocker.movement >= CONFIG.get("blocking_cost", 2):
            for enemy, dist in enemies_near_carrier:
                if self.is_adjacent(blocker, enemy):
                    # Try to block this enemy
                    DEBUG.log(f"Attempt block of {enemy.name} by {blocker.name}")
                    if self.movement_system.attempt_block(blocker, enemy):
                        DEBUG.log(f"Block succeeded!")
                        return True
        
        # Calculate priorities and possible moves
        possible_moves = self.movement_system.get_possible_moves(blocker)
        
        # Define offensive blocker goals based on situation:
        # 1. Position between carrier and closest enemies
        # 2. Move to block advancing enemies
        
        # Get direction to end zone
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        forward_dir = -1 if carrier.team == self.game.team1 else 1
        
        # Calculate optimal screening positions
        screening_positions = []
        
        # If enemies near carrier, try to screen them
        if enemies_near_carrier:
            # For each enemy, calculate a position between them and the carrier
            for enemy, dist in enemies_near_carrier:
                enemy_x, enemy_y = enemy.position
                
                # Calculate vector from carrier to enemy
                dx = enemy_x - carrier_x
                dy = enemy_y - carrier_y
                
                # Normalize and scale to get a position adjacent to the carrier
                length = max(1, abs(dx) + abs(dy))
                ndx = dx / length
                ndy = dy / length
                
                # Calculate position 1 step from carrier toward enemy
                screen_x = int(carrier_x + ndx)
                screen_y = int(carrier_y + ndy)
                
                # Ensure within grid bounds
                screen_x = max(0, min(screen_x, self.game.grid.width - 1))
                screen_y = max(0, min(screen_y, self.game.grid.height - 1))
                
                # Add to potential positions
                screening_positions.append((screen_x, screen_y))
        
        # Score each possible move
        move_scores = {}
        
        for move in possible_moves:
            move_x, move_y = move
            
            # Initialize score
            score = 0
            
            # Priority 1: Screening positions get highest priority
            if move in screening_positions:
                score += 1000
                
            # Priority 2: Stay close to carrier
            dist_to_carrier = manhattan_distance(move, carrier.position)
            carrier_proximity = 10 - min(10, dist_to_carrier)  # Higher for closer positions
            score += carrier_proximity * 100
            
            # Priority 3: Forward position (relative to direction of carrier movement)
            if forward_dir == -1:  # Moving upward
                forward_score = 10 - min(10, move_y)  # Higher for smaller y (closer to top)
            else:  # Moving downward
                forward_score = min(10, move_y)  # Higher for larger y (closer to bottom)
                
            score += forward_score * 10
            
            # Priority 4: Position to block enemies
            for enemy, _ in enemies_near_carrier:
                enemy_x, enemy_y = enemy.position
                
                # Calculate position of blocker relative to carrier and enemy
                is_between = False
                
                # Check if blocker would be between carrier and enemy
                if forward_dir == -1:  # Moving upward
                    if move_y < carrier_y and move_y > enemy_y and abs(move_x - enemy_x) <= 1:
                        is_between = True
                else:  # Moving downward
                    if move_y > carrier_y and move_y < enemy_y and abs(move_x - enemy_x) <= 1:
                        is_between = True
                        
                if is_between:
                    score += 200
                    
            # Slight penalty for moving backward
            current_dist_to_goal = abs(blocker_y - target_y)
            new_dist_to_goal = abs(move_y - target_y)
            
            if new_dist_to_goal > current_dist_to_goal:
                score -= 50
                
            # Add some randomness
            score += random.randint(-25, 25)
            
            # Store the score
            move_scores[move] = score
            
        # Choose the best move
        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            DEBUG.log(f"Offensive blocker chose move {best_move} with score {move_scores[best_move]}")
            return self.movement_system.move_goblin(blocker, best_move)
            
        return False
        
    def move_defensive_blocker(self, blocker):
        """Move a defensive blocker to intercept the carrier aggressively"""
        # Find the carrier
        carrier = self.game.offense_team.get_carrier()
        if not carrier:
            return False
            
        blocker_x, blocker_y = blocker.position
        carrier_x, carrier_y = carrier.position
        
        # Determine carrier's goal direction
        if carrier.team == self.game.team1:
            goal_y = 0
        else:
            goal_y = self.game.grid_size - 1
            
        # 1. If adjacent to carrier, try to block it immediately
        if is_adjacent(blocker.position, carrier.position):
            DEBUG.log(f"Defensive blocker {blocker.name} adjacent to carrier! Attempting block")
            return self.try_block(blocker, carrier)
            
        # 2. Check for torch row
        on_lit_row = self.game.torch_rows[blocker_y] if hasattr(self.game, 'torch_rows') else False
        if on_lit_row:
            # Need to escape the torch row
            DEBUG.log(f"Defensive blocker {blocker.name} on lit torch row {blocker_y}")
            
            # Move toward carrier while escaping torch
            possible_moves = self.movement_system.get_possible_moves(blocker)
            safe_moves = [pos for pos in possible_moves if not self.game.torch_rows[pos[1]]]
            
            if safe_moves:
                best_move = min(safe_moves, key=lambda pos: manhattan_distance(pos, carrier.position))
                return self.movement_system.move_goblin(blocker, best_move)
            
            # If no safe moves, just try to get off the row
            for y in [blocker_y - 1, blocker_y + 1]:
                if 0 <= y < self.game.grid_size and not self.game.torch_rows[y]:
                    for x in [blocker_x, blocker_x - 1, blocker_x + 1]:
                        if 0 <= x < self.game.grid_size and self.game.grid.get_entity_at_position((x, y)) is None:
                            return self.movement_system.move_goblin(blocker, (x, y))
        
        # 3. Interceptor strategy - try to intercept carrier's path to goal
        if random.random() < 0.6:  # 60% chance to use interceptor strategy
            DEBUG.log(f"Defensive blocker {blocker.name} using interception strategy")
            
            # Predict carrier's path to end zone
            predicted_path = []
            
            # For simplicity, assume carrier will move in a direct line to the goal
            predict_x = carrier_x
            step_y = -1 if carrier.team == self.game.team1 else 1
            
            for y in range(carrier_y, goal_y + step_y, step_y):
                predicted_path.append((predict_x, y))
                
            # Try to intercept at some point along the path
            # Prioritize closer intercept points
            intercept_positions = []
            
            for path_pos in predicted_path:
                # Find positions adjacent to this path point
                for dx, dy in self.formation_offsets:
                    intercept_x = path_pos[0] + dx
                    intercept_y = path_pos[1] + dy
                    if 0 <= intercept_x < self.game.grid_size and 0 <= intercept_y < self.game.grid_size:
                        intercept_positions.append((intercept_x, intercept_y))
            
            # Sort by distance from blocker
            intercept_positions.sort(key=lambda pos: manhattan_distance(pos, blocker.position))
            
            # Try each intercept position
            for pos in intercept_positions:
                if self.movement_system.move_goblin(blocker, pos):
                    DEBUG.log(f"Blocker intercepting at {pos}")
                    return True
        
        # 4. Direct pursuit - move directly toward carrier
        DEBUG.log(f"Defensive blocker {blocker.name} directly pursuing carrier")
        possible_moves = self.movement_system.get_possible_moves(blocker)
        if possible_moves:
            best_move = min(possible_moves, key=lambda pos: manhattan_distance(pos, carrier.position))
            return self.movement_system.move_goblin(blocker, best_move)
            
        return False
    
    def try_block(self, blocker, target):
        """Attempt to block a target goblin
        Returns True if the block was attempted, False otherwise"""
        # Check if we have enough movement points
        block_cost = CONFIG.get("blocking_cost", 2)
        if blocker.movement < block_cost:
            return False
            
        # Check if we're adjacent
        if not is_adjacent(blocker.position, target.position):
            return False
            
        # Perform the block
        block_result = blocker.block(target)
        
        # Create event
        self.game.event_manager.create_and_dispatch("block", {
            "blocker_id": blocker.id,
            "blocker_name": blocker.name,
            "target_id": target.id,
            "target_name": target.name,
            "result": block_result["result"],
            "margin": block_result["margin"],
            "blocker_roll": block_result["blocker_roll"],
            "target_roll": block_result["target_roll"]
        })
        
        # Apply block effects
        if block_result["result"] == "push":
            # Push the target back
            self.push_goblin(target, blocker.position)
        elif block_result["result"] == "knockdown":
            # Target is already marked as knocked down in the block function
            # Log the knockdown
            self.game.event_manager.create_and_dispatch("knockdown", {
                "blocker_name": blocker.name,
                "target_name": target.name
            })
            
        # Use movement points
        blocker.movement -= block_cost
        
        return True
    
    def push_goblin(self, goblin, from_position):
        """Push a goblin away from the given position"""
        # Get direction away from pusher
        dx, dy = get_direction_to(from_position, goblin.position)
        
        # Calculate push destination
        push_x = goblin.position[0] + dx
        push_y = goblin.position[1] + dy
        
        # Check if push destination is valid
        if not (0 <= push_x < self.game.grid_size and 0 <= push_y < self.game.grid_size):
            # Can't push out of bounds, target stays put
            return False
            
        # Check if destination is occupied
        if self.game.grid.get_entity_at_position((push_x, push_y)) is not None:
            # Destination occupied, target stays put
            return False
            
        # Move the goblin to the push destination
        current_x, current_y = goblin.position
        self.game.grid.move_entity(goblin, (push_x, push_y))
        goblin.position = (push_x, push_y)
        
        # Create push event
        self.game.event_manager.create_and_dispatch("push", {
            "goblin_name": goblin.name,
            "from": (current_x, current_y),
            "to": (push_x, push_y)
        })
        
        return True 