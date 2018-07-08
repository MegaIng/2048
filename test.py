from __future__ import annotations

from threading import Thread

from board import Board
from ki_controller import PredictController
from pygame_connection import PygameConnection, BoardConnection
from pygame_mainloop import PygameMainloop

pycon = PygameConnection()
loop = PygameMainloop([pycon], [pycon], (640, 400), 60)
bdcon = BoardConnection(pycon)
board = Board((4, 4))
loop.start_background()
Thread(target=board.run, args=([bdcon], PredictController()), daemon=True).start()
# board.run([bdcon], PredictController())
