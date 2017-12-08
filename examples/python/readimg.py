import cv2
import numpy as np


img = cv2.imread("teki.png")
img = img[:700, 700: ]
cv2.imshow("color", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
