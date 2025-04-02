import uuid
from config import CONFIG
from goblin import Goblin

class Team:
    def __init__(self, name, color):
        # Identity
        self.name = name
        self.id = str(uuid.uuid4())
        self.color = color
        
        # Goblins
        self.goblins = []
        
        # Game state
        self.score = 0
        self.is_offense = False
        self.current_formation = None
        
        # Carrier rotation tracking
        self.carrier_rotation_counter = 0
        self.carrier_history = []  # Track order of carriers
        
        # Statistics - preserved between games
        self.stats = {
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "points_for": 0,
            "points_against": 0,
            "touchdowns": 0,
            "field_goals": 0,
            "injuries_caused": 0,
            "injuries_suffered": 0,
            "games_played": 0,
            "season_points": 0
        }
        
    def add_goblin(self, goblin):
        """Add a goblin to the team"""
        self.goblins.append(goblin)
        goblin.team = self
        
    def create_team(self, num_goblins=5):
        """Create a team with the specified number of goblins"""
        for _ in range(num_goblins):
            goblin = Goblin()
            self.add_goblin(goblin)
        
    def get_carrier(self):
        """Get the current ball carrier"""
        for goblin in self.goblins:
            if goblin.has_ball:
                return goblin
        return None
        
    def select_next_carrier(self):
        """Select the next goblin to be carrier based on rotation"""
        # Reset current carrier
        current_carrier = self.get_carrier()
        if current_carrier:
            current_carrier.has_ball = False
            
        # Find eligible goblins (not unavailable)
        eligible_goblins = [g for g in self.goblins if not g.unavailable]
        if not eligible_goblins:
            return False  # No eligible carriers
            
        # Sort by when they were last carrier (oldest first)
        eligible_goblins.sort(key=lambda g: g.last_carrier_turn if g.last_carrier_turn is not None else -1)
        
        # Select next carrier
        next_carrier = eligible_goblins[0]
        next_carrier.has_ball = True
        next_carrier.last_carrier_turn = self.carrier_rotation_counter
        self.carrier_rotation_counter += 1
        self.carrier_history.append(next_carrier.id)
        
        return True
        
    def reset_for_new_game(self):
        """Reset the team for a new game"""
        self.score = 0
        self.is_offense = False
        self.current_formation = None
        self.carrier_rotation_counter = 0
        self.carrier_history = []
        
        # Reset goblins
        for goblin in self.goblins:
            goblin.has_ball = False
            goblin.knocked_down = False
            goblin.momentum = 0
            goblin.movement = goblin.max_movement
            goblin.out_of_game = False
            goblin.misses_plays = 0
            goblin.unavailable = False
            
            # Check for injuries from previous game
            if goblin.season_injury:
                # Still injured for the season
                goblin.out_of_game = True
                goblin.unavailable = True
                
            if goblin.next_game_penalty:
                # Was injured last game, apply penalty
                penalty = CONFIG.get("minor_injury_game_penalty", 1)
                goblin.movement = max(1, goblin.movement - penalty)
                goblin.next_game_penalty = False
                
    def update_stats(self, opponent_score):
        """Update team stats after a game"""
        self.stats["games_played"] += 1
        self.stats["points_for"] += self.score
        self.stats["points_against"] += opponent_score
        
        # Update win/loss/tie record
        if self.score > opponent_score:
            self.stats["wins"] += 1
            self.stats["season_points"] += 3  # 3 points for a win
        elif self.score < opponent_score:
            self.stats["losses"] += 1
        else:
            self.stats["ties"] += 1
            self.stats["season_points"] += 1  # 1 point for a tie
            
    def to_dict(self):
        """Convert team to dictionary for saving/loading"""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "score": self.score,
            "is_offense": self.is_offense,
            "current_formation": self.current_formation,
            "carrier_rotation_counter": self.carrier_rotation_counter,
            "carrier_history": self.carrier_history,
            "stats": self.stats,
            "goblin_ids": [g.id for g in self.goblins]
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create team from dictionary"""
        team = cls(data["name"], data["color"])
        
        team.id = data["id"]
        team.score = data["score"]
        team.is_offense = data["is_offense"]
        team.current_formation = data["current_formation"]
        team.carrier_rotation_counter = data["carrier_rotation_counter"]
        team.carrier_history = data["carrier_history"]
        team.stats = data["stats"]
        
        # Note: goblins need to be added separately
        return team 