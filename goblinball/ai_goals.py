import random
from utils import manhattan_distance
from logger import DEBUG

class AIGoalSystem:
    """Handles goal setting for goblins"""
    
    def __init__(self, game):
        self.game = game
        
    def set_goblin_goal(self, goblin):
        """Set a goal for this goblin based on current situation
        
        Args:
            goblin: The goblin to set a goal for
            
        Returns:
            str: The goal string
        """
        if goblin.has_ball:
            # Carrier goals
            target_y = 0 if goblin.team == self.game.team2 else self.game.grid.height - 1
            distance = abs(goblin.position[1] - target_y)
            
            # Check path to end zone for active defenders
            path_defender_count = self.count_defenders_in_path(goblin, target_y)
            
            # Count defenders that are still up nearby
            nearby_defender_count = self.count_nearby_opponents(goblin.position, goblin.team)
            
            # First check if very close to end zone, always prioritize scoring when close
            if distance <= 3:
                return "score_touchdown"
            # Next check if in field goal range but path to end zone is blocked
            elif self.in_field_goal_range(goblin) and path_defender_count >= 2:
                return "attempt_field_goal"
            # Next check for clear path to end zone - be more aggressive
            elif path_defender_count == 0:
                # Clear path to end zone, prioritize direct scoring run
                return "score_touchdown"
            # Only evade if multiple defenders are nearby and active
            elif nearby_defender_count >= 2:
                return "evade_defenders"
            # Default goal is to advance
            else:
                return "advance_downfield"
        
        elif goblin.team == self.game.offense_team:
            # Offensive blocker goals
            carrier = self.game.offense_team.get_carrier()
            if not carrier:
                return "general_advance"
                
            nearest_defender = self.find_closest_opponent_to(carrier)
            if nearest_defender and self.is_adjacent(goblin, nearest_defender):
                return "block_defender"
            elif self.is_near(goblin, carrier, 2):
                return "protect_carrier"
            else:
                return "advance_with_carrier"
        
        else:
            # Defensive blocker goals
            carrier = self.game.offense_team.get_carrier()
            if not carrier:
                return "general_defense"
                
            if self.is_adjacent(goblin, carrier):
                return "tackle_carrier"
            elif self.is_near(goblin, carrier, 3):
                return "pursue_carrier"
            else:
                target_y = 0 if self.game.offense_team == self.game.team2 else self.game.grid.height - 1
                if self.is_between(goblin, carrier, target_y):
                    return "maintain_position"
                else:
                    return "intercept_carrier"
    
    def in_field_goal_range(self, goblin):
        """Check if a goblin is in field goal range
        
        Args:
            goblin: The goblin to check
            
        Returns:
            bool: True if in field goal range, False otherwise
        """
        # Field goal is shot at the hoop in the middle of end zone
        if goblin.team == self.game.team1:
            hoop_y = 0  # Top
        else:
            hoop_y = self.game.grid.height - 1  # Bottom
            
        hoop_x = self.game.grid.width // 2  # Center
        hoop_pos = (hoop_x, hoop_y)
        
        # Check distance to hoop
        distance = manhattan_distance(goblin.position, hoop_pos)
        return distance <= self.game.config.get("field_goal_range", 3)
    
    def count_nearby_opponents(self, position, team):
        """Count enemy goblins near a position
        
        Args:
            position: The position to check around
            team: The friendly team
            
        Returns:
            int: Number of nearby enemies
        """
        count = 0
        x, y = position
        
        # Check a 3x3 area around the position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                check_pos = (x + dx, y + dy)
                if 0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height:
                    entity = self.game.grid.get_entity_at_position(check_pos)
                    if entity and hasattr(entity, 'team') and entity.team != team and not entity.knocked_down:
                        count += 1
                        
        return count
    
    def find_closest_opponent_to(self, goblin):
        """Find the closest enemy goblin to a goblin
        
        Args:
            goblin: The goblin to find enemies near
            
        Returns:
            Goblin or None: The closest enemy goblin, or None if none found
        """
        closest = None
        min_distance = float('inf')
        
        for x in range(self.game.grid.width):
            for y in range(self.game.grid.height):
                entity = self.game.grid.get_entity_at_position((x, y))
                if entity and hasattr(entity, 'team') and entity.team != goblin.team and not entity.knocked_down:
                    distance = manhattan_distance(goblin.position, (x, y))
                    if distance < min_distance:
                        min_distance = distance
                        closest = entity
                        
        return closest
    
    def is_adjacent(self, goblin1, goblin2):
        """Check if two goblins are adjacent
        
        Args:
            goblin1: First goblin
            goblin2: Second goblin
            
        Returns:
            bool: True if adjacent, False otherwise
        """
        return manhattan_distance(goblin1.position, goblin2.position) == 1
    
    def is_near(self, goblin1, goblin2, distance):
        """Check if two goblins are within a certain distance of each other
        
        Args:
            goblin1: First goblin
            goblin2: Second goblin
            distance: Maximum distance to check
            
        Returns:
            bool: True if within distance, False otherwise
        """
        return manhattan_distance(goblin1.position, goblin2.position) <= distance
    
    def is_between(self, goblin, target, end_y):
        """Check if a goblin is between a target and the end zone
        
        Args:
            goblin: The goblin to check
            target: The target goblin
            end_y: The y-coordinate of the end zone
            
        Returns:
            bool: True if the goblin is between target and end zone, False otherwise
        """
        # Check if the goblin is in roughly the same x-column as the target
        if abs(goblin.position[0] - target.position[0]) > 2:
            return False
            
        # Check if the goblin is between the target and the end zone in terms of y-coordinate
        if end_y < target.position[1]:  # End zone is above target
            return goblin.position[1] < target.position[1] and goblin.position[1] > end_y
        else:  # End zone is below target
            return goblin.position[1] > target.position[1] and goblin.position[1] < end_y
    
    def count_defenders_in_path(self, goblin, target_y):
        """Count defenders in the path between goblin and the end zone
        
        Args:
            goblin: The carrier goblin
            target_y: The y-coordinate of the target end zone
            
        Returns:
            int: Number of defenders in path
        """
        # Determine direction to end zone
        direction = -1 if target_y < goblin.position[1] else 1
        
        # Count opponents in a corridor between goblin and end zone
        count = 0
        current_x, current_y = goblin.position
        
        # Define the corridor width (wider = more conservative)
        corridor_width = 2  # Check 2 squares to each side of direct path
        
        # Scan squares in path to end zone
        for y in range(current_y + direction, target_y + direction, direction):
            if not (0 <= y < self.game.grid.height):
                break
                
            # Check squares in this row within corridor
            for x in range(current_x - corridor_width, current_x + corridor_width + 1):
                if not (0 <= x < self.game.grid.width):
                    continue
                    
                entity = self.game.grid.get_entity_at_position((x, y))
                if entity and hasattr(entity, 'team') and entity.team != goblin.team and not entity.knocked_down:
                    count += 1
        
        return count

class MovementStyleSelector:
    """Selects movement styles based on goals and situation"""
    
    def __init__(self, game):
        self.game = game
        
    def choose_movement_style(self, goblin, goal):
        """Choose a movement style based on goblin's goal and situation
        
        Args:
            goblin: The goblin to choose a style for
            goal: The goblin's current goal
            
        Returns:
            str: The movement style to use
        """
        # Base probabilities from config
        base_weights = self.game.config.get("movement_style_weights", {
            "direct": 0.3,
            "flanking": 0.2,
            "cautious": 0.2,
            "aggressive": 0.2,
            "deceptive": 0.1
        })
        
        # Copy weights
        weights = {k: v for k, v in base_weights.items()}
        
        # Adjust based on goal
        if goal == "score_touchdown":
            weights["direct"] += 0.3
            weights["aggressive"] += 0.2
            weights["cautious"] -= 0.2
        
        elif goal == "evade_defenders":
            weights["cautious"] += 0.3
            weights["deceptive"] += 0.2
            weights["direct"] -= 0.2
        
        elif goal == "block_defender" or goal == "tackle_carrier":
            weights["aggressive"] += 0.3
            weights["direct"] += 0.2
            weights["cautious"] -= 0.2
            
        elif goal == "protect_carrier":
            weights["cautious"] += 0.2
            weights["flanking"] += 0.1
            
        elif goal == "pursue_carrier":
            weights["direct"] += 0.2
            weights["aggressive"] += 0.1
            
        elif goal == "intercept_carrier":
            weights["flanking"] += 0.3
            weights["deceptive"] += 0.1
        
        # Special adjustments for carriers moving downfield
        if goal == "advance_downfield" and goblin.has_ball:
            # Count active defenders nearby
            active_defenders = 0
            for x in range(self.game.grid.width):
                for y in range(self.game.grid.height):
                    entity = self.game.grid.get_entity_at_position((x, y))
                    if entity and hasattr(entity, 'team') and entity.team != goblin.team and not entity.knocked_down:
                        # Only count defenders that are actually near enough to be a threat
                        if manhattan_distance(goblin.position, (x, y)) <= 4:
                            active_defenders += 1
            
            # If few defenders are active, be much more aggressive and direct
            if active_defenders == 0:
                weights["direct"] += 0.4
                weights["aggressive"] += 0.4
                weights["cautious"] -= 0.3
                weights["deceptive"] -= 0.1
            elif active_defenders <= 1:
                weights["direct"] += 0.3
                weights["aggressive"] += 0.3
                weights["cautious"] -= 0.2
            elif active_defenders <= 3:
                weights["direct"] += 0.1
                weights["aggressive"] += 0.1
                weights["cautious"] -= 0.1
        
        # Add randomness, but less than before to ensure more consistent behavior
        for style in weights:
            weights[style] += random.uniform(-0.05, 0.05)
            weights[style] = max(0.05, min(0.9, weights[style]))
        
        # Choose style based on weights
        styles = list(weights.keys())
        chances = [weights[s] for s in styles]
        
        return random.choices(styles, weights=chances)[0] 