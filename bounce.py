#!/usr/bin/env python
# Brian Loewe
# CPSC 386-03
# 2022-05-09
# bloewe@csu.fullerton.edu
# @bloewe21
#
# Lab 05-00
#
# This is the file bounce.py, which creates the game object, builds the scene
# for the game, and runs the game
#

"""
Imports the Bounce demo and executes the main function.
"""

import sys
from game import game

if __name__ == "__main__":
    NUM_BALLS = 5
    if len(sys.argv) > 1:
        NUM_BALLS = int(sys.argv[1])
    if NUM_BALLS >= 50:
        NUM_BALLS = 49
    NUM_BALLS = max(NUM_BALLS, 3)
    video_game = game.BounceDemo(NUM_BALLS)
    video_game.build_scene_graph()
    video_game.run()
