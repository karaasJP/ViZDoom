#!/usr/bin/env python

from __future__ import print_function
from vizdoom import *
from random import choice
import sys

from time import sleep
import cv2
import numpy as np
import random


def detect_yellow(img):
    # HSV色空間に変換
    img = cv2.bilateralFilter(img,9,100,500)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # cv2.imshow("hsv", hsv)
    # cv2.imshow("bilateral", hsv)
    # 緑色のHSVの値域1
    # hsv_min = np.array([50, 150, 50])
    # hsv_max = np.array([70, 255, 240])

    hsv_min = np.array([13, 130, 120])
    hsv_max = np.array([14, 175, 230])
    maskyellow = cv2.inRange(hsv, hsv_min, hsv_max)
    maskyellow = maskyellow[160:240,:]
    cv2.imshow("yellow", maskyellow)

    hsv_min = np.array([0, 0, 120])
    hsv_max = np.array([0, 0, 130])
    maskgray = cv2.inRange(hsv, hsv_min, hsv_max)
    maskgray = maskgray[160:240,:]
    cv2.imshow("gray", maskgray)

    cv2.imshow("yellow and gray", maskgray + maskyellow)
    maskall = maskgray + maskyellow

    image, contours, hierarchy = cv2.findContours(
        maskall, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    detect_count = 0    # 矩形検出された数（デフォルトで0を指定）
    output_screen = img
    for i in range(0, len(contours)):   # 各輪郭に対する処理
        area = cv2.contourArea(contours[i])  # 輪郭の領域を計算
        if area < 4 or 30 < area:    # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
            continue
        # print(area)
        # 外接矩形
        if len(contours[i]) > 0:
            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect)
            y += 160
            if h/1.5 < w < h:
                output_screen = cv2.rectangle(
                    output_screen, (x, y), (x + w, y + h), (100, 100, 255), 2)
                detect_count += 1
                print("x,y = " + str((x, y)))

    if 0 < detect_count < 4:
        print("detect enemy")
        cv2.imshow("yellow", output_screen)
        if x > 330:
            game.make_action([0,1,0,0,0,0])
        elif x < 315:
            game.make_action([1,0,0,0,0,0])
        else:
            game.make_action([0,0,1])
    else:
        choices = [[0,1,0], [0,0,0,0,0,1]]
        randomchoice = random.randint(0,1)
        game.make_action(choices[randomchoice])
    return (img)


game = DoomGame()

# Use CIG example config or your own.
game.load_config("../../scenarios/cig.cfg")

game.set_doom_map("map01")  # Limited deathmatch.
#game.set_doom_map("map02")  # Full deathmatch.

# Join existing game.
game.add_game_args("-join 127.0.0.1") # Connect to a host for a multiplayer game.

# Name your agent and select color
# colors: 0 - green, 1 - gray, 2 - brown, 3 - red, 4 - light gray, 5 - light brown, 6 - light red, 7 - light blue
game.add_game_args("+name MIYATA +colorset 0")

# During the competition, async mode will be forced for all agents.
#game.set_mode(Mode.PLAYER)
game.set_mode(Mode.ASYNC_PLAYER)

#game.set_window_visible(False)

# Sets resolution. Default is 320X240
game.set_screen_resolution(ScreenResolution.RES_640X480)

# Sets the screen buffer format. Not used here but now you can change it. Defalut is CRCGCB.
game.set_screen_format(ScreenFormat.RGB24)


game.init()

output_screen = None
# Three example sample actions
actions = [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0]]

# Get player's number
player_number = int(game.get_game_variable(GameVariable.PLAYER_NUMBER))
last_frags = 0

# sleep_time = 1.0 / DEFAULT_TICRATE  # = 0.028
sleep_time = 0.01

# Play until the game (episode) is over.
while not game.is_episode_finished():

    # Get the state.
    state = game.get_state()

    # Analyze the state.
    screen_buf = state.screen_buffer
    # cv2.imshow('screen_buf', screen_buf)

    output_screen = detect_yellow(screen_buf)

    if output_screen is not None:
        cv2.imshow('rect screen', output_screen)

    if sleep_time > 0:
        sleep(sleep_time)
        cv2.waitKey(int(sleep_time * 1000))


    frags = game.get_game_variable(GameVariable.FRAGCOUNT)
    if frags != last_frags:
        last_frags = frags
        print("Player " + str(player_number) + " has " + str(frags) + " frags.")

    # Check if player is dead
    if game.is_player_dead():
        print("Player " + str(player_number) + " died.")
        # Use this to respawn immediately after death, new state will be available.
        game.respawn_player()

game.close()
