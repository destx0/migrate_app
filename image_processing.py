import cv2
import numpy as np

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return rgb[::-1]

def remove_specific_color(img, target_color, tolerance=30):
    target_color = hex_to_bgr(target_color)
    lower_bound = np.array([max(0, c - tolerance) for c in target_color])
    upper_bound = np.array([min(255, c + tolerance) for c in target_color])
    mask = cv2.inRange(img, lower_bound, upper_bound)
    mask = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(img, img, mask=mask)
    result[mask == 0] = 255
    return result

def increase_contrast(image, alpha=1.5, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def make_greys_darker(image, gamma=0.7):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def process_image(img, target_color, contrast_alpha=1.5, gamma=0.2):
    result = remove_specific_color(img, target_color)
    result = increase_contrast(result, alpha=contrast_alpha)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    result = make_greys_darker(result, gamma=gamma)
    return result