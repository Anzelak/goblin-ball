#!/usr/bin/env python3
"""
Simple script to run goblinball.
"""
import sys
import os

# Change to the goblinball directory
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goblinball'))

# Run the main function from main.py
exec(open("main.py").read()) 