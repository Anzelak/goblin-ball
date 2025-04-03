import uuid
import random
import time
from config import CONFIG
from utils import weighted_choice, distance

def generate_goblin_name(names_file="names.txt"):
    """Generate a unique goblin name with prefix, suffix, surname, and optional title"""
    
    # 20 colorful goblin name prefixes
    prefixes = [
        "Grub", "Snot", "Grim", "Mug", "Stab", "Gut", "Lug", "Zog", "Skab", "Grak",  # Original 10
        "Blud", "Krak", "Glob", "Skriz", "Thrak", "Fizz", "Wort", "Krunk", "Splat", "Gnog"  # Added 10
    ]
    
    # 20 distinctive goblin name suffixes
    suffixes = [
        "nose", "gob", "basher", "smasher", "chomper", "biter", "face", "fist", "tooth", "foot",  # Original 10
        "skull", "mangler", "finger", "stomper", "chewer", "crusher", "slicer", "gulper", "stabber", "squisher"  # Added 10
    ]
    
    # List of potential titles
    titles = ["", "", "", "the Quick", "the Strong", "the Sly", "the Tough", "the Brutal", 
             "the Cunning", "the Mighty", "the Fierce", "the Sneaky"]
    
    # Generate first part of name
    first_name = random.choice(prefixes) + random.choice(suffixes)
    
    # Load a random surname from external file
    try:
        with open(names_file, 'r') as f:
            # Read all lines and split them into individual words
            all_names = []
            for line in f:
                # Split the line by spaces or tabs and add each non-empty word
                names_in_line = [name.strip() for name in line.split() if name.strip()]
                all_names.extend(names_in_line)
            
            if all_names:
                surname = random.choice(all_names)
            else:
                surname = ""  # Fallback if file is empty
    except FileNotFoundError:
        # Fallback if file doesn't exist
        surname = ""
        print(f"Warning: Names file '{names_file}' not found")
    
    # Decide whether to include title and surname
    include_title = random.random() < 0.25  # 25% chance of having a title
    include_surname = bool(surname) and random.random() < 0.4  # 40% chance of surname if available
    
    # Assemble the full name
    name = first_name
    
    if include_surname:
        name += f" {surname}"
        
    if include_title:
        name += f" {random.choice(titles)}"
        
    return name

class Goblin:
    def __init__(self, name=None, strength=None, toughness=None, movement=None):
        # Identity
        self.name = name or generate_goblin_name()
        self.id = str(uuid.uuid4())
        
        # Base stats - randomly generated if not provided
        self.strength = strength or random.randint(CONFIG.get("min_strength", 1), CONFIG.get("max_strength", 10))
        self.toughness = toughness or random.randint(CONFIG.get("min_toughness", 1), CONFIG.get("max_toughness", 10))
        self.movement = movement or random.randint(CONFIG.get("min_movement", 1), CONFIG.get("max_movement", 4))
        self.max_movement = self.movement  # To reset each turn
        
        # Current state
        self.position = (0, 0)  # (x, y) coordinates
        self.has_ball = False
        self.knocked_down = False
        self.momentum = 0
        
        # Carrier tracking
        self.last_carrier_turn = None  # When this goblin was last the carrier
        
        # Team reference
        self.team = None
        
        # Game status
        self.out_of_game = False
        self.season_injury = False
        self.next_game_penalty = False
        self.misses_plays = 0
        self.unavailable = False
        
        # Phase 3: Combat Stats
        self.block_skill = random.randint(0, 2)  # Bonus to blocking attempts
        self.dodge_skill = random.randint(0, 2)  # Bonus to dodging blocks
        self.injury_resistance = random.randint(0, 2)  # Bonus to injury rolls
        
        # Statistics - preserved between games for season tracking
        self.stats = {
            "blocks_attempted": 0,
            "blocks_successful": 0,
            "knockdowns_caused": 0,
            "touchdowns": 0,
            "field_goals": 0,
            "injuries": {"none": 0, "dazed": 0, "minor": 0, "serious": 0},
            "knocked_down_count": 0,
            "moves_made": 0,
            "successful_dukes": 0,
            "games_played": 0,
            "career_touchdowns": 0,
            "career_blocks": 0,
            "career_injuries_caused": 0,
            "career_injuries_suffered": 0,
            "times_blocked": 0,
            "injuries_caused": 0,
            "injuries_suffered": 0
        }
        
    def block(self, target):
        """Attempt to block another goblin
        Returns a dictionary with the result of the block"""
        # Update stats
        self.stats["blocks_attempted"] += 1
        target.stats["times_blocked"] += 1
        
        # Roll dice for both goblins
        blocker_roll = random.randint(1, 10)
        target_roll = random.randint(1, 10)
        
        # Apply skill bonuses
        blocker_total = blocker_roll + self.strength + self.block_skill
        target_total = target_roll + target.toughness + target.dodge_skill
        
        # Calculate margin of success/failure
        margin = blocker_total - target_total
        
        # Determine result
        result = "failure"  # Default result is failure
        
        if margin >= 5:
            # Strong success - knockdown with injury check
            result = "knockdown_with_injury"
            target.knocked_down = True
            self.stats["blocks_successful"] += 1
            self.perform_injury_check(target)
        elif margin > 0:
            # Regular success - knockdown
            result = "knockdown"
            target.knocked_down = True
            self.stats["blocks_successful"] += 1
        elif margin >= -2:
            # Partial success - push
            result = "push"
            self.stats["blocks_successful"] += 1
        else:
            # Failure
            result = "failure"
        
        # If blocking the ball carrier and successful, ball is dropped
        if target.has_ball and (result == "knockdown" or result == "knockdown_with_injury"):
            # Ball is dropped and carrier loses ball
            target.has_ball = False
            
            # TODO: Handle ball scatter logic
        
        return {
            "result": result,
            "margin": margin,
            "blocker_roll": blocker_roll,
            "target_roll": target_roll
        }
    
    def perform_injury_check(self, target):
        """Perform an injury check on the target when a block is very successful
        Returns the result of the injury check"""
        # Roll for injury
        injury_roll = random.randint(1, 10)
        
        # Apply toughness and injury resistance
        injury_threshold = 5 + target.toughness // 3 + target.injury_resistance
        
        # Determine result
        if injury_roll >= injury_threshold:
            # No injury
            return "no_injury"
        elif injury_roll >= 3:
            # Minor injury - miss next play
            target.misses_plays = 1
            target.stats["injuries_suffered"] += 1
            self.stats["injuries_caused"] += 1
            return "minor_injury"
        else:
            # Major injury - miss multiple plays
            target.misses_plays = random.randint(2, 3)
            target.stats["injuries_suffered"] += 1
            self.stats["injuries_caused"] += 1
            
            # Check for career-ending injury
            if injury_roll == 1 and random.random() < 0.2:
                target.out_of_game = True
                return "career_ending_injury"
            
            return "major_injury"
    
    def stand_up(self):
        """Stand up from being knocked down
        Returns True if successful, False otherwise"""
        if not self.knocked_down:
            return True  # Already standing
            
        # Standing up costs 2 movement points
        if self.movement >= 2:
            self.knocked_down = False
            self.movement -= 2
            return True
        
        return False
    
    def add_game_stats_to_career(self):
        """Move game stats to career stats at the end of a game"""
        self.stats["career_touchdowns"] += self.stats["touchdowns"]
        self.stats["career_blocks"] += self.stats["blocks_successful"]
        self.stats["career_injuries_caused"] += self.stats["injuries_caused"]
        self.stats["career_injuries_suffered"] += self.stats["injuries_suffered"]
        self.stats["games_played"] += 1
        
        # Reset game stats
        self.stats["blocks_attempted"] = 0
        self.stats["blocks_successful"] = 0
        self.stats["knockdowns_caused"] = 0
        self.stats["touchdowns"] = 0
        self.stats["field_goals"] = 0
        self.stats["injuries"] = {"none": 0, "dazed": 0, "minor": 0, "serious": 0}
        self.stats["knocked_down_count"] = 0
        self.stats["moves_made"] = 0
        self.stats["successful_dukes"] = 0
        self.stats["times_blocked"] = 0
        self.stats["injuries_caused"] = 0
        self.stats["injuries_suffered"] = 0
        
    def to_dict(self):
        """Convert goblin to dictionary for saving/loading"""
        return {
            "id": self.id,
            "name": self.name,
            "strength": self.strength,
            "toughness": self.toughness,
            "movement": self.movement,
            "max_movement": self.max_movement,
            "position": self.position,
            "has_ball": self.has_ball,
            "knocked_down": self.knocked_down,
            "momentum": self.momentum,
            "last_carrier_turn": self.last_carrier_turn,
            "team_id": self.team.id if self.team else None,
            "out_of_game": self.out_of_game,
            "season_injury": self.season_injury,
            "next_game_penalty": self.next_game_penalty,
            "misses_plays": self.misses_plays,
            "unavailable": self.unavailable,
            "stats": self.stats
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create goblin from dictionary"""
        goblin = cls(
            name=data["name"],
            strength=data["strength"],
            toughness=data["toughness"],
            movement=data["movement"]
        )
        
        goblin.id = data["id"]
        goblin.max_movement = data["max_movement"]
        goblin.position = tuple(data["position"])
        goblin.has_ball = data["has_ball"]
        goblin.knocked_down = data["knocked_down"]
        goblin.momentum = data["momentum"]
        goblin.last_carrier_turn = data["last_carrier_turn"]
        goblin.out_of_game = data["out_of_game"]
        goblin.season_injury = data["season_injury"]
        goblin.next_game_penalty = data["next_game_penalty"]
        goblin.misses_plays = data["misses_plays"]
        goblin.unavailable = data["unavailable"]
        goblin.stats = data["stats"]
        
        return goblin 