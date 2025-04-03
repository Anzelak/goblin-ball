# Goblinball Specification Document

## 1. Game Overview

Goblinball is a turn-based sports simulation played on a 10x10 grid. Two teams of five goblins compete to score points by moving the ball to the opponent's end zone or kicking/throwing it through a central hoop. The game features blocking, dodging, injuries, and team tactics, and is designed to be entertaining to watch as an automated simulation.

### 1.1 Key Features

- **Grid-Based Movement**: Goblins move on a 10x10 grid with end zones at the north and south
- **Team Structure**: 5 goblins per team (1 ball carrier, 4 blockers)
- **Carrier Rotation**: Each goblin must take a turn as carrier before any goblin repeats
- **Dynamic AI**: Goblins use different movement strategies and adapt to the game situation
- **Dramatic Events**: Blocking, injuries, and scoring create exciting moments
- **Configurable Systems**: Game rules and balancing factors are adjustable via config file
- **Modular Architecture**: Core game separate from future season/tournament systems
- **Turn-based Gameplay**: Strategic blocking, dodging, and ball carrying
- **Scoring System**: Touchdowns (3 points) and field goals (1 point)
- **Animations and Visuals**: Visual effects for game events

## 2. Technology Stack

- **Programming Language**: Python 3.9+ (3.8+ minimum)
- **Graphics Library**: Pygame
- **Additional Libraries**:
    - Random (built-in)
    - JSON (for configuration)
    - UUID (for unique identifiers)
    - Math (for calculations)
    - Collections (for data structures)

## 3. Core Game Systems

### 3.1 Game Board

- **Grid Size**: 10x10
- **End Zones**: Top row (y=0) and bottom row (y=9) are end zones
- **Scoring Hoop**: Located in center of each end zone (position x=5, y=0/9)

### 3.2 Goblin Attributes

- **Name**: Generated unique name for each goblin
- **Strength**: Used in blocking contests and determining block success (1-10)
- **Toughness**: Used to resist injury (1-10)
- **Agility**: Used in DUKE checks and to avoid blocks (1-10)
- **Movement**: Squares a goblin can move per turn (1-4)
- **Position**: Carrier (has ball) or Blocker (has cudgel)
- **Momentum**: Builds up during successful actions (0-5)
- **Injury Resistance**: Bonus to injury rolls (0-2)

### 3.3 Movement System

- **Basic Movement**: Goblins can move up to their movement value in squares **per turn**
- **Movement Points**: Goblins receive their full movement points at the beginning of **each turn**
- **Zone of Control**: Blockers control adjacent squares (orthogonal and diagonal)
- **DUKE Check**: Required to move through or leave controlled squares (using Agility)
- **Failed DUKE Check**: Results in knockdown and potential injury
- **Movement Styles**:
    - **Direct**: Straight path to target
    - **Flanking**: Approaches from the side
    - **Cautious**: Prioritizes safety over progress
    - **Aggressive**: Takes risks for big gains
    - **Deceptive**: Uses misdirection and unpredictable movement
- **Carrier Movement Logic**:
    - Evaluates multiple potential paths (direct, flanking, safe)
    - Prioritizes paths based on progress toward end zone
    - Checks for clear paths to the end zone
    - Evaluates blocker screening for protection
    - Avoids moving adjacent to defenders without sufficient protection
- **Blocker Screening**:
    - Blockers positioned between carrier and defenders create protection
    - AI evaluates screening effectiveness for move selection
    - Screens don't require action points (passive protection)

### 3.4 Blocking System

- **Adjacent Requirement**: Blocker must be adjacent to target
- **Movement Cost**: 2 movement points to initiate a block
- **Resolution**:
    - Blocker: Strength + d10
    - Defender: Agility + d10 (-3 if carrying ball)
    - Results:
        - Tie: Bounce (no movement)
        - Win by 1-2: No effect
        - Win by 3-5 (Push threshold): Push back opponent
        - Win by 6+ (Knockdown threshold): Knock down opponent (trigger injury check)
    - **Critical Success/Failure**: 5% chance of automatic success/failure

### 3.5 Injury System

After being knocked down, goblins make an injury check:

- Roll d10 - Toughness - Injury Resistance
- Results:
    - 8+: Serious injury (out for season, permanent stat reduction)
    - 6-7: Minor injury (miss next game, temporary stat reduction)
    - 4-5: Dazed (miss next play)
    - 0-3: No effect (just knocked down for current play)

### 3.6 Scoring System

- **Touchdown**: 3 points for carrying ball into end zone
- **Field Goal**: 1 point for kicking/throwing through hoop
    - Must be within range (configurable, default 3 squares)
    - Success chance is configurable (default 50%)

### 3.7 Team Formations

Teams can adopt different formations that affect their movement patterns:

- **Standard**: Balanced formation
- **Wedge**: V-shaped to create a path for the carrier
- **Spread**: Spread out to cover the field
- **Bunker**: Defensive wall to protect a specific area
- **Blitz**: All-out attack to reach the carrier

### 3.8 Carrier Rotation System

- Each goblin on a team must take a turn as carrier before any goblin repeats
    
- Teams track which goblins have already been carrier in the current cycle
    
- The next carrier is selected at the beginning of each play
    
- If a goblin is injured/unavailable, the system selects the next eligible goblin
    
- Algorithm:
    
    ```python
    def select_next_carrier(team):    
        eligible_goblins = [g for g in team.goblins if not g.unavailable]    
        # Sort by when they were last carrier (oldest first)    
        eligible_goblins.sort(key=lambda g: g.last_carrier_turn or -1)    
        next_carrier = eligible_goblins[0]    
        next_carrier.has_ball = True    
        next_carrier.last_carrier_turn = team.carrier_rotation_counter    
        team.carrier_rotation_counter += 1
    ```
    

### 3.9 Goblin Naming System

- Each goblin receives a unique generated name
- Names combine prefixes, suffixes, and a surname from an external file
- Optional titles add flavor and distinctiveness
- Example name generator:

```python
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
```

- The function handles cases where the names file might be missing
- Goblin names follow patterns like:
    - "Grakbasher" (prefix + suffix)
    - "Snotsmasher Smith" (prefix + suffix + surname)
    - "Mugchomper the Fierce" (prefix + suffix + title)
    - "Blutooth Johnson the Mighty" (prefix + suffix + surname + title)
- Each combination creates unique characters with memorable names

## 4. Data Structures

### 4.1 Goblin Class

```python
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
```

### 4.2 Team Class

```python
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
        eligible_goblins.sort(key=lambda g: g.last_carrier_turn or -1)
        
        # Select next carrier
        next_carrier = eligible_goblins[0]
        next_carrier.has_ball = True
        next_carrier.last_carrier_turn = self.carrier_rotation_counter
        self.carrier_rotation_counter += 1
        self.carrier_history.append(next_carrier.id)
        
        return True
```

### 4.3 Game Class

```python
class Game:
    def __init__(self, team1, team2, config=None):
        # Configuration
        self.config = CONFIG
        
        # Teams
        self.team1 = team1
        self.team2 = team2
        
        # Field
        self.grid_size = CONFIG.get("grid_size", 10)
        self.grid = Grid(self.grid_size, self.grid_size)
        
        # Game state
        self.current_play = 0
        self.max_plays = CONFIG.get("plays_per_game", 20)
        self.turn = 0
        self.play_complete = False
        self.game_complete = False
        self.auto_advance = False
        self.turn_delay = 0.5  # Seconds between automatic turns
        self.last_turn_time = time.time()
        
        # Turn history for Previous Turn functionality
        self.turn_history = []
        self.max_history = 20  # Maximum number of turns to keep in history
        self.current_history_index = -1  # -1 means we're at the current state
        
        # Role assignment
        self.offense_team = team1
        self.defense_team = team2
        self.offense_team.is_offense = True
        
        # Events and logs
        self.event_manager = EventManager()
        
        # Animation system
        self.animation_manager = AnimationManager()
        
        # Movement systems
        self.movement_system = MovementSystem(self)
        self.carrier_movement = CarrierMovement(self, self.movement_system)
        self.blocker_movement = BlockerMovement(self, self.movement_system)
        
        # AI systems
        self.goal_system = AIGoalSystem(self)
        self.style_selector = MovementStyleSelector(self)
        
        # Game-specific stats that don't persist to team/goblin records
        self.game_stats = {
            "longest_play_turns": 0,
            "most_blocks_in_play": 0,
            "injuries_this_game": 0
        }
        
        # For each new game, reset team scores but preserve stats
        self.team1.score = 0
        self.team2.score = 0
        
        # Reset carrier tracking for new game
        self.team1.carrier_rotation_counter = 0
        self.team2.carrier_rotation_counter = 0
        self.team1.carrier_history = []
        self.team2.carrier_history = []
        
        # Movement trail tracking
        self.movement_trails = {}  # Dictionary to store recent positions of goblins
        self.trail_length = 5  # Number of previous positions to track
        self.max_turn_movement = 3  # Maximum number of moves a goblin can make in a turn
        
        # Create the game controller
        self.controller = GameController(self)
```

### 4.4 Configuration System

```python
class Config:
    def __init__(self, config_file="goblinball_config.json"):
        # Default configuration
        self.default_config = {
            # Game rules
            "grid_size": 10,
            "plays_per_game": 20,
            "touchdown_points": 3,
            "field_goal_points": 1,
            "max_turns_per_play": 30,
            
            # Goblin stats
            "min_strength": 1,
            "max_strength": 10,
            "min_toughness": 1,
            "max_toughness": 10,
            "min_movement": 1,
            "max_movement": 4,
            
            # Game mechanics
            "blocking_cost": 2,
            "push_threshold": 3,
            "knockdown_threshold": 6,
            "carrier_penalty": -3,
            "dodge_bonus": 3,
            "field_goal_range": 3,
            "field_goal_success_chance": 0.5,
            "critical_success_chance": 0.05,
            "critical_failure_chance": 0.05,
            
            # AI behavior
            "ai_aggression": 0.7,
            "ai_blocking_preference": 0.6,
            "movement_style_weights": {
                "direct": 0.3,
                "flanking": 0.2,
                "cautious": 0.2,
                "aggressive": 0.2,
                "deceptive": 0.1
            },
            
            # Injuries
            "serious_injury_permanent_penalty": 1,
            "minor_injury_game_penalty": 1,
            "dazed_plays_missed": 1,
            
            # Visuals
            "animation_speed": 1.0,
            "show_grid": True,
            "show_debug_info": False
        }
        
        # Load custom config if exists
        self.config = self.load_config(config_file)
    
    def load_config(self, file_path):
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                # Ensure all settings exist
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            # Save default config and return it
            self.save_config(self.default_config, file_path)
            return self.default_config
    
    def save_config(self, config, file_path):
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
```

### 4.5 Event System

```python
class GameEvent:
    """Represents a significant game event for logging and visualization"""
    def __init__(self, event_type, data=None):
        self.event_type = event_type  # "move", "block", "score", etc.
        self.data = data or {}        # Event-specific data
        self.timestamp = time.time()
        
    def __str__(self):
        """String representation for logging"""
        if self.event_type == "move":
            return f"{self.data.get('goblin_name')} moved to {self.data.get('target')}"
        elif self.event_type == "block":
            return f"{self.data.get('blocker_name')} blocked {self.data.get('target_name')} with result: {self.data.get('result')}"
        elif self.event_type == "score":
            return f"{self.data.get('goblin_name')} scored {self.data.get('points')} points!"
        # Add more event types as needed
        return f"Event: {self.event_type} - {self.data}"
```

## 5. Game Flow

### 5.1 Play Structure

Each play proceeds as follows:

1. **Setup Phase**:
    
    - Assign offense/defense roles
    - Position teams on the field
    - Designate ball carrier (based on rotation)
    - Select team formations
2. **Turn Phase**:
    
    - Reset goblin movement points
    - Move carrier first
        - Check for DUKE if leaving a zone of control
        - Check for DUKE when moving through zones of control
    - Move offensive blockers
        - Check for DUKE if leaving a zone of control
        - Check for DUKE when moving through zones of control
    - Move defensive blockers
        - Check for DUKE if leaving a zone of control
        - Check for DUKE when moving through zones of control
    - Process blocks and dukes
    - Check for scoring
    - Check if play is complete
3. **Resolution Phase**:
    
    - Update scores
    - Process injuries
    - Check for game completion

### 5.2 Game AI Processing Order

For each turn:

1. **Assign Goals**: Set a goal for each goblin based on the current situation
2. **Choose Formations**: Select team formations based on game state
3. **Select Movement Styles**: Choose a style for each goblin based on their goal
4. **Process Carrier Movement**: Move the ball carrier first
5. **Process Offensive Blockers**: Move blockers on offense team
6. **Process Defensive Blockers**: Move blockers on defense team
7. **Handle Interactions**: Process blocks, dukes, and other interactions
8. **Check Scoring**: Determine if a score has occurred
9. **Log Events**: Record significant events for animation and statistics

### 5.3 Carrier Movement Logic

```python
def move_carrier(self, carrier):
    # Get the carrier's goal
    goal = self.set_goblin_goal(carrier)
    
    # Choose movement style based on goal and situation
    style = self.choose_movement_style(carrier, goal)
    
    # Get potential targets based on style
    targets = self.get_movement_targets(carrier, style)
    
    # Move toward the best target
    remaining_moves = carrier.movement
    while remaining_moves > 0 and targets:
        # Sort targets by priority
        targets = self.prioritize_targets(carrier, targets, goal)
        
        # Evaluate safety of each target using blocker positions as screens
        targets = self.evaluate_move_safety(carrier, targets)
        
        # Try to move to the best target
        if self.move_toward_target(carrier, targets[0], remaining_moves):
            # Update remaining moves
            remaining_moves = carrier.movement
            
            # Check for scoring
            if self.check_scoring(carrier):
                break
            
            # Update targets
            targets = self.get_movement_targets(carrier, style)
        else:
            # Unable to move to target
            targets.pop(0)
```

### 5.4 Blocker Movement Logic

```python
def move_blocker(self, blocker):
    # Get the blocker's goal
    goal = self.set_goblin_goal(blocker)
    
    # Choose movement style based on goal
    style = self.choose_movement_style(blocker, goal)
    
    # Check for blocking opportunities
    if goal in ["block_defender", "tackle_carrier"]:
        target = self.find_blocking_target(blocker, goal)
        if target and self.is_adjacent(blocker, target):
            if blocker.movement >= CONFIG.get("blocking_cost", 2):
                # Perform block
                result = blocker.block(target)
                blocker.movement -= CONFIG.get("blocking_cost", 2)
                self.log_event("block", blocker, target, result)
                return
    
    # Get movement targets
    targets = self.get_movement_targets(blocker, style)
    
    # Move toward best target
    remaining_moves = blocker.movement
    while remaining_moves > 0 and targets:
        # Sort targets by priority
        targets = self.prioritize_targets(blocker, targets, goal)
        
        # Try to move to the best target
        if self.move_toward_target(blocker, targets[0], remaining_moves):
            # Update remaining moves
            remaining_moves = blocker.movement
            
            # Check for blocking opportunity after movement
            if goal in ["block_defender", "tackle_carrier"]:
                target = self.find_blocking_target(blocker, goal)
                if target and self.is_adjacent(blocker, target):
                    if blocker.movement >= CONFIG.get("blocking_cost", 2):
                        # Perform block
                        result = blocker.block(target)
                        blocker.movement -= CONFIG.get("blocking_cost", 2)
                        self.log_event("block", blocker, target, result)
                        break
            
            # Update targets
            targets = self.get_movement_targets(blocker, style)
        else:
            # Unable to move to target
            targets.pop(0)
```

## 6. AI Systems

### 6.1 Goblin Goal System

```python
def set_goblin_goal(self, goblin):
    """Set a goal for this goblin based on current situation"""
    if goblin.has_ball:
        # Carrier goals
        target_y = 0 if goblin.team == self.team2 else self.grid_size - 1
        distance = abs(goblin.position[1] - target_y)
        
        # Check for clear path to end zone
        path_defender_count = self.count_defenders_in_path(goblin, target_y)
        
        # First check if very close to end zone, always prioritize scoring when close
        if distance <= 3:
            return "score_touchdown"
        # Next check if in field goal range but path to end zone is blocked
        elif self.in_field_goal_range(goblin) and path_defender_count >= 2:
            return "attempt_field_goal"
        # Next check for clear path to end zone - be more aggressive
        elif path_defender_count == 0:
            # Clear path to end zone, prioritize direct scoring run
            return "score_touchdown"
        # Only evade if multiple defenders are nearby and active
        elif self.count_nearby_opponents(goblin.position, goblin.team) >= 2:
            return "evade_defenders"
        # Default goal is to advance
        else:
            return "advance_downfield"
    
    elif goblin.team == self.offense_team:
        # Offensive blocker goals
        carrier = self.offense_team.get_carrier()
        
        nearest_defender = self.find_closest_opponent_to(carrier)
        if nearest_defender and self.is_adjacent(goblin, nearest_defender):
            return "block_defender"
        elif self.is_near(goblin, carrier, 2):
            return "protect_carrier"
        else:
            return "advance_with_carrier"
    
    else:
        # Defensive blocker goals
        carrier = self.offense_team.get_carrier()
        
        if self.is_adjacent(goblin, carrier):
            return "tackle_carrier"
        elif self.is_near(goblin, carrier, 3):
            return "pursue_carrier"
        else:
            target_y = 0 if self.offense_team == self.team2 else self.grid_size - 1
            if self.is_between(goblin, carrier, target_y):
                return "maintain_position"
            else:
                return "intercept_carrier"
```

### 6.2 Movement Style Selection

```python
def choose_movement_style(self, goblin, goal):
    """Choose a movement style based on goblin's goal and situation"""
    import random
    
    # Base probabilities from config
    base_weights = CONFIG.get("movement_style_weights", {
        "direct": 0.3,
        "flanking": 0.2,
        "cautious": 0.2,
        "aggressive": 0.2,
        "deceptive": 0.1
    })
    
    # Copy weights
    weights = {k: v for k, v in base_weights.items()}
    
    # Adjust based on goal
    if goal == "score_touchdown":
        weights["direct"] += 0.3
        weights["aggressive"] += 0.2
        weights["cautious"] -= 0.2
    
    elif goal == "evade_defenders":
        weights["cautious"] += 0.3
        weights["deceptive"] += 0.2
        weights["direct"] -= 0.2
    
    elif goal == "block_defender" or goal == "tackle_carrier":
        weights["aggressive"] += 0.3
        weights["direct"] += 0.2
        weights["cautious"] -= 0.2
    
    # Add randomness
    for style in weights:
        weights[style] += random.uniform(-0.1, 0.1)
        weights[style] = max(0.05, min(0.9, weights[style]))
    
    # Choose style based on weights
    styles = list(weights.keys())
    chances = [weights[s] for s in styles]
    
    return random.choices(styles, weights=chances)[0]
```

## 7. UI Components

### 7.1 Main Game View

```python
class GameRenderer:
    def __init__(self, game, screen_width=800, screen_height=800):
        pygame.init()
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Goblinball")
        
        # Calculate grid cell size
        self.cell_size = min(screen_width, screen_height - 150) // game.grid_size
        
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
```

### 7.2 Animation System

```python
class Animation:
    def __init__(self, type, source=None, target=None, result=None, duration=30):
        self.type = type  # "move", "block", "knockdown", "score", etc.
        self.source = source  # Source goblin
        self.target = target  # Target position or goblin
        self.result = result  # Outcome
        self.duration = duration  # In frames
        self.frame = 0  # Current frame
        self.complete = False
    
    def update(self, delta_time=1.0):
        """Update the animation frame counter"""
        self.frame += delta_time
        if self.frame >= self.duration:
            self.complete = True
    
    def is_complete(self):
        """Check if the animation is complete"""
        return self.complete
        
    def get_progress(self):
        """Get animation progress as a value between 0.0 and 1.0"""
        return min(1.0, self.frame / self.duration)

class AnimationManager:
    """Manages a queue of animations"""
    def __init__(self):
        self.animations = []
        self.active_animation = None
        self.paused = False
        
    def add_animation(self, animation_type, source=None, target=None, result=None, duration=30):
        """Add a new animation to the queue"""
        animation = Animation(animation_type, source, target, result, duration)
        self.animations.append(animation)
        
        # If no active animation, start this one
        if not self.active_animation:
            self.active_animation = self.animations.pop(0)
```

## 8. Project Structure

The game is organized into several modules:

```
goblinball/
├── main.py              # Entry point and main game loop
├── goblin.py            # Goblin class
├── team.py              # Team class
├── game.py              # Game logic
├── config.py            # Configuration
├── renderer.py          # Pygame rendering
├── grid_renderer.py     # Grid visualization
├── goblin_renderer.py   # Goblin visualization
├── ui_renderer.py       # UI components
├── animation_renderer.py # Animation system
├── game_controller.py   # Controls game flow and turn processing
├── movement_system.py   # Handles goblin movement and blocking
├── carrier_movement.py  # Specialized carrier movement logic
├── blocker_movement.py  # Specialized blocker movement logic
├── ai_goals.py          # AI behavior
├── animation.py         # Animation system
├── event.py             # Event system
├── grid.py              # Grid management
├── utils.py             # Utility functions
└── logs/                # Log directory
```

## 9. Running the Game

### 9.1 Prerequisites

- Python 3.8 or higher
- Pygame library
- All dependencies listed in requirements.txt

### 9.2 Installation

1. Clone the repository or download the code
2. Install required dependencies:
    
    ```
    pip install -r requirements.txt
    ```

### 9.3 Running the Game

#### Recommended Method: Using run_game.bat (EASIEST)

The simplest and most reliable way to run the game is using the batch file in the project root:

```
Double-click run_game.bat
```

These scripts handle all path setup automatically and will show error information if the game crashes. They guarantee that the game is run with the correct working directory and module paths.

#### From the parent directory (Alternative Method)

You can also run the game from the parent directory:

**Windows Command Prompt:**

```
cd \path\to\goblin-ball
python -m goblinball.main
```

**Windows PowerShell:**

```
cd \path\to\goblin-ball
python -m goblinball.main
```

**Linux/Mac Terminal:**

```
cd /path/to/goblin-ball
python -m goblinball.main
```

#### From within the goblinball directory (Alternative Method)

Alternatively, you can run the game directly from within the goblinball directory:

**Windows Command Prompt:**

```
cd \path\to\goblin-ball\goblinball
python main.py
```

**Windows PowerShell:**

```
cd \path\to\goblin-ball\goblinball
python main.py
```

**Linux/Mac Terminal:**

```
cd /path/to/goblin-ball/goblinball
python main.py
```

### 9.4 Game Controls

- **Next Turn** - Advance to the next game turn
- **Previous Turn** - View the previous game turn (if available)
- **Auto Play** - Toggle automatic advancement of turns
- **New Play** - Start a new play
- **Debug** - Toggle debug information display

### 9.5 Common Run Errors and Solutions

- **ModuleNotFoundError: No module named 'config'**
    
    - You're likely running from the wrong directory
    - Solution: Use method #1 above (python -m goblinball.main)
- **AttributeError: 'Game' object has no attribute 'x'**
    
    - A required attribute is missing, usually due to code changes
    - Solution: Check that all required attributes are initialized in the Game class
- **NameError: name 'x' is not defined**
    
    - Missing import or variable not defined
    - Solution: Check imports and variable declarations

### 9.6 Comprehensive Troubleshooting Guide

#### Missing Module Errors

If you encounter `ModuleNotFoundError: No module named 'X'` (e.g., 'animation_renderer'):

1. **Check file existence**: Verify that all required module files exist in the goblinball directory:
   - Essential files: main.py, config.py, goblin.py, team.py, grid.py, renderer.py, animation.py, animation_renderer.py

2. **Fix missing files**: If a file is missing, it needs to be created with the appropriate content. The minimal requirements for each file are:
   - animation_renderer.py: Must contain the AnimationRenderer class
   - renderer.py: Must import AnimationRenderer from animation_renderer
   - main.py: Must import the renderer module

3. **Check import structure**: Make sure imports are correct in all files:
   ```python
   # In renderer.py
   from animation_renderer import AnimationRenderer
   
   # In main.py
   from renderer import GameRenderer
   ```

4. **Use the batch file**: The provided run_game.bat file ensures proper path setup and will display errors if they occur.

#### Path and Directory Issues

If you encounter incorrect path errors:

1. **Always run from project root**: Use `run_game.bat` or run the command from the project root directory
2. **Check your current directory**: Verify you're in the correct location using `cd` or `pwd`
3. **Avoid spaces in paths**: Ensure your project path doesn't contain spaces or special characters

#### Attribute Errors

If you encounter `AttributeError: 'NoneType' object has no attribute 'X'`:

1. **Defensive coding**: All code that accesses object attributes should check if the object exists first:
   ```python
   if obj is not None and hasattr(obj, 'attribute'):
       # Access the attribute safely
   ```

2. **Provide fallbacks**: Always have default values for missing attributes:
   ```python
   attacker_name = attacker.name if attacker else "Unknown"
   ```

#### Critical Game Errors

For severe errors that prevent the game from running:

1. **Check the logs**: Look in the goblinball/logs directory for detailed error messages
2. **Validate all imports**: Ensure all required modules are present and correctly imported
3. **Restart from a clean state**: Sometimes restarting Python or your IDE can resolve issues
4. **Reinstall dependencies**: Run `pip install -r requirements.txt` to ensure all dependencies are installed

If all else fails, the most reliable fix is to run the game using:
```
run_game.bat
```
Which handles all path setup automatically, or run as a module from the parent directory:
```
cd path\to\goblin-ball
python -m goblinball.main
```

## 10. Modular Design Approach

To ensure the core game can be extended with season/event systems without major refactoring, we implement these key architectural patterns:

### 10.1 Clear Interface Boundaries

```python
# game.py contains all game-specific logic
class Game:
    # Methods that interact with external systems use clear, stable interfaces
    
    def get_game_state(self):
        """Returns a complete snapshot of the current game state
        This is the primary interface for external systems"""
        return {
            "current_play": self.current_play,
            "max_plays": self.max_plays,
            "turn": self.turn,
            "team1": self.team1.get_state(),
            "team2": self.team2.get_state(),
            "offense_team_id": self.offense_team.id,
            "events": [e.to_dict() for e in self.events[-10:]],  # Last 10 events
            "game_complete": self.game_complete,
            "score": {
                "team1": self.team1.score,
                "team2": self.team2.score
            }
        }
    
    def get_results(self):
        """Returns final game results for external systems"""
        if not self.game_complete:
            return None
            
        return {
            "team1": {
                "id": self.team1.id,
                "name": self.team1.name,
                "score": self.team1.score,
                "goblins": [self.get_goblin_stats(g) for g in self.team1.goblins]
            },
            "team2": {
                "id": self.team2.id,
                "name": self.team2.name,
                "score": self.team2.score,
                "goblins": [self.get_goblin_stats(g) for g in self.team2.goblins]
            },
            "winner": self.team1.id if self.team1.score > self.team2.score else self.team2.id,
            "events": [e.to_dict() for e in self.key_events]
        }
```

### 10.2 Independent Entity Management

Teams and Goblins exist independently of games:

```python
# team.py
class Team:
    def update_from_game_results(self, results):
        """Update team stats from game results"""
        if results["winner"] == self.id:
            self.stats["wins"] += 1
        else:
            self.stats["losses"] += 1
            
        self.stats["points_for"] += results["score"][self.id]
        self.stats["points_against"] += results["opponent_score"]
        self.stats["games_played"] += 1
        
        # Calculate season points (for league standings)
        self.stats["season_points"] += 3 if results["winner"] == self.id else 0
```

### 10.3 Event System for Extensibility

Create an event system that future components can hook into:

```python
# event.py
class EventManager:
    def __init__(self):
        self.listeners = {}
        
    def add_listener(self, event_type, callback):
        """Add a callback function for an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def dispatch(self, event):
        """Dispatch an event to all registered listeners"""
        event_type = event.event_type
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(event)
```

### 10.4 Configuration System

Centralized configuration allows easy extension:

```python
# config.py
class Config:
    def __init__(self):
        self.config = {}
        
    def register_module(self, module_name, default_config):
        """Register a new module's configuration"""
        if module_name not in self.config:
            self.config[module_name] = default_config
            
    def get(self, module, key, default=None):
        """Get a configuration value"""
        if module in self.config and key in self.config[module]:
            return self.config[module][key]
        return default
```

### 10.5 Save/Load System

Implement a comprehensive save/load system that preserves all game state:

```python
# game.py
def save_game(self, filename):
    """Save the current game state to a file"""
    game_state = {
        "version": "1.0",
        "timestamp": time.time(),
        "game": self.to_dict(),
        "team1": self.team1.to_dict(),
        "team2": self.team2.to_dict(),
        "goblins": {}
    }
    
    # Save all goblin data
    for goblin in self.team1.goblins + self.team2.goblins:
        game_state["goblins"][goblin.id] = goblin.to_dict()
        
    with open(filename, 'w') as f:
        json.dump(game_state, f, indent=2)
        
@classmethod
def load_game(cls, filename):
    """Load a game from a file"""
    with open(filename, 'r') as f:
        game_state = json.load(f)
        
    # Recreate teams
    teams_dict = {}
    team1 = Team.from_dict(game_state["team1"])
    team2 = Team.from_dict(game_state["team2"])
    teams_dict[team1.id] = team1
    teams_dict[team2.id] = team2
    
    # Recreate goblins
    for goblin_id, goblin_data in game_state["goblins"].items():
        goblin = Goblin.from_dict(goblin_data)
        team_id = goblin_data["team_id"]
        if team_id in teams_dict:
            teams_dict[team_id].add_goblin(goblin)
    
    # Recreate game
    game = cls.from_dict(game_state["game"], teams_dict)
    
    return game
```

### 10.6 Statistics Tracking

Implement a comprehensive stats system ready for season tracking:

```python
# stats.py
class StatsTracker:
    def __init__(self):
        self.game_stats = {}
        self.team_stats = {}
        self.goblin_stats = {}
        
    def update_from_game(self, game_results):
        """Update statistics from a completed game"""
        game_id = game_results["id"]
        self.game_stats[game_id] = game_results
        
        # Update team stats
        for team_key in ["team1", "team2"]:
            team_data = game_results[team_key]
            team_id = team_data["id"]
            
            if team_id not in self.team_stats:
                self.team_stats[team_id] = {
                    "games_played": 0,
                    "wins": 0,
                    "losses": 0,
                    "points_for": 0,
                    "points_against": 0
                }
                
            self.team_stats[team_id]["games_played"] += 1
            self.team_stats[team_id]["points_for"] += team_data["score"]
            
            if team_key == "team1":
                opponent_score = game_results["team2"]["score"]
            else:
                opponent_score = game_results["team1"]["score"]
                
            self.team_stats[team_id]["points_against"] += opponent_score
            
            if game_results["winner"] == team_id:
                self.team_stats[team_id]["wins"] += 1
            else:
                self.team_stats[team_id]["losses"] += 1
        
        # Update goblin stats
        for team_key in ["team1", "team2"]:
            for goblin_data in game_results[team_key]["goblins"]:
                goblin_id = goblin_data["id"]
                
                if goblin_id not in self.goblin_stats:
                    self.goblin_stats[goblin_id] = {
                        "games_played": 0,
                        "touchdowns": 0,
                        "blocks": 0,
                        "injuries": {
                            "caused": 0,
                            "received": 0
                        }
                    }
                
                self.goblin_stats[goblin_id]["games_played"] += 1
                self.goblin_stats[goblin_id]["touchdowns"] += goblin_data["touchdowns"]
                self.goblin_stats[goblin_id]["blocks"] += goblin_data["blocks"]
                self.goblin_stats[goblin_id]["injuries"]["caused"] += goblin_data["injuries_caused"]
                self.goblin_stats[goblin_id]["injuries"]["received"] += goblin_data["injury_level"]
```

## 11. Configuration Reference

```json
{
  "grid_size": 10,
  "plays_per_game": 20,
  "touchdown_points": 3,
  "field_goal_points": 1,
  "max_turns_per_play": 30,
  
  "min_strength": 1,
  "max_strength": 10,
  "min_toughness": 1,
  "max_toughness": 10,
  "min_movement": 1,
  "max_movement": 4,
  
  "blocking_cost": 2,
  "push_threshold": 3,
  "knockdown_threshold": 6,
  "carrier_penalty": -3,
  "dodge_bonus": 3,
  "field_goal_range": 3,
  "field_goal_success_chance": 0.5,
  "critical_success_chance": 0.05,
  "critical_failure_chance": 0.05,
  
  "ai_aggression": 0.7,
  "ai_blocking_preference": 0.6,
  "movement_style_weights": {
    "direct": 0.3,
    "flanking": 0.2,
    "cautious": 0.2,
    "aggressive": 0.2,
    "deceptive": 0.1
  },
  
  "serious_injury_permanent_penalty": 1,
  "minor_injury_game_penalty": 1,
  "dazed_plays_missed": 1,
  
  "animation_speed": 1.0,
  "show_grid": true,
  "show_debug_info": false
}
```

## 12. Implementation Plan

### 12.1 Project Setup

1. Create the basic project structure:
    
    ```
    goblinball/
    ├── main.py              # Entry point
    ├── goblin.py            # Goblin class
    ├── team.py              # Team class
    ├── game.py              # Game logic
    ├── config.py            # Configuration
    ├── renderer.py          # Pygame rendering
    ├── ai.py                # AI behavior
    ├── animation.py         # Animation system
    ├── event.py             # Event system
    ├── utils.py             # Utility functions
    └── assets/              # Images, fonts, etc.
    ```
    
2. Install necessary dependencies:
    
    ```
    pip install pygame
    ```
    
3. Create default configuration:
    
    ```python
    # In config.py
    CONFIG = {}  # Initialize empty config
    
    def load_default_config():
        global CONFIG
        CONFIG = {
            # Game rules
            "grid_size": 10,
            "plays_per_game": 20,
            # ... other config values
        }
    ```
    

### 12.2 Development Phases

#### Phase 1: Core Game Framework (1-2 days)

1. Implement the `Goblin` class with basic attributes
2. Implement the `Team` class for team management
3. Implement the `Game` class for game state
4. Create a simple renderer to display the game board
5. Implement goblin name generator

#### Phase 2: Movement System (2-3 days)

1. Implement basic grid movement
2. Add zone of control and duke checks
3. Implement carrier and blocker movement logic
4. Add collision detection and handling
5. Implement carrier rotation system

#### Phase 3: Blocking and Combat (2-3 days)

1. Implement blocking mechanics
2. Add knockdown handling
3. Implement injury system
4. Add momentum system
5. Create event logging system

#### Phase 4: AI and Strategy (3-4 days)

1. Implement goal setting for goblins
2. Add movement style selection
3. Implement formation system
4. Add opportunity recognition
5. Create varied AI behaviors

#### Phase 5: Game Flow and UI (3-4 days)

1. Implement play sequence
2. Add turn management
3. Create animation system
4. Build UI controls for game viewing
5. Add scoring system and statistics tracking

#### Phase 6: Testing and Refinement (2-3 days)

1. Create test games with various configurations
2. Implement debugging tools
3. Fine-tune AI behaviors
4. Balance game mechanics
5. Optimize performance

## 13. Defensive Coding Guidelines

To ensure the game remains robust against future changes, follow these guidelines:

1. **Always check for attribute existence**:
    
    ```python
    if hasattr(obj, 'attribute_name'):
        # Use attribute
    ```
    
2. **Provide default values for missing attributes**:
    
    ```python
    value = getattr(obj, 'attribute_name', default_value)
    ```
    
3. **Handle import errors gracefully**:
    
    ```python
    try:
        from module import Class
    except ImportError:
        # Provide fallback or error message
    ```
    
4. **Log all exceptions**:
    
    ```python
    try:
        # Code that might fail
    except Exception as e:
        logger.error(f"Error: {e}")
    ```
    
5. **Check index bounds before accessing lists**:
    
    ```python
    if 0 <= index < len(my_list):
        value = my_list[index]
    ```
    

### 13.1 Adding New Features

When adding new features to Goblinball:

1. **Update all relevant constructors** - Ensure new attributes are properly initialized
2. **Add comprehensive error handling** - Check for missing attributes, invalid states
3. **Update visualization components** - Any new game features should be properly visualized
4. **Add tests for new functionality** - Ensure your changes don't break existing features

## 14. Potential Issues and Challenges

### 14.1 Technical Challenges

1. **Performance Bottlenecks**:
    
    - Problem: Animation system might slow down during complex interactions
    - Solution: Implement frame limiting and optimize rendering loop
    - Mitigation: Add config option to reduce animation complexity
2. **Path Planning Issues**:
    
    - Problem: Goblins might get stuck in impossible movement patterns
    - Solution: Implement timeouts for movement attempts
    - Mitigation: Add escape routes in AI when movement is blocked
3. **Memory Management**:
    
    - Problem: Large event logs could consume excessive memory in long games
    - Solution: Implement event pruning to keep only significant events
    - Mitigation: Limit event history to recent events only
4. **Input Handling**:
    
    - Problem: Pygame events might be missed during complex animations
    - Solution: Implement event queue to process inputs after animations
    - Mitigation: Provide keyboard shortcuts for all important functions

### 14.2 Game Design Challenges

1. **Balance Issues**:
    
    - Problem: Certain strategies might be overpowered
    - Solution: Use config system to tune parameters based on testing
    - Mitigation: Implement multiple AI strategies to test balance
2. **Readability**:
    
    - Problem: Complex game state might be difficult to understand
    - Solution: Add clear visual indicators for important game elements
    - Mitigation: Implement highlight system for active goblins/actions
3. **Engagement**:
    
    - Problem: Games might become repetitive
    - Solution: Add variety in goblin behaviors and event outcomes
    - Mitigation: Implement "drama" system to ensure exciting moments
4. **Simulation Speed**:
    
    - Problem: Finding the right balance between speed and comprehension
    - Solution: Implement variable simulation speed controls
    - Mitigation: Add auto-pause for significant events

### 14.3 Future Integration Challenges

1. **Data Persistence**:
    
    - Problem: Ensuring season data is properly saved/loaded
    - Solution: Implement robust serialization for all game objects
    - Mitigation: Use clear interfaces between game and season systems
2. **UI Scaling**:
    
    - Problem: Adding more features might clutter the UI
    - Solution: Design modular UI components from the start
    - Mitigation: Use tabs and collapsible panels for future content
3. **AI Complexity**:
    
    - Problem: More complex strategies might slow down gameplay
    - Solution: Implement AI caching for common decisions
    - Mitigation: Pre-compute some AI decisions during idle time
4. **Code Organization**:
    
    - Problem: Growing codebase might become unwieldy
    - Solution: Strict adherence to modular design principles
    - Mitigation: Regular refactoring sessions to maintain clean code

## 15. Current Implementation Status

### 15.1 Core Functionality

The current implementation of Goblinball has achieved the following milestones:

- **Complete Game Logic**: The core game systems are implemented and functional
- **UI Visualization**: The game is visually playable with all key components displayed
- **AI Behavior**: Basic AI decision-making is implemented for goblin actions
- **Movement System**: Movement, blocking, and DUKE mechanisms are fully functional
- **Event System**: Events are tracked and displayed in the game log

Recent improvements include:

- **Enhanced UI**: Improved visual feedback with symbols for DUKE, blocks, and knockdowns
- **Better Visualization**: Arrows showing block attempts and results
- **Hover Information**: Detailed information appears when hovering over goblins
- **Improved Layout**: The game UI has been refactored for better readability with the event log positioned on the left side
- **Bug Fixes**: Fixed carrier movement restrictions and movement trail visualization
- **Logging**: Enhanced logging for debugging and game analysis

### 15.2 Known Issues

Several aspects of the implementation require attention:

1. **DUKE Mechanic**: The DUKE mechanic implementation may not be working as intended (see detailed analysis in section 16.1)
2. **Animation Speed**: Animations may be too fast for some game events
3. **AI Decision-Making**: The AI sometimes makes suboptimal decisions, especially with blockers
4. **UI Clarity**: Some game events could be more clearly visualized
5. **Movement Trail**: The movement trail visualization could be improved

## 16. Detailed Mechanic Analysis

### 16.1 DUKE Mechanic Analysis

The DUKE (Dodge Under Killer Enemies) mechanic is implemented in the `movement_system.py` file. Here's a detailed analysis of its implementation:

#### How DUKE is Triggered

DUKE checks are triggered in two scenarios:

1. When a goblin attempts to **leave** a square that is within an opponent's zone of control
2. When a goblin attempts to **move through** a square that is within an opponent's zone of control

When a move is attempted, the system:

1. First checks if the goblin is currently in any opponent's zone of control
2. If so, a DUKE check is performed to see if the goblin can leave
3. Then calculates a path from the current position to the target
4. For each square along the path, checks if it's within any opponent's zone of control
5. If so, additional DUKE checks are performed for each of these squares

#### DUKE Check Calculation

```python
def perform_duke_check(self, goblin, blockers):
    # Base success chance
    success_chance = 0.5
    
    # Adjust for number of blockers (-10% per additional blocker)
    success_chance -= (len(blockers) - 1) * 0.1
    
    # Adjust for goblin's agility (+10% per point)
    success_chance += goblin.agility * 0.1
    
    # Ball carrier penalty (-20%)
    if goblin.has_ball:
        success_chance -= 0.2
    
    # Ensure chance is between 0.1 and 0.9
    success_chance = max(0.1, min(0.9, success_chance))
    
    # Roll for success
    success = random.random() < success_chance
```

#### Failed DUKE Consequences

If a DUKE check fails:
1. The goblin is knocked down
2. If the goblin was carrying the ball, the ball is dropped and the play ends
3. A knockdown event is created and dispatched
4. The movement attempt fails, and the goblin stays in its current position

#### AI Considerations

The AI takes DUKE checks into account when determining possible moves:
1. It calculates the success chance for each potential move
2. Moves with a very low success chance (below 30%) are filtered out
3. If a goblin is surrounded by opponents, the AI may choose to stay in place and block instead of attempting a risky move

## 17. Future Improvements

Based on the analysis of the current implementation and the user's feedback, here are detailed answers to the "What Could Be Better" questions:

### 17.1 AI Nuance & Target Prioritization

#### When a goblin has multiple potential targets, AI should prioritize as follows:

1. **For Ball Carriers**:
   - Prioritize targets based on clear path to end zone (fewest opponents in the way)
   - When blocked, evaluate diagonal movement to find flanking opportunities
   - Consider field position, weighting moves closer to the end zone higher
   - Base risk-taking on score differential (more aggressive when behind)

2. **For Offensive Blockers**:
   - Prioritize targets that threaten the current ball carrier's path
   - Target opponents with high strength who could easily knock down the carrier
   - Position to form protective formations around the carrier
   - Block defenders who are in ideal intercept positions

3. **For Defensive Blockers**:
   - Prioritize direct interception of the ball carrier
   - Target the squares the carrier must move through to reach the end zone
   - Prioritize blocking support blockers before targeting the carrier directly
   - Position to maintain a defense in depth, especially near the end zone

#### Conflicting Goal Resolution:

The AI should use a weighted decision system where:
1. **Primary goal weight**: 0.7 (e.g., protect_carrier)
2. **Opportunity goal weight**: 0.3 (e.g., block_defender)
3. **Contextual modifiers**:
   - +0.2 to opportunity weight if success chance > 70%
   - +0.1 to primary goal if carrier is within 3 squares of end zone
   - Shift weights based on score differential (more aggressive when behind)

#### Movement Style Factors:

1. **Game State Factors**:
   - Score differential: More aggressive when behind, more cautious when ahead
   - Turn number: More aggressive in later turns
   - Field position: More aggressive near opposing end zone, more cautious near own end zone

2. **Team Situation**:
   - Number of knocked down teammates: More cautious with many casualties
   - Ball carrier strength: More aggressive with stronger carrier
   - Opponent positioning: More deceptive when multiple opponents nearby

3. **Specific Modifiers**:
   - When score is tied with few turns left: +0.3 to aggressive style
   - When protecting a lead in final turns: +0.3 to cautious style
   - When path to end zone is clear: +0.2 to direct style

#### Pathfinding When Blocked:

1. **First Attempt**: Try to find a path around the blockage using A* pathfinding
2. **If No Path**: Evaluate if blocking the blocker is viable
3. **If Blocked Completely**: 
   - Carrier: Change goal to "evade_defenders" and move laterally
   - Blockers: Change goal to "create_opening" and target the blocking opponent
4. **Timeout Prevention**: After three failed movement attempts, switch to a completely different approach or pass to another goblin

### 17.2 Formation Implementation

#### Specific Starting Positions:

1. **Standard Formation**:
   - Carrier: (5, 9) for Team 1 or (5, 0) for Team 2
   - Blockers: (3, 8), (7, 8), (4, 7), (6, 7) for Team 1
   - Blockers: (3, 1), (7, 1), (4, 2), (6, 2) for Team 2

2. **Wedge Formation**:
   - Carrier: (5, 9) for Team 1 or (5, 0) for Team 2
   - Blockers: (4, 8), (6, 8), (3, 7), (7, 7) for Team 1
   - Blockers: (4, 1), (6, 1), (3, 2), (7, 2) for Team 2

3. **Spread Formation**:
   - Carrier: (5, 9) for Team 1 or (5, 0) for Team 2
   - Blockers: (2, 8), (8, 8), (3, 7), (7, 7) for Team 1
   - Blockers: (2, 1), (8, 1), (3, 2), (7, 2) for Team 2

4. **Bunker Formation**:
   - Carrier: (5, 9) for Team 1 or (5, 0) for Team 2
   - Blockers: (4, 8), (6, 8), (3, 8), (7, 8) for Team 1
   - Blockers: (4, 1), (6, 1), (3, 1), (7, 1) for Team 2

5. **Blitz Formation**:
   - Carrier: (5, 8) for Team 1 or (5, 1) for Team 2
   - Blockers: (3, 7), (7, 7), (4, 6), (6, 6) for Team 1
   - Blockers: (3, 2), (7, 2), (4, 3), (6, 3) for Team 2

#### Formation Influence on AI:

Formations should influence AI behavior beyond starting positions:

1. **Standard**: Balanced approach with even weighting of styles
2. **Wedge**: 
   - Blockers prioritize maintaining the V-shape
   - Middle blockers focus on clearing direct path
   - Wing blockers protect against flanking attempts
   - All blockers get +0.2 to "direct" movement style

3. **Spread**:
   - Blockers maintain wider spacing (avoid clustering)
   - Each blocker is responsible for a zone of the field
   - +0.2 to "flanking" movement style
   - Emphasis on controlling space rather than direct blocking

4. **Bunker**:
   - Blockers prioritize staying between carrier and opponents
   - Strong defensive emphasis with +0.3 to "cautious" style
   - Blocking attempts are more selective
   - Focus on protecting carrier rather than advancing

5. **Blitz**:
   - All goblins get +0.3 to "aggressive" style
   - Higher priority for blocks, even at risk
   - Faster advancement with less concern for protection
   - Prioritize knocking down opponents over position

### 17.3 Field Goal Specifics

#### Field Goal Mechanics:

1. **Initiation**:
   - Field goal attempts should cost 2 movement points
   - The carrier must have line of sight to the goal
   - Attempting ends the carrier's turn
   - The action should be automated when the carrier is within range and has no clear path to touchdown

2. **Success Factors**:
   - Base success chance of 50% at maximum range (3 squares)
   - +10% per square closer to the goal
   - -5% per adjacent enemy goblin (representing defensive pressure)
   - +5% per point of the carrier's strength (representing throwing power)
   - -10% if the carrier was moved this turn (representing being rushed)

3. **Visual Representation**:
   - Throw arc animation from carrier to goal
   - Ball spinning in flight
   - Flash effect for success or "thunk" effect for failure
   - Camera focus shift to the goal area during attempt

### 17.4 Momentum Impact

#### Momentum Generation:

1. **Gaining Momentum**:
   - +1 for successful block
   - +1 for successful DUKE
   - +2 for causing knockdown
   - +3 for scoring touchdown
   - +1 for field goal
   - +1 for moving 3+ squares in a single turn

2. **Effects**:
   - Each point provides +5% to block success
   - Each point provides +5% to DUKE success
   - Each point reduces injury chance by 5%
   - At 3+ momentum, unlock special moves (extra block, longer move)
   - At 5 momentum, all actions get +10% success chance

3. **Loss Conditions**:
   - Reset to 0 when knocked down
   - -1 when blocked unsuccessfully
   - -2 when failing a DUKE check
   - All momentum reset at end of play
   - -1 per turn if no action taken

### 17.5 UI/Animation Detail

#### Visual Cues for States:

1. **Dazed**:
   - Small stars circling the goblin's head
   - Slightly wobbling animation
   - 50% opacity "Dazed" text above the goblin
   - Yellow outline pulsing slowly

2. **Minor Injury**:
   - Bandage overlay on the goblin
   - Limping animation when moving
   - Red cross icon above goblin
   - Reduced movement speed in animations

3. **Knocked Down**:
   - Goblin lying flat on the ground
   - Small "X" eyes
   - Dust cloud animation on knockdown
   - Team-colored ring around the goblin (not just red for all teams)

#### Block Animation Distinctions:

1. **Push**:
   - Orange arrow showing push direction
   - "Push" text appearing briefly
   - Short sliding animation for pushed goblin
   - Sound effect of scuffling/shoving

2. **Knockdown**:
   - Red impact star at point of contact
   - "Knockdown" text with "!" suffix
   - Falling animation with spin
   - Louder impact sound effect

3. **Successful DUKE**:
   - Green trail showing the evasion path
   - Brief speed lines around the moving goblin
   - "Duke!" text appearing with glow effect
   - Quick sidestep animation

4. **Field Goal**:
   - Ball arc following a parabolic path
   - Camera panning to follow the ball
   - Goal flashing when scored
   - Cheering sound effect for success

#### Essential UI Elements:

1. **Always Visible**:
   - Score for both teams
   - Current play/turn counter
   - Offense team indicator
   - Time remaining/turns remaining
   - Ball carrier highlight
   - Team formation names

2. **Context Sensitive**:
   - Current goblin's action points
   - Success chances for blocks/DUKEs
   - Field goal range indicator
   - Zone of control visualization on hover
   - Recent event summary

## 18. Troubleshooting and Implementation Notes

### 18.1 Common Issues and Resolutions

#### Movement Issues

- **Carrier Not Advancing**: If the carrier seems overly cautious or trapped:
  - Check for proper blocker positioning (blockers should be positioned to screen defenders)
  - Verify that `count_defenders_in_path` is correctly assessing the path to the end zone
  - Ensure the `evaluate_move_safety` method isn't being too restrictive with safety requirements

- **Defender AI Problems**: If defenders aren't effectively tackling the carrier:
  - Check the DUKE mechanics implementation in `movement_system.py`
  - Verify that blocking costs are appropriate in the config (currently set to 1)
  - Ensure defenders are using appropriate movement styles for their goals

#### Blocking Issues

- **Ineffective Blocking**: If blockers aren't protecting the carrier effectively:
  - Verify blocker goal assignment in `set_goblin_goal` is prioritizing protection
  - Check that offensive blockers are positioning themselves between defenders and carrier
  - Ensure the `evaluate_move_safety` method is correctly identifying screening blockers

- **Excessive Blocking**: If blockers are too focused on hitting defenders instead of screening:
  - Adjust the `ai_blocking_preference` in the config
  - Modify goal weighting in the `AIGoalSystem`
  - Consider reducing the reward for successful blocks

### 18.2 Key Implementation Details

#### Critical AI Functions

The AI system revolves around these key components:

1. **Goal Setting (`set_goblin_goal` in `ai_goals.py`)**
   - Determines what each goblin is trying to accomplish
   - Uses field position, defender count, and team role
   - Critical for coordinating team behavior

2. **Movement Style Selection (`choose_movement_style` in `ai_goals.py`)**
   - Influences how goblins move toward their goals
   - Balances directness, caution, and aggression
   - Adjusts based on goal and game situation

3. **Path Generation (`get_direct_path`, `get_flanking_paths`, `get_safe_paths` in `carrier_movement.py`)**
   - Creates potential movement paths based on style
   - Critical for finding routes through defenders
   - Adapts to defensive formations

4. **Move Safety Evaluation (`evaluate_move_safety` in `carrier_movement.py`)**
   - Assesses how well protected each potential move is
   - Identifies where blockers are creating screens
   - Balances progress with protection

### 18.3 Interdependencies

Important codebase interdependencies to be aware of:

1. **Movement and Blocking**
   - The `movement_system.py` handles both movement and blocking
   - DUKE checks occur within movement but impact blocking strategy
   - Blocking costs affect both offensive and defensive strategy

2. **Goal System and Movement**
   - Goals set in `ai_goals.py` directly influence movement in `carrier_movement.py` and `blocker_movement.py`
   - Changes to goal priority impact entire game flow
   - Movement styles are determined by goals

3. **Config Parameters**
   - Key config values that affect gameplay:
     - `blocking_cost`: Cost to attempt a block (reduced from 2 to 1)
     - `push_threshold`: Threshold for pushing back an opponent
     - `knockdown_threshold`: Threshold for knocking down an opponent
     - `carrier_penalty`: Penalty applied to carrier in DUKE/block contests
     - `movement_style_weights`: Base weights for different movement styles

## 19. Recent Enhancements

The following key enhancements have been made to the Goblinball codebase to improve gameplay dynamics and AI behavior:

### 19.1 Carrier Movement Improvements

#### Clear Path Detection
- Added logic to detect when a clear path to the end zone exists
- Carrier now prioritizes direct movement toward the end zone when path is clear
- Implemented in `move_carrier` method of `CarrierMovement` class

```python
# Check if there's a clear path to the end zone
has_clear_path = True
path_to_end = []

# Calculate path to end zone
# [path calculation logic...]

# Check if each square in path is empty or has a knocked down opponent
for pos in path_to_end:
    entity = self.game.grid.get_entity_at_position(pos)
    if entity and (not hasattr(entity, 'team') or entity.team == carrier.team or not entity.knocked_down):
        has_clear_path = False
        break

# If clear path exists, prioritize direct movement
if has_clear_path and carrier.movement > 0:
    # Find the farthest point we can reach
    reachable_path = [pos for pos in path_to_end if manhattan_distance(carrier.position, pos) <= carrier.movement]
    if reachable_path:
        target_pos = reachable_path[-1]
        # [safety check and movement logic...]
```

#### Blocker Screening System
- Implemented safety evaluation for all potential moves
- Carrier now identifies and prioritizes positions screened by friendly blockers
- Added in `evaluate_move_safety` method of `CarrierMovement` class

#### Adaptive Path Selection
- Path selection now adapts based on number of active defenders
- More direct/aggressive paths when few defenders are active
- More cautious paths when many defenders are present

### 19.2 AI Decision Making Enhancements

#### Goal System Improvements
- Enhanced goal selection logic in `AIGoalSystem`
- Added `count_defenders_in_path` to assess path clarity to end zone
- Goal prioritization now considers clear paths to end zone

```python
# Carrier goal selection logic
path_defender_count = self.count_defenders_in_path(goblin, target_y)

if distance <= 3:
    return "score_touchdown"
elif self.in_field_goal_range(goblin) and path_defender_count >= 2:
    return "attempt_field_goal"
elif path_defender_count == 0:
    # Clear path, prioritize scoring
    return "score_touchdown"
```

#### Move Scoring System
- Implemented comprehensive move scoring based on multiple factors:
  - Base priority score (3 for direct path, 2 for flanking, 1 for safe)
  - Safety score from blocker screening
  - Progress toward end zone
  - Distance from current position

```python
# Move scoring logic
base_score = priority * 10.0
safety_score = self.evaluate_move_safety(carrier, move)
progress_score = 10.0 - abs(move[1] - target_y) / self.game.grid.height * 10.0
distance_score = (carrier.movement - distance) * 0.2
total_score = base_score + safety_score + progress_score + distance_score
```

### 19.3 Game Balance Adjustments

#### Configuration Changes
- Reduced `blocking_cost` from 2 to 1 movement points
- This change allows more frequent blocking attempts
- Makes defense more effective against carriers

#### Lateral Movement Improvements
- Enhanced fallback logic for when direct movement isn't possible
- Carrier now evaluates lateral moves based on safety
- Prevents carriers from becoming trapped when blocked

### 19.4 Safety Checking Logic

#### Defender Proximity Checks
- Added safety validation before movement:
```python
# Count defenders near the target position
defenders_near_target = 0
for dx in range(-1, 2):
    for dy in range(-1, 2):
        check_pos = (target_pos[0] + dx, target_pos[1] + dy)
        if 0 <= check_pos[0] < self.game.grid.width and 0 <= check_pos[1] < self.game.grid.height:
            entity = self.game.grid.get_entity_at_position(check_pos)
            if entity and hasattr(entity, 'team') and entity.team != carrier.team and not entity.knocked_down:
                defenders_near_target += 1

# Only take clear path if safe
if defenders_near_target == 0:
    # [movement logic...]
```

#### Screen Effectiveness Calculation
- Implemented detailed logic to determine if a blocker is effectively screening a defender:
```python
# Check if blocker is screening a defender
dx = defender.position[0] - move_pos[0]
dy = defender.position[1] - move_pos[1]

# Calculate expected screening position
if dx != 0:
    expected_x = move_pos[0] + (1 if dx > 0 else -1)
else:
    expected_x = move_pos[0]
    
if dy != 0:
    expected_y = move_pos[1] + (1 if dy > 0 else -1)
else:
    expected_y = move_pos[1]

# Check if blocker is at or near expected position
blocker_screens = (abs(blocker_x - expected_x) <= 1 and abs(blocker_y - expected_y) <= 1)
```

These enhancements collectively improve the strategic depth and realism of the game, ensuring carriers make intelligent use of blockers while creating exciting gameplay moments when defenders are knocked down, opening paths to the end zone.

## 10. Game Mechanics

### 10.1 Blocker Screening

Blockers can perform two forms of blocking:

1. **Active Blocking:** A goblin action that costs movement points and requires a skill check to knock down an opponent.
2. **Passive Screening:** Blockers positioned between the carrier and defenders act as screens, providing protection without requiring a skill check.

The carrier AI evaluates potential moves not just by distance to the end zone, but also by how well screened those positions are. When choosing moves, the carrier will:

1. Identify potential threat vectors from nearby defenders
2. Calculate positions where friendly blockers provide screening protection
3. Prioritize paths where blockers form a protective screen
4. Avoid moving adjacent to defenders unless sufficiently screened by friendly blockers

This creates a more realistic and strategic gameplay experience where the offense coordinates carrier movement with blocker positioning, similar to blocking and screening concepts in physical sports.

### 10.2 Path Evaluation Logic

The carrier's movement AI uses several factors to evaluate potential moves:

1. **Progress Value:** Positions closer to the end zone receive higher scores
2. **Safety Score:** Positions with better blocker screening receive higher scores
3. **Defender Proximity:** Positions adjacent to active defenders are penalized
4. **Clear Path Detection:** When no defenders are in a direct path to the end zone, the carrier will prioritize direct movement

The carrier will adapt its strategy based on the game situation:
- With few defenders on the field, the carrier will move more directly toward the end zone
- With many active defenders, the carrier will seek protective screens from blockers
- In scoring range with a clear path, the carrier will sprint toward the end zone

These mechanics encourage strategic team formations and proper use of blockers as protection for the ball carrier.

### 10.3 Carrier Movement Evaluation

The carrier's movement evaluation process follows these steps:

1. **Goal Setting**: Determine the carrier's goal based on field position and game state
2. **Style Selection**: Choose a movement style based on goal and defender positions
3. **Path Generation**: Generate potential paths (direct, flanking, safe)
4. **Safety Evaluation**: For each potential position:
   - Count nearby defenders
   - Check if friendly blockers are screening those defenders
   - Calculate a safety score based on screening effectiveness
5. **Final Scoring**: Combine safety score with progress toward end zone
6. **Move Selection**: Choose the position with the highest combined score
7. **Clear Path Check**: Override with direct movement if a clear path to the end zone exists

The `evaluate_move_safety` method performs a detailed analysis of each potential move:

```python
def evaluate_move_safety(self, carrier, move_pos):
    safety_score = 0.0
    
    # Get all defenders and friendly blockers
    defenders = [entity for entity in all_entities if entity.team != carrier.team]
    blockers = [entity for entity in all_entities if entity.team == carrier.team and entity != carrier]
    
    # For each defender, check if screened by a blocker
    for defender in defenders:
        def_distance = manhattan_distance(defender.position, move_pos)
        
        if def_distance <= 3:  # Only consider nearby defenders
            # Check if screened by a blocker
            is_screened = any(
                manhattan_distance(blocker.position, expected_screening_position) <= 1
                for blocker in blockers
            )
            
            # Adjust safety score
            if is_screened:
                safety_score += 2.0  # Bonus for being screened
            else:
                safety_score -= 1.0  # Penalty for being exposed
                
    return safety_score
```

This evaluation ensures carriers make intelligent use of blockers for protection.

### 10.4 Defender Count and Path Adaptation

The carrier's path selection adapts based on the number of active defenders:

```python
def get_direct_path(self, carrier, target_pos):
    # Count active defenders on the field
    active_defenders = sum(
        1 for entity in all_entities 
        if entity.team != carrier.team and not entity.knocked_down
    )
    
    # Generate more direct paths if few defenders are active
    if active_defenders <= 1:
        # More aggressive, direct path calculation
        # [implementation details]
    else:
        # More cautious path calculation
        # [implementation details]
```

This adaptive behavior creates dynamic gameplay where the carrier becomes more aggressive when defenders are knocked down, leading to exciting late-game situations.