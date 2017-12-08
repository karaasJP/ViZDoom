#!/usr/bin/env python

from __future__ import print_function

from random import choice
from vizdoom import *
from time import sleep

import cv2
import numpy as np


def yellow(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 緑色のHSVの値域1
    # hsv_min = np.array([50, 150, 50])
    # hsv_max = np.array([70, 255, 240])

    #
    hsv_min = np.array([13, 130, 120])
    hsv_max = np.array([14, 175, 230])
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    mask = mask[:400,:]
    cv2.imshow("yellow", mask)

    image, contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    detect_count = 0    # 矩形検出された数（デフォルトで0を指定）
    output_screen = mask
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
                    mask, (x, y), (x + w, y + h), (100, 100, 255), 2)
                detect_count += 1
                print("x,y = " + str((x, y)))
    if output_screen is not mask:
        cv2.imshow("yellow", output_screen)
        if x > 325:
            game.make_action([0,1,0,0,0,0])
        elif x < 315:
            game.make_action([1,0,0,0,0,0])
        else:
            game.make_action(actions[5])
    else:
        game.make_action(actions[5])
    return (mask)
