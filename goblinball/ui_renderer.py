import pygame
import time
import math
import logging

logger = logging.getLogger(__name__)

class UIRenderer:
    """Renders UI components like buttons, status, and event log"""
    
    def __init__(self, game, screen_width, screen_height):
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate grid cell size - adjusted for wider play area
        # Leave more space on the left for the event log
        usable_width = screen_width - 300  # Reserve space for event log on the left
        usable_height = screen_height - 150  # Reserve space for UI elements at top and bottom
        
        # The grid should remain centered in the usable area
        self.cell_size = min(usable_width // game.grid_size, usable_height // game.grid_size)
        
        self.colors = {
            "text": (255, 255, 255),  # White
            "button": (80, 80, 80),  # Dark gray
            "button_hover": (120, 120, 120),  # Light gray
            "button_text": (255, 255, 255),  # White
            "message_bg": (0, 0, 0, 180),  # Semi-transparent black
            "success": (0, 200, 0),  # Green for successful events
            "warning": (200, 200, 0),  # Yellow for warning events
            "danger": (200, 0, 0),  # Red for dangerous events
            "team1": game.team1.color,
            "team2": game.team2.color,
            "info_bg": (0, 0, 0, 200),  # Black with high transparency for info popups
        }
        
        # Fonts
        self.fonts = {
            "small": pygame.font.SysFont(None, 16),
            "medium": pygame.font.SysFont(None, 24),
            "large": pygame.font.SysFont(None, 32),
            "symbol": pygame.font.SysFont(None, 20, bold=True),  # Bold font for symbols
        }
        
        # UI buttons
        button_y = self.screen_height - 50
        button_width = 120
        button_height = 40
        button_spacing = 10
        total_buttons_width = button_width * 5 + button_spacing * 4
        start_x = (self.screen_width - 300 - total_buttons_width) // 2 + 300  # Center buttons under the game board
        
        self.buttons = [
            {
                "text": "Next Turn",
                "rect": pygame.Rect(start_x, button_y, button_width, button_height),
                "action": "next_turn"
            },
            {
                "text": "Previous Turn",
                "rect": pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
                "action": "prev_turn"
            },
            {
                "text": "Auto Play",
                "rect": pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height),
                "action": "auto_play"
            },
            {
                "text": "New Play",
                "rect": pygame.Rect(start_x + (button_width + button_spacing) * 3, button_y, button_width, button_height),
                "action": "new_play"
            },
            {
                "text": "Debug",
                "rect": pygame.Rect(start_x + (button_width + button_spacing) * 4, button_y, button_width, button_height),
                "action": "toggle_debug"
            }
        ]
        
        # Event display
        self.displayed_events = []
        self.max_displayed_events = 10  # Show more events
        self.event_display_time = 3.0  # Seconds to display each event
        
        # Message system
        self.message = None
        self.message_time = 0
        self.message_duration = 3.0  # Seconds to display important messages
        
        # Block visualization
        self.block_visualizations = []  # Store active block visualizations
        self.block_viz_duration = 5.0  # How long to show block arrows and results - increased from 2.0 to 5.0
        
        # DUKE visualization
        self.duke_visualizations = []  # Store active DUKE visualizations
        self.duke_viz_duration = 5.0  # How long to show DUKE checks - increased from 2.0 to 5.0
        
        # Persistent event symbols
        self.event_symbols = []  # List of event symbols to display (persists longer)
        self.event_symbol_duration = 10.0  # Symbols stay visible for 10 seconds
        
        # Hover state
        self.hovered_goblin = None
        self.hovered_symbol = None
        self.flash_timer = 0  # Timer for flashing effects
        
    def draw(self, screen, hover_pos=None):
        """Draw all UI components
        
        Args:
            screen: The pygame screen to draw on
            hover_pos: The current mouse position for hover effects
        """
        # Draw scoreboard
        self.draw_scoreboard(screen)
        
        # Draw current play/turn info
        self.draw_game_status(screen)
        
        # Draw buttons
        self.draw_buttons(screen, hover_pos)
        
        # Draw event log
        self.draw_event_log(screen)
        
        # Update hover state
        if hover_pos:
            self.update_hover_state(screen, hover_pos)
        else:
            self.hovered_goblin = None
            self.hovered_symbol = None
        
        # Draw block visualizations
        self.draw_block_visualizations(screen)
        
        # Draw DUKE visualizations
        self.draw_duke_visualizations(screen)
        
        # Draw event symbols
        self.draw_event_symbols(screen)
        
        # Draw hover info if any
        if self.hovered_goblin or self.hovered_symbol:
            self.draw_hover_info(screen, hover_pos)
        
        # Draw message if any
        if self.message:
            self.draw_message(screen)
            
    def draw_scoreboard(self, screen):
        """Draw the scoreboard with team scores
        
        Args:
            screen: The pygame screen to draw on
        """
        # Draw team 1 score
        team1_text = f"{self.game.team1.name}: {self.game.team1.score}"
        team1_surface = self.fonts["large"].render(team1_text, True, self.colors["team1"])
        screen.blit(team1_surface, (20, 10))
        
        # Draw team 2 score
        team2_text = f"{self.game.team2.name}: {self.game.team2.score}"
        team2_surface = self.fonts["large"].render(team2_text, True, self.colors["team2"])
        screen.blit(team2_surface, (self.screen_width - 20 - team2_surface.get_width(), 10))
        
    def draw_game_status(self, screen):
        """Draw current play and turn information
        
        Args:
            screen: The pygame screen to draw on
        """
        # Draw play/turn info
        status_text = f"Play {self.game.current_play}/{self.game.max_plays} - Turn {self.game.turn}"
        status_surface = self.fonts["medium"].render(status_text, True, self.colors["text"])
        screen.blit(status_surface, (self.screen_width // 2 - status_surface.get_width() // 2, 15))
        
        # Draw offense team info
        offense_text = f"Offense: {self.game.offense_team.name}"
        offense_color = self.colors["team1"] if self.game.offense_team == self.game.team1 else self.colors["team2"]
        offense_surface = self.fonts["medium"].render(offense_text, True, offense_color)
        screen.blit(offense_surface, (self.screen_width // 2 - offense_surface.get_width() // 2, 40))
        
    def draw_buttons(self, screen, hover_pos=None):
        """Draw UI buttons
        
        Args:
            screen: The pygame screen to draw on
            hover_pos: The current mouse position for hover effects
        """
        for button in self.buttons:
            # Check if mouse is over button
            is_hovered = hover_pos and button["rect"].collidepoint(hover_pos)
            
            # Choose color based on hover state
            color = self.colors["button_hover"] if is_hovered else self.colors["button"]
            
            # Draw button
            pygame.draw.rect(screen, color, button["rect"], border_radius=5)
            pygame.draw.rect(screen, self.colors["text"], button["rect"], width=2, border_radius=5)
            
            # Draw button text
            text_surface = self.fonts["medium"].render(button["text"], True, self.colors["button_text"])
            text_rect = text_surface.get_rect(center=button["rect"].center)
            screen.blit(text_surface, text_rect)
    
    def draw_event_log(self, screen):
        """Draw the event log showing recent game events
        
        Args:
            screen: The pygame screen to draw on
        """
        # Draw event log background
        log_width = 280  # Slightly wider log
        log_height = self.screen_height - 160  # Almost full height, leaving space for buttons at bottom
        
        # Position log on the far left side of the screen
        log_rect = pygame.Rect(10, 80, log_width, log_height)
        log_surface = pygame.Surface((log_rect.width, log_rect.height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Add a border to make it stand out
        pygame.draw.rect(log_surface, (100, 100, 100, 200), log_surface.get_rect(), 2)
        
        # Draw title
        title_text = "Event Log"
        title_surface = self.fonts["medium"].render(title_text, True, (200, 200, 200))
        log_surface.blit(title_surface, (log_rect.width // 2 - title_surface.get_width() // 2, 5))
        
        # Draw events
        y_offset = 40  # Start below the title
        for event in self.displayed_events:
            event_text = event["text"]
            event_color = event["color"]
            
            # Wrap text if it's too long
            words = event_text.split(' ')
            lines = []
            line = ""
            for word in words:
                test_line = line + word + " "
                # If line would be too long with the new word, start a new line
                if self.fonts["small"].size(test_line)[0] > log_rect.width - 20:
                    lines.append(line)
                    line = word + " "
                else:
                    line = test_line
            if line:
                lines.append(line)
            
            # Draw each line of the event
            for line in lines:
                text_surface = self.fonts["small"].render(line, True, event_color)
                log_surface.blit(text_surface, (10, y_offset))
                y_offset += 20
            
            # Add spacing between events
            y_offset += 5
            
            # Draw a subtle separator line between events
            pygame.draw.line(log_surface, (100, 100, 100, 100), 
                          (20, y_offset - 3), (log_rect.width - 20, y_offset - 3), 1)
            
            # Don't draw more events than will fit
            if y_offset > log_rect.height - 30:
                break
                
        # Blit log to screen
        screen.blit(log_surface, log_rect)
        
    def draw_message(self, screen):
        """Draw an important message on screen
        
        Args:
            screen: The pygame screen to draw on
        """
        # Check if message has expired
        if time.time() - self.message_time > self.message_duration:
            self.message = None
            return
            
        # Draw message background
        message_width = 400
        message_height = 100
        message_rect = pygame.Rect(
            self.screen_width // 2 - message_width // 2,
            self.screen_height // 2 - message_height // 2,
            message_width,
            message_height
        )
        
        message_surface = pygame.Surface((message_width, message_height), pygame.SRCALPHA)
        message_surface.fill(self.colors["message_bg"])
        
        # Draw message title
        if "title" in self.message:
            title_surface = self.fonts["large"].render(self.message["title"], True, self.message["color"])
            title_rect = title_surface.get_rect(centerx=message_width // 2, top=10)
            message_surface.blit(title_surface, title_rect)
            
        # Draw message text
        text_surface = self.fonts["medium"].render(self.message["text"], True, self.colors["text"])
        text_rect = text_surface.get_rect(centerx=message_width // 2, centery=message_height // 2 + 10)
        message_surface.blit(text_surface, text_rect)
        
        # Blit message to screen
        screen.blit(message_surface, message_rect)
        
    def show_message(self, title, text, duration=3.0, color=(255, 255, 255)):
        """Show an important message
        
        Args:
            title: The message title
            text: The message text
            duration: How long to display the message (seconds)
            color: The color for the title
        """
        self.message = {
            "title": title,
            "text": text,
            "color": color
        }
        self.message_time = time.time()
        self.message_duration = duration
        
    def add_event(self, text, color=(255, 255, 255)):
        """Add an event to the event log
        
        Args:
            text: The event text to display
            color: The color for the event text
        """
        self.displayed_events.insert(0, {
            "text": text,
            "color": color,
            "time": time.time()
        })
        
        # Keep only the most recent events
        while len(self.displayed_events) > self.max_displayed_events:
            self.displayed_events.pop()
    
    def handle_click(self, pos):
        """Handle mouse click on UI elements
        
        Args:
            pos: The mouse position that was clicked
            
        Returns:
            str or None: The action to perform, or None if no button was clicked
        """
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
                
        return None 
    
    def add_block_visualization(self, blocker, target, result, blocker_roll, defender_roll):
        """Add a block visualization to be displayed
        
        Args:
            blocker: The goblin doing the blocking
            target: The goblin being blocked
            result: The result of the block
            blocker_roll: The roll value of the blocker
            defender_roll: The roll value of the defender
        """
        # Add to block visualizations for the arrow
        self.block_visualizations.append({
            "blocker": blocker,
            "target": target,
            "result": result,
            "blocker_roll": blocker_roll,
            "defender_roll": defender_roll,
            "time": time.time()
        })
        
        # Also add a persistent symbol at the target position
        # Choose color based on result
        if result == "knockdown":
            color = (255, 0, 0)  # Red for knockdown
            symbol_type = "knockdown"
        elif result == "push":
            color = (255, 165, 0)  # Orange for push
            symbol_type = "push"
        else:
            color = (255, 255, 0)  # Yellow for attempt
            symbol_type = "block"
            
        # Add a small offset to avoid overlapping with the goblin
        x_offset = self.cell_size // 2 - 5
        y_offset = -self.cell_size // 3
        
        # Add symbol to list of event symbols
        self.event_symbols.append({
            "type": symbol_type,
            "position": target.position,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "color": color,
            "time": time.time(),
            "details": {
                "blocker_name": blocker.name,
                "target_name": target.name,
                "result": result,
                "blocker_roll": blocker_roll,
                "defender_roll": defender_roll
            }
        })
        
    def add_duke_visualization(self, goblin, blockers, success, chance):
        """Add a DUKE visualization to be displayed
        
        Args:
            goblin: The goblin attempting to DUKE
            blockers: List of enemy goblins in zone of control
            success: Whether the DUKE was successful
            chance: The success chance of the DUKE
        """
        # Add to DUKE visualizations for the indicator circle
        self.duke_visualizations.append({
            "goblin": goblin,
            "blockers": blockers,
            "success": success,
            "chance": chance,
            "time": time.time()
        })
        
        # Also add a persistent symbol at the goblin's position
        # Choose color based on success
        color = (0, 200, 0) if success else (200, 0, 0)  # Green for success, red for failure
        
        # Add a small offset to avoid overlapping with the goblin
        x_offset = self.cell_size // 2
        y_offset = -self.cell_size // 3
        
        # Add symbol to list of event symbols
        self.event_symbols.append({
            "type": "duke",
            "position": goblin.position,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "color": color,
            "time": time.time(),
            "details": {
                "goblin_name": goblin.name,
                "blockers": blockers,
                "success": success,
                "chance": chance,
                "blocker_count": len(blockers)
            }
        })
        
    def draw_block_visualizations(self, screen):
        """Draw all active block visualizations
        
        Args:
            screen: The pygame screen to draw on
        """
        # Make sure we have the cell_size attribute
        if not hasattr(self, 'cell_size'):
            logger.warning("UI Renderer missing cell_size attribute")
            return
            
        # Calculate grid offsets for drawing arrows
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Draw each active block visualization
        current_time = time.time()
        active_blocks = []
        
        for block in self.block_visualizations:
            # Check if the block visualization has expired
            if current_time - block["time"] > self.block_viz_duration:
                continue
                
            active_blocks.append(block)
            
            blocker = block["blocker"]
            target = block["target"]
            result = block["result"]
            blocker_roll = block["blocker_roll"]
            defender_roll = block["defender_roll"]
            
            # Get screen positions
            blocker_x = offset_x + blocker.position[0] * self.cell_size + self.cell_size // 2
            blocker_y = offset_y + blocker.position[1] * self.cell_size + self.cell_size // 2
            target_x = offset_x + target.position[0] * self.cell_size + self.cell_size // 2
            target_y = offset_y + target.position[1] * self.cell_size + self.cell_size // 2
            
            # Choose color based on result
            if result == "knockdown":
                color = (255, 0, 0)  # Red for knockdown
            elif result == "push":
                color = (255, 165, 0)  # Orange for push
            else:
                color = (255, 255, 0)  # Yellow for attempt
            
            # Calculate the age of the visualization
            age = current_time - block["time"]
            
            # Make the arrow more prominent for newer blocks
            if age < 1.0:
                # Draw a thicker, more opaque arrow for new blocks
                arrow_width = 5
                
                # Draw a glowing effect around the arrow
                glow_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
                for glow_width in range(10, 2, -2):
                    # Fade the glow as it gets wider
                    glow_opacity = int(200 * (1 - glow_width / 10))
                    glow_color = (*color, glow_opacity)
                    self.draw_arrow(glow_surface, 
                                  (blocker_x - offset_x, blocker_y - offset_y), 
                                  (target_x - offset_x, target_y - offset_y), 
                                  glow_color, 
                                  glow_width)
                
                # Blit the glow to the screen
                screen.blit(glow_surface, (offset_x, offset_y))
            else:
                # Regular arrow for older blocks
                arrow_width = 3
            
            # Draw the main arrow
            self.draw_arrow(screen, (blocker_x, blocker_y), (target_x, target_y), color, arrow_width)
            
            # Draw result text
            midpoint_x = (blocker_x + target_x) // 2
            midpoint_y = (blocker_y + target_y) // 2 - 20
            
            # Draw rolls
            roll_text = f"{blocker_roll} vs {defender_roll}"
            roll_surface = self.fonts["small"].render(roll_text, True, (255, 255, 255))
            roll_rect = roll_surface.get_rect(center=(midpoint_x, midpoint_y))
            
            # Draw background for text
            background_rect = roll_rect.inflate(10, 5)
            background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            background_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(background_surface, background_rect)
            
            # Draw the text
            screen.blit(roll_surface, roll_rect)
            
            # Draw result
            result_text = result.upper()
            result_surface = self.fonts["small"].render(result_text, True, color)
            result_rect = result_surface.get_rect(center=(midpoint_x, midpoint_y + 15))
            
            # Draw background for result text
            result_bg_rect = result_rect.inflate(10, 5)
            result_bg_surface = pygame.Surface((result_bg_rect.width, result_bg_rect.height), pygame.SRCALPHA)
            result_bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(result_bg_surface, result_bg_rect)
            
            # Draw the result text
            screen.blit(result_surface, result_rect)
            
        # Replace the list with only active visualizations
        self.block_visualizations = active_blocks
        
    def draw_duke_visualizations(self, screen):
        """Draw all active DUKE visualizations
        
        Args:
            screen: The pygame screen to draw on
        """
        # Make sure we have the cell_size attribute
        if not hasattr(self, 'cell_size'):
            logger.warning("UI Renderer missing cell_size attribute")
            return
            
        # Calculate grid offsets for drawing
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Draw each active DUKE visualization
        current_time = time.time()
        active_dukes = []
        
        for duke in self.duke_visualizations:
            # Check if the DUKE visualization has expired
            if current_time - duke["time"] > self.duke_viz_duration:
                continue
                
            active_dukes.append(duke)
            
            goblin = duke["goblin"]
            blockers = duke["blockers"]
            success = duke["success"]
            chance = duke["chance"]
            
            # Get goblin screen position
            goblin_x = offset_x + goblin.position[0] * self.cell_size + self.cell_size // 2
            goblin_y = offset_y + goblin.position[1] * self.cell_size + self.cell_size // 2
            
            # Draw a circle around the goblin
            color = (0, 255, 0) if success else (255, 0, 0)  # Green for success, red for failure
            pygame.draw.circle(screen, color, (goblin_x, goblin_y), self.cell_size // 2 + 5, 2)
            
            # Draw lines to all blockers
            for blocker in blockers:
                blocker_x = offset_x + blocker.position[0] * self.cell_size + self.cell_size // 2
                blocker_y = offset_y + blocker.position[1] * self.cell_size + self.cell_size // 2
                
                # Draw dashed line
                self.draw_dashed_line(screen, (goblin_x, goblin_y), (blocker_x, blocker_y), color, 2)
            
            # Draw DUKE text with success chance
            duke_text = f"DUKE: {'SUCCESS' if success else 'FAIL'} ({int(chance*100)}%)"
            duke_surface = self.fonts["small"].render(duke_text, True, color)
            duke_rect = duke_surface.get_rect(center=(goblin_x, goblin_y - 25))
            
            # Draw background for text
            background_rect = duke_rect.inflate(10, 5)
            background_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            background_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(background_surface, background_rect)
            
            # Draw the text
            screen.blit(duke_surface, duke_rect)
            
        # Replace the list with only active visualizations
        self.duke_visualizations = active_dukes
        
    def draw_arrow(self, screen, start, end, color, width=1):
        """Draw an arrow from start to end
        
        Args:
            screen: The pygame screen to draw on
            start: The start position (x, y)
            end: The end position (x, y)
            color: The color of the arrow
            width: The width of the arrow line
        """
        # Draw the line
        pygame.draw.line(screen, color, start, end, width)
        
        # Calculate arrowhead
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        arrow_size = 10
        
        # Calculate arrowhead points
        point1 = (
            end[0] - arrow_size * math.cos(angle - math.pi/6),
            end[1] - arrow_size * math.sin(angle - math.pi/6)
        )
        point2 = (
            end[0] - arrow_size * math.cos(angle + math.pi/6),
            end[1] - arrow_size * math.sin(angle + math.pi/6)
        )
        
        # Draw arrowhead
        pygame.draw.polygon(screen, color, [end, point1, point2])
        
    def draw_dashed_line(self, screen, start, end, color, width=1):
        """Draw a dashed line from start to end
        
        Args:
            screen: The pygame screen to draw on
            start: The start position (x, y)
            end: The end position (x, y)
            color: The color of the line
            width: The width of the line
        """
        # Calculate line length and angle
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        # Calculate normalized direction vector
        if length > 0:
            dx /= length
            dy /= length
        
        # Draw dashed segments
        dash_length = 5
        gap_length = 3
        i = 0
        
        while i < length:
            # Calculate segment start point
            p1 = (
                start[0] + i * dx,
                start[1] + i * dy
            )
            
            # Calculate segment end point
            i += dash_length
            if i > length:
                i = length
                
            p2 = (
                start[0] + i * dx,
                start[1] + i * dy
            )
            
            # Draw the segment
            pygame.draw.line(screen, color, p1, p2, width)
            
            # Skip the gap
            i += gap_length
        
    def draw_event_symbols(self, screen):
        """Draw persistent symbols for game events
        
        Args:
            screen: The pygame screen to draw on
        """
        # Calculate grid offsets
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Remove expired symbols
        current_time = time.time()
        active_symbols = []
        
        for symbol in self.event_symbols:
            if current_time - symbol["time"] <= self.event_symbol_duration:
                active_symbols.append(symbol)
                
                # Draw the symbol
                position = symbol["position"]
                x_offset = symbol["x_offset"]
                y_offset = symbol["y_offset"]
                
                # Calculate screen position
                screen_x = offset_x + position[0] * self.cell_size + x_offset
                screen_y = offset_y + position[1] * self.cell_size + y_offset
                
                # Draw circle background
                pygame.draw.circle(screen, symbol["color"], (screen_x, screen_y), 10)
                
                # Draw letter
                letter = symbol["type"][0].upper()  # First letter of event type (B for Block, D for Duke, etc.)
                letter_text = self.fonts["symbol"].render(letter, True, (255, 255, 255))
                letter_rect = letter_text.get_rect(center=(screen_x, screen_y))
                screen.blit(letter_text, letter_rect)
        
        # Update the list
        self.event_symbols = active_symbols
        
    def update_hover_state(self, screen, hover_pos):
        """Update which goblin or symbol is being hovered over
        
        Args:
            screen: The pygame screen to draw on
            hover_pos: The current mouse position
        """
        # Calculate grid offsets
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Check if hovering over a goblin
        self.hovered_goblin = None
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                if goblin.out_of_game:
                    continue
                
                # Get goblin screen position
                goblin_x = offset_x + goblin.position[0] * self.cell_size + self.cell_size // 2
                goblin_y = offset_y + goblin.position[1] * self.cell_size + self.cell_size // 2
                
                # Check if mouse is within goblin radius
                radius = self.cell_size // 3
                distance = math.sqrt((hover_pos[0] - goblin_x) ** 2 + (hover_pos[1] - goblin_y) ** 2)
                
                if distance <= radius:
                    self.hovered_goblin = goblin
                    break
        
        # Check if hovering over an event symbol
        self.hovered_symbol = None
        for symbol in self.event_symbols:
            # Calculate symbol position
            symbol_x = offset_x + symbol["position"][0] * self.cell_size + symbol["x_offset"]
            symbol_y = offset_y + symbol["position"][1] * self.cell_size + symbol["y_offset"]
            
            # Define symbol hit area (20x20 pixels)
            symbol_rect = pygame.Rect(symbol_x - 10, symbol_y - 10, 20, 20)
            
            if symbol_rect.collidepoint(hover_pos):
                self.hovered_symbol = symbol
                break
                
        # Update flash timer for animations - slowed down by factor of 4
        self.flash_timer = (self.flash_timer + 0.025) % 1.0  # Oscillates between 0 and 1, 4x slower
            
    def draw_hover_info(self, screen, hover_pos):
        """Draw information popup for hovered goblin or event symbol
        
        Args:
            screen: The pygame screen to draw on
            hover_pos: The current mouse position
        """
        # Calculate grid offsets
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # If hovering over a goblin
        if self.hovered_goblin:
            goblin = self.hovered_goblin
            
            # Highlight movement trail by making it flash
            trail = self.game.get_movement_trail(goblin)
            if trail and len(trail) >= 2:
                # Flash only if we're in the bright half of the cycle
                if self.flash_timer > 0.5:
                    # Draw a highlighted version of the trail
                    trail_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
                    
                    # Choose trail color based on team but brighter for flashing
                    if goblin.team == self.game.team1:
                        flash_color = (255, 100, 100, 255)  # Bright red
                    else:
                        flash_color = (100, 100, 255, 255)  # Bright blue
                    
                    # Draw the trail with thicker lines
                    for i in range(len(trail) - 1):
                        start_x, start_y = trail[i]
                        end_x, end_y = trail[i + 1]
                        
                        # Convert to screen coordinates
                        start_screen_x = start_x * self.cell_size + self.cell_size // 2
                        start_screen_y = start_y * self.cell_size + self.cell_size // 2
                        end_screen_x = end_x * self.cell_size + self.cell_size // 2
                        end_screen_y = end_y * self.cell_size + self.cell_size // 2
                        
                        # Draw thicker line
                        pygame.draw.line(trail_surface, flash_color, 
                                      (start_screen_x, start_screen_y), 
                                      (end_screen_x, end_screen_y), 5)
                        
                        # Draw larger circles at endpoints
                        pygame.draw.circle(trail_surface, flash_color, 
                                        (start_screen_x, start_screen_y), 8)
                    
                    # Draw final point
                    last_x, last_y = trail[-1]
                    last_screen_x = last_x * self.cell_size + self.cell_size // 2
                    last_screen_y = last_y * self.cell_size + self.cell_size // 2
                    pygame.draw.circle(trail_surface, flash_color, (last_screen_x, last_screen_y), 10)
                    
                    # Blit the trail surface
                    screen.blit(trail_surface, (offset_x, offset_y))
            
            # Look for any duke attempts by this goblin
            duke_attempts = []
            for duke in self.duke_visualizations:
                if duke["goblin"] == goblin:
                    duke_attempts.append(duke)
            
            # Create info popup
            popup_width = 250
            popup_height = 200 if duke_attempts else 150  # Larger popup if we have duke attempts
            popup_x = min(hover_pos[0] + 10, self.screen_width - popup_width - 10)
            popup_y = min(hover_pos[1] + 10, self.screen_height - popup_height - 10)
            
            # Create popup surface
            popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
            popup.fill(self.colors["info_bg"])
            
            # Draw goblin name
            name_text = self.fonts["medium"].render(goblin.name, True, self.colors["text"])
            popup.blit(name_text, (10, 10))
            
            # Draw team name and color
            team_name = goblin.team.name
            team_color = self.colors["team1"] if goblin.team == self.game.team1 else self.colors["team2"]
            team_text = self.fonts["small"].render(team_name, True, team_color)
            popup.blit(team_text, (10, 35))
            
            # Draw detailed stats
            stats = [
                f"Strength: {goblin.strength}",
                f"Toughness: {goblin.toughness}",
                f"Movement: {goblin.movement}/{goblin.max_movement}",
                f"Status: {'Knocked Down' if goblin.knocked_down else 'Active'}",
                f"Has Ball: {'Yes' if goblin.has_ball else 'No'}"
            ]
            
            y_offset = 60
            for stat in stats:
                stat_text = self.fonts["small"].render(stat, True, self.colors["text"])
                popup.blit(stat_text, (10, y_offset))
                y_offset += 15
            
            # If there are any duke attempts, show them
            if duke_attempts:
                y_offset += 10
                duke_title = self.fonts["medium"].render("Recent DUKE Attempts:", True, (200, 200, 200))
                popup.blit(duke_title, (10, y_offset))
                y_offset += 25
                
                for duke in duke_attempts:
                    success = duke["success"]
                    chance = duke["chance"]
                    duke_color = (0, 200, 0) if success else (200, 0, 0)
                    
                    duke_result = f"{'SUCCESS' if success else 'FAILURE'} - {int(chance*100)}% chance"
                    duke_text = self.fonts["small"].render(duke_result, True, duke_color)
                    popup.blit(duke_text, (15, y_offset))
                    y_offset += 15
                
                    # If it failed, also show how many blockers
                    if not success:
                        blockers_text = f"Blockers: {len(duke['blockers'])}"
                        blockers_surface = self.fonts["small"].render(blockers_text, True, self.colors["text"])
                        popup.blit(blockers_surface, (15, y_offset))
                        y_offset += 15
            
            # Blit popup to screen
            screen.blit(popup, (popup_x, popup_y))
            
            # Also highlight any duke symbols associated with this goblin
            for symbol in self.event_symbols:
                if symbol["type"] == "duke" and "goblin_name" in symbol["details"]:
                    if symbol["details"]["goblin_name"] == goblin.name:
                        # Calculate symbol position
                        symbol_x = offset_x + symbol["position"][0] * self.cell_size + symbol["x_offset"]
                        symbol_y = offset_y + symbol["position"][1] * self.cell_size + symbol["y_offset"]
                        
                        # Draw a highlighted circle around the duke symbol
                        highlight_color = (255, 255, 100, 180)
                        pygame.draw.circle(screen, highlight_color, (symbol_x, symbol_y), 15, 3)
        
        # If hovering over an event symbol
        elif self.hovered_symbol:
            symbol = self.hovered_symbol
            
            # Create info popup
            popup_width = 280
            popup_height = 180
            popup_x = min(hover_pos[0] + 10, self.screen_width - popup_width - 10)
            popup_y = min(hover_pos[1] + 10, self.screen_height - popup_height - 10)
            
            # Create popup surface
            popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
            popup.fill(self.colors["info_bg"])
            
            # Draw event type
            event_type = symbol["type"].upper()
            type_text = self.fonts["medium"].render(event_type, True, symbol["color"])
            popup.blit(type_text, (10, 10))
            
            # Draw event details
            details = symbol["details"]
            lines = []
            
            if symbol["type"] == "block" or symbol["type"] == "knockdown" or symbol["type"] == "push":
                lines = [
                    f"Blocker: {details['blocker_name']}",
                    f"Target: {details['target_name']}",
                    f"Result: {details['result'].upper()}",
                    f"Roll: {details['blocker_roll']} vs {details['defender_roll']}"
                ]
                
                # Add explanation of roll
                if 'blocker_roll' in details and 'defender_roll' in details:
                    blocker_roll = details['blocker_roll']
                    defender_roll = details['defender_roll']
                    if blocker_roll > defender_roll:
                        margin = blocker_roll - defender_roll
                        lines.append(f"Blocker won by {margin}")
                        if margin >= 2:
                            lines.append("Margin of 2+ causes knockdown")
                        else:
                            lines.append("Margin of 1 causes push")
                    else:
                        lines.append("Defender stopped the block")
                
            elif symbol["type"] == "duke":
                success = details["success"] if "success" in details else False
                result_text = "SUCCESS" if success else "FAILURE"
                chance_text = f"{int(details['chance']*100)}%" if "chance" in details else "??"
                
                lines = [
                    f"Goblin: {details['goblin_name'] if 'goblin_name' in details else 'Unknown'}",
                    f"Result: {result_text}",
                    f"Success Chance: {chance_text}"
                ]
                
                # Add more details about the DUKE mechanic
                lines.append("")
                lines.append("DUKE roll checks if a goblin can")
                lines.append("escape from adjacent enemy goblins.")
                
                if "blocker_count" in details:
                    lines.append(f"Blockers: {details['blocker_count']}")
                    lines.append(f"Each blocker reduces success chance")
            
            y_offset = 40
            for line in lines:
                line_text = self.fonts["small"].render(line, True, self.colors["text"])
                popup.blit(line_text, (10, y_offset))
                y_offset += 20
            
            # Blit popup to screen
            screen.blit(popup, (popup_x, popup_y))
            
            # Highlight the symbol
            symbol_pos = symbol["position"]
            symbol_x = offset_x + symbol_pos[0] * self.cell_size + symbol["x_offset"]
            symbol_y = offset_y + symbol_pos[1] * self.cell_size + symbol["y_offset"]
            
            # Make it pulse/grow larger when hovered
            pulse_size = 12 + int(3 * math.sin(time.time() * 4))  # Pulsing effect
            pygame.draw.circle(screen, (255, 255, 255, 150), (symbol_x, symbol_y), pulse_size, 2)
    