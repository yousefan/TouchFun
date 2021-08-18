import cv2
from lib.Processor import Processor
import time
class TicTacToc:
    
    def __init__(self, cam_id: int, processor: Processor):
        self.cam_id = cam_id
        self.playing = True
        self.processor = processor

    def play(self):
        cap = cv2.VideoCapture(self.cam_id)
        detected_time = 0
        circleid = 0
        while self.playing:
            ret, img = cap.read()
            img, mask_edge, blurred = self.processor.preprocess(img, False)
            if self.processor.detect_ball(blurred) is not None and (time.time() - detected_time) > 3:
                detected_time = time.time()
                circleid += 1
                x, y, r = self.processor.detect_ball(blurred)
                print((x, y, r))
                cv2.imwrite("circ/circles "+str(circleid)+".png", blurred)
                cv2.circle(img, (x, y), r, (255, 0, 0), 3)

            cv2.imshow("orig", img)
            cv2.imshow("mask", mask_edge)
            cv2.imshow("blurred", blurred)

            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                break