#!/usr/bin/env python3
"""
Simple script to run goblinball from the project root.
"""
import os
import sys

# Add the current directory to the path so modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the game
from goblinball.main import main

if __name__ == "__main__":
    main() 