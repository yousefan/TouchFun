import time

import cv2
import pygame

from lib.Calibration import Calibration
from lib.Processor import Processor


class TicTacToc:

    def __init__(self, cam_id: int):
        self.cam_id = cam_id
        self.processor = None
        self.calib = Calibration(cam_id)

        self.playing = False
        self.width = 700
        self.ROWS = 3
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)

        self.x_image = None
        self.o_image = None
        self.END_FONT = None

        self.w = 640
        self.h = 480

        self.turn = "x"
        self.hit_cells = []

    def play(self):
        cal = False
        while True:
            cap = cv2.VideoCapture(self.cam_id)
            detected_time = 0
            circleid = 0

            pygame.init()
            window = pygame.display.set_mode((self.width, self.width))
            pygame.display.set_caption("Tic Tac Toc")
            self.x_image = pygame.transform.scale(pygame.image.load(r"./assets/tictactoc/x.png"), (150, 150))
            self.o_image = pygame.transform.scale(pygame.image.load(r"./assets/tictactoc/o.png"), (150, 150))
            self.END_FONT = pygame.font.SysFont('arial', 40)
            self.END_FONT.set_bold(True)

            self.playing = True
            self.hit_cells = []
            game_array = self.initialize_grid()
            window.fill(self.WHITE)
            while self.playing:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # pygame.quit()
                        self.playing = False
                self.render(window)
                if self.has_won(window, game_array) or self.has_drawn(window, game_array):
                    self.playing = False

                if not cal:
                    self.calib.calibrate()
                    self.processor = Processor(self.calib.corners)
                    cal = True
                ret, img = cap.read()
                img, mask_edge, blurred = self.processor.preprocess(img, False)
                if self.processor.detect_ball(blurred) is not None and (time.time() - detected_time) > 3:
                    detected_time = time.time()
                    circleid += 1
                    x, y, r = self.processor.detect_ball(blurred)
                    print((x, y, r))
                    cv2.circle(blurred, (x, y), r, (255, 0, 0), 3)
                    cv2.imwrite("circ/circles " + str(circleid) + ".png", blurred)
                    game_array = self.on_touch_wall(x, y, r, game_array)

                cv2.imshow("blurred", blurred)
                k = cv2.waitKey(20) & 0xFF
                if k == 27:
                    break

    def on_touch_wall(self, circle_x, circle_y, r, game_array):

        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                x_lower, x_upper, y_lower, y_upper, x_img, y_img, char, can_hit = game_array[i][j]

                # distance = math.sqrt((x - circle_x) ** 2 + (y - circle_y) ** 2)
                if x_lower < circle_x < x_upper and y_lower < circle_y < y_upper and can_hit:
                    if self.turn == "x":
                        self.hit_cells.append((x_img, y_img, self.x_image))
                        game_array[i][j] = (x_lower, x_upper, y_lower, y_upper, x_img, y_img, "x", False)
                        self.turn = "o"

                    elif self.turn == "o":
                        self.hit_cells.append((x_img, y_img, self.o_image))
                        game_array[i][j] = (x_lower, x_upper, y_lower, y_upper, x_img, y_img, "o", False)
                        self.turn = "x"
        print("turn: " + self.turn)
        return game_array

    def render(self, window):

        self.draw_grid(window)

        for image in self.hit_cells:
            x, y, img = image
            window.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
        pygame.display.update()

    def draw_grid(self, window):
        gap = self.width // self.ROWS
        x = y = 0
        for i in range(self.ROWS):
            x = i * gap
            pygame.draw.line(window, self.GRAY, (x, 0), (x, self.width), 3)
            pygame.draw.line(window, self.GRAY, (0, x), (self.width, x), 3)

    def has_drawn(self, window, game_array):
        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                if game_array[i][j][6] == "":
                    return False

        self.display_message(window, "It's a draw!")
        return True

    def has_won(self, window, game_array):
        # Checking rows
        for row in range(len(game_array)):
            if (game_array[row][0][6] == game_array[row][1][6] == game_array[row][2][6]) and game_array[row][0][
                6] != "":
                self.display_message(window, game_array[row][0][6].upper() + " has won!")
                return True

        # Checking columns
        for col in range(len(game_array)):
            if (game_array[0][col][6] == game_array[1][col][6] == game_array[2][col][6]) and game_array[0][col][
                6] != "":
                self.display_message(window, game_array[0][col][6].upper() + " has won!")
                return True

        # Checking main diagonal
        if (game_array[0][0][6] == game_array[1][1][6] == game_array[2][2][6]) and game_array[0][0][6] != "":
            self.display_message(window, game_array[0][0][6].upper() + " has won!")
            return True

        # Checking reverse diagonal
        if (game_array[0][2][6] == game_array[1][1][6] == game_array[2][0][6]) and game_array[0][2][6] != "":
            self.display_message(window, game_array[0][2][6].upper() + " has won!")
            return True

        return False

    def display_message(self, window, content):
        pygame.time.delay(500)
        window.fill(self.WHITE)
        end_text = self.END_FONT.render(content, 1, self.BLACK)
        window.blit(end_text, ((self.width - end_text.get_width()) // 2, (self.width - end_text.get_height()) // 2))
        pygame.display.update()
        pygame.time.delay(3000)

    def initialize_grid(self):
        cell_width = self.w // self.ROWS
        cell_height = self.h // self.ROWS
        dis_to_cen = self.width // self.ROWS // 2
        game_array = [[None, None, None],
                      [None, None, None],
                      [None, None, None]]
        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                x_img = dis_to_cen * (2 * j + 1)
                y_img = dis_to_cen * (2 * i + 1)
                x_lower = cell_width * j
                x_upper = cell_width * (j + 1)
                y_lower = cell_height * i
                y_upper = cell_height * (i + 1)
                game_array[i][j] = (x_lower, x_upper, y_lower, y_upper, x_img, y_img, "", True)
        return game_array
