import numpy as np
import cv2


def limpieza(imagen, erosion, dilatacion, kblur):
    # Convertir a escala de grises
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    kernel_ero = np.ones(erosion, np.uint8)
    kernel_dil = np.ones(dilatacion, np.uint8)

    # Aplicar Dilatacion
    erosion = cv2.erode(gray, kernel_ero, iterations=1)

    # Aplicar blur
    blur = cv2.blur(erosion, kblur)

    # Umbralización
    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV)

    # Aplicar Dilatacion
    dilatacion = cv2.dilate(mask, kernel_dil, iterations=1)

    return dilatacion


def calculo_hsv(h_prom, s_prom, v_prom, imagen, hsv):
    anchura, altura, _ = np.shape(imagen)
    h, s, v = cv2.split(hsv)

    # Matrices Blanca y Negra
    white = np.full(h.shape + (3,), 255, np.uint8)
    black = np.full(h.shape + (3,), 0, np.uint8)

    h_condition = np.abs(h - h_prom) < 10
    t_condition = np.sqrt((s - s_prom) ** 2 + (v - v_prom) ** 2) < 50

    dilatacion = limpieza(
        # Matriz condicional
        np.where(np.logical_and(h_condition, t_condition)[..., None], black, white),
        (5, 5),
        (51, 51),
        (21, 21)
    )

    contornos, hierarchy = cv2.findContours(dilatacion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    imagen_leyenda = cv2.putText(imagen, str(len(contornos)), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    return cv2.drawContours(imagen_leyenda, contornos, -1, (0, 255, 0), 3)
