from __future__ import annotations

from operator import itemgetter
from random import choice
from typing import List

from board import BoardController, BoardType, MoveDirection, Board, move


def possible_moves(board) -> List[MoveDirection]:
    up = any(board[x][y] != 0 and board[x][y - 1] in (0, board[x][y]) for x in range(len(board)) for y in range(1, len(board[1])))
    down = any(board[x][y] != 0 and board[x][y + 1] in (0, board[x][y]) for x in range(len(board)) for y in range(len(board[1]) - 1))
    left = any(board[x][y] != 0 and board[x - 1][y] in (0, board[x][y]) for y in range(len(board[0])) for x in range(1, len(board)))
    right = any(board[x][y] != 0 and board[x + 1][y] in (0, board[x][y]) for y in range(len(board[0])) for x in range(len(board) - 1))
    pms = []
    if up:
        pms.append(MoveDirection.UP)
    if down:
        pms.append(MoveDirection.DOWN)
    if left:
        pms.append(MoveDirection.LEFT)
    if right:
        pms.append(MoveDirection.RIGHT)
    return pms


class RandomController(BoardController):
    def get_input(self, board: BoardType):
        return choice(list(MoveDirection.__members__.values()))

    def should_restart(self):
        return True


class AlwaysUp(BoardController):
    def get_input(self, board: BoardType):
        pms = possible_moves(board)
        for d in (MoveDirection.UP, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.DOWN):
            if d in pms:
                return d
        print("no move found")
        return MoveDirection.UP

    def should_restart(self):
        return True


class PredictController(BoardController):
    def get_input(self, board: BoardType) -> MoveDirection:
        pms = possible_moves(board)
        if len(pms) == 1:
            return pms[0]
        elif len(pms) == 0:
            print("No moves found")
            return MoveDirection.UP
        else:
            moves = [(self.count_average_points(board, m, 3), m) for m in pms]
            print(moves)
            return max(moves, key=itemgetter(0))[1]

    def count_average_points(self, board, first_move, depth):
        board = move(board, first_move)[1]
        if depth == 0:
            return sum(3**v for c in board for v in c)
        else:
            possible_spawns = [((x, y), v) for x in range(len(board)) for y in range(len(board[0])) for v in (1, 2) if board[x][y] == 0]
            s = 0
            c = 0
            for (x, y), v in possible_spawns:
                new_board = board.copy()
                new_board[x][y] = v
                for m in possible_moves(new_board):
                    s += self.count_average_points(new_board, m, depth - 1)
                    c += 1
            if c != 0:
                return s / c
            else:
                return 0

    def should_restart(self):
        return True
