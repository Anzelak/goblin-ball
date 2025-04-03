import pygame
from config import CONFIG
import time
from grid_renderer import GridRenderer
from goblin_renderer import GoblinRenderer
from ui_renderer import UIRenderer
from animation_renderer import AnimationRenderer

class GameRenderer:
    def __init__(self, game, screen_width=1024, screen_height=768):
        """Initialize the Pygame renderer for displaying the game"""
        pygame.init()
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Goblinball")
        
        # Calculate grid cell size
        # Use a different calculation now that we have a rectangular window
        # allowing more space for the event log on the left
        self.cell_size = min((screen_width - 300) // game.grid_size, (screen_height - 150) // game.grid_size)
        
        # Create specialized renderers
        self.grid_renderer = GridRenderer(game, self.cell_size)
        self.goblin_renderer = GoblinRenderer(game, self.cell_size)
        self.ui_renderer = UIRenderer(game, screen_width, screen_height)
        self.animation_renderer = AnimationRenderer(game, self.cell_size)
        
        # Animation state
        self.animation_speed = CONFIG.get("animation_speed", 1.0)
        self.paused = True
        
        # Debug state
        self.show_debug = CONFIG.get("show_debug_info", False)
        self.selected_goblin = None
        
        # Listen for events
        game.event_manager.add_listener("touchdown", self.handle_game_event)
        game.event_manager.add_listener("field_goal", self.handle_game_event)
        game.event_manager.add_listener("block", self.handle_game_event)
        game.event_manager.add_listener("knockdown", self.handle_game_event)
        game.event_manager.add_listener("push", self.handle_game_event)
        game.event_manager.add_listener("play_start", self.handle_game_event)
        game.event_manager.add_listener("play_end", self.handle_game_event)
        game.event_manager.add_listener("game_end", self.handle_game_event)
        game.event_manager.add_listener("block_attempt", self.handle_game_event)
        game.event_manager.add_listener("injury", self.handle_game_event)
        game.event_manager.add_listener("ball_pickup", self.handle_game_event)
        game.event_manager.add_listener("ball_pickup_failed", self.handle_game_event)
        game.event_manager.add_listener("ball_dropped", self.handle_game_event)
        game.event_manager.add_listener("duke_check", self.handle_game_event)
        
    def draw(self):
        """Draw the game state to the screen"""
        # Clear screen
        self.screen.fill((20, 100, 20))  # Field green background
        
        # Calculate offsets for centering the grid in the right portion of the screen
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        
        # Adjust offset to account for the event log on the left (300px reserved space)
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        # Draw grid
        self.grid_renderer.draw(self.screen, offset_x, offset_y)
        
        # Draw goblins
        self.goblin_renderer.draw(self.screen, offset_x, offset_y, self.selected_goblin)
        
        # Draw current animation from animation manager
        if self.game.animation_manager and self.game.animation_manager.active_animation:
            self.animation_renderer.draw(self.screen, self.game.animation_manager, offset_x, offset_y)
        
        # Draw UI elements
        mouse_pos = pygame.mouse.get_pos() if pygame.get_init() else None
        self.ui_renderer.draw(self.screen, mouse_pos)
        
        # Draw debug info if enabled
        if self.show_debug:
            self.draw_debug_info()
        
        # Update display
        pygame.display.flip()
        
    def draw_debug_info(self):
        """Draw debug information"""
        debug_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Display game state information
        lines = [
            f"Turn: {self.game.turn}",
            f"Play: {self.game.current_play}/{self.game.max_plays}",
            f"Offense: {self.game.offense_team.name}",
            f"Defense: {self.game.defense_team.name}",
            f"Ball Carrier: {self.game.get_ball_carrier().name if self.game.get_ball_carrier() else 'None'}",
            f"Animation Speed: {self.animation_speed:.1f}x"
        ]
        
        # Display selected goblin info if any
        if self.selected_goblin:
            g = self.selected_goblin
            lines.extend([
                "---",
                f"Selected: {g.name}",
                f"Team: {g.team.name}",
                f"Pos: {g.position}",
                f"Stats: S{g.strength} T{g.toughness} M{g.movement}",
                f"MP Left: {g.movement_points}",
                f"Knocked Down: {g.knocked_down}",
                f"Has Ball: {g.has_ball}"
            ])
            
            # Add AI info if available
            if hasattr(g, "current_goal"):
                lines.append(f"Goal: {g.current_goal}")
            
        y = 10
        for line in lines:
            text = pygame.font.SysFont(None, 16).render(line, True, (255, 255, 255))
            debug_surface.blit(text, (self.screen_width - 200, y))
            y += 20
            
        self.screen.blit(debug_surface, (0, 0))
        
    def handle_game_event(self, event):
        """Process a game event"""
        # Add event to UI event log with appropriate color
        text = self.format_event_message(event)
        color = self.get_event_color(event)
        self.ui_renderer.add_event(text, color)
        
        # Show important messages as overlays
        if event.event_type == "touchdown":
            scorer = event.data.get("goblin")
            if scorer and hasattr(scorer, 'team'):
                team = scorer.team
                self.ui_renderer.show_message(
                    "TOUCHDOWN!", 
                    f"{team.name} scores! {scorer.name} made the touchdown!",
                    duration=5.0,
                    color=(255, 215, 0)
                )
            else:
                # Handle case where goblin reference is missing
                team_name = event.data.get("team_name", "A team")
                carrier_name = event.data.get("carrier_name", "Someone")
                self.ui_renderer.show_message(
                    "TOUCHDOWN!", 
                    f"{team_name} scores! {carrier_name} made the touchdown!",
                    duration=5.0,
                    color=(255, 215, 0)
                )
            
        elif event.event_type == "field_goal":
            scorer = event.data.get("goblin")
            if scorer and hasattr(scorer, 'team'):
                team = scorer.team
                self.ui_renderer.show_message(
                    "FIELD GOAL!", 
                    f"{team.name} scores! {scorer.name} made the field goal!",
                    duration=5.0,
                    color=(255, 215, 0)
                )
            else:
                # Handle case where goblin reference is missing
                team_name = event.data.get("team_name", "A team")
                carrier_name = event.data.get("carrier_name", "Someone")
                self.ui_renderer.show_message(
                    "FIELD GOAL!", 
                    f"{team_name} scores! {carrier_name} made the field goal!",
                    duration=5.0,
                    color=(255, 215, 0)
                )
            
        elif event.event_type == "game_end":
            winner = event.data.get("winner")
            if winner:
                self.ui_renderer.show_message(
                    "GAME OVER!", 
                    f"{winner.name} wins the game!",
                    duration=10.0,
                    color=(255, 215, 0)
                )
            else:
                winner_name = event.data.get("winner_name", "A team")
                self.ui_renderer.show_message(
                    "GAME OVER!", 
                    f"{winner_name} wins the game!",
                    duration=10.0,
                    color=(255, 215, 0)
                )
            
        elif event.event_type == "injury":
            goblin = event.data.get("goblin")
            if goblin:
                self.ui_renderer.show_message(
                    "INJURY!", 
                    f"{goblin.name} is injured and out of the game!",
                    duration=3.0,
                    color=(200, 0, 0)
                )
            else:
                goblin_name = event.data.get("goblin_name", "A goblin")
                self.ui_renderer.show_message(
                    "INJURY!", 
                    f"{goblin_name} is injured and out of the game!",
                    duration=3.0,
                    color=(200, 0, 0)
                )
    
    def format_event_message(self, event):
        """Format a game event into a displayable message"""
        data = event.data
        
        if event.event_type == "touchdown":
            goblin = data.get("goblin")
            return f"TOUCHDOWN by {goblin.name if goblin else 'unknown'}!"
            
        elif event.event_type == "field_goal":
            goblin = data.get("goblin")
            return f"FIELD GOAL by {goblin.name if goblin else 'unknown'}!"
            
        elif event.event_type == "block":
            blocker = data.get("blocker")
            target = data.get("target")
            if blocker and target:
                return f"{blocker.name} blocks {target.name}!"
            elif blocker:
                return f"{blocker.name} attempts a block!"
            elif target:
                return f"Someone blocks {target.name}!"
            else:
                return "Block attempt!"
            
        elif event.event_type == "knockdown":
            goblin = data.get("goblin")
            if goblin:
                return f"{goblin.name} is knocked down!"
            else:
                return "A goblin is knocked down!"
            
        elif event.event_type == "push":
            pusher = data.get("pusher")
            target = data.get("target")
            if pusher and target:
                return f"{pusher.name} pushes {target.name}!"
            elif pusher:
                return f"{pusher.name} pushes someone!"
            elif target:
                return f"Someone pushes {target.name}!"
            else:
                return "Push attempt!"
            
        elif event.event_type == "play_start":
            offense = data.get("offense")
            return f"Play started! {offense.name} on offense."
            
        elif event.event_type == "play_end":
            return "Play ended!"
            
        elif event.event_type == "game_end":
            winner = data.get("winner")
            return f"Game over! {winner.name} wins!"
            
        elif event.event_type == "block_attempt":
            blocker = data.get("blocker")
            target = data.get("target")
            return f"{blocker.name} attempts to block {target.name}..."
            
        elif event.event_type == "injury":
            goblin = data.get("goblin")
            return f"{goblin.name} is injured!"
            
        elif event.event_type == "ball_pickup":
            goblin = data.get("goblin")
            return f"{goblin.name} picks up the ball!"
            
        elif event.event_type == "ball_pickup_failed":
            goblin = data.get("goblin")
            return f"{goblin.name} fails to pick up the ball!"
            
        elif event.event_type == "ball_dropped":
            goblin = data.get("goblin")
            return f"{goblin.name} drops the ball!"
            
        elif event.event_type == "duke_check":
            attacker = data.get("attacker")
            defender = data.get("defender")
            result = data.get("result", False)
            
            # Handle case where attacker or defender is None
            attacker_name = attacker.name if attacker else data.get("goblin_name", "Unknown")
            defender_name = defender.name if defender else data.get("blocker_name", "Unknown")
            
            return f"DUKE check: {attacker_name} vs {defender_name} - {'Success' if result else 'Fail'}"
            
        return f"{event.event_type}: {str(data)}"
    
    def get_event_color(self, event):
        """Get the appropriate color for an event type"""
        if event.event_type in ["touchdown", "field_goal"]:
            return (255, 215, 0)  # Gold
        elif event.event_type in ["block", "knockdown", "injury"]:
            return (200, 0, 0)  # Red
        elif event.event_type in ["ball_pickup", "ball_pickup_failed", "ball_dropped"]:
            return (200, 200, 0)  # Yellow
        elif event.event_type in ["play_start", "play_end", "game_end"]:
            return (0, 200, 200)  # Cyan
        else:
            return (255, 255, 255)  # White
    
    def next_turn(self):
        """Process the next turn"""
        self.game.next_turn()
        
    def toggle_auto_play(self):
        """Toggle automatic play mode"""
        self.paused = not self.paused
        
    def new_play(self):
        """Start a new play"""
        self.game.controller.start_play()
        
    def increase_speed(self):
        """Increase animation speed"""
        self.animation_speed = min(5.0, self.animation_speed + 0.5)
        
    def decrease_speed(self):
        """Decrease animation speed"""
        self.animation_speed = max(0.5, self.animation_speed - 0.5)
        
    def toggle_debug(self):
        """Toggle debug information display"""
        self.show_debug = not self.show_debug
        
    def handle_click(self, pos):
        """Handle mouse click on the game"""
        # Check UI elements first
        action = self.ui_renderer.handle_click(pos)
        if action:
            if action == "next_turn":
                self.next_turn()
            elif action == "prev_turn":
                self.game.previous_turn()  # Handle Previous Turn button
            elif action == "auto_play":
                self.toggle_auto_play()
            elif action == "new_play":
                self.new_play()
            elif action == "toggle_debug":
                self.toggle_debug()
            return
        
        # Calculate grid coordinates
        grid_width = self.game.grid_size * self.cell_size
        grid_height = self.game.grid_size * self.cell_size
        offset_x = (self.screen_width - 300 - grid_width) // 2 + 300
        offset_y = (self.screen_height - grid_height - 100) // 2
        
        if (pos[0] < offset_x or pos[0] >= offset_x + grid_width or 
            pos[1] < offset_y or pos[1] >= offset_y + grid_height):
            # Click outside grid
            self.selected_goblin = None
            return
            
        # Convert to grid coordinates
        grid_x = (pos[0] - offset_x) // self.cell_size
        grid_y = (pos[1] - offset_y) // self.cell_size
        
        # Find goblin at this position
        for team in [self.game.team1, self.game.team2]:
            for goblin in team.goblins:
                if not goblin.out_of_game and goblin.position == (grid_x, grid_y):
                    self.selected_goblin = goblin
                    return
                    
        # No goblin at this position
        self.selected_goblin = None
    
    def run(self):
        """Run the game loop"""
        running = True
        clock = pygame.time.Clock()
        fps = 60
        
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.next_turn()
                    elif event.key == pygame.K_a:
                        self.toggle_auto_play()
                    elif event.key == pygame.K_n:
                        self.new_play()
                    elif event.key == pygame.K_d:
                        self.toggle_debug()
            
            # Auto advance turns if enabled
            if not self.paused and self.game.auto_advance_turns():
                pass  # Turn was advanced
                
            # Update animations
            if self.game.animation_manager:
                self.game.animation_manager.update(1.0 / fps * self.animation_speed)
            
            # Draw the game
            self.draw()
            
            # Limit to 60 FPS
            clock.tick(fps)
        
        # Clean up
        pygame.quit() 