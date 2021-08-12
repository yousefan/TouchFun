import cv2
import imutils
from numpy import savetxt, loadtxt


class Calibration:
    def __init__(self, cam_id):
        self.corners = []
        self.cam_img = None
        self.cam_id = cam_id

    def on_click_select_corner(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.cam_img, (x, y), 5, (255, 255, 255), -1)
            self.corners.append([x, y])

    def calibrate(self):
        cap = cv2.VideoCapture(self.cam_id)
        self.corners = []
        cv2.namedWindow('camera calibration')
        cv2.setMouseCallback('camera calibration', self.on_click_select_corner)
        rows = cols = 0
        while len(self.corners) < 4:
            ret, self.cam_img = cap.read()
            self.cam_img = imutils.resize(self.cam_img)
            cv2.imshow('camera calibration', self.cam_img)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                break
        self.write_calibration()
        cap.release()
        cv2.destroyWindow('camera calibration')


    def read_calibration(self):
        self.corners = loadtxt('calib.csv', delimiter=',').astype('int')

    def write_calibration(self):
        savetxt('calib.csv', self.corners, delimiter=',')
