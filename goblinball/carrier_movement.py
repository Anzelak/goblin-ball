import random
import logging
from utils import manhattan_distance, get_adjacent_positions
from logger import DEBUG

class CarrierMovement:
    """Handles movement logic for the ball carrier"""
    
    def __init__(self, game, movement_system):
        self.game = game
        self.movement_system = movement_system
        self.logger = logging.getLogger("goblinball.carrier")
        
    def move_carrier(self, carrier):
        """Move the ball carrier using an appropriate strategy
        
        Args:
            carrier: The carrier goblin to move
            
        Returns:
            bool: True if the carrier moved successfully, False otherwise
        """
        # Check if the carrier can move
        if carrier.movement <= 0 or carrier.knocked_down or carrier.unavailable:
            return False
            
        DEBUG.log(f"Moving carrier {carrier.name} with {carrier.movement} movement points")
        
        # Get current position
        current_x, current_y = carrier.position
        
        # Set a base goal based on offense direction
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        target_x = self.game.grid.width // 2  # Center of the field
        
        # Determine forward direction (towards end zone)
        forward_direction = -1 if carrier.team == self.game.team1 else 1
        
        # Check if carrier is in field goal range
        if self.in_field_goal_range(carrier):
            # Check if touchdown is possible (within movement range)
            if abs(current_y - target_y) <= carrier.movement:
                # Touchdown is possible, don't attempt field goal
                # (AI will prioritize direct path to end zone)
                pass
            else:
                # Touchdown not possible, attempt field goal
                self.attempt_field_goal(carrier)
                return True
        
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
        
        # Get previously visited positions in this play
        previously_visited = set(self.game.get_movement_trail(carrier))
        
        # Filter out moves that are beyond movement range, blocked, backwards, or previously visited
        valid_moves = []
        for move, priority in all_paths:
            # Check if we have enough movement points
            distance = manhattan_distance(carrier.position, move)
            if distance <= carrier.movement:
                # Check if the move is valid (empty space, on grid)
                if self.is_valid_move(carrier, move):
                    # Check if this move is backwards (away from end zone)
                    move_y_diff = move[1] - current_y
                    
                    # Determine if the move is backwards based on team direction
                    is_backwards = (forward_direction == -1 and move_y_diff > 0) or \
                                  (forward_direction == 1 and move_y_diff < 0)
                    
                    # Only include moves that are not backwards and not previously visited
                    if not is_backwards and move not in previously_visited:
                        valid_moves.append(move)
                    
        # If we have valid moves, try to execute the best one
        if valid_moves:
            for move in valid_moves:
                # Try to move the carrier
                if self.movement_system.move_goblin(carrier, move):
                    DEBUG.log(f"Carrier {carrier.name} moved to {move}")
                    return True
            
        # If no valid moves with the new restrictions, allow lateral moves but still block backwards
        # This prevents carrier from getting completely stuck
        lateral_moves = []
        for move, priority in all_paths:
            distance = manhattan_distance(carrier.position, move)
            if distance <= carrier.movement and self.is_valid_move(carrier, move):
                # Check if move is backwards
                move_y_diff = move[1] - current_y
                is_backwards = (forward_direction == -1 and move_y_diff > 0) or \
                              (forward_direction == 1 and move_y_diff < 0)
                
                # Allow lateral (not backwards) moves even if previously visited
                if not is_backwards:
                    lateral_moves.append(move)
                
        # Try the lateral moves
        for move in lateral_moves:
            if self.movement_system.move_goblin(carrier, move):
                DEBUG.log(f"Carrier {carrier.name} moved to lateral position {move}")
                return True
                
        # If we get here, no valid moves found or all moves failed
        DEBUG.log(f"Carrier {carrier.name} couldn't find valid move")
        return False
        
    def get_direct_path(self, carrier, target_pos):
        """Get a direct path from carrier to target
        
        Args:
            carrier: The carrier goblin
            target_pos: The target position (x, y) tuple
            
        Returns:
            list: List of positions to move to for a direct path
        """
        positions = []
        current_x, current_y = carrier.position
        target_x, target_y = target_pos
        
        # Calculate direction vector
        dx = 1 if target_x > current_x else -1 if target_x < current_x else 0
        dy = 1 if target_y > current_y else -1 if target_y < current_y else 0
        
        # Generate positions in a direct line
        for i in range(1, carrier.movement + 1):
            # Don't go beyond the target
            if (dx > 0 and current_x + i * dx > target_x) or \
               (dx < 0 and current_x + i * dx < target_x):
                new_x = target_x
            else:
                new_x = current_x + i * dx
                
            if (dy > 0 and current_y + i * dy > target_y) or \
               (dy < 0 and current_y + i * dy < target_y):
                new_y = target_y
            else:
                new_y = current_y + i * dy
                
            # Check if we've reached a boundary
            if 0 <= new_x < self.game.grid.width and 0 <= new_y < self.game.grid.height:
                positions.append((new_x, new_y))
                
            # Stop if we've reached the target
            if new_x == target_x and new_y == target_y:
                break
                
        return positions
        
    def get_flanking_paths(self, carrier, target_y):
        """Get paths that flank around obstacles
        
        Args:
            carrier: The carrier goblin
            target_y: The target y-coordinate
            
        Returns:
            list: List of positions for flanking paths
        """
        positions = []
        current_x, current_y = carrier.position
        
        # Determine if we want to move up or down
        move_up = target_y < current_y
        
        # Generate potential flanking positions
        for i in range(1, carrier.movement + 1):
            # Left flank
            left_x = max(0, current_x - i)
            # Right flank
            right_x = min(self.game.grid.width - 1, current_x + i)
            
            # Vertical movement (toward target)
            if move_up:
                vert_y = max(0, current_y - i)  # Move up
            else:
                vert_y = min(self.game.grid.height - 1, current_y + i)  # Move down
                
            # Add flanking positions
            positions.append((left_x, current_y))   # Left
            positions.append((right_x, current_y))  # Right
            positions.append((current_x, vert_y))   # Vertical
            
            # Add diagonal positions
            positions.append((left_x, vert_y))   # Left + Vertical
            positions.append((right_x, vert_y))  # Right + Vertical
            
        return positions
        
    def get_safe_paths(self, carrier):
        """Get paths that avoid enemies
        
        Args:
            carrier: The carrier goblin
            
        Returns:
            list: List of positions for safe movement
        """
        positions = []
        current_x, current_y = carrier.position
        
        # Get positions of all enemy goblins
        enemy_positions = []
        for x in range(self.game.grid.width):
            for y in range(self.game.grid.height):
                entity = self.game.grid.get_entity_at_position((x, y))
                if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                    enemy_positions.append((x, y))
                    
        # Generate all possible moves within range
        for i in range(1, carrier.movement + 1):
            for dx in range(-i, i + 1):
                for dy in range(-i, i + 1):
                    if abs(dx) + abs(dy) <= i:  # Manhattan distance check
                        new_x = current_x + dx
                        new_y = current_y + dy
                        
                        # Check if position is on the grid
                        if 0 <= new_x < self.game.grid.width and 0 <= new_y < self.game.grid.height:
                            # Check if position is safe (no enemies adjacent)
                            is_safe = True
                            for enemy_x, enemy_y in enemy_positions:
                                if manhattan_distance((new_x, new_y), (enemy_x, enemy_y)) <= 1:
                                    is_safe = False
                                    break
                                    
                            if is_safe:
                                positions.append((new_x, new_y))
                                
        return positions
        
    def is_valid_move(self, goblin, position):
        """Check if a move is valid (empty space, on grid)
        
        Args:
            goblin: The goblin to move
            position: The target position (x, y) tuple
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        x, y = position
        
        # Check if position is on the grid
        if not (0 <= x < self.game.grid.width and 0 <= y < self.game.grid.height):
            return False
            
        # Check if position is empty
        if self.game.grid.get_entity_at_position(position) is not None:
            return False
            
        return True 

    def in_field_goal_range(self, carrier):
        """Check if a carrier is in field goal range
        
        Args:
            carrier: The carrier goblin
            
        Returns:
            bool: True if in field goal range, False otherwise
        """
        # Field goal is shot at the hoop in the middle of end zone
        if carrier.team == self.game.team1:
            hoop_y = 0  # Top
        else:
            hoop_y = self.game.grid.height - 1  # Bottom
            
        hoop_x = self.game.grid.width // 2  # Center
        hoop_pos = (hoop_x, hoop_y)
        
        # Check distance to hoop
        distance = manhattan_distance(carrier.position, hoop_pos)
        return distance <= self.game.config.get("field_goal_range", 3)
        
    def attempt_field_goal(self, carrier):
        """Attempt a field goal from the current position
        
        Args:
            carrier: The carrier goblin attempting the field goal
            
        Returns:
            bool: True if the field goal was successful, False otherwise
        """
        if not carrier or not carrier.has_ball:
            return False
            
        # Calculate base success chance
        # Further from hoop = harder
        if carrier.team == self.game.team1:
            hoop_y = 0
        else:
            hoop_y = self.game.grid.height - 1
            
        hoop_x = self.game.grid.width // 2
        hoop_pos = (hoop_x, hoop_y)
        
        distance = manhattan_distance(carrier.position, hoop_pos)
        base_chance = 0.8 - (distance * 0.1)  # 0.8 when adjacent, decreasing with distance
        
        # Adjust for goblin's strength (treat as "kicking power")
        strength_bonus = carrier.strength * 0.02  # +0.02 per strength point
        
        # Final chance
        success_chance = min(0.9, max(0.2, base_chance + strength_bonus))
        
        # Roll for success
        roll = random.random()
        success = roll < success_chance
        
        # Log the attempt
        self.logger.info(f"Field goal attempt by {carrier.name} from distance {distance}")
        self.logger.info(f"Success chance: {success_chance:.2f}, Roll: {roll:.2f}, Result: {'SUCCESS' if success else 'FAIL'}")
        
        # If successful, score points
        if success:
            self.game.score_field_goal(carrier)
            return True
        else:
            # Failed attempt, ball is turned over
            carrier.has_ball = False
            
            # Log the event
            self.game.event_manager.create_and_dispatch("field_goal_miss", {
                "carrier_id": carrier.id,
                "carrier_name": carrier.name,
                "team_id": carrier.team.id,
                "team_name": carrier.team.name,
                "position": carrier.position,
                "distance": distance,
                "success_chance": success_chance,
                "roll": roll
            })
            
            # End the play
            self.game.end_play()
            return False 