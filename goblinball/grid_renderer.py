import pygame

class GridRenderer:
    """Renders the game grid with end zones and hoops"""
    
    def __init__(self, game, cell_size):
        self.game = game
        self.cell_size = cell_size
        self.colors = {
            "background": (20, 100, 20),  # Field green
            "grid": (255, 255, 255, 50),  # Semi-transparent white
            "endzone1": (200, 200, 200, 100),  # Semi-transparent light gray
            "endzone2": (150, 150, 150, 100),  # Semi-transparent gray
            "hoop": (150, 75, 0),  # Brown
            "text": (255, 255, 255),  # White
        }
        
        # Fonts
        self.fonts = {
            "small": pygame.font.SysFont(None, 14),
            "medium": pygame.font.SysFont(None, 20),
        }
        
    def draw(self, screen, offset_x, offset_y):
        """Draw the game grid with end zones
        
        Args:
            screen: The pygame screen to draw on
            offset_x: The x offset for drawing
            offset_y: The y offset for drawing
            
        Returns:
            pygame.Surface: The grid surface that was drawn
        """
        grid_size = self.game.grid_size
        cell_size = self.cell_size
        
        # Create surface for grid
        grid_surface = pygame.Surface((grid_size * cell_size, grid_size * cell_size), pygame.SRCALPHA)
        
        # Draw end zones
        pygame.draw.rect(grid_surface, self.colors["endzone1"], (0, 0, grid_size * cell_size, cell_size))
        pygame.draw.rect(grid_surface, self.colors["endzone2"], (0, (grid_size - 1) * cell_size, grid_size * cell_size, cell_size))
        
        # Draw row numbers
        for y in range(grid_size):
            # Draw row number on left side
            row_text = self.fonts["medium"].render(f"{y+1}", True, self.colors["text"])
            grid_surface.blit(row_text, (5, y * cell_size + cell_size // 3))
        
        # Draw grid lines
        for x in range(grid_size + 1):
            # Vertical lines
            pygame.draw.line(
                grid_surface, 
                self.colors["grid"], 
                (x * cell_size, 0), 
                (x * cell_size, grid_size * cell_size), 
                1
            )
            
        for y in range(grid_size + 1):
            # Horizontal lines
            pygame.draw.line(
                grid_surface, 
                self.colors["grid"], 
                (0, y * cell_size), 
                (grid_size * cell_size, y * cell_size), 
                1
            )
            
        # Draw hoops at center of each end zone
        hoop_radius = cell_size // 4
        center_x = grid_size * cell_size // 2
        
        # Top hoop (team1 scores here)
        top_hoop_y = cell_size // 2
        pygame.draw.circle(grid_surface, self.colors["hoop"], (center_x, top_hoop_y), hoop_radius)
        pygame.draw.circle(grid_surface, self.colors["background"], (center_x, top_hoop_y), hoop_radius - 5)
        
        # Bottom hoop (team2 scores here)
        bottom_hoop_y = (grid_size - 0.5) * cell_size
        pygame.draw.circle(grid_surface, self.colors["hoop"], (center_x, bottom_hoop_y), hoop_radius)
        pygame.draw.circle(grid_surface, self.colors["background"], (center_x, bottom_hoop_y), hoop_radius - 5)
            
        # Blit the grid to the screen at the specified offset
        screen.blit(grid_surface, (offset_x, offset_y))
        
        return grid_surface 