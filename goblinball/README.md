# Goblinball

A turn-based fantasy sports simulation game where goblins compete in a brutal ball game.

## Description

Goblinball is a turn-based sports simulation played on a 10x10 grid. Two teams of five goblins compete to score points by moving the ball to the opponent's end zone or kicking/throwing it through a central hoop. The game features blocking, dodging, injuries, and team tactics, and is designed to be entertaining to watch as an automated simulation.

## Installation

1. Make sure you have Python 3.9+ installed
2. Clone this repository
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

To start the game, run:

```bash
python main.py
```

## Controls

- **Space**: Pause/unpause the game
- **D**: Toggle debug information
- **ESC**: Exit the game
- **Mouse click**: Select a goblin to view its stats

## Game Rules

- The game is played on a 10x10 grid
- Each team has 5 goblins (1 carrier, 4 blockers)
- Teams take turns as offense and defense
- Each goblin must take a turn as carrier before any goblin repeats
- Score points by:
  - Carrying the ball into the opponent's end zone (3 points)
  - Kicking/throwing the ball through the hoop (1 point)
- Goblins can block opponents, potentially knocking them down and causing injuries

## Configuration

Game settings can be adjusted in the `goblinball_config.json` file that will be created the first time you run the game.

## Development

This project is in active development. Current features include:
- Basic game mechanics and rules
- Team and goblin management
- Simple visualization
- Event logging system

Future features will include:
- Full AI for goblin decision making
- Season/tournament management
- Team management and progression
- More complex game strategies and formations 