import cv2
import random
import numpy as np

def label(labels_buf, screen_buf, actions, action, repeat, lock, pre_finders, pre2_finders):
    current_finders = []
    img = cv2.threshold(labels_buf, 10, 255,

                        cv2.THRESH_BINARY)[1]

    for i in range(0,230):
        img[400][i] = 0
    for i in range(400,640):
        img[400][i] = 0

    image, contours, hierarchy = cv2.findContours(
        img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    detect_count = 0    # 矩形検出された数（デフォルトで0を指定）
    enemy = []

    output_screen = screen_buf
    for i in range(0, len(contours)):   # 各輪郭に対する処理
        area = cv2.contourArea(contours[i])  # 輪郭の領域を計算
        if area < 20 or area > 50000:    # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
            continue
        # 外接矩形
        if len(contours[i]) > 0:
            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect)
            rect_area = w * h
            dS = rect_area - area
            DS = int((dS / area) * 100)
            # print(str(i) + " DS = " + str(DS) +
            #       " (x,y) = " + str((x, y)), end=", ")
            current_finders.append([i, x, y, w, h])

            if w * 2.5 > h > w * 1.3:
                if DS >= 70:
                    enemy.append(i)
                    print("enemy" + str(DS))
                # else:
                    # print("")
            # else:
                # print("")

            # 矩形の描写
            output_screen = cv2.rectangle(
                output_screen, (x, y), (x + w, y + h), (100, 100, 255), 2)
            # 数字をふる
            cv2.putText(output_screen, str(i), (int(
                x), int(y)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 150, 150))
            detect_count += 1

        # 矩形を描写した画像の表示
        cv2.imshow("output", output_screen)
        cv2.moveWindow('output', 1280, 0)

    if 0 < detect_count:
        # アクションを決める
        if enemy != []:
            x, y, w, h = cv2.boundingRect(contours[enemy[0]])

            dx = 321 - x
            center = x + w/2
            print(dx)
            if 340 < center:
                action = [0, 0, 0, 0, 0, 0, 0, 5, 0]
            elif 327 < center <= 340:
                action = [0, 0, 0, 0, 0, 0, 0, 1, 0]
            elif 321 < center <= 327:
                action = [0, 0, 1, 0, 0, 0, 0, 1, 0]
            elif 313 <= center <= 321:
                action = [0, 0, 1, 0, 0, 0, 0, -1, 0]
            elif 300 <= center < 313:
                action = [0, 0, 0, 0, 0, 0, 0, -1, 0]
            elif center < 300:
                action = [0, 0, 0, 0, 0, 0, 0, -5, 0]
            else:
                if 190 < y and y+h < 210:
                    action = [0, 0, 1]
                else:
                    action = actions[5]
        else:
            if y >= 30:
                if x > 335:
                    action = [0, 1, 0, 0, 0, 0]
                elif x < 305:
                    action = [1, 0, 0, 0, 0, 0]
                else:
                    action = actions[5]

    # 前のフレームと比較
    if pre_finders != []:
        if current_finders == []:
            repeat = [3, actions[5], "パックを取得"]
        elif pre2_finders == current_finders and lock == 0:
            # repeat = [5, actions[5], "首振り解除"]
            action = [0, 0, 0, 0, 0, 0, 0, 80]
    pre2_finders = pre_finders
    pre_finders = current_finders

    return (action, repeat, pre_finders, pre2_finders)


def depth(depth_buf, actions, repeat):
    x_left = 250
    x_right = 390
    y_range = [240,350]
    left = right = 0

    for y in range(y_range[0], y_range[1]):
        left += depth_buf[y][x_left]
        right += depth_buf[y][x_right]

    left = int(left / 110)
    right = int(right / 110)

    # print("left = " + str(left) + ", right = " + str(right))
    if left <= 7 and right <= 7:
        repeat = [1, [0,0,0,0,0,0,0,70,0], "前方に壁"]
    elif left <= 7:
        repeat = [2, [0,0,0,1,0,1,0,0,0], "左が暗いので右へ移動"]
    elif right <= 7:
        repeat = [2, [0,0,0,0,1,1,0,0,0], "右が暗いので左へ移動"]
    elif left <= 10:
        repeat = [2, [0,1,0,0,0,1,0,0,0], "左に障害物あり、射撃をロック"]
    elif right <= 10:
        repeat = [2, [1,0,0,0,0,1,0,0,0], "右に障害物あり、射撃をロック"]

    return (repeat)
