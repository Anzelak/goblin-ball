import json
import os

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

# Create a global instance of the config
CONFIG = Config() 