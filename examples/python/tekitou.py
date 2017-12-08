import cv2


def tekitou(labels_buf):
    enemy1 = cv2.imread('images/lifebox.png')

    # A-KAZE検出器の生成
    akaze = cv2.AKAZE_create()

    # 特徴量の検出と特徴量ベクトルの計算
    kp1, des1 = akaze.detectAndCompute(labels_buf, None)
    kp2, des2 = akaze.detectAndCompute(enemy1, None)

    # Brute-Force Matcher生成
    bf = cv2.BFMatcher()
    # 特徴量ベクトル同士をBrute-Force＆KNNでマッチング
    matches = bf.knnMatch(des1, des2, k=2)

    # データを間引きする
    ratio = 0.5
    good = []
    for m, n in matches:
        if m.distance < ratio * n.distance:
            good.append([m])

    # 対応する特徴点同士を描画
    img3 = cv2.drawMatchesKnn(labels_buf, kp1, enemy1, kp2, good[:], None, flags=2)

    # 画像表示
    cv2.imshow('kaze', img3)
    cv2.moveWindow('kaze', 700, 0)
