import cv2
import numpy as np


# H, S, V, GIRO
# AMARILLO = [30, 240, 253, 0]
# AZUL = [100, 255, 227, 1]
# ROJO = [0, 161, 255, 0]
# VERDE = [71, 163, 201, 1]

def procesamiento_imagen(img_hsv, color):
    h, s, v = cv2.split(img_hsv)
    m_negro = np.full(h.shape + (3,), 0, np.uint8)
    condicion_h = np.logical_and(h > color[0] - 5, h < color[0] + 5)
    # condicion_s = np.logical_and(condicion_h, s > color[1]-2, s < color[1]+2)
    # condicion_v = np.logical_and(condicion_s, v > color[2]-2, v < color[2]+2)
    imagen_final = np.where(condicion_h[..., None], img_hsv, m_negro)
    gray = cv2.cvtColor(cv2.cvtColor(imagen_final, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
    _, thrash = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thrash, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours:
        return cv2.contourArea(max(contours, key=cv2.contourArea)) >= 1000


def Image_Processing(image):
    lowerb = (0, 43, 46)
    upperb = (10, 255, 255)

    color_mask = image.copy()

    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color = cv2.inRange(hsv_img, lowerb, upperb)

    color_mask[color == 0] = [0, 0, 0]

    gray_img = cv2.cvtColor(color_mask, cv2.COLOR_RGB2GRAY)

    ret, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY)
    
    cv2.imshow("WM_DELETE_WINDOW", binary)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    contours, heriachy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # python3}
    if contours:
        print(str(cv2.contourArea(max(contours, key=cv2.contourArea))))
    return 1100 < v2.contourArea(max(contours, key=cv2.contourArea)) < 1500

def detectar_color(img, parametros_color):
    return procesamiento_imagen(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), parametros_color)