import pygame
import math
from animation import Animation

class AnimationRenderer:
    """Handles rendering of animations in the game"""
    def __init__(self, game, cell_size):
        self.game = game
        self.cell_size = cell_size
        self.animation_manager = game.animation_manager
        
    def draw(self, screen, animation_manager, offset_x, offset_y):
        """Draw the current animation
        
        Args:
            screen: The pygame screen to draw on
            animation_manager: The AnimationManager instance
            offset_x: The x offset for drawing
            offset_y: The y offset for drawing
        """
        if not animation_manager.active_animation:
            return
            
        animation = animation_manager.active_animation
        
        if animation.type == "move":
            self._render_move_animation(screen, animation, offset_x, offset_y)
        elif animation.type == "block":
            self._render_block_animation(screen, animation, offset_x, offset_y)
        elif animation.type == "knockdown":
            self._render_knockdown_animation(screen, animation, offset_x, offset_y)
        elif animation.type == "score":
            self._render_score_animation(screen, animation, offset_x, offset_y)
            
    def _render_move_animation(self, screen, animation, offset_x, offset_y):
        """Render a goblin movement animation"""
        if not animation.source or not animation.target:
            return
            
        progress = animation.get_progress()
        
        # Calculate interpolated position
        start_x, start_y = animation.source.position
        end_x, end_y = animation.target
        
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        
        # Convert to screen coordinates
        screen_x = offset_x + current_x * self.cell_size + self.cell_size // 2
        screen_y = offset_y + current_y * self.cell_size + self.cell_size // 2
        
        # Draw goblin at current position
        radius = self.cell_size // 3
        color = animation.source.team.color if animation.source.team else (255, 255, 255)
        
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)
        
    def _render_block_animation(self, screen, animation, offset_x, offset_y):
        """Render a blocking animation"""
        if not animation.source or not animation.target:
            return
            
        progress = animation.get_progress()
        
        # Get blocker and target positions
        blocker_x, blocker_y = animation.source.position
        target_x, target_y = animation.target.position
        
        # Convert to screen coordinates
        blocker_screen_x = offset_x + blocker_x * self.cell_size + self.cell_size // 2
        blocker_screen_y = offset_y + blocker_y * self.cell_size + self.cell_size // 2
        target_screen_x = offset_x + target_x * self.cell_size + self.cell_size // 2
        target_screen_y = offset_y + target_y * self.cell_size + self.cell_size // 2
        
        # Draw line between blocker and target
        width = max(1, int(5 * (1 - progress)))  # Line gets thinner as animation progresses
        pygame.draw.line(screen, (255, 0, 0), 
                         (blocker_screen_x, blocker_screen_y), 
                         (target_screen_x, target_screen_y), width)
        
        # Draw impact at midpoint
        if 0.4 <= progress <= 0.6:
            mid_x = (blocker_screen_x + target_screen_x) // 2
            mid_y = (blocker_screen_y + target_screen_y) // 2
            impact_size = int(self.cell_size / 4 * (1 - abs(progress - 0.5) * 5))
            pygame.draw.circle(screen, (255, 255, 0), (mid_x, mid_y), impact_size)
            
    def _render_knockdown_animation(self, screen, animation, offset_x, offset_y):
        """Render a knockdown animation"""
        if not animation.target:
            return
            
        progress = animation.get_progress()
        
        # Get target position
        target_x, target_y = animation.target.position
        
        # Convert to screen coordinates
        screen_x = offset_x + target_x * self.cell_size + self.cell_size // 2
        screen_y = offset_y + target_y * self.cell_size + self.cell_size // 2
        
        # Draw stars around knocked down goblin
        if progress < 0.8:
            star_count = 5
            star_radius = self.cell_size // 5
            
            for i in range(star_count):
                angle = (progress * 5 + i / star_count) * 2 * math.pi
                distance = star_radius * 1.5
                
                star_x = screen_x + math.cos(angle) * distance
                star_y = screen_y + math.sin(angle) * distance
                
                # Draw a small star/spark
                pygame.draw.circle(screen, (255, 255, 0), (int(star_x), int(star_y)), 
                                  int(star_radius * (1 - progress)))
                
    def _render_score_animation(self, screen, animation, offset_x, offset_y):
        """Render a scoring animation"""
        if not animation.source:
            return
            
        progress = animation.get_progress()
        
        # Get source position
        source_x, source_y = animation.source.position
        
        # Convert to screen coordinates
        screen_x = offset_x + source_x * self.cell_size + self.cell_size // 2
        screen_y = offset_y + source_y * self.cell_size + self.cell_size // 2
        
        # Draw expanding circle representing score
        max_radius = self.cell_size * 5
        current_radius = max_radius * progress
        alpha = int(255 * (1 - progress))
        
        # Create a transparent surface for the glow
        glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
        
        # Draw the glow
        team_color = animation.source.team.color if animation.source.team else (255, 255, 255)
        glow_color = (team_color[0], team_color[1], team_color[2], alpha)
        pygame.draw.circle(glow_surface, glow_color, 
                         (current_radius, current_radius), current_radius)
                         
        # Draw the circle to the screen
        screen.blit(glow_surface, 
                  (screen_x - current_radius, screen_y - current_radius))
        
        # Draw the score text
        if 0.2 <= progress <= 0.8:
            font_size = int(48 * (1 - abs(progress - 0.5) * 2.5))
            try:
                font = pygame.font.SysFont("Arial", font_size, bold=True)
                score_text = f"+{animation.result}" if animation.result else "+1"
                text_surface = font.render(score_text, True, (255, 255, 0))
                text_rect = text_surface.get_rect(center=(screen_x, screen_y - self.cell_size))
                screen.blit(text_surface, text_rect)
            except:
                # Fallback if font rendering fails
                pass 