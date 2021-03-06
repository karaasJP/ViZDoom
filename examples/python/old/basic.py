#!/usr/bin/env python

#####################################################################
# This script presents how to use the most basic features of the environment.
# It configures the engine, and makes the agent perform random actions.
# It also gets current state and reward earned with the action.
# <episodes> number of episodes are played.
# Random combination of buttons is chosen for every action.
# Game variables from state and last reward are printed.
#
# To see the scenario description go to "../../scenarios/README.md"
#####################################################################

from __future__ import print_function
from vizdoom import *

from random import choice
from time import sleep

import cv2  # OpenCVのインポートを追加


# Create DoomGame instance. It will run the game and communicate with you.
game = DoomGame()

# Now it's time for configuration!
# load_config could be used to load configuration instead of doing it here with code.
# If load_config is used in-code configuration will also work - most recent changes will add to previous ones.
# game.load_config("../../scenarios/basic.cfg")

# Sets path to additional resources wad file which is basically your scenario wad.
# If not specified default maps will be used and it's pretty much useless... unless you want to play good old Doom.
game.set_doom_scenario_path("../../scenarios/basic.wad")

# Sets map to start (scenario .wad files can contain many maps).
game.set_doom_map("map02")

# Sets resolution. Default is 320X240
game.set_screen_resolution(ScreenResolution.RES_640X480)

# Sets the screen buffer format. Not used here but now you can change it. Defalut is CRCGCB.
game.set_screen_format(ScreenFormat.RGB24)

# Enables depth buffer.
game.set_depth_buffer_enabled(True)

# Enables labeling of in game objects labeling.
game.set_labels_buffer_enabled(True)

# Enables buffer with top down map of the current episode/level.
game.set_automap_buffer_enabled(True)

# Sets other rendering options (all of these options except crosshair are enabled (set to True) by default)
game.set_render_hud(False)
game.set_render_minimal_hud(False)  # If hud is enabled
game.set_render_crosshair(False)
game.set_render_weapon(True)
game.set_render_decals(False)  # Bullet holes and blood on the walls
game.set_render_particles(False)
game.set_render_effects_sprites(False)  # Smoke and blood
game.set_render_messages(False)  # In-game messages
game.set_render_corpses(False)
# Effect upon taking damage or picking up items
game.set_render_screen_flashes(True)

# Adds buttons that will be allowed.
game.add_available_button(Button.MOVE_LEFT)
game.add_available_button(Button.MOVE_RIGHT)
game.add_available_button(Button.ATTACK)

# Adds game variables that will be included in state.
game.add_available_game_variable(GameVariable.AMMO2)

# Causes episodes to finish after 200 tics (actions)
game.set_episode_timeout(200)

# Makes episodes start after 10 tics (~after raising the weapon)
game.set_episode_start_time(10)

# Makes the window appear (turned on by default)
game.set_window_visible(True)

# Turns on the sound. (turned off by default)
game.set_sound_enabled(True)

# Sets the livin reward (for each move) to -1
game.set_living_reward(-1)

# Sets ViZDoom mode (PLAYER, ASYNC_PLAYER, SPECTATOR, ASYNC_SPECTATOR, PLAYER mode is default)
game.set_mode(Mode.PLAYER)

# Enables engine output to console.
# game.set_console_enabled(True)

# Initialize the game. Further configuration won't take any effect from now on.
game.init()

# Define some actions. Each list entry corresponds to declared buttons:
# MOVE_LEFT, MOVE_RIGHT, ATTACK
# 5 more combinations are naturally possible but only 3 are included for transparency when watching.
actions = [[True, False, False], [False, True, False], [False, False, True]]

# Run this many episodes
episodes = 10

# Sets time that will pause the engine after each action (in seconds)
# Without this everything would go too fast for you to keep track of what's happening.
sleep_time = 1.0 / DEFAULT_TICRATE  # = 0.028

for i in range(episodes):
    print("Episode #" + str(i + 1))

    # Starts a new episode. It is not needed right after init() but it doesn't cost much. At least the loop is nicer.
    game.new_episode()

    while not game.is_episode_finished():

        # Gets the state
        state = game.get_state()
        # Which consists of:
        n = state.number
        vars = state.game_variables
        screen_buf = state.screen_buffer
        depth_buf = state.depth_buffer
        labels_buf = state.labels_buffer
        automap_buf = state.automap_buffer
        labels = state.labels

        ret, bw_buf = cv2.threshold(
            labels_buf, 50, 255, cv2.THRESH_BINARY_INV)    # 2値化
        # cv2.imshow('ViZDoom 2ti Buffer', bw_buf)    # 2ちか画像を表示
        # 輪郭の抽出
        image, contours, hierarchy = cv2.findContours(
            bw_buf, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        detect_count = 0    # 矩形検出された数（デフォルトで0を指定）

        for i in range(0, len(contours)):   # 各輪郭に対する処理
            area = cv2.contourArea(contours[i])  # 輪郭の領域を計算
            if area < 100 or 20000 < area:    # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
                continue
            print(area)
            # 外接矩形
            if len(contours[i]) > 0:
                rect = contours[i]
                x, y, w, h = cv2.boundingRect(rect)
                output_screen = cv2.rectangle(
                    bw_buf, (x, y), (x + w, y + h), (0, 255, 0), 2)
                detect_count += 1
                print("x,y = " + str((x,y)))

        cv2.imshow('rect screen', output_screen)
        cv2.moveWindow('labels_buf', 700, 0)
        # Makes a random action and get remember reward.
        # r = game.make_action(choice(actions))

        position_center = x + w/2
        position_left = x
        position_right = x + w
        print("center = " + str(position_center))
        if position_left >= 335:
            r = game.make_action([0, 1, 0])
            print("go right")
        elif position_right <= 315:
            r = game.make_action([1, 0, 0])
            print('go left')
        else:
            r = game.make_action([0, 0, 1])

        # Makes a "prolonged" action and skip frames:
        # skiprate = 4
        # r = game.make_action(choice(actions), skiprate)

        # The same could be achieved with:
        # game.set_action(choice(actions))
        # game.advance_action(skiprate)
        # r = game.get_last_reward()

        # Prints state's game variables and reward.
        print("State #" + str(n))
        print("Game variables:", vars)
        print("Reward:", r)
        print("=====================")

        if sleep_time > 0:
            sleep(sleep_time)
            cv2.waitKey(int(sleep_time * 1000))

    # Check how the episode went.
    print("Episode finished.")
    print("Total reward:", game.get_total_reward())
    print("************************")

# It will be done automatically anyway but sometimes you need to do it in the middle of the program...
cv2.destroyAllWindows()
game.close()
