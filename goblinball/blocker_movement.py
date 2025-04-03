import random
import logging
from utils import manhattan_distance, is_adjacent
from logger import DEBUG

class BlockerMovement:
    """Handles movement logic for blockers (both offensive and defensive)"""
    
    def __init__(self, game, movement_system):
        self.game = game
        self.movement_system = movement_system
        self.logger = logging.getLogger("goblinball.blocker")
        
        # Formation offsets for positioning blockers around the carrier
        self.formation_offsets = [
            (-1, -1), (0, -1), (1, -1),  # Row in front
            (-1, 0),           (1, 0),   # Sides
            (-1, 1),  (0, 1),  (1, 1)    # Row behind
        ]
        
    def move_blocker(self, blocker):
        """Move a blocker according to its team role
        
        Args:
            blocker: The blocker goblin to move
            
        Returns:
            bool: True if the blocker moved successfully, False otherwise
        """
        # Check if the blocker can move
        if blocker.movement <= 0 or blocker.knocked_down or blocker.unavailable:
            return False
            
        # Check if blocker is on offense or defense
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
        if blocker.movement >= self.game.config.get("blocking_cost", 2):
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
        """Move a defensive blocker to tackle the carrier or disrupt the offense
        
        Args:
            blocker: The blocker goblin to move
            
        Returns:
            bool: True if the blocker moved successfully, False otherwise
        """
        # If no movement points left, can't move
        if blocker.movement <= 0 or blocker.knocked_down or blocker.unavailable:
            return False
            
        DEBUG.log(f"Moving defensive blocker {blocker.name} with {blocker.movement} movement points")
        
        # Get carrier
        carrier = self.game.offense_team.get_carrier()
        if not carrier:
            DEBUG.log(f"No carrier found for team {self.game.offense_team.name}!")
            return False
            
        # Get blocker and carrier positions
        blocker_x, blocker_y = blocker.position
        carrier_x, carrier_y = carrier.position
        
        # 1. If adjacent to carrier, try to block
        if self.is_adjacent(blocker, carrier) and blocker.movement >= self.game.config.get("blocking_cost", 2):
            DEBUG.log(f"Defensive blocker {blocker.name} attempting to block carrier {carrier.name}")
            if self.movement_system.attempt_block(blocker, carrier):
                DEBUG.log(f"Block succeeded!")
                return True
                
        # 2. If not adjacent to carrier but close enough, move toward carrier
        distance_to_carrier = manhattan_distance(blocker.position, carrier.position)
        
        if distance_to_carrier <= 3:
            DEBUG.log(f"Defensive blocker {blocker.name} pursuing carrier {carrier.name}")
            
            # Get possible moves
            possible_moves = self.movement_system.get_possible_moves(blocker)
            
            # Find the best move toward carrier
            best_move = None
            best_distance = float('inf')
            
            for move in possible_moves:
                distance = manhattan_distance(move, carrier.position)
                if distance < best_distance:
                    best_distance = distance
                    best_move = move
                    
            if best_move:
                return self.movement_system.move_goblin(blocker, best_move)
                
        # 3. If far from carrier, try to intercept
        # Calculate where carrier is likely heading (based on team, moving toward end zone)
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        
        # Get possible moves
        possible_moves = self.movement_system.get_possible_moves(blocker)
        
        # Score each move
        move_scores = {}
        
        for move in possible_moves:
            move_x, move_y = move
            
            # Initialize score
            score = 0
            
            # Factor 1: Intercept path - position between carrier and their goal
            # If carrier is team1 (moving up), blocker wants to be above carrier
            # If carrier is team2 (moving down), blocker wants to be below carrier
            is_intercepting = False
            
            if carrier.team == self.game.team1:
                # Carrier moving up, blocker should be above (lower y)
                if move_y < carrier_y:
                    is_intercepting = True
                    # Bonus for being in the same column or adjacent
                    if abs(move_x - carrier_x) <= 1:
                        score += 300
            else:
                # Carrier moving down, blocker should be below (higher y)
                if move_y > carrier_y:
                    is_intercepting = True
                    # Bonus for being in the same column or adjacent
                    if abs(move_x - carrier_x) <= 1:
                        score += 300
                        
            if is_intercepting:
                score += 200
                
            # Factor 2: Distance to carrier - closer is better, but not if we're already intercepting
            if not is_intercepting:
                dist_to_carrier = manhattan_distance(move, carrier.position)
                proximity_score = 10 - min(10, dist_to_carrier)  # Higher for closer positions
                score += proximity_score * 100
                
            # Factor 3: Position relative to end zone
            # Defense should focus on positions between carrier and end zone
            dist_to_target = abs(move_y - target_y)
            dist_carrier_to_target = abs(carrier_y - target_y)
            
            if dist_to_target < dist_carrier_to_target:
                # Position is between carrier and their goal
                score += 150
                
            # Add some randomness
            score += random.randint(-25, 25)
            
            # Store the score
            move_scores[move] = score
            
        # Choose the best move
        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            DEBUG.log(f"Defensive blocker chose move {best_move} with score {move_scores[best_move]}")
            return self.movement_system.move_goblin(blocker, best_move)
            
        return False
        
    def is_adjacent(self, goblin1, goblin2):
        """Check if two goblins are adjacent"""
        return is_adjacent(goblin1.position, goblin2.position) 