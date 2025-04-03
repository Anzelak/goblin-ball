import logging

logger = logging.getLogger("goblinball.grid")

class Grid:
    """
    Represents the game grid for GoblinBall.
    Manages entities on the grid and their positions.
    """
    
    def __init__(self, width, height):
        """Initialize a new grid of the specified size"""
        self.width = width
        self.height = height
        self.cells = [[None for _ in range(width)] for _ in range(height)]
        
    def clear(self):
        """Clear all entities from the grid"""
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
        
    def is_valid_position(self, position):
        """Check if a position is within the grid bounds"""
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
        
    def get_entity_at_position(self, position):
        """Get the entity at the specified position
        
        Args:
            position: Tuple (x, y) of the position to check
            
        Returns:
            The entity at the position, or None if empty
        """
        if not self.is_valid_position(position):
            return None
            
        x, y = position
        return self.cells[y][x]
        
    def place_entity(self, entity, position):
        """Place an entity at the specified position
        
        Args:
            entity: The entity to place
            position: Tuple (x, y) of the position to place at
            
        Returns:
            bool: True if the entity was placed, False otherwise
        """
        if not self.is_valid_position(position):
            logger.error(f"Invalid position {position}")
            return False
            
        x, y = position
        if self.cells[y][x] is not None:
            logger.error(f"Position {position} is already occupied")
            return False
            
        self.cells[y][x] = entity
        return True
        
    def move_entity(self, entity, new_position):
        """Move an entity from its current position to a new position
        
        Args:
            entity: The entity to move
            new_position: Tuple (x, y) of the new position
            
        Returns:
            bool: True if the entity was moved, False otherwise
        """
        if not self.is_valid_position(new_position):
            logger.error(f"Invalid position {new_position}")
            return False
            
        # Find the entity's current position
        current_position = None
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] == entity:
                    current_position = (x, y)
                    break
            if current_position:
                break
                
        if not current_position:
            logger.error(f"Entity {entity} not found on grid")
            return False
            
        # Check if the new position is empty
        nx, ny = new_position
        if self.cells[ny][nx] is not None:
            logger.error(f"New position {new_position} is already occupied")
            return False
            
        # Move the entity
        cx, cy = current_position
        self.cells[cy][cx] = None
        self.cells[ny][nx] = entity
        return True
        
    def remove_entity(self, entity):
        """Remove an entity from the grid
        
        Args:
            entity: The entity to remove
            
        Returns:
            bool: True if the entity was removed, False otherwise
        """
        # Find the entity on the grid
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] == entity:
                    self.cells[y][x] = None
                    return True
                    
        logger.error(f"Entity {entity} not found on grid")
        return False
        
    def get_empty_positions(self):
        """Get all empty positions on the grid
        
        Returns:
            list: List of (x, y) tuples representing empty positions
        """
        empty_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] is None:
                    empty_positions.append((x, y))
                    
        return empty_positions
        
    def get_adjacent_positions(self, position):
        """Get all adjacent positions to the specified position
        
        Args:
            position: Tuple (x, y) of the position
            
        Returns:
            list: List of (x, y) tuples representing adjacent positions
        """
        x, y = position
        adjacent_positions = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the center position
                    
                adj_pos = (x + dx, y + dy)
                if self.is_valid_position(adj_pos):
                    adjacent_positions.append(adj_pos)
                    
        return adjacent_positions
        
    def get_entities_by_type(self, entity_type):
        """Get all entities of a specific type
        
        Args:
            entity_type: The type of entity to find
            
        Returns:
            list: List of entities of the specified type
        """
        entities = []
        for y in range(self.height):
            for x in range(self.width):
                entity = self.cells[y][x]
                if entity and isinstance(entity, entity_type):
                    entities.append(entity)
                    
        return entities
        
    def __str__(self):
        """String representation of the grid for debugging"""
        result = ""
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                entity = self.cells[y][x]
                if entity:
                    row += "X"
                else:
                    row += "."
            result += row + "\n"
        return result 