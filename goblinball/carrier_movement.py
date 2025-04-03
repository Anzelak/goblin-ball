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
        
        # Check if there's a clear path to the end zone
        has_clear_path = True
        path_to_end = []
        
        # Determine the direct path to end zone target
        end_zone_target = (target_x, target_y)
        
        # Calculate the direct path
        direction_x = 1 if target_x > current_x else -1 if target_x < current_x else 0
        direction_y = forward_direction  # Already calculated based on team
        
        # Simple path calculation - move diagonally as far as possible, then straight
        # Calculate the number of diagonal moves (min of x and y distance)
        x_distance = abs(target_x - current_x)
        y_distance = abs(target_y - current_y)
        diagonal_moves = min(x_distance, y_distance)
        
        # Add diagonal moves
        x, y = current_x, current_y
        for i in range(diagonal_moves):
            x += direction_x
            y += direction_y
            path_to_end.append((x, y))
        
        # Add remaining horizontal moves
        for i in range(diagonal_moves, x_distance):
            x += direction_x
            path_to_end.append((x, y))
            
        # Add remaining vertical moves
        x = target_x  # Reset to where the horizontal moves ended
        y = current_y + diagonal_moves * direction_y  # Reset to where the diagonal moves ended
        for i in range(diagonal_moves, y_distance):
            y += direction_y
            path_to_end.append((x, y))
        
        # Check if each square in path is empty or has a knocked down opponent
        for pos in path_to_end:
            entity = self.game.grid.get_entity_at_position(pos)
            if entity and (not hasattr(entity, 'team') or entity.team == carrier.team or not entity.knocked_down):
                has_clear_path = False
                break
        
        # If there's a clear path to end zone, prioritize direct movement
        if has_clear_path and carrier.movement > 0:
            # Find the farthest point on the path we can reach with our movement
            reachable_path = [pos for pos in path_to_end if manhattan_distance(carrier.position, pos) <= carrier.movement]
            
            if reachable_path:
                # Move to the farthest reachable point on the path
                target_pos = reachable_path[-1]
                
                # NEW: Safety check - ensure we're not moving directly into danger
                # Count defenders near the target position
                defenders_near_target = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        check_pos = (target_pos[0] + dx, target_pos[1] + dy)
                        if 0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height:
                            entity = self.game.grid.get_entity_at_position(check_pos)
                            if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                                defenders_near_target += 1
                
                # Only take clear path if there are no nearby defenders threatening the target position
                if defenders_near_target == 0:
                    # Try to move directly to this position
                    if self.movement_system.move_goblin(carrier, target_pos):
                        DEBUG.log(f"Carrier {carrier.name} moved along clear path to {target_pos}")
                        return True

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
                        valid_moves.append((move, priority))
        
        # NEW: Evaluate safety of each valid move
        if valid_moves:
            move_scores = []
            for move, priority in valid_moves:
                # Base score is the priority (3, 2, or 1)
                base_score = priority * 10.0
                
                # Add safety score based on blocker screening
                safety_score = self.evaluate_move_safety(carrier, move)
                
                # Combined score
                total_score = base_score + safety_score
                
                # Progress toward end zone (higher score for moves closer to end zone)
                progress_score = 10.0 - abs(move[1] - target_y) / self.game.grid.height * 10.0
                total_score += progress_score
                
                # Calculate distance from current position (closer moves are slightly preferred)
                distance = manhattan_distance(carrier.position, move)
                distance_score = (carrier.movement - distance) * 0.2  # Small bonus for shorter moves
                total_score += distance_score
                
                move_scores.append((move, total_score))
            
            # Sort by score (highest first)
            move_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Try moves in order of score
            for move, score in move_scores:
                # Extra safety check - don't move directly adjacent to a defender
                adjacent_defender = False
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        check_pos = (move[0] + dx, move[1] + dy)
                        if 0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height:
                            entity = self.game.grid.get_entity_at_position(check_pos)
                            if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                                adjacent_defender = True
                                break
                
                # Skip moves that put carrier directly next to a defender unless well screened
                # (high safety score indicates good screening)
                if adjacent_defender and score < 15.0:  # Threshold for required safety
                    continue
                
                # Try to move to this position
                if self.movement_system.move_goblin(carrier, move):
                    DEBUG.log(f"Carrier {carrier.name} moved to {move} (score: {score:.1f})")
                    return True
        
        # If we get here, try lateral moves as a fallback
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
                    # Evaluate safety of lateral move
                    safety_score = self.evaluate_move_safety(carrier, move)
                    lateral_moves.append((move, safety_score))
        
        # Sort lateral moves by safety score
        lateral_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Try lateral moves in order of safety
        for move, score in lateral_moves:
            # Extra safety check - don't move directly adjacent to a defender
            adjacent_defender = False
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    check_pos = (move[0] + dx, move[1] + dy)
                    if 0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height:
                        entity = self.game.grid.get_entity_at_position(check_pos)
                        if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                            adjacent_defender = True
                            break
            
            # Skip moves that put carrier directly next to a defender unless well screened
            if adjacent_defender and score < 2.0:  # Lower threshold for lateral moves
                continue
                
            if self.movement_system.move_goblin(carrier, move):
                DEBUG.log(f"Carrier {carrier.name} moved to lateral position {move} (safety: {score:.1f})")
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
        
        # Check how many defenders are active on the field - if few or none, be more aggressive
        active_defenders = 0
        for x in range(self.game.grid.width):
            for y in range(self.game.grid.height):
                entity = self.game.grid.get_entity_at_position((x, y))
                if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                    active_defenders += 1
                    
        # Generate more direct paths if few defenders are active
        if active_defenders <= 1:
            # Generate positions more directly to the target
            # Use diagonal movement (moving x and y simultaneously)
            steps = max(abs(target_x - current_x), abs(target_y - current_y))
            for i in range(1, min(carrier.movement + 1, steps + 1)):
                # Calculate position along the line between carrier and target
                progress = i / steps
                new_x = int(current_x + progress * (target_x - current_x))
                new_y = int(current_y + progress * (target_y - current_y))
                
                # Check if we've reached a boundary
                if 0 <= new_x < self.game.grid.width and 0 <= new_y < self.game.grid.height:
                    positions.append((new_x, new_y))
                    
                # Stop if we've reached the target
                if new_x == target_x and new_y == target_y:
                    break
        else:
            # Original implementation for when defenders are active
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
        
        # Prioritize positions closer to the end zone by sorting
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        positions.sort(key=lambda pos: abs(pos[1] - target_y))
                
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

    def evaluate_move_safety(self, carrier, move_pos):
        """Evaluate how safe a potential move is based on blocker positions
        
        Args:
            carrier: The carrier goblin
            move_pos: The potential move position (x, y)
            
        Returns:
            float: Safety score (higher is safer)
        """
        safety_score = 0.0
        
        # Get all defenders and friendly blockers
        defenders = []
        blockers = []
        
        for x in range(self.game.grid.width):
            for y in range(self.game.grid.height):
                entity = self.game.grid.get_entity_at_position((x, y))
                if entity and hasattr(entity, 'team') and not entity.knocked_down:
                    if entity.team != carrier.team:
                        defenders.append(entity)
                    elif entity != carrier:  # Friendly blocker, not the carrier
                        blockers.append(entity)
        
        # For each defender, check if they're screened by a friendly blocker
        for defender in defenders:
            # Calculate distance between defender and potential move
            def_distance = manhattan_distance(defender.position, move_pos)
            
            # Only consider defenders that are relatively close
            if def_distance <= 3:
                # Defender is close, check if screened by a blocker
                is_screened = False
                
                for blocker in blockers:
                    # A blocker effectively screens if it's between the carrier and defender
                    # Calculate if the blocker is roughly on the line between move and defender
                    
                    # Get direction from move to defender
                    dx = defender.position[0] - move_pos[0]
                    dy = defender.position[1] - move_pos[1]
                    
                    # Calculate "expected" blocker position (1 step from move towards defender)
                    if dx != 0:
                        expected_x = move_pos[0] + (1 if dx > 0 else -1)
                    else:
                        expected_x = move_pos[0]
                        
                    if dy != 0:
                        expected_y = move_pos[1] + (1 if dy > 0 else -1)
                    else:
                        expected_y = move_pos[1]
                    
                    # If a blocker is at or adjacent to the expected screening position
                    blocker_x, blocker_y = blocker.position
                    blocker_screens = (abs(blocker_x - expected_x) <= 1 and 
                                       abs(blocker_y - expected_y) <= 1)
                                      
                    if blocker_screens:
                        is_screened = True
                        break
                
                # Add to safety score based on screening
                if is_screened:
                    safety_score += 2.0  # Big bonus for being screened
                else:
                    safety_score -= 1.0  # Penalty for being exposed to defender
            
        return safety_score 