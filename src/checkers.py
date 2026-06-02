from __future__ import annotations
import re
from typing import List, Optional, Tuple

Position = Tuple[int, int]

class CheckersGame:
    EMPTY = '.'
    BLACK_REGULAR = 'b'
    WHITE_REGULAR = 'w'
    BLACK_KING = 'B'
    WHITE_KING = 'W'

    DIRECTIONS = {
        BLACK_REGULAR: [(1, -1), (1, 1)],
        WHITE_REGULAR: [(-1, -1), (-1, 1)],
        BLACK_KING: [(1, -1), (1, 1), (-1, -1), (-1, 1)],
        WHITE_KING: [(1, -1), (1, 1), (-1, -1), (-1, 1)],
    }

    PLAYERS = {
        BLACK_REGULAR: 'b',
        BLACK_KING: 'b',
        WHITE_REGULAR: 'w',
        WHITE_KING: 'w',
    }

    def __init__(self) -> None:
        self.board = self._initial_board()
        self.current_player = self.BLACK_REGULAR

    def _initial_board(self) -> List[List[str]]:
        board = [[self.EMPTY for _ in range(8)] for _ in range(8)]
        for row in range(3):
            for col in range(8):
                if (row + col) % 2:
                    board[row][col] = self.BLACK_REGULAR
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2:
                    board[row][col] = self.WHITE_REGULAR
        return board

    def render(self) -> str:
        lines = ["  a b c d e f g h"]
        for row in range(8):
            line = [str(8 - row)]
            for col in range(8):
                line.append(self.board[row][col])
            lines.append(' '.join(line))
        return '\n'.join(lines)

    def algebraic_to_coords(self, notation: str) -> Position:
        notation = notation.strip().lower()
        if not re.fullmatch(r'[a-h][1-8]', notation):
            raise ValueError(f"Invalid square '{notation}'. Use a1..h8.")
        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        if not self._is_valid_square(row, col):
            raise ValueError(f"Square {notation} is not playable in checkers.")
        return (row, col)

    def coords_to_algebraic(self, pos: Position) -> str:
        row, col = pos
        return f"{chr(col + ord('a'))}{8 - row}"

    def _is_valid_square(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8 and (row + col) % 2 == 1

    def get_piece(self, pos: Position) -> str:
        row, col = pos
        return self.board[row][col]

    def set_piece(self, pos: Position, value: str) -> None:
        row, col = pos
        self.board[row][col] = value

    def is_player_piece(self, piece: str) -> bool:
        return piece in self.PLAYERS and self.PLAYERS[piece] == self.current_player

    def opponent(self) -> str:
        return self.WHITE_REGULAR if self.current_player == self.BLACK_REGULAR else self.BLACK_REGULAR

    def get_player_pieces(self) -> List[Position]:
        return [
            (r, c)
            for r in range(8)
            for c in range(8)
            if self.board[r][c] != self.EMPTY and self.PLAYERS[self.board[r][c]] == self.current_player
        ]

    def get_moves(self) -> List[List[Position]]:
        captures = []
        steps = []
        for piece_pos in self.get_player_pieces():
            captures.extend(self._capture_moves(piece_pos))
            steps.extend(self._step_moves(piece_pos))
        return captures if captures else steps

    def _step_moves(self, pos: Position) -> List[List[Position]]:
        moves = []
        piece = self.get_piece(pos)
        for dr, dc in self.DIRECTIONS[piece]:
            target = (pos[0] + dr, pos[1] + dc)
            if self._is_valid_square(*target) and self.get_piece(target) == self.EMPTY:
                moves.append([pos, target])
        return moves

    def _capture_moves(self, pos: Position) -> List[List[Position]]:
        piece = self.get_piece(pos)
        captures: List[List[Position]] = []
        for dr, dc in self.DIRECTIONS[piece]:
            jump = (pos[0] + 2 * dr, pos[1] + 2 * dc)
            middle = (pos[0] + dr, pos[1] + dc)
            if self._is_valid_square(*jump) and self.get_piece(jump) == self.EMPTY:
                middle_piece = self.get_piece(middle)
                if middle_piece != self.EMPTY and self.PLAYERS.get(middle_piece) == self.opponent():
                    board_snapshot = [row.copy() for row in self.board]
                    captured_moves = self._capture_chain(pos, jump, board_snapshot, piece)
                    captures.extend(captured_moves)
        return captures

    def _capture_chain(self, start: Position, landing: Position, board_snapshot: List[List[str]], piece: str) -> List[List[Position]]:
        source_piece = board_snapshot[start[0]][start[1]]
        mid_row = (start[0] + landing[0]) // 2
        mid_col = (start[1] + landing[1]) // 2
        board_snapshot[start[0]][start[1]] = self.EMPTY
        board_snapshot[mid_row][mid_col] = self.EMPTY
        board_snapshot[landing[0]][landing[1]] = source_piece

        moves = [[start, landing]]
        added = False
        for dr, dc in self.DIRECTIONS[piece]:
            next_jump = (landing[0] + 2 * dr, landing[1] + 2 * dc)
            next_middle = (landing[0] + dr, landing[1] + dc)
            if self._is_valid_square(*next_jump) and board_snapshot[next_jump[0]][next_jump[1]] == self.EMPTY:
                middle_piece = board_snapshot[next_middle[0]][next_middle[1]]
                if middle_piece != self.EMPTY and self.PLAYERS.get(middle_piece) == self.opponent():
                    deeper = self._capture_chain(landing, next_jump, [row.copy() for row in board_snapshot], piece)
                    for chain in deeper:
                        moves.append([start] + chain[1:])
                        added = True
        return moves if added else moves

    def _move_requires_capture(self) -> bool:
        return any(len(path) > 2 or self._is_capture_path(path) for path in self.get_moves())

    def _is_capture_path(self, path: List[Position]) -> bool:
        return len(path) > 2 or abs(path[0][0] - path[1][0]) == 2

    def make_move(self, move_text: str) -> None:
        tokens = re.split(r'[\s\-x]+', move_text.strip())
        if len(tokens) < 2:
            raise ValueError('Move format must be like b6-a5 or b6xc4.')
        path = [self.algebraic_to_coords(token) for token in tokens]
        legal_moves = self.get_moves()
        if self._move_requires_capture() and not self._is_capture_path(path):
            raise ValueError('A capture move is available and must be taken.')
        if path not in legal_moves:
            raise ValueError('Illegal move.')
        self._apply_move(path)
        self.current_player = self.opponent()

    def _apply_move(self, path: List[Position]) -> None:
        start = path[0]
        piece = self.get_piece(start)
        self.set_piece(start, self.EMPTY)
        for idx in range(1, len(path)):
            if abs(path[idx][0] - path[idx - 1][0]) == 2:
                middle = ((path[idx][0] + path[idx - 1][0]) // 2, (path[idx][1] + path[idx - 1][1]) // 2)
                self.set_piece(middle, self.EMPTY)
        self.set_piece(path[-1], piece)
        self._promote(path[-1])

    def _promote(self, pos: Position) -> None:
        row, col = pos
        piece = self.get_piece(pos)
        if piece == self.BLACK_REGULAR and row == 7:
            self.set_piece(pos, self.BLACK_KING)
        elif piece == self.WHITE_REGULAR and row == 0:
            self.set_piece(pos, self.WHITE_KING)

    def is_game_over(self) -> bool:
        return len(self.get_moves()) == 0

    def winner(self) -> Optional[str]:
        if not self.is_game_over():
            return None
        return self.opponent()
