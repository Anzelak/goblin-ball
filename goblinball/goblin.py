import uuid
import random
import time
from config import CONFIG

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
            surnames = f.read().splitlines()
            # Filter out empty lines and strip whitespace
            surnames = [name.strip() for name in surnames if name.strip()]
            
            if surnames:
                surname = random.choice(surnames)
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
            "career_blocks": 0
        }
        
    def block(self, target):
        """Perform a blocking action against another goblin"""
        self.stats["blocks_attempted"] += 1
        
        # Calculate block results
        blocker_roll = random.randint(1, 10)
        target_roll = random.randint(1, 10)
        
        # Critical success/failure
        if random.random() < CONFIG.get("critical_success_chance", 0.05):
            blocker_total = self.strength + 20  # Automatic success
        elif random.random() < CONFIG.get("critical_failure_chance", 0.05):
            blocker_total = 0  # Automatic failure
        else:
            blocker_total = self.strength + blocker_roll
            
        # Apply carrier penalty if target has the ball
        target_modifier = CONFIG.get("carrier_penalty", -3) if target.has_ball else 0
        target_total = target.strength + target_roll + target_modifier
        
        # Calculate margin
        margin = blocker_total - target_total
        
        # Determine result
        if margin <= 0:
            result = "bounce"  # No effect, both goblins bounce off each other
        elif margin < CONFIG.get("push_threshold", 3):
            result = "no_effect"  # Not enough to push
        elif margin < CONFIG.get("knockdown_threshold", 6):
            result = "push"  # Push target back
            # Update stats
            self.stats["blocks_successful"] += 1
        else:
            result = "knockdown"  # Knock target down
            target.knocked_down = True
            # Update stats
            self.stats["blocks_successful"] += 1
            self.stats["knockdowns_caused"] += 1
            target.stats["knocked_down_count"] += 1
            
            # Roll for injury
            self.check_injury(target)
            
        # Return the result for the game to process
        return {
            "result": result,
            "margin": margin,
            "blocker_roll": blocker_roll,
            "target_roll": target_roll
        }
    
    def check_injury(self, target):
        """Check if a knocked down goblin is injured"""
        injury_roll = random.randint(1, 10)
        toughness_check = injury_roll - target.toughness
        
        if toughness_check >= 8:
            # Serious injury
            target.out_of_game = True
            target.season_injury = True
            target.unavailable = True
            # Permanent stat reduction
            penalty = CONFIG.get("serious_injury_permanent_penalty", 1)
            target.strength = max(1, target.strength - penalty)
            target.toughness = max(1, target.toughness - penalty)
            result = "serious"
            target.stats["injuries"]["serious"] += 1
        elif toughness_check >= 6:
            # Minor injury
            target.out_of_game = True
            target.next_game_penalty = True
            target.unavailable = True
            result = "minor"
            target.stats["injuries"]["minor"] += 1
        elif toughness_check >= 4:
            # Dazed
            target.misses_plays = CONFIG.get("dazed_plays_missed", 1)
            target.unavailable = True
            result = "dazed"
            target.stats["injuries"]["dazed"] += 1
        else:
            # No effect
            result = "none"
            target.stats["injuries"]["none"] += 1
            
        return result
        
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