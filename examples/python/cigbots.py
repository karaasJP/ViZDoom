#!/usr/bin/env python

from __future__ import print_function

from random import choice
from vizdoom import *
from time import sleep

import cv2
import numpy as np


def detect_green(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 緑色のHSVの値域1
    # hsv_min = np.array([50, 150, 50])
    # hsv_max = np.array([70, 255, 240])
    # 肌色
    hsv_min = np.array([13, 130, 75])
    hsv_max = np.array([14, 175, 230])
    mask = cv2.inRange(hsv, hsv_min, hsv_max)

    cv2.imshow("green", mask)

    image, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    detect_count = 0    # 矩形検出された数（デフォルトで0を指定）
    output_screen = None
    for i in range(0, len(contours)):   # 各輪郭に対する処理
        area = cv2.contourArea(contours[i])  # 輪郭の領域を計算
        if area < 50 or 100 < area:    # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
            continue
        print(area)
        # 外接矩形
        if len(contours[i]) > 0:
            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect)
            if h/1.5 < w < h:
                output_screen = cv2.rectangle(
                    screen_buf, (x, y), (x + w, y + h), (100, 100, 255), 2)
                detect_count += 1
                print("x,y = " + str((x, y)))
    if output_screen is not None:
        cv2.imshow("green", output_screen)
        if x > 325:
            game.make_action([0,1,0,0,0,0])
        elif x < 315:
            game.make_action([1,0,0,0,0,0])
        else:
            game.make_action(actions[5])
    else:
        game.make_action(actions[5])
    return (mask)


game = DoomGame()

# Use CIG example config or your own.
game.load_config("../../scenarios/cig.cfg")

game.set_doom_map("map01")  # Limited deathmatch.
# game.set_doom_map("map02")  # Full deathmatch.


# Sets resolution. Default is 320X240
game.set_screen_resolution(ScreenResolution.RES_640X480)

# Sets the screen buffer format. Not used here but now you can change it. Defalut is CRCGCB.
game.set_screen_format(ScreenFormat.RGB24)


# Start multiplayer game only with your AI (with options that will be used in the competition, details in cig_host example).
game.add_game_args("-host 1 -deathmatch +timelimit 1.0 "
                   "+sv_forcerespawn 1 +sv_noautoaim 1 +sv_respawnprotect 1 +sv_spawnfarthest 1 +sv_nocrouch 1 "
                   "+viz_respawn_delay 10 +viz_nocheat 1")

# Name your agent and select color
# colors: 0 - green, 1 - gray, 2 - brown, 3 - red, 4 - light gray, 5 - light brown, 6 - light red, 7 - light blue
game.add_game_args("+name MIYATA +colorset 0")

game.set_mode(Mode.PLAYER)

# game.set_window_visible(False)

game.init()
output_screen = None
# Three example sample actions
actions = [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0]]
last_frags = 0

# Play with this many bots
bots = 7

# Run this many episodes
episodes = 1
# sleep_time = 1.0 / DEFAULT_TICRATE  # = 0.028
sleep_time = 0.028
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
        state = game.get_state()

        # Analyze the state.
        screen_buf = state.screen_buffer
        # cv2.imshow('screen_buf', screen_buf)

        output_screen = detect_green(screen_buf)

        if output_screen is not None:
            cv2.imshow('rect screen', output_screen)

        # Make your action.
        # game.make_action(actions[5])

        frags = game.get_game_variable(GameVariable.FRAGCOUNT)
        if frags != last_frags:
            last_frags = frags
            print("Player has " + str(frags) + " frags.")

        # Check if player is dead
        if game.is_player_dead():
            print("Player died.")
            # Use this to respawn immediately after death, new state will be available.
            game.respawn_player()

        if sleep_time > 0:
            sleep(sleep_time)
            cv2.waitKey(int(sleep_time * 1000))

    print("Episode finished.")
    print("************************")

    # Starts a new episode. All players have to call new_episode() in multiplayer mode.
    game.new_episode()

game.close()
