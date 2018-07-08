from __future__ import annotations

from colorsys import hsv_to_rgb
from time import sleep
from typing import List, Tuple

from board import BoardRenderer, BoardType, Move, MoveDirection, BoardController, Pos
from pygame_mainloop import PygameSurfaceRenderer, PygameEventHandler, pygame


class PygameConnection(PygameSurfaceRenderer, PygameEventHandler):
    def __init__(self):
        self.board = None
        self.last_pressed = None
        self.font = None
        self.font_big = None
        self.animation_total = 0
        self.animation_counter = 0
        self.animation_tiles: List[Tuple[Pos, Pos, int]] = None
        self.text_overlay = None

    def handle(self, event: pygame.event.EventType):
        if event.type == self.pygame.KEYDOWN:
            if event.key == self.pygame.K_UP:
                self.last_pressed = MoveDirection.UP
            elif event.key == self.pygame.K_DOWN:
                self.last_pressed = MoveDirection.DOWN
            elif event.key == self.pygame.K_LEFT:
                self.last_pressed = MoveDirection.LEFT
            elif event.key == self.pygame.K_RIGHT:
                self.last_pressed = MoveDirection.RIGHT
            else:
                self.last_pressed = None

    def render(self, screen: pygame.Surface, clock: pygame.time.Clock):
        if self.font is None:
            self.font = self.pygame.font.SysFont("arial", 20)
            self.font_big = self.pygame.font.SysFont("arial", 100)
        screen.fill((255, 255, 255))
        sw, sh = screen.get_size()
        if self.board is not None:
            bw, bh = len(self.board), len(self.board[0])
            ts = (min(sw, sh) - 5 * (min(bw, bh) - 1) - 50) / min(bw, bh)
            iw, ih = int(bw * ts + (bw - 1) * 5), int(bh * ts + (bh - 1) * 5)
            ox, oy = (sw - iw) // 2, (sh - ih) // 2
            screen.fill((200, 200, 200), (ox, oy, iw, ih))
            if self.animation_counter >= self.animation_total:
                for x, c in enumerate(self.board):
                    for y, v in enumerate(c):
                        if v:
                            s = self.font.render(str(2 ** v), True, (0, 0, 0))
                            r, g, b = hsv_to_rgb(v / 7 % 1, 1 - (v / 13) % 1, 1)
                            color = (int(r * 255), int(g * 255), int(b * 255))
                            screen.fill(color, (ox + (ts + 5) * x, oy + (ts + 5) * y, ts, ts))
                            r = s.get_rect(center=(ox + (ts + 5) * x + ts // 2, oy + (ts + 5) * y + ts // 2))
                            screen.blit(s, r)
                        else:
                            screen.fill((150, 150, 150), (ox + (ts + 5) * x, oy + (ts + 5) * y, ts, ts))
            else:
                for x, c in enumerate(self.board):
                    for y, v in enumerate(c):
                        screen.fill((150, 150, 150), (ox + (ts + 5) * x, oy + (ts + 5) * y, ts, ts))
                self.animation_counter += 1
                f = self.animation_counter / self.animation_total
                for (sx, sy), (ex, ey), v in self.animation_tiles:
                    x, y = sx + (ex - sx) * f, sy + (ey - sy) * f
                    s = self.font.render(str(2 ** v), True, (0, 0, 0))
                    r, g, b = hsv_to_rgb(v / 7 % 1, 1 - (v / 13) % 1, 1)
                    color = (int(r * 255), int(g * 255), int(b * 255))
                    screen.fill(color, (ox + (ts + 5) * x, oy + (ts + 5) * y, ts, ts))
                    r = s.get_rect(center=(ox + (ts + 5) * x + ts // 2, oy + (ts + 5) * y + ts // 2))
                    screen.blit(s, r)
        if self.text_overlay:
            s = self.font_big.render(self.text_overlay, True, (0, 0, 0))
            r = s.get_rect(center=(sw // 2, sh // 2))
            img = self.pygame.Surface(r.inflate(10, 10).size, self.pygame.SRCALPHA)
            img.fill((255, 255, 255, 150))
            screen.blit(img, r.inflate(10, 10))
            screen.blit(s, r)


class BoardConnection(BoardRenderer, BoardController):
    def get_input(self, board: BoardType):
        while self.connection.last_pressed is None:
            sleep(0.1)
        d = self.connection.last_pressed
        self.connection.last_pressed = None
        return d

    connection: PygameConnection

    def __init__(self, connection: PygameConnection):
        self.connection = connection

    def restart(self, board: BoardType):
        self.connection.board = board

    def display_move(self, move: MoveDirection, new_board: BoardType, old_board: BoardType, moves: List[Move]):
        self.connection.board = new_board
        sp_ep = {sp: ep for sp, ep, _ in moves}
        sp_ep.update({(x, y): (x, y) for x, c in enumerate(old_board) for y, v in enumerate(c) if v and (x, y) not in sp_ep})
        self.connection.animation_tiles = [(sp, ep, old_board[sp[0]][sp[1]]) for sp, ep in sp_ep.items()]
        self.connection.animation_total = 6
        self.connection.animation_counter = 0
        while self.connection.animation_counter < self.connection.animation_total:
            sleep(0.1)

    def should_restart(self):
        return True

    def died(self, board: BoardType):
        self.connection.text_overlay = "Lose"
        sleep(1)
        self.connection.text_overlay = None
