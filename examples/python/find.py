import cv2
import random


def label(labels_buf, screen_buf, actions):
    img = cv2.threshold(labels_buf, 10, 255,
                        cv2.THRESH_BINARY)[1]

    image, contours, hierarchy = cv2.findContours(
        img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cv2.imshow("labels_buf", image)
    cv2.moveWindow('labels_buf', 0, 1000)

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

            print(str(i) + " area = " + str(area), end=", ")
            print("(x,y) = " + str((x, y)), end=" ")

            if w*2.5 > h > w * 2:
                enemy.append(i)
                print("enemy")
            else:
                print("")

            # 矩形の描写
            output_screen = cv2.rectangle(
                output_screen, (x, y), (x + w, y + h), (100, 100, 255), 2)
            # 数字をふる
            cv2.putText(output_screen, str(i), (int(
                x + w / 2), int(y + h / 2)), cv2.FONT_HERSHEY_PLAIN, 2, (255, 150, 150))
            detect_count += 1

    # 矩形を描写した画像の表示
    if 0 < detect_count:
        cv2.imshow("output", output_screen)
        cv2.moveWindow('output', 700, 870)

        # アクションを決める
        if enemy != []:
            x, y, w, h = cv2.boundingRect(contours[enemy[0]])

            dx = 320 - x
            if x > 335:
                action = [0, 1, 0, 0, 0, 0]
            elif x < 305:
                action = [1, 0, 0, 0, 0, 0]
            else:
                if 160 < y+h/2 < 240:
                    action = [0, 0, 1]
                else:
                    action = actions[5]
        else:
            if x > 335:
                action = [0, 1, 0, 0, 0, 0]
            elif x < 305:
                action = [1, 0, 0, 0, 0, 0]
            else:
                action = actions[5]
    else:   # 矩形が見つからないとき探索モード
        choices = [[0, 1, 0], [0, 0, 0, 0, 0, 1]]
        randomchoice = random.randint(0, 1)
        action = choices[randomchoice]

    return (action)
