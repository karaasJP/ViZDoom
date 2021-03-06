#!/usr/bin/env python

from __future__ import print_function

from random import choice
from vizdoom import *
from time import sleep

import cv2
import numpy as np
import random
import copy
import datetime

import find

game = DoomGame()

# Use CIG example config or your own.
game.load_config("../../scenarios/cig.cfg")

game.set_doom_map("map01")  # Limited deathmatch.
# game.set_doom_map("map02")  # Full deathmatch.


# Sets resolution. Default is 320X240
game.set_screen_resolution(ScreenResolution.RES_640X480)

# Enables depth buffer.
game.set_depth_buffer_enabled(True)
# Enables labeling of in game objects labeling.
game.set_labels_buffer_enabled(True)
# Enables buffer with top down map of he current episode/level .
game.set_automap_buffer_enabled(True)
game.set_automap_mode(AutomapMode.OBJECTS)
game.set_automap_rotate(False)
game.set_automap_render_textures(False)

game.set_render_hud(True)
game.set_render_minimal_hud(False)

# Sets the screen buffer format. Not used here but now you can change it. Defalut is CRCGCB.
game.set_screen_format(ScreenFormat.RGB24)

# Start multiplayer game only with your AI (with options that will be used in the competition, details in cig_host example).
game.add_game_args("-host 1 -deathmatch +timelimit 3.0 "
                   "+sv_forcerespawn 1 +sv_noautoaim 1 +sv_respawnprotect 1 +sv_spawnfarthest 1 +sv_nocrouch 1 "
                   "+viz_respawn_delay 10 +viz_nocheat 0")

# Name your agent and select color
# colors: 0 - green, 1 - gray, 2 - brown, 3 - red, 4 - light gray, 5 - light brown, 6 - light red, 7 - light blue
game.add_game_args("+name dynamite +colorset 0")

game.set_mode(Mode.PLAYER)

# game.set_window_visible(False)

game.init()
# Three example sample actions
actions = [[1, 0, 0, 0, 0, 0, 0, 0, 0],  # 0 TURN_LEFT
           [0, 1, 0, 0, 0, 0, 0, 0, 0],  # 1 TURN_RIGHT
           [0, 0, 1, 0, 0, 0, 0, 0, 0],  # 2 ATTACK
           [0, 0, 0, 1, 0, 0, 0, 0, 0],  # 3 MOVE_LEFT
           [0, 0, 0, 0, 1, 0, 0, 0, 0],  # 4 MOVE_RIGHT
           [0, 0, 0, 0, 0, 1, 0, 0, 0],  # 5 MOVE_FORWARD
           [0, 0, 0, 0, 0, 0, 1, 0, 0],  # 6 MOVE_BACKWARD
           [0, 0, 0, 0, 0, 0, 0, 1, 0],  # 7 TURN_LEFT_RIGHT_DELTA
           [0, 0, 0, 0, 0, 0, 0, 0, 1]]  # 8 LOOK_UP_DOWN_DELTA

search_actions = [[0, 0, 0, 0, 0, 0, 0, 5, 0],
                  [0, 1, 0, 0, 0, 1, 0, 0, 0]]
last_frags = 0
repeat = [0, actions[1], "action name"]
pre_finders = []
pre2_finders = []
lock = 0

# Play with this many bots
bots = 12

# Run this many episodes
episodes = 3
# sleep_time = 1.0 / DEFAULT_TICRATE  # = 0.028
sleep_time = 0.006

for i in range(episodes):

    print("Episode #" + str(i + 1))

    # Add specific number of bots
    # (file examples/bots.cfg must be placed in the same directory as the Doom executable file,
    # edit this file to adjust bots).
    game.send_game_command("removebots")
    for i in range(bots):
        game.send_game_command("addbot")

    # Play until the game (episode) is over.
    while not game.is_episode_finished():

        # Get the state.
        s = game.get_state()
        n = s.number
        vars = s.game_variables
        screen_buf = s.screen_buffer
        depth_buf = s.depth_buffer
        labels_buf = s.labels_buffer
        automap_buf = s.automap_buffer
        labels = s.labels
        if n % 10 == 0:
            print(n)
        action = None

# ***********************************************************
        # Analyze the state.
        # cv2.imshow('depth_buf', depth_buf)
        # cv2.imshow('labels_buf', labels_buf)
        # cv2.imshow('automap_buf', automap_buf)

        # cv2.moveWindow('automap_buf', 0, 0)
        # cv2.moveWindow('depth_buf', 640, 0)
        # cv2.moveWindow('labels_buf', 0, 1000)

        if n > 15:
            # labels_bufを見る
            action, repeat, pre_finders, pre2_finders = find.label(
                labels_buf, screen_buf, actions, action, repeat, lock, pre_finders, pre2_finders)
            # depth_bufを見る
            repeat = find.depth(depth_buf, actions, repeat)

        # Make your action.
        if n <= 15:
            # [i * 100 for i in actions[7]]
            game.make_action([0, 0, 0, 0, 0, 1, 0, 0, 0])

        elif repeat[0] != 0:
            game.make_action(repeat[1])
            print("REPEAT " + repeat[2])
            repeat[0] -= 1

        elif action is not None:
            if len(action) >= 3:
                if action[2] == 1:  # ショット時動作
                    if lock > 0:
                        action = actions[5]
                    else:
                        lock = 30
                        print("ショット時動作、ロック")

            game.make_action(action)

            if action == [0, 0, 0, 0, 0, 0, 0, 80]:
                print("首振り解除動作")

        else:
            print("サーチアクションを実行中")
            game.make_action(random.choice(search_actions))

        if lock > 0:
            lock -= 1
# *************************************************************

        frags = game.get_game_variable(GameVariable.FRAGCOUNT)
        if frags != last_frags:
            last_frags = frags
            print("Player has " + str(frags) + " frags.")

        # Check if player is dead
        if game.is_player_dead():
            if n > 100:
                repeat = [10, actions[5], "死んだときの初期動作"]
            print("Player died.")
            # Use this to respawn immediately after death, new state will be available.
            game.respawn_player()

        if sleep_time > 0:
            sleep(sleep_time)
            cv2.waitKey(int(sleep_time * 500))

    print("Episode finished.")
    f = open('results.txt', 'a')
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    intfrags = int(last_frags)
    if intfrags >= 0:

        strfrags = " " + str(intfrags)
    else:
        strfrags = " " + str(intfrags)
    f.write(strfrags + '   @' + now + '\n')
    f.close
    print("************************")

    # Starts a new episode. All players have to call new_episode() in multiplayer mode.
    game.new_episode()

game.close()
