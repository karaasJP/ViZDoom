from __future__ import print_function
from vizdoom import *
from random import choice
import sys

import cv2
import numpy as np

from time import sleep

game = DoomGame()

# Use CIG example config or your own.
game.load_config("../../scenarios/cig.cfg")

game.set_doom_map("map01")  # Limited deathmatch.
#game.set_doom_map("map02")  # Full deathmatch.

game.set_screen_format(ScreenFormat.RGB24)

# Join existing game.
game.add_game_args("-join 127.0.0.1") # Connect to a host for a multiplayer game.

# Name your agent and select color
# colors: 0 - green, 1 - gray, 2 - brown, 3 - red, 4 - light gray, 5 - light brown, 6 - light red, 7 - light blue
game.add_game_args("+name KOMONO +colorset 0")

# During the competition, async mode will be forced for all agents.
#game.set_mode(Mode.PLAYER)
game.set_mode(Mode.ASYNC_PLAYER)

# Sets resolution for all buffers.
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

#game.set_window_visible(False)

game.init()
# sleep_time = 1.0 / DEFAULT_TICRATE  # = 0.028
sleep_time = 0.01


# Three example sample actions
actions = [[1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0],[0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0,0],[0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,1]]

#-------------------------------------------------------------------
def extract_color(src, low_array, high_array):

    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    lower = np.array(low_array)
    upper = np.array(high_array)

    img_mask = cv2.inRange(hsv, lower, upper)
    img_color = cv2.bitwise_and(src, src, mask=img_mask)
    gray_color = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
#    cv2.imshow("SHOW COLOR IMAGE", gray_color)

    ret,thresh = cv2.threshold(gray_color,10,255,cv2.THRESH_BINARY)
    return thresh


def start_green():
        tri=screen[0:400,0:640]
        green_image= extract_color(tri, [20,100,100], [100,255,255])
        contours,_ = cv2.findContours(green_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        mono = [[0 for i in range(4)] for j in range(len(contours))]
        area=[[0 for i in range(1)]for j in range(len(contours))]
        j=0
        maxarea=[0,0,0]
        for i in range(len(contours)):
            area[i] = cv2.contourArea(contours[i])
            cnt =contours[i]
            cv2.drawContours(green_image, contours, -1, (255,255,255),3)
            x,y,w,h = cv2.boundingRect(cnt)
            mono[i]=[x,y,w,h]
            if i==0:
               maxarea[0]=area[0]
            else:
              if area[i-1]>area[i]:
                 maxarea[0]=area[i-1]
                 j=i-1
              else:
                 maxarea[0]=area[i]
                 j=i
        if len(contours)==0:
              mono=[[0,0,0,0],[0,0,0,0]]
        maxarea[1]=mono[j][0]
        maxarea[2]=mono[j][2]
        print("start green=" +str(maxarea))
        if maxarea[0]>200:
            return 1
        return 0


def kamen():
    tri=screen[0:400,0:640]
    blue_image= extract_color(tri, [100,0,0], [360,255,255])
    contours,_ = cv2.findContours(blue_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#    cv2.imshow('blue', blue_image)
    kamen = [[0 for i in range(4)] for j in range(len(contours))]
    for i in range(len(contours)):
        cnt =contours[i]
        cv2.drawContours(blue_image, contours, -1, (255,255,255),3)
        x,y,w,h = cv2.boundingRect(cnt)
        if w>1:
            kamen[i]=[x,y,w,h]

    if len(kamen)==0:
        return [0,0,0,0]
    max=0
    for i in range(len(kamen)):
        if kamen[max][2]*kamen[max][3]<kamen[i][2]*kamen[i][3]:
            max=i
    print("kamennnnnnnnnnnnnnnn")
    return kamen[i]



def maxwall():
        state = game.get_state()
        if not game.is_episode_finished():
          depth = state.depth_buffer
          x1 = 0
          y1 = 0
          width = 640
          height = 300
          tri = depth[y1:y1+height,x1:x1+width]

          ret,thresh = cv2.threshold(tri,8,255,cv2.THRESH_BINARY_INV)
          contours,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

          mono = [[0 for i in range(4)] for j in range(len(contours))]
          area=[[0 for i in range(1)]for j in range(len(contours))]
          j=0
          maxarea=[0,0,0]
          for i in range(len(contours)):
              area[i] = cv2.contourArea(contours[i])
              cnt =contours[i]
              cv2.drawContours(thresh, contours, -1, (255,255,255),3)
#              cv2.imshow('kabe',thresh)
              x,y,w,h = cv2.boundingRect(cnt)
              mono[i]=[x,y,w,h]
              if i==0:
                 maxarea[0]=area[0]
              else:
                if area[i-1]>area[i]:
                   maxarea[0]=area[i-1]
                   j=i-1
                else:
                   maxarea[0]=area[i]
                   j=i
          if len(contours)==0:
                mono=[[0,0,0,0],[0,0,0,0]]
          maxarea[1]=mono[j][0]
          maxarea[2]=mono[j][2]
          print("maxarea=" +str(maxarea))
          return maxarea


def get_rect(xx, ww):
        x1 = 0
        y1 = 0
        width = 640
        height = 500
        tri = labels[y1:y1+height,x1:x1+width]

        ret,thresh = cv2.threshold(tri,100,255,cv2.THRESH_BINARY)
        contours,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#        print(len(contours)
        teki = [[0 for i in range(4)] for j in range(len(contours))]
        bingo=-1
        for i in range(len(contours)):
         cnt =contours[i]
         cv2.drawContours(thresh, contours, -1, (255,255,255),3)
#         cv2.imshow('rinkaku',thresh)
         x,y,w,h = cv2.boundingRect(cnt)
         teki[i]=[x,y,w,h]
         if x<=xx and (x+w)>=(xx+ww):
           bingo=i

        if bingo==-1:
          return [0,0,0,0]
        else:
          print(teki[bingo])
          return teki[bingo]


def get_centerx():
    kamenzahyo=kamen()
    [x,y,w,h]=get_rect(kamenzahyo[0], kamenzahyo[2])
    return (x+w)/2-315


def get_action():

    dx=get_centerx()
    print("dx=" + str(dx))





    if abs(dx)<25:
        print("shoot")
        return actions[2] #shoot
    if dx>0:
        print("right")
        return actions[6] #right
    if dx==-315:
        maxarea=[0,0]
        maxarea=maxwall()
        if maxarea[0]>60000:
            if maxarea[1]<450 and maxarea[1]!=1:
                print("Rwall")
                return actions[0] #turn left
            elif maxarea[1]==1 and maxarea[2]>150:
                print("Lwall")
                return actions[1] #turn right
        print("foward")
        return actions[5]#foword
    print("left")
    return actions[4] #left






 #----------------------------------------------------------

# Get player's number
player_number = int(game.get_game_variable(GameVariable.PLAYER_NUMBER))
last_frags = 0

# Play until the game (episode) is over.
while not game.is_episode_finished():

    # Get the state.
#    s = game.get_state()

    # Analyze the state.
    state = game.get_state()
    screen = state.screen_buffer
    depth = state.depth_buffer
    labels = state.labels_buffer
    # cv2.imshow('labels', labels)
    set_action=get_action()
    if start_green()==1:
        set_action=actions[5]

    if sleep_time > 0:
        sleep(sleep_time)
        cv2.waitKey(int(sleep_time * 1000))

    # Make your action.
    game.make_action(set_action)
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
