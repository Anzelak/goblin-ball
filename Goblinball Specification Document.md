### 3.6 Scoring System

- **Touchdown**: 3 points for carrying ball into end zone
- **Field Goal**: 1 point for kicking/throwing through hoop
    - Can be attempted from anywhere on the field
    - Success chance based on distance:
        - 40% base chance at 5 squares away
        - +10% for each square closer (50% at 4, 60% at 3, etc.)
        - "Hail Magoo" shots (beyond 5 squares) capped at 10% chance
    - Modified by carrier's dexterity:
        - 0% modification at 5 dexterity
        - -5% at 4 dexterity, -10% at 3, etc.
        - +5% at 6 dexterity, +10% at 7, etc.
    - -10% for each defender's zone of control the carrier is in
    - -10% for each defender's zone of control the shot passes through
    - Field goals are a "last resort" option when a touchdown is unlikely
    - Both successful and unsuccessful attempts end the current play

### 17.3 Field Goal Specifics

#### Field Goal Mechanics:

1. **When to Attempt**:
   - Field goals should be a "last resort" option when:
   - Multiple defenders blocking path to the end zone
   - Carrier is in immediate danger of being blocked with no good escape
   - Path to end zone is heavily defended with low chance of advancing
   - AI only attempts if estimated success chance is above 20%

2. **Success Calculation**:
   - Base chance is distance-dependent:
     - 40% at 5 squares from hoop
     - 50% at 4 squares
     - 60% at 3 squares
     - 70% at 2 squares
     - 80% at 1 square
   - "Hail Magoo" shots (beyond 5 squares) have maximum 10% chance
   - Dexterity modifier: (goblin's dexterity - 5) * 5%
   - -10% per defender zone of control the carrier is in
   - -10% per defender zone of control in the path to the hoop
   - Minimum 5% chance, maximum 95% chance

3. **AI Decision Logic**:
   - Estimate field goal success chance
   - Compare with probability of reaching end zone
   - Choose field goal if:
     - End zone path is blocked by 2+ defenders
     - Adjacent to defenders with few escape options
     - Multiple defenders (3+) surrounding carrier
     - Estimated success chance exceeds 20%
   - Prioritize touchdown when within 3 squares of end zone

4. **Visual Representation**:
   - Shot trajectory from carrier to hoop
   - Success/failure animation and sound effects
   - Event log entry with attempt details
   - Play ends after attempt 

### 3.3 Movement System

- **Basic Movement**: Goblins can move up to their movement value in squares **per turn**
- **Movement Points**: Goblins receive their full movement points at the beginning of **each turn**
- **Zone of Control**: Blockers control adjacent squares (orthogonal and diagonal)
- **DUKE Check**: Required when leaving a controlled square (using Agility)
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
    - Blockers positioned between the carrier and defenders create protection
    - AI evaluates screening effectiveness for move selection
    - Screens don't require action points (passive protection)

### 16.1 DUKE Mechanic Analysis

The DUKE (Dodge Under Killer Enemies) mechanic is implemented in the `movement_system.py` file. Here's a detailed analysis of its implementation:

#### How DUKE is Triggered

DUKE checks are triggered when a goblin attempts to **leave** a square that is within an opponent's zone of control. When a move is attempted, the system:

1. First checks if the goblin is currently in any opponent's zone of control
2. If so, a DUKE check is performed to see if the goblin can leave
3. If the DUKE check succeeds, the goblin can move to its destination
4. If the DUKE check fails, the goblin is knocked down and can't complete the move

Note: Unlike previous versions of the game, DUKE checks are NOT required when moving through an opponent's zone of control - only when leaving a zone of control.

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
1. It calculates the success chance for leaving a zone of control
2. Moves with a very low success chance (below 30%) are filtered out
3. If a goblin is surrounded by opponents, the AI may choose to stay in place and block instead of attempting a risky move 