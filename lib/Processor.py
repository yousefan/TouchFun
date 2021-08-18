import cv2
import numpy as np


class Processor:
    def __init__(self, corners):
        self.corners = corners
        self.pts1 = np.float32(self.corners)
        self.pts2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])
        self.M = cv2.getPerspectiveTransform(self.pts1, self.pts2)

    def preprocess(self, img, blur=True):
        img = cv2.warpPerspective(img, self.M, (img.shape[1], img.shape[0]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 5, 0)
        if blur:
            mask_edge = cv2.Canny(blurred, 50, 150)
        else:
            mask_edge = cv2.Canny(gray, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        mask_edge = cv2.dilate(mask_edge, kernel)

        return img, mask_edge, blurred

    @staticmethod
    def detect_edges(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask_edge = cv2.Canny(gray, 50, 150)
        return mask_edge

    @staticmethod
    def detect_ball(img):
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT_ALT, 1, 20,
                                   param1=50, param2=0.84,
                                   minRadius=15, maxRadius=200)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            circle = circles[0, :]
            circle = circle[0]
            x, y, radius = circle[0], circle[1], circle[2]
            return x, y, radius
        else:
            return None
