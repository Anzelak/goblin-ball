import pygame
import math

class GoblinRenderer:
    """Renders goblins on the game grid"""
    
    def __init__(self, game, cell_size):
        self.game = game
        self.cell_size = cell_size
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        self.colors = {
            "team1": game.team1.color,
            "team2": game.team2.color,
            "carrier": (255, 215, 0),  # Gold
            "selected": (255, 255, 255),  # White
            "text": (255, 255, 255),  # White
            "ball": (255, 255, 0),  # Yellow
            "knocked_down": (150, 50, 50),  # Dark red
        }
        
        # Fonts
        self.fonts = {
            "tiny": pygame.font.SysFont(None, 12),
            "small": pygame.font.SysFont(None, 14),
            "medium": pygame.font.SysFont(None, 18, bold=True),
            "large": pygame.font.SysFont(None, 22, bold=True),
        }
        
        # Load or create goblin images
        self.load_goblin_images()
        
    def load_goblin_images(self):
        """Load or create goblin images for different states"""
        self.goblin_images = {}
        image_size = (self.cell_size, self.cell_size)
        
        # Create basic images for red goblins
        red_normal = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.circle(red_normal, (220, 60, 60), (self.cell_size//2, self.cell_size//2), self.cell_size//3)
        pygame.draw.circle(red_normal, (255, 255, 255), (self.cell_size//2, self.cell_size//2), self.cell_size//3, 2)
        self.goblin_images['red_normal'] = red_normal
        
        red_knocked = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.ellipse(red_knocked, (150, 40, 40), 
                         (self.cell_size//4, self.cell_size//2 - self.cell_size//6, 
                          self.cell_size//2, self.cell_size//3))
        pygame.draw.ellipse(red_knocked, (255, 255, 255), 
                         (self.cell_size//4, self.cell_size//2 - self.cell_size//6, 
                          self.cell_size//2, self.cell_size//3), 2)
        red_font = pygame.font.SysFont(None, 20)
        ko_text = red_font.render("K.O.", True, (255, 255, 255))
        ko_rect = ko_text.get_rect(center=(self.cell_size//2, self.cell_size//4))
        red_knocked.blit(ko_text, ko_rect)
        self.goblin_images['red_knocked_down'] = red_knocked
        
        red_carrier = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.circle(red_carrier, (255, 215, 0), (self.cell_size//2, self.cell_size//2), self.cell_size//3)
        pygame.draw.circle(red_carrier, (255, 255, 255), (self.cell_size//2, self.cell_size//2), self.cell_size//3, 2)
        # Add ball to carrier
        pygame.draw.circle(red_carrier, (255, 255, 0), 
                        (self.cell_size//2 + self.cell_size//6, self.cell_size//2 - self.cell_size//6), 
                        self.cell_size//6)
        self.goblin_images['red_carrier'] = red_carrier
        
        # Create basic images for blue goblins
        blue_normal = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.circle(blue_normal, (60, 60, 220), (self.cell_size//2, self.cell_size//2), self.cell_size//3)
        pygame.draw.circle(blue_normal, (255, 255, 255), (self.cell_size//2, self.cell_size//2), self.cell_size//3, 2)
        self.goblin_images['blue_normal'] = blue_normal
        
        blue_knocked = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.ellipse(blue_knocked, (40, 40, 150), 
                         (self.cell_size//4, self.cell_size//2 - self.cell_size//6, 
                          self.cell_size//2, self.cell_size//3))
        pygame.draw.ellipse(blue_knocked, (255, 255, 255), 
                         (self.cell_size//4, self.cell_size//2 - self.cell_size//6, 
                          self.cell_size//2, self.cell_size//3), 2)
        blue_font = pygame.font.SysFont(None, 20)
        ko_text = blue_font.render("K.O.", True, (255, 255, 255))
        ko_rect = ko_text.get_rect(center=(self.cell_size//2, self.cell_size//4))
        blue_knocked.blit(ko_text, ko_rect)
        self.goblin_images['blue_knocked_down'] = blue_knocked
        
        blue_carrier = pygame.Surface(image_size, pygame.SRCALPHA)
        pygame.draw.circle(blue_carrier, (255, 215, 0), (self.cell_size//2, self.cell_size//2), self.cell_size//3)
        pygame.draw.circle(blue_carrier, (255, 255, 255), (self.cell_size//2, self.cell_size//2), self.cell_size//3, 2)
        # Add ball to carrier
        pygame.draw.circle(blue_carrier, (255, 255, 0), 
                        (self.cell_size//2 + self.cell_size//6, self.cell_size//2 - self.cell_size//6), 
                        self.cell_size//6)
        self.goblin_images['blue_carrier'] = blue_carrier
        
    def draw(self, screen, offset_x, offset_y, selected_goblin=None):
        """Draw all goblins on the screen
        
        Args:
            screen: The pygame screen to draw on
            offset_x: The x offset for drawing
            offset_y: The y offset for drawing
            selected_goblin: The currently selected goblin or None
        """
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                # Skip goblins that are out of the game
                if goblin.out_of_game:
                    continue
                    
                # Get goblin position on screen
                x, y = goblin.position
                screen_x = offset_x + x * self.cell_size + self.cell_size // 2
                screen_y = offset_y + y * self.cell_size + self.cell_size // 2
                
                # Draw movement trail if available
                trail = self.game.get_movement_trail(goblin)
                if trail and len(trail) > 1:
                    self.draw_movement_trail(screen, offset_x, offset_y, goblin, trail)
                
                # Determine goblin color
                if goblin.knocked_down:
                    color = self.colors["knocked_down"]
                elif goblin.has_ball:
                    color = self.colors["carrier"]
                else:
                    color = self.colors["team1"] if goblin.team == self.game.team1 else self.colors["team2"]
                
                # Draw selection indicator if selected
                if goblin == selected_goblin:
                    pygame.draw.circle(screen, self.colors["selected"], (screen_x, screen_y), 
                                      self.cell_size // 2 + 2, 2)
                
                # Draw the goblin
                self.draw_goblin(screen, screen_x, screen_y, goblin, color)
    
    def draw_goblin(self, screen, x, y, goblin, color):
        """Draw a single goblin
        
        Args:
            screen: The pygame screen to draw on
            x: The x coordinate on screen
            y: The y coordinate on screen
            goblin: The goblin to draw
            color: The color to use
        """
        # Draw goblin body
        radius = self.cell_size // 3
        
        # Get the base team color
        team_color = self.colors["team1"] if goblin.team == self.game.team1 else self.colors["team2"]
        
        # Set color based on state
        if goblin.knocked_down:
            # Use a darker version of the team's color for knocked down goblins
            # instead of always using red
            darkened_color = (
                max(0, team_color[0] - 100),
                max(0, team_color[1] - 100),
                max(0, team_color[2] - 100)
            )
            draw_color = darkened_color
        elif goblin.has_ball:
            draw_color = self.colors["carrier"]
        else:
            draw_color = team_color
            
        # Draw the goblin shape
        if goblin.knocked_down:
            # Draw as oval if knocked down
            pygame.draw.ellipse(screen, draw_color, 
                             (x - radius, y - radius // 2, radius * 2, radius))
        else:
            # Draw as circle if standing
            pygame.draw.circle(screen, draw_color, (x, y), radius)
        
        # Draw ball if carrier
        if goblin.has_ball:
            ball_x = x + radius // 2
            ball_y = y - radius // 2
            pygame.draw.circle(screen, self.colors["ball"], (ball_x, ball_y), radius // 2)
        
        # Draw initial of goblin name
        text = self.fonts["small"].render(goblin.name[0], True, self.colors["text"])
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
        
        # Draw stats if hovering/selected
        # (This would normally be linked to mouse position, but here we always show it)
        stat_text = self.fonts["tiny"].render(f"S{goblin.strength} T{goblin.toughness} M{goblin.movement}", 
                                           True, self.colors["text"])
        screen.blit(stat_text, (x - stat_text.get_width() // 2, y + radius + 2))
        
    def draw_movement_trail(self, screen, offset_x, offset_y, goblin, trail):
        """Draw the movement trail for a goblin
        
        Args:
            screen: The pygame screen to draw on
            offset_x: The x offset for drawing
            offset_y: The y offset for drawing
            goblin: The goblin whose trail to draw
            trail: The list of positions in the trail
        """
        # Skip if trail is too short
        if len(trail) <= 1:
            return
            
        # Current turn's movement is the last position (to allow for clear visualization)
        # We'll show the trail from the previous turn's end position to the current position
        
        # Create trail surface
        trail_surface = pygame.Surface((self.game.grid.width * self.cell_size, 
                                     self.game.grid.height * self.cell_size), pygame.SRCALPHA)
        
        # Choose trail color based on team
        if goblin.team == self.game.team1:
            base_color = (220, 60, 60)  # Brighter red
        else:
            base_color = (60, 60, 220)  # Brighter blue
            
        # Always make the most recent move stand out
        # This is the move from the second-to-last position to the current position
        if len(trail) >= 2:
            prev_x, prev_y = trail[-2]
            curr_x, curr_y = trail[-1]
            
            # Convert to screen coordinates
            prev_screen_x = prev_x * self.cell_size + self.cell_size // 2
            prev_screen_y = prev_y * self.cell_size + self.cell_size // 2
            curr_screen_x = curr_x * self.cell_size + self.cell_size // 2
            curr_screen_y = curr_y * self.cell_size + self.cell_size // 2
            
            # Draw a thicker, fully opaque line for the most recent move
            last_move_color = (*base_color, 255)  # Full opacity
            
            # Draw an arrow from previous position to current
            pygame.draw.line(trail_surface, last_move_color, 
                          (prev_screen_x, prev_screen_y), 
                          (curr_screen_x, curr_screen_y), 4)
            
            # Draw arrow head to indicate direction
            self.draw_arrow_head(trail_surface, prev_screen_x, prev_screen_y, 
                               curr_screen_x, curr_screen_y, last_move_color, 8)
            
            # Draw circles at endpoints
            pygame.draw.circle(trail_surface, last_move_color, (prev_screen_x, prev_screen_y), 5)
            pygame.draw.circle(trail_surface, last_move_color, (curr_screen_x, curr_screen_y), 7)
        
        # Draw older parts of the trail with less opacity
        if len(trail) > 2:
            for i in range(len(trail) - 2):
                start_x, start_y = trail[i]
                end_x, end_y = trail[i + 1]
                
                # Convert to screen coordinates
                start_screen_x = start_x * self.cell_size + self.cell_size // 2
                start_screen_y = start_y * self.cell_size + self.cell_size // 2
                end_screen_x = end_x * self.cell_size + self.cell_size // 2
                end_screen_y = end_y * self.cell_size + self.cell_size // 2
                
                # Older lines are more transparent
                opacity = max(40, 120 - (len(trail) - i - 2) * 30)  # Fades out for older moves
                older_color = (*base_color, opacity)
                
                pygame.draw.line(trail_surface, older_color, 
                              (start_screen_x, start_screen_y), 
                              (end_screen_x, end_screen_y), 2)
                
                # Small circle at each point
                pygame.draw.circle(trail_surface, older_color, (start_screen_x, start_screen_y), 3)
        
        # Blit the trail surface to the screen
        screen.blit(trail_surface, (offset_x, offset_y))
    
    def draw_arrow_head(self, surface, from_x, from_y, to_x, to_y, color, size):
        """Draw an arrow head to indicate direction
        
        Args:
            surface: The surface to draw on
            from_x: Starting x coordinate
            from_y: Starting y coordinate
            to_x: Ending x coordinate
            to_y: Ending y coordinate
            color: Arrow color
            size: Size of the arrow head
        """
        # Calculate direction vector
        dx = to_x - from_x
        dy = to_y - from_y
        
        # Normalize
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
            
        dx /= length
        dy /= length
        
        # Calculate perpendicular vector
        px = -dy
        py = dx
        
        # Calculate arrow head points
        # At the destination point, draw a triangle
        point1 = (to_x, to_y)
        point2 = (to_x - dx*size - px*size/2, to_y - dy*size - py*size/2)
        point3 = (to_x - dx*size + px*size/2, to_y - dy*size + py*size/2)
        
        # Draw the arrow head
        pygame.draw.polygon(surface, color, [point1, point2, point3])

    def draw_goblins(self, screen, game):
        """Draw all goblins on the screen
        
        Args:
            screen: The pygame screen to draw on
            game: The game object
        """
        # Check if we have the necessary attributes
        if not hasattr(self, 'goblin_images') or not hasattr(self, 'cell_size'):
            logger.warning("Goblin renderer missing required attributes")
            return
            
        # Calculate grid offsets
        grid_width = game.grid_size * self.cell_size
        grid_height = game.grid_size * self.cell_size
        offset_x = (self.screen_width - grid_width) // 2
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        hovered_goblin = None
        
        # Draw each goblin
        for goblin in game.goblins:
            # Convert grid position to screen coordinates
            x = offset_x + goblin.position[0] * self.cell_size
            y = offset_y + goblin.position[1] * self.cell_size
            
            # Get the appropriate image based on goblin state
            goblin_img = self.get_goblin_image(goblin)
            
            # Scale the image to fit the cell size
            scaled_img = pygame.transform.scale(goblin_img, (self.cell_size, self.cell_size))
            
            # Draw the goblin
            screen.blit(scaled_img, (x, y))
            
            # Check if this goblin is being hovered over
            goblin_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            if goblin_rect.collidepoint(mouse_pos):
                hovered_goblin = goblin
                
                # Draw highlight around the goblin
                highlight_color = (255, 255, 100, 150)  # Yellow highlight with transparency
                highlight_rect = pygame.Rect(x - 3, y - 3, self.cell_size + 6, self.cell_size + 6)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, highlight_color, highlight_surface.get_rect(), 3)
                screen.blit(highlight_surface, highlight_rect)
                
                # Highlight this goblin's movement trail
                self.highlight_movement_trail(screen, goblin, offset_x, offset_y)
            
            # Draw goblin info
            self.draw_goblin_info(screen, goblin, (x, y))
            
        # If a goblin is being hovered over, draw detailed information
        if hovered_goblin:
            self.draw_hover_info(screen, hovered_goblin)
    
    def highlight_movement_trail(self, screen, goblin, offset_x, offset_y):
        """Highlight the movement trail of a goblin
        
        Args:
            screen: The pygame screen to draw on
            goblin: The goblin to highlight
            offset_x: The x offset for grid drawing
            offset_y: The y offset for grid drawing
        """
        if not hasattr(goblin, 'movement_trail') or not goblin.movement_trail:
            return
            
        # Make a copy of the movement trail
        trail = goblin.movement_trail.copy()
        
        # Add current position to trail if not already there
        if not trail or trail[-1] != goblin.position:
            trail.append(goblin.position)
            
        # Create a semi-transparent surface for the trail
        trail_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw lines connecting trail points
        if len(trail) > 1:
            points = [(offset_x + pos[0] * self.cell_size + self.cell_size // 2, 
                      offset_y + pos[1] * self.cell_size + self.cell_size // 2) 
                     for pos in trail]
            
            # Team-based color with high visibility
            if goblin.team == 'red':
                line_color = (255, 100, 100, 230)  # Bright red
                glow_color = (255, 50, 50, 100)    # Red glow
            else:
                line_color = (100, 100, 255, 230)  # Bright blue
                glow_color = (50, 50, 255, 100)    # Blue glow
            
            # Draw a glowing effect
            for width in range(12, 2, -2):
                # Fade the glow as it gets wider
                glow_opacity = int(150 * (1 - width / 12))
                current_glow = (glow_color[0], glow_color[1], glow_color[2], glow_opacity)
                pygame.draw.lines(trail_surface, current_glow, False, points, width)
            
            # Draw the main line
            pygame.draw.lines(trail_surface, line_color, False, points, 3)
            
            # Draw dots at each position
            for point in points:
                pygame.draw.circle(trail_surface, line_color, point, 5)
            
        # Blit the trail surface to the screen
        screen.blit(trail_surface, (0, 0))
        
    def draw_hover_info(self, screen, goblin):
        """Draw detailed hover info for a goblin
        
        Args:
            screen: The pygame screen to draw on
            goblin: The goblin to show info for
        """
        # Position the info box near the mouse but ensure it stays on screen
        mouse_pos = pygame.mouse.get_pos()
        info_width = 250
        info_height = 180
        
        # Adjust position to keep box on screen
        box_x = mouse_pos[0] + 20
        if box_x + info_width > self.screen_width:
            box_x = mouse_pos[0] - info_width - 10
            
        box_y = mouse_pos[1] - 10
        if box_y + info_height > self.screen_height:
            box_y = self.screen_height - info_height - 10
        
        # Create info box surface with transparency
        info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 200))  # Semi-transparent black
        
        # Add border
        pygame.draw.rect(info_surface, (200, 200, 200, 255), info_surface.get_rect(), 2)
        
        # Prepare the font
        if not hasattr(self, 'fonts'):
            self.fonts = {
                'small': pygame.font.SysFont('Arial', 14),
                'medium': pygame.font.SysFont('Arial', 16, bold=True),
                'large': pygame.font.SysFont('Arial', 18, bold=True)
            }
        
        # Title - Goblin ID with team color
        if goblin.team == 'red':
            title_color = (255, 150, 150)
        else:
            title_color = (150, 150, 255)
            
        title_text = f"{goblin.team.upper()} Goblin #{goblin.id}"
        title_surface = self.fonts['large'].render(title_text, True, title_color)
        info_surface.blit(title_surface, (10, 10))
        
        # Status info
        y_offset = 40
        line_height = 20
        
        # Position
        pos_text = f"Position: ({goblin.position[0]}, {goblin.position[1]})"
        pos_surface = self.fonts['small'].render(pos_text, True, (255, 255, 255))
        info_surface.blit(pos_surface, (10, y_offset))
        y_offset += line_height
        
        # State (carrying ball, knocked down, etc.)
        state_info = []
        if hasattr(goblin, 'carrying_ball') and goblin.carrying_ball:
            state_info.append("Carrying Ball")
        if hasattr(goblin, 'knocked_down') and goblin.knocked_down:
            state_info.append("Knocked Down")
        if not state_info:
            state_info.append("Active")
            
        state_text = f"State: {', '.join(state_info)}"
        state_surface = self.fonts['small'].render(state_text, True, (255, 255, 255))
        info_surface.blit(state_surface, (10, y_offset))
        y_offset += line_height
        
        # Movement info
        if hasattr(goblin, 'movement_trail') and goblin.movement_trail:
            move_count = len(goblin.movement_trail)
            move_text = f"Moves made: {move_count}"
            move_surface = self.fonts['small'].render(move_text, True, (255, 255, 255))
            info_surface.blit(move_surface, (10, y_offset))
            y_offset += line_height
        
        # Stats
        stats_text = f"Block: {goblin.block_skill}  Dodge: {goblin.dodge_skill}"
        stats_surface = self.fonts['small'].render(stats_text, True, (255, 255, 255))
        info_surface.blit(stats_surface, (10, y_offset))
        y_offset += line_height
        
        # Recent actions
        y_offset += 5  # Add some space
        recent_title = "Recent Actions:"
        recent_title_surface = self.fonts['medium'].render(recent_title, True, (200, 200, 200))
        info_surface.blit(recent_title_surface, (10, y_offset))
        y_offset += line_height
        
        # Check for recent blocks or dukes associated with this goblin
        recent_actions = []
        
        # Add some examples (need to be replaced with actual game data)
        if hasattr(self, 'game'):
            # Get the UI renderer to check for visualizations
            ui_renderer = None
            for renderer in self.game.renderers:
                if hasattr(renderer, 'block_visualizations'):
                    ui_renderer = renderer
                    break
            
            if ui_renderer:
                # Check blocks involving this goblin
                for block in ui_renderer.block_visualizations:
                    if block["blocker"] == goblin:
                        recent_actions.append(f"Blocked #{block['target'].id}: {block['result'].upper()}")
                    elif block["target"] == goblin:
                        recent_actions.append(f"Was blocked by #{block['blocker'].id}: {block['result'].upper()}")
                
                # Check dukes involving this goblin
                if hasattr(ui_renderer, 'duke_visualizations'):
                    for duke in ui_renderer.duke_visualizations:
                        if duke["goblin"] == goblin:
                            result = "SUCCESS" if duke["success"] else "FAILURE"
                            recent_actions.append(f"DUKE attempt: {result}")
        
        # If no actions found, show a message
        if not recent_actions:
            recent_actions.append("No recent actions")
        
        # Show recent actions (up to 3)
        for i, action in enumerate(recent_actions[:3]):
            action_surface = self.fonts['small'].render(action, True, (200, 200, 200))
            info_surface.blit(action_surface, (20, y_offset))
            y_offset += line_height
        
        # Draw the info box
        screen.blit(info_surface, (box_x, box_y))

    def get_goblin_image(self, goblin):
        """Get the appropriate image for a goblin based on its state
        
        Args:
            goblin: The goblin to get an image for
            
        Returns:
            The pygame surface for the goblin image
        """
        # Make sure we have goblin images loaded
        if not hasattr(self, 'goblin_images'):
            logger.warning("Goblin images not loaded")
            # Create a default image as fallback
            default_img = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(default_img, (255, 0, 0), (self.cell_size//2, self.cell_size//2), self.cell_size//2)
            return default_img
            
        # Determine which image to use based on goblin state
        if goblin.team == 'red':
            base_img = self.goblin_images['red_normal']
            
            if hasattr(goblin, 'knocked_down') and goblin.knocked_down:
                return self.goblin_images['red_knocked_down']
            elif hasattr(goblin, 'carrying_ball') and goblin.carrying_ball:
                return self.goblin_images['red_carrier']
            else:
                return base_img
        else:
            base_img = self.goblin_images['blue_normal']
            
            if hasattr(goblin, 'knocked_down') and goblin.knocked_down:
                return self.goblin_images['blue_knocked_down']
            elif hasattr(goblin, 'carrying_ball') and goblin.carrying_ball:
                return self.goblin_images['blue_carrier']
            else:
                return base_img 