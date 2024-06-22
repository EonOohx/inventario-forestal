# !/usr/bin/env python
# coding: utf-8
import random
import cv2 as cv
import numpy as np
import tkinter as tk


class update_hsv:
    def __init__(self):

        self.image = None
        self.binary = None

    def Image_Processing(self, hsv_range):

        (lowerb, upperb) = hsv_range

        color_mask = self.image.copy()

        hsv_img = cv.cvtColor(self.image, cv.COLOR_BGR2HSV)

        color = cv.inRange(hsv_img, lowerb, upperb)

        color_mask[color == 0] = [0, 0, 0]

        gray_img = cv.cvtColor(color_mask, cv.COLOR_RGB2GRAY)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))

        dst_img = cv.morphologyEx(gray_img, cv.MORPH_CLOSE, kernel)

        ret, binary = cv.threshold(dst_img, 10, 255, cv.THRESH_BINARY)

        # _, contours, heriachy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) #python2
        contours, heriachy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # python3
        return contours, binary

    def draw_contours(self, hsv_name, contours):
        x = 0
        y = 0
        for i, cnt in enumerate(contours):

            mm = cv.moments(cnt)
            if mm['m00'] == 0:
                continue
            cx = mm['m10'] / mm['m00']
            cy = mm['m01'] / mm['m00']

            (x, y) = (np.int(cx), np.int(cy))

            area = cv.contourArea(cnt)

            if area > 200:

                cv.circle(self.image, (x, y), 5, (0, 0, 255), -1)

                rect = cv.minAreaRect(cnt)

                box = cv.boxPoints(rect)

                box = np.int0(box)

                cv.drawContours(self.image, [box], 0, (255, 0, 0), 2)
                cv.putText(self.image, hsv_name, (int(x - 15), int(y - 15)),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        return x,y

    def get_contours(self, img, color_hsv):
        binary = None

        self.image = cv.resize(img, (320, 240), )
        for key, value in color_hsv.items():

            color_contours, binary = self.Image_Processing(color_hsv[key])

            x,y = self.draw_contours(key, color_contours)
        return self.image, binary, x, y

