# Goblinball UI Design Proposal

## Overview

The Goblinball user interface needs a complete redesign to clearly communicate game mechanics and create an intuitive, engaging player experience. The current UI does not effectively convey critical information such as zones of control, DUKE checks, and movement paths, making gameplay confusing and unintuitive.

This proposal outlines a comprehensive UI system that prioritizes clarity, visual feedback, and player understanding.

## Core UI Principles

1. **Visual Clarity**: Game mechanics should be visible and understandable at a glance
2. **Consistent Feedback**: Player actions should have clear, consistent visual and textual feedback
3. **Informative Hover States**: Important information should be accessible via hover tooltips
4. **Progressive Disclosure**: Show basic information by default, reveal complexity on demand
5. **Clear Action Sequences**: Events should be shown in logical, sequential order

## Main UI Components

### 1. Game Board

#### Field Design
- **Grid Lines**: Subtle, non-intrusive grid lines
- **End Zones**: Clearly marked with team colors and goal posts
- **Hoops**: Visible targets for field goals at center of each end zone
- **Position Labels**: Coordinates (A1-J10) displayed at edges of grid

#### Goblin Representation
- **Base Tokens**: Team-colored circular tokens (current implementation works well)
- **Role Indicator**: Clear visual distinction between carriers and blockers
  - Carrier: Ball icon overlaid on goblin token
  - Blocker: Small cudgel icon
- **Stat Visualization**: Small icons representing strength, agility, movement stats
- **Status Effects**: Animated overlays for knocked down, dazed, injured states
  - Knocked Down: Goblin displayed horizontally with "X" eyes
  - Dazed: Spinning stars around head
  - Injured: Bandage wrapping and limping animation

### 2. Zone of Control Visualization

#### Active Display
- Show zones of control for selected goblin (8 surrounding squares)
- Highlight in team color with semi-transparency (30-40% opacity)
- Pulse effect to indicate active control

#### Toggle Options
- "Show All Zones" toggle to display all zones of control
- Keyboard shortcut (Z) to temporarily show all zones

#### Interactive Elements
- Zones light up when hovered (60-70% opacity)
- Tooltip shows "Zone of Control: [Goblin Name]"
- Red highlight when zone contains enemy goblin (potential DUKE check)

### 3. Movement System

#### Path Visualization
- **Path Preview**: When selecting a move destination, show path as dotted line
- **Zone Crossings**: Path changes to dashed red line when crossing zones of control
- **DUKE Indicators**: Warning icon at points where DUKE checks will be required
- **Range Indicator**: Show movement range as green highlight on valid squares

#### Movement Animation
- Smooth animation along calculated path
- Slow down when passing through danger zones
- Quick "hop" animation when successfully leaving a zone of control

#### DUKE Check Visualization
- **Pre-Check Warning**: "DUKE required" popup before confirming movement
- **Check Animation**: 
  - Dice rolling animation with goblin's agility value
  - Success: Green flash and "swoosh" effect
  - Failure: Red flash and "thud" effect with goblin falling
- **Result Overlay**: Clear "Success" or "Failure" text with odds shown

### 4. Event Log and History

#### Enhanced Event Log
- Color-coded events by type (movement, DUKE, block, score)
- Timestamps or turn numbers for each event
- Click on event to highlight relevant position on grid
- Expandable details for complex events

#### Visual Event History
- Timeline visualization showing key events in chronological order
- Playback controls for reviewing previous turns
- Scrubbing capability to quickly navigate game history

#### Event Types and Formatting
- **Movement**: "[Goblin] moved from [X1,Y1] to [X2,Y2]"
- **DUKE Check**: "[Goblin] attempted to leave [Defender]'s zone of control - Success/Failure (X% chance)"
- **Block**: "[Goblin] blocked [Target] - Success/Failure (Result details)"
- **Knockdown**: "[Goblin] was knocked down by [Cause]"
- **Score**: "[Goblin] scored a touchdown/field goal! (+X points)"

### 5. Goblin Detail Panel

#### Goblin Stats View
- Comprehensive stat display when goblin is selected
- Visual stat bars for strength, agility, toughness
- Current movement points remaining
- Success chances for common actions (block, DUKE)

#### Action Menu
- Context-sensitive actions based on goblin's state
- Block, Move, Field Goal buttons when applicable
- Estimate success chance for each action

#### Tooltip System
- Rich tooltips explaining game mechanics
- Example: "DUKE Check: Roll using Agility to leave an opponent's zone of control"
- Visual examples in tooltips where helpful

### 6. Turn Management

#### Turn Information
- Clear display of current turn, play number, and phase
- Whose team is on offense/defense
- Timer for auto-advance mode

#### Turn Controls
- Next/Previous turn buttons
- Auto-advance toggle with speed control
- "Jump to Play" navigation

#### Turn Transition
- Brief animation between turns
- Summary of key events from previous turn
- Preview of which goblins will act next

## Specific Mechanics Visualization

### 1. DUKE Check System

#### When Leaving Zone of Control
- Visual indication when goblin is in a zone of control
- Warning when selecting move that requires DUKE check
- Clear animation of DUKE check with success chance
- Detailed log entry explaining the check and outcome

#### Success/Failure Feedback
- Success: Goblin "dodges" with agile animation, green success indicator
- Failure: Goblin "trips" with stumble animation, red failure indicator
- Show actual dice roll alongside success threshold

#### UI Mock-up Description
```
1. Player selects goblin in zone of control
2. Zone flashes with "Controlled Zone" warning
3. When move is selected:
   - Dialog: "DUKE check required (65% chance)"
   - Animation: Dice roll with agility + d10 vs. defense
   - Result: Clear success/failure message
4. Log entry: "Grubface attempted DUKE check vs. Snotnose - Success (rolled 7, needed 5)"
```

### 2. Blocking System

#### Block Visualization
- Show valid blocking targets in red highlight
- Display expected success chance before committing
- Animated clash effect when blocks occur
- Show strength vs. agility comparison

#### Outcomes Visualization
- Push: Arrow showing push direction
- Knockdown: Impact star and falling animation
- Critical success/failure: Special effects and text

#### Block Resolution
- Clear step-by-step resolution display:
  1. Attacker roll: Strength + d10
  2. Defender roll: Agility + d10 (-3 if carrier)
  3. Comparison with outcome explanation

### 3. Field Goal System

#### Field Goal Setup
- Range indicator showing success chances from different positions
- Path visualization from carrier to hoop
- Warning if path crosses defender zones

#### Attempt Animation
- Ball flying in arc toward hoop
- Defender influence shown as "wind" effects
- Success/failure determined by visual position of ball

#### Success Calculation Display
- Base chance based on distance
- Agility modifier
- Defender penalty modifications
- Clear final percentage

## Implementation Roadmap

### Phase 1: Core Visualization Improvements
1. Zone of control visibility
2. Path visualization with DUKE check indicators
3. Improved event log with detailed information

### Phase 2: Animation and Feedback
1. Movement and action animations
2. Success/failure feedback effects
3. Turn transition improvements

### Phase 3: Enhanced Information Display
1. Detailed goblin stats panel
2. Hover tooltips and contextual help
3. Probability displays for actions

### Phase 4: Advanced Features
1. Game history timeline
2. Replay system
3. Tutorial overlays for new players

## Technical Implementation Considerations

### Layered Rendering Approach
- Base layer: Field and static elements
- Middle layer: Goblins and game entities
- Effect layer: Animations, highlights, zones
- UI layer: Controls, panels, text

### State Management
- Clear separation between game state and visual state
- Consistent state transitions for animations
- Observer pattern for UI updates from game events

### Performance Optimizations
- Batched rendering for static elements
- Sprite-based animation system
- Throttled updates for non-critical elements

## Conclusion

The proposed UI redesign addresses the core issues with the current Goblinball interface, particularly concerning DUKE checks and zones of control. By focusing on clear visual feedback, intuitive controls, and detailed event information, this design will significantly improve the player experience and game comprehension.

The most critical changes focus on making game mechanics visible and understandable, ensuring players can clearly see why certain outcomes occur and what options are available to them. This transparency will enhance both the strategic depth and accessibility of Goblinball. 