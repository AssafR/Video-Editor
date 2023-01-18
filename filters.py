import cv2 as cv2
import numpy as np


def flip_image(img):
    return cv2.flip(img, 1)


def find_rectangle(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# new_img = cv2.line(image, start_point, end_point, color, thickness)

img = cv2.imread(r'C:\Users\Assaf\Dropbox\Program\VideoSamples\20221208_202936.jpg')
img = cv2.resize(img, dsize=(800, 600), fx=0.5, fy=0.5)

gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

cnts = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
cnts_filtered = []

for cnt in cnts:
    area = cv2.contourArea(cnt)
    if area < 30000:
        continue
    cnts_filtered.append(cnt)
    num_vtx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
    print(f'vertices: {len(num_vtx)} , area: {area}')
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    print(rect)
    box = np.int0(box)
    cv2.drawContours(img, [box], 0, (0, 0, 255), 2) # Draw rectangle in red

cv2.drawContours(img, cnts_filtered, -1, (0, 255, 0), 3) # Draw original contour in green

cv2.imshow('image', img)
cv2.imshow('Binary', thresh_img)
cv2.waitKey()
