from __future__ import annotations

from enum import Enum
from random import choice
from typing import List, Tuple


class MoveDirection(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


BoardType = List[List[int]]
Pos = Size = Tuple[int, int]
Move = Tuple[Pos, Pos, bool]


class Board:
    size: Size
    board: BoardType

    def __init__(self, size: Size):
        self.size = size
        self.reset_board()

    def reset_board(self):
        self.board = [[0 for _ in range(self.size[1])] for _ in range(self.size[0])]

    def generate_random(self) -> Pos:
        x, y = choice([(x, y) for x in range(self.size[0]) for y in range(self.size[1]) if self.board[x][y] == 0])
        self.board[x][y] = choice((1,) * 9 + (2,))
        return x, y

    def run(self, renderers: List[BoardRenderer], controller: BoardController):
        self.reset_board()
        self.generate_random()
        self.generate_random()
        for renderer in renderers:
            renderer.restart(self.board)
        while self.can_move():
            d = controller.get_input(self.board)
            old, self.board, moves = move(self.board, d)
            if moves:
                self.generate_random()
            for renderer in renderers:
                renderer.display_move(d, self.board, old, moves)
            if not self.can_move():
                for renderer in renderers:
                    renderer.died(self.board)
                if controller.should_restart():
                    self.reset_board()
                    self.generate_random()
                    self.generate_random()
                    for renderer in renderers:
                        renderer.restart(self.board)

    def can_move(self):
        return any(v == 0 for c in self.board for v in c) or any(
            v in (self.board[x][y - 1] if y > 0 else -1,
                  self.board[x][y + 1] if y < self.size[1] - 1 else -1,
                  self.board[x - 1][y] if x > 0 else -1,
                  self.board[x + 1][y] if x < self.size[0] - 1 else -1,
                  ) for x, c in enumerate(self.board) for y, v in enumerate(c))


def move(board: BoardType, direction: MoveDirection) -> Tuple[BoardType, BoardType, List[Move]]:
    old, board = board, [c[:] for c in board]
    size = len(board), len(board[0])
    already_merged = []
    moves = []
    if direction == MoveDirection.UP:
        for x in range(size[0]):
            for y in range(1, size[1]):
                v = board[x][y]
                if v == 0:
                    continue
                board[x][y] = 0
                for ny in reversed(range(0, y)):
                    if board[x][ny] == v and (x, ny) not in already_merged:
                        board[x][ny] = v + 1
                        already_merged.append((x, ny))
                        moves.append(((x, y), (x, ny), True))
                        break
                    elif board[x][ny] != 0:
                        board[x][ny + 1] = v
                        if ny + 1 != y:
                            moves.append(((x, y), (x, ny + 1), False))
                        break
                else:
                    board[x][0] = v
                    moves.append(((x, y), (x, 0), False))
    elif direction == MoveDirection.DOWN:
        for x in range(size[0]):
            for y in reversed(range(size[1] - 1)):
                v = board[x][y]
                if v == 0:
                    continue
                board[x][y] = 0
                for ny in range(y + 1, size[1]):
                    if board[x][ny] == v and (x, ny) not in already_merged:
                        board[x][ny] = v + 1
                        already_merged.append((x, ny))
                        moves.append(((x, y), (x, ny), True))
                        break
                    elif board[x][ny] != 0:
                        board[x][ny - 1] = v
                        if ny - 1 != y:
                            moves.append(((x, y), (x, ny - 1), False))
                        break
                else:
                    board[x][-1] = v
                    moves.append(((x, y), (x, size[1] - 1), False))
    elif direction == MoveDirection.LEFT:
        for y in range(size[1]):
            for x in range(1, size[0]):
                v = board[x][y]
                if v == 0 or x == 0:
                    continue
                board[x][y] = 0
                for nx in reversed(range(0, x)):
                    if board[nx][y] == v and (nx, y) not in already_merged:
                        board[nx][y] = v + 1
                        already_merged.append((nx, y))
                        moves.append(((x, y), (nx, y), True))
                        break
                    elif board[nx][y] != 0:
                        board[nx + 1][y] = v
                        if nx + 1 != x:
                            moves.append(((x, y), (nx + 1, y), False))
                        break
                else:
                    board[0][y] = v
                    moves.append(((x, y), (0, y), False))
    elif direction == MoveDirection.RIGHT:
        for y in range(size[1]):
            for x in reversed(range(size[0] - 1)):
                v = board[x][y]
                if v == 0:
                    continue
                board[x][y] = 0
                for nx in range(x + 1, size[0]):
                    if board[nx][y] == v and (nx, y) not in already_merged:
                        board[nx][y] = v + 1
                        already_merged.append((nx, y))
                        moves.append(((x, y), (nx, y), True))
                        break
                    elif board[nx][y] != 0:
                        board[nx - 1][y] = v
                        if nx - 1 != x:
                            moves.append(((x, y), (nx - 1, y), False))
                        break
                else:
                    board[-1][y] = v
                    moves.append(((x, y), (size[0] - 1, y), False))
    else:
        raise ValueError()
    return old, board, moves


class BoardController:
    def get_input(self, board: BoardType) -> MoveDirection:
        raise NotImplementedError

    def should_restart(self) -> bool:
        raise NotImplementedError


class BoardRenderer:
    def restart(self, board: BoardType):
        raise NotImplementedError

    def display_move(self, move: MoveDirection, new_board: BoardType, old_board: BoardType, moves: List[Move]):
        raise NotImplementedError

    def died(self, board: BoardType):
        raise NotImplementedError


class TextBoardRenderer(BoardRenderer):
    @staticmethod
    def print(board: BoardType):
        w, h = len(board), len(board[0])
        m = max(len(str(2 ** n)) for c in board for n in c) + 2
        print(('+' + '-' * m) * w + '+')
        for y in range(h):
            print(('|' + ' ' * m) * w + '|')
            print('|' + '|'.join((f'{2**board[x][y]:^{m}}' if board[x][y] else ' ' * m) for x in range(w)) + '|')
            print(('|' + ' ' * m) * w + '|')
            print(('+' + '-' * m) * w + '+')

    def restart(self, board: BoardType):
        self.print(board)

    def display_move(self, move: MoveDirection, new_board: BoardType, old_board: BoardType, moves: List[Move]):
        print(moves)
        self.print(new_board)

    def died(self, board: BoardType):
        pass


class TextBoardController(BoardController):
    def get_input(self, board: BoardType) -> MoveDirection:
        return getattr(MoveDirection, input("> ").upper())

    def should_restart(self):
        return not input("Restart? (Y/n) ").lower().startswith("n")
