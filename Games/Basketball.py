import time

import cv2
import pygame

from lib.Calibration import Calibration
from lib.Processor import Processor


class Basketball:

    def __init__(self, cam_id: int):
        self.cam_id = cam_id
        self.processor = None
        self.calib = Calibration(cam_id)

        self.playing = False
        self.width = 1000
        self.height = 700
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)

        self.left_image = None
        self.right_image = None
        self.FONT = None

        self.w = 640
        self.h = 480

        self.turn = "left"
        self.left_player = None
        self.right_player = None

    def play(self):
        cal = False
        while True:
            cap = cv2.VideoCapture(self.cam_id)
            detected_time = 0
            circleid = 0

            pygame.init()
            window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Basketball")
            self.right_image = self.left_image = pygame.transform.scale(
                pygame.image.load(r"./assets/basketball/basket1.png"), (190, 250))
            self.FONT = pygame.font.SysFont('arial', 40)
            # self.FONT.set_bold(True)

            self.playing = True
            self.turn = "left"

            gap = 20

            left_basket_pos = {
                "x_lower": self.w * 0.1 + gap,
                "x_upper": self.w * 0.1 + self.left_image.get_width() - gap,
                "y_lower": self.h // 2 - self.left_image.get_height() // 2,
                "y_upper": self.h // 2 - self.left_image.get_height() // 2 + self.left_image.get_height() - gap * 2.6
            }

            right_basket_pos = {
                "x_lower": self.w - self.right_image.get_width() - self.w * 0.1 + gap,
                "x_upper": self.w - self.w * 0.1 - gap,
                "y_lower": self.h // 2 - self.left_image.get_height() // 2,
                "y_upper": self.h // 2 - self.left_image.get_height() // 2 + self.left_image.get_height() - gap * 2.6
            }

            self.left_player = Player(hits=10, basket_pos=left_basket_pos)
            self.right_player = Player(hits=10, basket_pos=right_basket_pos)

            window.fill(self.WHITE)

            while self.playing:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.playing = False

                self.render(window)

                if not cal:
                    self.calib.calibrate()
                    self.processor = Processor(self.calib.corners, 0.95)
                    cal = True
                ret, img = cap.read()

                img, mask_edge, blurred = self.processor.preprocess(img, False)
                if self.processor.detect_ball(blurred) is not None and (time.time() - detected_time) > 2.3:
                    detected_time = time.time()
                    circleid += 1
                    x, y, r = self.processor.detect_ball(blurred)
                    # print((x, y, r))
                    cv2.circle(blurred, (x, y), r, (255, 0, 0), 3)
                    cv2.imwrite("circ/circles " + str(circleid) + ".png", blurred)
                    self.on_touch_wall(x, y, r)

                if self.has_finished(window):
                    self.playing = False

                cv2.imshow("blurred", blurred)
                k = cv2.waitKey(20) & 0xFF
                if k == 27:
                    break

    def on_touch_wall(self, circle_x, circle_y, r):
        if self.turn == "left":
            self.turn = "right"
            self.left_player.hit()
            if self.left_player.basket_pos.get("x_lower") < circle_x < self.left_player.basket_pos.get("x_upper") \
                    and self.left_player.basket_pos.get("y_lower") < circle_y < self.left_player.basket_pos.get(
                "y_upper"):
                self.left_player.add_score()
        elif self.turn == "right":
            self.turn = "left"
            self.right_player.hit()
            if self.right_player.basket_pos.get("x_lower") < circle_x < self.right_player.basket_pos.get("x_upper") \
                    and self.right_player.basket_pos.get("y_lower") < circle_y < self.right_player.basket_pos.get(
                "y_upper"):
                self.right_player.add_score()

        print("turn: " + self.turn)

    def render(self, window):
        window.fill(self.WHITE)
        pygame.draw.line(window, self.GRAY, (0, 50), (self.width, 50), 3)

        window.blit(self.left_image, (self.width * 0.1, self.height // 2 - self.left_image.get_height() // 2))
        window.blit(self.right_image, (self.width - self.right_image.get_width() - self.width * 0.1,
                                       self.height // 2 - self.left_image.get_height() // 2))

        text = "Goals: " + str(self.left_player.score) + "   Hits: " + str(self.left_player.hits)
        left_text = self.FONT.render(text, True, self.BLACK)
        left_text_rect = left_text.get_rect()
        left_text_rect.x, left_text_rect.y = self.width * 0.05, 25 - left_text.get_height() // 2
        window.blit(left_text, left_text_rect)

        text = "Goals: " + str(self.right_player.score) + "   Hits: " + str(self.right_player.hits)
        right_text = self.FONT.render(text, True, self.BLACK)
        right_text_rect = right_text.get_rect()
        right_text_rect.x, right_text_rect.y = self.width - self.width * 0.05 - left_text.get_width(), 25 - left_text.get_height() // 2
        window.blit(right_text, right_text_rect)
        pygame.display.update()

    def has_finished(self, window):
        if self.left_player.hits == 0 and self.right_player.hits == 0:
            if self.left_player.score > self.right_player.score:
                self.display_message(window, " Left Player Won!")
                return True
            elif self.right_player.score > self.left_player.score:
                self.display_message(window, " Right Player Won")
                return True
            else:
                self.display_message(window, "It's a draw!")
                return True
        return False

    def display_message(self, window, content):
        pygame.time.delay(500)
        window.fill(self.WHITE)
        end_text = self.FONT.render(content, 1, self.BLACK)
        window.blit(end_text, ((self.width - end_text.get_width()) // 2, (self.width - end_text.get_height()) // 2))
        pygame.display.update()
        pygame.time.delay(3000)


class Player:
    def __init__(self, hits, basket_pos):
        self.hits = hits
        self.total_hits = hits
        self.score = 0
        self.basket_pos = basket_pos

    def add_score(self):
        self.score += 1

    def hit(self):
        self.hits -= 1
