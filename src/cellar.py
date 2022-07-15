'''
現状使わないけど残しておきたい関数置き場
'''

import pyautogui
import cv2
import numpy as np

from PIL import Image, ImageEnhance, ImageOps, ImageDraw




def ScreenShot(x1, y1, x2, y2):
    sc = pyautogui.screenshot(region=(x1, y1, x2, y2))
    sc.save('TransActor.jpg')
    img = cv2.imread('TransActor.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tmp = cv2.resize(gray, (gray.shape[1]*2, gray.shape[0]*2), interpolation=cv2.INTER_LINEAR)
    cv2.imwrite('TransActor.jpg', tmp)




def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image




def findRect(path_to_img, paint = False):
    rate = 1

    image = Image.open(path_to_img)
    # image_cv = pil2cv(image)
    image_cv = cv2.imread(path_to_img)
    lines = image_cv.copy()
    lines = cv2.resize(lines, dsize=None, fx=rate, fy=rate)

    # 輪郭を抽出する
    canny = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    canny = cv2.GaussianBlur(canny, (5, 5), 0)
    canny = cv2.resize(canny, dsize=None, fx=rate, fy=rate)
    canny = cv2.Canny(canny, 150, 200) # (input, 線の延長, エッジ検出の閾値)
    # cv2.imshow('canny', canny)
    cv2.imwrite('canny.png', canny)

    cnts, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 抽出した輪郭に近似する直線（？）を探す。
    cnt_count = {}
    for cnt in cnts:
        key = len(cnt)
        if key in cnt_count:
            cnt_count[key] += 1
        else:
            cnt_count[key] = 1

    print(sorted(cnt_count.items(), key=lambda x:x[0]))
    cnts_sorted = sorted(cnts, key=cv2.contourArea, reverse=True)
    print(cv2.contourArea(cnts_sorted[0]))
    print(cv2.contourArea(cnts_sorted[1]))
    print(cv2.contourArea(cnts_sorted[2]))
    print(cv2.contourArea(cnts_sorted[10]))
    # cnts.sort(key=cv2.contourArea, reverse=True) # 面積が大きい順に並べ替える。

    for c in cnts:
        if (cv2.contourArea(c) < 3000): continue; # 面積が小さい場合は表示しない

        arclen = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*arclen, True)

        if len(approx) == 4:
            cv2.drawContours(lines, [approx], -1, (0, 0, 255), 2)
        else:
            cv2.drawContours(lines, [approx], -1, (0, 255, 0), 2)

        for pos in approx:
            cv2.circle(lines, tuple(pos[0]), 4, (255, 0, 0))

    # cv2.imshow('edge', lines)
    cv2.imwrite('edge.png', lines)