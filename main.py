from lib.Calibration import Calibration
from lib.Processor import Processor
from Games.TicTacToc import TicTacToc
cam_id = 1
calib = Calibration(cam_id)
calib.calibrate()
proc = Processor(calib.corners)
xo = TicTacToc(cam_id, proc)
xo.play()