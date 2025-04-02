import pygame
from config import CONFIG

class GameRenderer:
    def __init__(self, game, screen_width=800, screen_height=800):
        """Initialize the Pygame renderer for displaying the game"""
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Goblinball")
        
        # Calculate grid cell size
        self.cell_size = min(screen_width, screen_height) // game.grid_size
        
        # Colors
        self.colors = {
            "background": (20, 100, 20),  # Field green
            "grid": (255, 255, 255, 50),  # Semi-transparent white
            "endzone1": (200, 200, 200, 100),  # Semi-transparent light gray
            "endzone2": (150, 150, 150, 100),  # Semi-transparent gray
            "team1": game.team1.color,
            "team2": game.team2.color,
            "carrier": (255, 215, 0),  # Gold
            "selected": (255, 255, 255),  # White
            "text": (255, 255, 255),  # White
            "hoop": (150, 75, 0)  # Brown
        }
        
        # Fonts
        self.fonts = {
            "small": pygame.font.SysFont(None, 14),
            "medium": pygame.font.SysFont(None, 20),
            "large": pygame.font.SysFont(None, 28)
        }
        
        # Animation queues
        self.animations = []
        self.active_animation = None
        
        # UI state
        self.paused = True
        self.animation_speed = CONFIG.get("animation_speed", 1.0)
        self.show_debug = CONFIG.get("show_debug_info", False)
        self.selected_goblin = None
        
    def draw(self):
        """Draw the game state to the screen"""
        # Clear screen
        self.screen.fill(self.colors["background"])
        
        # Draw grid
        self.draw_grid()
        
        # Draw goblins
        self.draw_goblins()
        
        # Draw current animation
        if self.active_animation:
            self.draw_animation()
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw debug info if enabled
        if self.show_debug:
            self.draw_debug_info()
        
        # Update display
        pygame.display.flip()
        
    def draw_grid(self):
        """Draw the game grid with end zones"""
        grid_size = self.game.grid_size
        cell_size = self.cell_size
        
        # Create surface for grid
        grid_surface = pygame.Surface((grid_size * cell_size, grid_size * cell_size), pygame.SRCALPHA)
        
        # Draw end zones
        pygame.draw.rect(grid_surface, self.colors["endzone1"], (0, 0, grid_size * cell_size, cell_size))
        pygame.draw.rect(grid_surface, self.colors["endzone2"], (0, (grid_size - 1) * cell_size, grid_size * cell_size, cell_size))
        
        # Draw hoops
        hoop_radius = cell_size // 4
        # Top hoop (center of top row)
        pygame.draw.circle(grid_surface, self.colors["hoop"], ((grid_size // 2) * cell_size + cell_size // 2, cell_size // 2), hoop_radius)
        # Bottom hoop (center of bottom row)
        pygame.draw.circle(grid_surface, self.colors["hoop"], ((grid_size // 2) * cell_size + cell_size // 2, (grid_size - 1) * cell_size + cell_size // 2), hoop_radius)
        
        # Draw grid lines if enabled
        if CONFIG.get("show_grid", True):
            for x in range(grid_size + 1):
                pygame.draw.line(grid_surface, self.colors["grid"], (x * cell_size, 0), (x * cell_size, grid_size * cell_size))
            for y in range(grid_size + 1):
                pygame.draw.line(grid_surface, self.colors["grid"], (0, y * cell_size), (grid_size * cell_size, y * cell_size))
        
        # Draw the grid to the screen
        self.screen.blit(grid_surface, (0, 0))
        
    def draw_goblins(self):
        """Draw all goblins on the field"""
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                if goblin.out_of_game:
                    continue  # Skip goblins that are out of the game
                    
                # Determine goblin color
                color = self.colors["team1"] if goblin.team == self.game.team1 else self.colors["team2"]
                
                # Draw goblin position
                x, y = goblin.position
                center_x = (x * self.cell_size) + (self.cell_size // 2)
                center_y = (y * self.cell_size) + (self.cell_size // 2)
                
                # Highlight carrier or knocked down goblins
                if goblin.has_ball:
                    # Draw carrier with ball (larger circle with gold border)
                    radius = self.cell_size // 2 - 4
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, self.colors["carrier"], (center_x, center_y), radius, 3)
                    
                    # Draw ball
                    ball_offset = 5
                    pygame.draw.circle(self.screen, (150, 75, 0), (center_x + ball_offset, center_y - ball_offset), radius // 3)
                elif goblin.knocked_down:
                    # Draw knocked down goblin (X shape)
                    radius = self.cell_size // 2 - 8
                    pygame.draw.line(self.screen, color, 
                                     (center_x - radius, center_y - radius),
                                     (center_x + radius, center_y + radius), 3)
                    pygame.draw.line(self.screen, color, 
                                     (center_x + radius, center_y - radius),
                                     (center_x - radius, center_y + radius), 3)
                else:
                    # Normal goblin (circle)
                    radius = self.cell_size // 2 - 8
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                
                # Highlight selected goblin
                if goblin == self.selected_goblin:
                    pygame.draw.circle(self.screen, self.colors["selected"], (center_x, center_y), radius + 4, 2)
                
                # Draw goblin initial
                text = self.fonts["small"].render(goblin.name[0], True, self.colors["text"])
                text_rect = text.get_rect(center=(center_x, center_y))
                self.screen.blit(text, text_rect)
    
    def draw_ui(self):
        """Draw UI elements like score, current play, etc."""
        # Draw game info at the top of the screen
        team1_text = f"{self.game.team1.name}: {self.game.team1.score}"
        team2_text = f"{self.game.team2.name}: {self.game.team2.score}"
        play_text = f"Play: {self.game.current_play}/{self.game.max_plays} | Turn: {self.game.turn}"
        
        # Render text
        team1_surface = self.fonts["large"].render(team1_text, True, self.colors["team1"])
        team2_surface = self.fonts["large"].render(team2_text, True, self.colors["team2"])
        play_surface = self.fonts["medium"].render(play_text, True, self.colors["text"])
        
        # Position text
        self.screen.blit(team1_surface, (10, self.game.grid_size * self.cell_size + 10))
        self.screen.blit(team2_surface, (self.game.grid_size * self.cell_size - team2_surface.get_width() - 10, 
                                         self.game.grid_size * self.cell_size + 10))
        self.screen.blit(play_surface, ((self.game.grid_size * self.cell_size - play_surface.get_width()) // 2, 
                                       self.game.grid_size * self.cell_size + 10))
        
        # Draw offense indicator
        offense_text = f"Offense: {self.game.offense_team.name}"
        offense_surface = self.fonts["medium"].render(offense_text, True, 
                                                     self.colors["team1"] if self.game.offense_team == self.game.team1 
                                                     else self.colors["team2"])
        self.screen.blit(offense_surface, ((self.game.grid_size * self.cell_size - offense_surface.get_width()) // 2, 
                                         self.game.grid_size * self.cell_size + 40))
        
        # Draw selected goblin info if any
        if self.selected_goblin:
            goblin = self.selected_goblin
            goblin_info = f"{goblin.name} - STR: {goblin.strength} TOU: {goblin.toughness} MOV: {goblin.movement}/{goblin.max_movement}"
            if goblin.has_ball:
                goblin_info += " (Carrier)"
            if goblin.knocked_down:
                goblin_info += " (Knocked Down)"
                
            info_surface = self.fonts["medium"].render(goblin_info, True, 
                                                      self.colors["team1"] if goblin.team == self.game.team1 
                                                      else self.colors["team2"])
            self.screen.blit(info_surface, (10, self.game.grid_size * self.cell_size + 70))
    
    def draw_debug_info(self):
        """Draw debug information if enabled"""
        if not self.show_debug:
            return
            
        # Draw some debug info
        debug_lines = [
            f"Carrier Rotation Counter: {self.game.offense_team.carrier_rotation_counter}",
            f"Carrier History: {', '.join([g[:6] for g in self.game.offense_team.carrier_history[-5:]])}",
            f"Play Complete: {self.game.play_complete}",
            f"Game Complete: {self.game.game_complete}"
        ]
        
        y_offset = self.game.grid_size * self.cell_size + 100
        for line in debug_lines:
            debug_surface = self.fonts["small"].render(line, True, self.colors["text"])
            self.screen.blit(debug_surface, (10, y_offset))
            y_offset += 20
            
    def draw_animation(self):
        """Draw the current animation"""
        if not self.active_animation:
            return
            
        # Example for a simple move animation
        if self.active_animation.type == "move":
            # Draw a moving goblin animation (simple example)
            progress = self.active_animation.frame / self.active_animation.duration
            source = self.active_animation.source
            target = self.active_animation.target
            
            # Interpolate position
            start_x, start_y = source.position
            end_x, end_y = target
            
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            center_x = (current_x * self.cell_size) + (self.cell_size // 2)
            center_y = (current_y * self.cell_size) + (self.cell_size // 2)
            
            # Draw moving goblin
            color = self.colors["team1"] if source.team == self.game.team1 else self.colors["team2"]
            radius = self.cell_size // 2 - 8
            
            pygame.draw.circle(self.screen, color, (int(center_x), int(center_y)), radius)
            
            # Draw trail
            trail_length = 5
            for i in range(1, trail_length + 1):
                trail_progress = max(0, progress - (i * 0.1))
                trail_x = start_x + (end_x - start_x) * trail_progress
                trail_y = start_y + (end_y - start_y) * trail_progress
                
                trail_center_x = (trail_x * self.cell_size) + (self.cell_size // 2)
                trail_center_y = (trail_y * self.cell_size) + (self.cell_size // 2)
                
                # Draw fading trail circle
                alpha = 255 * (1 - (i / trail_length))
                trail_color = (*color, alpha)
                
                trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color, (radius, radius), radius // 2)
                
                self.screen.blit(trail_surface, (int(trail_center_x - radius), int(trail_center_y - radius)))
    
    def handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to quit
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Exit on ESC
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused  # Toggle pause
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug  # Toggle debug info
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if a goblin was clicked
                x, y = event.pos
                grid_x = x // self.cell_size
                grid_y = y // self.cell_size
                
                # Check for goblin at this position
                if 0 <= grid_x < self.game.grid_size and 0 <= grid_y < self.game.grid_size:
                    self.selected_goblin = None
                    for team in [self.game.team1, self.game.team2]:
                        for goblin in team.goblins:
                            if not goblin.out_of_game and goblin.position == (grid_x, grid_y):
                                self.selected_goblin = goblin
                                break
                                
        return True  # Continue running
        
    def add_animation(self, animation_type, source=None, target=None, result=None, duration=30):
        """Add a new animation to the queue"""
        from animation import Animation
        animation = Animation(animation_type, source, target, result, duration)
        self.animations.append(animation)
        
        # If no active animation, start this one
        if not self.active_animation:
            self.active_animation = self.animations.pop(0)
            
    def update_animations(self):
        """Update current animation"""
        if self.active_animation:
            self.active_animation.update()
            
            if self.active_animation.is_complete():
                # Move to next animation
                if self.animations:
                    self.active_animation = self.animations.pop(0)
                else:
                    self.active_animation = None
                    
    def run(self):
        """Main rendering loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update animations
            if not self.paused:
                self.update_animations()
            
            # Draw everything
            self.draw()
            
            # Cap framerate
            clock.tick(60)
            
        pygame.quit() 