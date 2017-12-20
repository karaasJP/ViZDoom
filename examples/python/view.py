import cv2


def IMSHOW(depth_buf, automap_buf, output_screen):
    cv2.imshow('depth_buf', depth_buf)
    cv2.moveWindow('depth_buf', 0, 500)

    cv2.imshow('automap_buf', automap_buf)
    cv2.moveWindow('automap_buf', 0, 0)

    # cv2.imshow('labels_buf', labels_buf)
    # cv2.moveWindow('labels_buf', 0, 1000)

    # cv2.imshow("rect_buf", rect)
    # cv2.moveWindow('rect_buf', 1280, 0)

    # 矩形を描写した画像の表示
    #cv2.imshow("output", output_screen)
    #cv2.moveWindow('output', 0, 480)
