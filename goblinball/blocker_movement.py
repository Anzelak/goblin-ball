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
        
        # Get possible moves
        possible_moves = self.movement_system.get_possible_moves(blocker)
        
        # Get direction to end zone
        target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
        forward_dir = -1 if carrier.team == self.game.team1 else 1
        
        # Score each possible move
        move_scores = {}
        
        for move in possible_moves:
            move_x, move_y = move
            
            # Initialize score
            score = 0
            
            # HIGHEST PRIORITY: Getting adjacent to a threatening enemy to block them
            for enemy, dist in enemies_near_carrier:
                enemy_x, enemy_y = enemy.position
                
                # Check if this move would put us adjacent to a threatening enemy
                would_be_adjacent_to_enemy = manhattan_distance(move, enemy.position) == 1
                
                if would_be_adjacent_to_enemy:
                    # Higher score for enemies closer to carrier (more threatening)
                    threat_score = 10 - min(10, dist) 
                    score += 1500 + (threat_score * 50)
                    
                    # If blocker has enough movement to block after moving, even better
                    if blocker.movement - manhattan_distance(blocker.position, move) >= self.game.config.get("blocking_cost", 2):
                        score += 500
            
            # SECOND PRIORITY: Blocking path between carrier and enemies
            for enemy, dist in enemies_near_carrier:
                enemy_x, enemy_y = enemy.position
                
                # Calculate vector from carrier to enemy
                dx = enemy_x - carrier_x
                dy = enemy_y - carrier_y
                
                # Check if this move would put us between carrier and enemy
                is_between = False
                
                # Simple check: if we're on a line between carrier and enemy
                # For simplicity, we'll check if move is on a grid line between them
                if (min(carrier_x, enemy_x) <= move_x <= max(carrier_x, enemy_x) and
                    min(carrier_y, enemy_y) <= move_y <= max(carrier_y, enemy_y)):
                    
                    # Calculate position on the line from carrier to enemy
                    on_line = False
                    
                    # Horizontal line
                    if carrier_y == enemy_y and move_y == carrier_y:
                        on_line = True
                    # Vertical line
                    elif carrier_x == enemy_x and move_x == carrier_x:
                        on_line = True
                    # Diagonal line
                    elif abs(carrier_x - enemy_x) == abs(carrier_y - enemy_y):
                        # Check if on the same diagonal
                        dx1 = move_x - carrier_x
                        dy1 = move_y - carrier_y
                        if abs(dx1) == abs(dy1) and dx1 * dx >= 0 and dy1 * dy >= 0:
                            on_line = True
                    
                    if on_line:
                        is_between = True
                
                if is_between:
                    # Score is higher for more threatening enemies (closer to carrier)
                    score += 1000 - (dist * 100)
            
            # THIRD PRIORITY: Stay close to carrier
            dist_to_carrier = manhattan_distance(move, carrier.position)
            carrier_proximity = 10 - min(10, dist_to_carrier)  # Higher for closer positions
            score += carrier_proximity * 80
            
            # FOURTH PRIORITY: Forward position (relative to direction of carrier movement)
            # Less important now compared to blocking and protection
            if forward_dir == -1:  # Moving upward
                forward_score = 10 - min(10, move_y)  # Higher for smaller y (closer to top)
            else:  # Moving downward
                forward_score = min(10, move_y)  # Higher for larger y (closer to bottom)
                
            score += forward_score * 5
            
            # Slight penalty for moving backward
            current_dist_to_goal = abs(blocker_y - target_y)
            new_dist_to_goal = abs(move_y - target_y)
            
            if new_dist_to_goal > current_dist_to_goal:
                score -= 25
                
            # Add some randomness
            score += random.randint(-20, 20)
            
            # Store the score
            move_scores[move] = score
            
        # Choose the best move
        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            DEBUG.log(f"Offensive blocker chose move {best_move} with score {move_scores[best_move]}")
            
            # If this move puts us adjacent to an enemy, try to block after moving
            move_successful = self.movement_system.move_goblin(blocker, best_move)
            
            if move_successful:
                # Check if we can block an enemy after moving
                if blocker.movement >= self.game.config.get("blocking_cost", 2):
                    for enemy, _ in enemies_near_carrier:
                        if self.is_adjacent(blocker, enemy):
                            DEBUG.log(f"Offensive blocker {blocker.name} attempting to block {enemy.name} after moving")
                            self.movement_system.attempt_block(blocker, enemy)
                            return True
                return True
            
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
        
        # 1. If adjacent to carrier, ALWAYS try to block
        if self.is_adjacent(blocker, carrier) and blocker.movement >= self.game.config.get("blocking_cost", 2):
            DEBUG.log(f"Defensive blocker {blocker.name} attempting to block carrier {carrier.name}")
            if self.movement_system.attempt_block(blocker, carrier):
                DEBUG.log(f"Block succeeded!")
                return True
                
        # 2. If not adjacent to carrier but close enough, prioritize getting adjacent over intercepting
        distance_to_carrier = manhattan_distance(blocker.position, carrier.position)
        
        # Get possible moves
        possible_moves = self.movement_system.get_possible_moves(blocker)
        
        # Score each move with a high emphasis on getting adjacent to carrier
        move_scores = {}
        
        for move in possible_moves:
            move_x, move_y = move
            
            # Initialize score
            score = 0
            
            # Check if this move would put us adjacent to the carrier
            would_be_adjacent = manhattan_distance(move, carrier.position) == 1
            
            # HIGHEST PRIORITY: Get adjacent to carrier for blocking
            if would_be_adjacent:
                # Much higher score for positions that enable blocking
                score += 2000
                
                # If blocker has enough movement to block after moving, even better
                if blocker.movement - manhattan_distance(blocker.position, move) >= self.game.config.get("blocking_cost", 2):
                    score += 1000
            
            # SECOND PRIORITY: Get as close as possible to carrier
            distance = manhattan_distance(move, carrier.position)
            proximity_score = 20 - min(20, distance)  # Higher for closer positions
            score += proximity_score * 50
                
            # THIRD PRIORITY: Intercept path to end zone
            target_y = 0 if carrier.team == self.game.team1 else self.game.grid.height - 1
            
            # Check if position is between carrier and their goal
            is_intercepting = False
            if carrier.team == self.game.team1:
                # Carrier moving up, blocker should be above (lower y)
                if move_y < carrier_y:
                    is_intercepting = True
                    # Bonus for being in the same column or adjacent
                    if abs(move_x - carrier_x) <= 1:
                        score += 200
            else:
                # Carrier moving down, blocker should be below (higher y)
                if move_y > carrier_y:
                    is_intercepting = True
                    # Bonus for being in the same column or adjacent
                    if abs(move_x - carrier_x) <= 1:
                        score += 200
                        
            if is_intercepting:
                score += 150
                
            # Position relative to end zone
            dist_to_target = abs(move_y - target_y)
            dist_carrier_to_target = abs(carrier_y - target_y)
            
            if dist_to_target < dist_carrier_to_target:
                # Position is between carrier and their goal
                score += 100
                
            # Add some randomness
            score += random.randint(-25, 25)
            
            # Store the score
            move_scores[move] = score
            
        # Choose the best move
        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            DEBUG.log(f"Defensive blocker chose move {best_move} with score {move_scores[best_move]}")
            
            # If this move puts us adjacent to carrier, try to block after moving
            if manhattan_distance(best_move, carrier.position) == 1:
                # First move to the position
                if self.movement_system.move_goblin(blocker, best_move):
                    # Then check if we can still block
                    if blocker.movement >= self.game.config.get("blocking_cost", 2) and self.is_adjacent(blocker, carrier):
                        DEBUG.log(f"Defensive blocker {blocker.name} attempting to block carrier {carrier.name} after moving")
                        self.movement_system.attempt_block(blocker, carrier)
                        return True
                    return True
            else:
                # Just move normally
                return self.movement_system.move_goblin(blocker, best_move)
            
        return False
        
    def is_adjacent(self, goblin1, goblin2):
        """Check if two goblins are adjacent"""
        return is_adjacent(goblin1.position, goblin2.position) 