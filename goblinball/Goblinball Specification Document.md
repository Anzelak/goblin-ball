# Goblinball Specification Document

## Table of Contents

1. [Game Overview](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#1-game-overview)
2. [Technology Stack](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#2-technology-stack)
3. [Core Game Systems](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#3-core-game-systems)
4. [Data Structures](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#4-data-structures)
5. [Game Flow](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#5-game-flow)
6. [AI Systems](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#6-ai-systems)
7. [UI Components](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#7-ui-components)
8. [Project Structure](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#8-project-structure)
9. [Running the Game](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#9-running-the-game)
10. [Modular Design Approach](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#10-modular-design-approach)
11. [Configuration Reference](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#11-configuration-reference)
12. [Implementation Plan](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#12-implementation-plan)
13. [Defensive Coding Guidelines](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#13-defensive-coding-guidelines)
14. [Potential Issues and Challenges](https://claude.ai/chat/8b735f4e-0c7b-4504-a827-b28573e5a0ed#14-potential-issues-and-challenges)

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
- **Strength**: Used in blocking contests (1-10)
- **Toughness**: Used to resist injury (1-10)
- **Movement**: Squares a goblin can move per turn (1-4)
- **Position**: Carrier (has ball) or Blocker (has cudgel)
- **Momentum**: Builds up during successful actions (0-5)
- **Block Skill**: Bonus to blocking attempts (0-2)
- **Dodge Skill**: Bonus to dodging blocks (0-2)
- **Injury Resistance**: Bonus to injury rolls (0-2)

### 3.3 Movement System

- **Basic Movement**: Goblins can move up to their movement value in squares **per turn**
- **Movement Points**: Goblins receive their full movement points at the beginning of **each turn**
- **Zone of Control**: Blockers control adjacent squares
- **Duke Check**: Required to move through controlled squares (Dodge+3 vs Strength)
- **Movement Styles**:
    - **Direct**: Straight path to target
    - **Flanking**: Approaches from the side
    - **Cautious**: Prioritizes safety over progress
    - **Aggressive**: Takes risks for big gains
    - **Deceptive**: Uses misdirection and unpredictable movement

### 3.4 Blocking System

- **Adjacent Requirement**: Blocker must be adjacent to target
- **Movement Cost**: 2 movement points to initiate a block
- **Resolution**:
    - Blocker: Strength + d10 + Block Skill
    - Defender: Strength + d10 + Dodge Skill (-3 if carrying ball)
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
    - Move offensive blockers
    - Move defensive blockers
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
        
        if distance <= 3:
            return "score_touchdown"
        elif self.in_field_goal_range(goblin):
            return "attempt_field_goal"
        else:
            defender_count = self.count_nearby_opponents(goblin.position, goblin.team)
            if defender_count >= 2:
                return "evade_defenders"
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