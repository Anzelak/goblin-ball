import math
import random

def distance(pos1, pos2):
    """Calculate the distance between two positions (x1, y1) and (x2, y2)"""
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
def manhattan_distance(pos1, pos2):
    """Calculate the Manhattan distance between two positions (x1, y1) and (x2, y2)"""
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x2 - x1) + abs(y2 - y1)
    
def is_adjacent(pos1, pos2):
    """Check if two positions are adjacent (including diagonally)"""
    x1, y1 = pos1
    x2, y2 = pos2
    return max(abs(x2 - x1), abs(y2 - y1)) == 1
    
def get_adjacent_positions(pos, grid_size):
    """Get all valid adjacent positions to the given position"""
    x, y = pos
    adjacent = []
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue  # Skip the center position
                
            nx, ny = x + dx, y + dy
            
            # Check grid bounds
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                adjacent.append((nx, ny))
                
    return adjacent
    
def get_direction_to(from_pos, to_pos):
    """Get the direction (dx, dy) from from_pos to to_pos"""
    x1, y1 = from_pos
    x2, y2 = to_pos
    
    dx = 0 if x1 == x2 else (1 if x2 > x1 else -1)
    dy = 0 if y1 == y2 else (1 if y2 > y1 else -1)
    
    return dx, dy
    
def get_line_positions(start, end):
    """Get all positions in a line from start to end using Bresenham's algorithm"""
    x1, y1 = start
    x2, y2 = end
    
    positions = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        positions.append((x1, y1))
        
        if x1 == x2 and y1 == y2:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
            
    return positions
    
def get_positions_in_range(center, max_distance, grid_size):
    """Get all positions within max_distance of center"""
    x, y = center
    positions = []
    
    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):
            nx, ny = x + dx, y + dy
            
            # Check grid bounds
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                # Check distance
                if manhattan_distance(center, (nx, ny)) <= max_distance:
                    positions.append((nx, ny))
                    
    return positions
    
def weighted_choice(choices):
    """Make a weighted random choice from a list of (item, weight) tuples"""
    total = sum(weight for _, weight in choices)
    r = random.random() * total
    
    running_total = 0
    for item, weight in choices:
        running_total += weight
        if running_total > r:
            return item
            
    return choices[-1][0]  # Fallback in case of rounding errors 