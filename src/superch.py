"""
Interactive Checkers GUI — v2 (fixed turn logic).
Uses existing CheckersGame for game rules.
Adds click-based input, smooth animations, tactile feedback.

Controls:
  Mouse click  — select / move
  R            — restart
  U            — undo
  T            — cycle theme
  ESC          — quit
"""

import math
import sys
import os
import time

import pygame

# Подключаем папку src, чтобы работал import checkers
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

try:
    from checkers import CheckersGame
except ImportError:
    # Если файл лежит рядом с checkers.py — пробуем так
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from checkers import CheckersGame


# ============================================================
# Конфигурация
# ============================================================
WINDOW_W, WINDOW_H = 760, 880
BOARD_SIZE = 8
SQUARE = 80
BOARD_W = SQUARE * BOARD_SIZE
BOARD_H = SQUARE * BOARD_SIZE
BOARD_X = (WINDOW_W - BOARD_W) // 2
BOARD_Y = 160
FPS = 60

MOVE_DURATION = 0.32
CAPTURE_DURATION = 0.50
HOVER_SPD = 14.0
SELECT_SPD = 10.0


# ============================================================
# Темы
# ============================================================
THEMES = {
    "bw": {
        "name": "Classic B&W",
        "bg":          (28, 28, 30),
        "panel":       (40, 40, 44),
        "light":       (220, 220, 225),
        "dark":        (35, 35, 40),
        "hint":        (95, 95, 105),
        "rim":         (10, 10, 12),
        "white":       (245, 245, 248),
        "white_hl":    (255, 255, 255),
        "white_rim":   (170, 170, 178),
        "black":       (15, 15, 18),
        "black_hl":    (35, 35, 40),
        "gold":        (230, 200, 90),
        "gold_dark":   (160, 130, 30),
        "glow":        (255, 230, 130),
        "valid":       (95, 210, 130),
        "capture":     (235, 95, 95),
        "text":        (235, 235, 240),
        "dim":         (150, 150, 160),
    },
    "wood": {
        "name": "Wood",
        "bg":          (32, 22, 16),
        "panel":       (48, 32, 22),
        "light":       (232, 210, 178),
        "dark":        (78, 50, 34),
        "hint":        (110, 80, 58),
        "rim":         (90, 60, 35),
        "white":       (245, 235, 215),
        "white_hl":    (255, 250, 230),
        "white_rim":   (200, 180, 150),
        "black":       (25, 18, 12),
        "black_hl":    (50, 35, 25),
        "gold":        (220, 175, 65),
        "gold_dark":   (170, 130, 30),
        "glow":        (255, 215, 100),
        "valid":       (95, 200, 115),
        "capture":     (220, 90, 90),
        "text":        (245, 235, 215),
        "dim":         (180, 160, 130),
    },
    "marble": {
        "name": "Marble",
        "bg":          (40, 42, 48),
        "panel":       (60, 62, 70),
        "light":       (240, 240, 245),
        "dark":        (55, 60, 72),
        "hint":        (120, 130, 145),
        "rim":         (80, 85, 95),
        "white":       (250, 250, 255),
        "white_hl":    (255, 255, 255),
        "white_rim":   (200, 200, 215),
        "black":       (20, 25, 35),
        "black_hl":    (45, 50, 60),
        "gold":        (230, 200, 90),
        "gold_dark":   (160, 130, 30),
        "glow":        (255, 230, 130),
        "valid":       (100, 220, 140),
        "capture":     (240, 100, 100),
        "text":        (240, 240, 248),
        "dim":         (160, 165, 175),
    },
    "neon": {
        "name": "Neon",
        "bg":          (10, 10, 18),
        "panel":       (18, 18, 30),
        "light":       (40, 45, 65),
        "dark":        (20, 22, 38),
        "hint":        (60, 70, 100),
        "rim":         (0, 255, 200),
        "white":       (230, 240, 255),
        "white_hl":    (255, 255, 255),
        "white_rim":   (0, 220, 255),
        "black":       (15, 12, 25),
        "black_hl":    (50, 30, 70),
        "gold":        (255, 220, 80),
        "gold_dark":   (255, 130, 30),
        "glow":        (255, 100, 220),
        "valid":       (0, 255, 150),
        "capture":     (255, 60, 120),
        "text":        (220, 240, 255),
        "dim":         (120, 140, 170),
    },
}


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


# ============================================================
# Визуальная шашка
# ============================================================
class DrawPiece:
    def __init__(self, symbol, row, col):
        self.symbol = symbol
        self.target_row = row
        self.target_col = col
        self.x = self.tx()
        self.y = self.ty()

        self.move_t = 1.0
        self.move_from = (self.x, self.y)
        self.move_to = (self.x, self.y)

        self.press_t = 1.0
        self.spawn_t = 0.0
        self.capture_t = 1.0
        self.dying = False

        self.hover = 0.0
        self.target_hover = 0.0
        self.selected = 0.0
        self.target_selected = 0.0

    def tx(self):
        return BOARD_X + self.target_col * SQUARE + SQUARE // 2

    def ty(self):
        return BOARD_Y + self.target_row * SQUARE + SQUARE // 2

    def is_black(self):
        return self.symbol in ("b", "B")

    def is_king(self):
        return self.symbol in ("B", "W")

    def player(self):
        return "b" if self.is_black() else "w"

    def start_move(self, to_row, to_col):
        self.target_row, self.target_col = to_row, to_col
        self.move_from = (self.x, self.y)
        self.move_to = (self.tx(), self.ty())
        self.move_t = 0.0

    def press(self):
        self.press_t = 0.0

    def set_selected(self, sel):
        self.target_selected = 1.0 if sel else 0.0

    def set_hover(self, hov):
        self.target_hover = 1.0 if hov else 0.0

    def start_capture(self):
        self.capture_t = 0.0
        self.dying = True

    def update(self, dt):
        if self.spawn_t < 1.0:
            self.spawn_t = min(1.0, self.spawn_t + dt / 0.25)
        if self.move_t < 1.0:
            self.move_t = min(1.0, self.move_t + dt / MOVE_DURATION)
            e = ease_out_cubic(self.move_t)
            arc = math.sin(self.move_t * math.pi) * 10
            self.x = lerp(self.move_from[0], self.move_to[0], e)
            self.y = lerp(self.move_from[1], self.move_to[1], e) - arc
        if self.capture_t < 1.0:
            self.capture_t = min(1.0, self.capture_t + dt / CAPTURE_DURATION)
        if self.press_t < 1.0:
            self.press_t = min(1.0, self.press_t + dt / 0.18)

        sp = HOVER_SPD * dt
        self.hover += max(-sp, min(sp, self.target_hover - self.hover))
        sp2 = SELECT_SPD * dt
        self.selected += max(-sp2, min(sp2, self.target_selected - self.selected))

    def is_dead(self):
        return self.dying and self.capture_t >= 1.0

    def draw(self, surface, palette):
        if self.dying and self.capture_t >= 1.0:
            return

        if self.dying:
            scale_mult = (1.0 + math.sin(self.capture_t * math.pi) * 0.1) * (1 - self.capture_t * 0.3)
            alpha_mult = 1.0 - self.capture_t
        else:
            if self.spawn_t < 1.0:
                p = self.spawn_t
                scale_mult = 0.5 + math.sin(p * math.pi) * 0.4 + p * 0.3
            else:
                scale_mult = 1.0
            alpha_mult = 1.0

        scale_mult *= (1 + self.hover * 0.10 + self.selected * 0.06)

        y_offset = 0
        if self.press_t < 1.0:
            p = ease_out_cubic(self.press_t)
            scale_mult *= (1 - 0.10 * (1 - p))
            y_offset = 3 * (1 - p)

        base_r = SQUARE // 2 - 7
        r = max(2, int(base_r * scale_mult))

        shadow_r = int(r * 1.1)
        sh = pygame.Surface((shadow_r * 2 + 8, shadow_r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, int(95 * alpha_mult)),
                            (4, 4, shadow_r * 2, shadow_r * 2))
        surface.blit(sh, (self.x - shadow_r - 4, self.y - shadow_r + 5))

        if self.selected > 0.05:
            glow_r = int(r * 1.75)
            gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for i in range(3):
                ring_r = int(glow_r * (0.55 + i * 0.18))
                ring_a = int(80 * self.selected * (1 - i / 3))
                pygame.draw.circle(gs, (*palette["glow"], ring_a),
                                   (glow_r, glow_r), ring_r, 3)
            surface.blit(gs, (self.x - glow_r, self.y - glow_r))

        ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        if self.is_black():
            rim, body, hl = palette["rim"], palette["black"], palette["black_hl"]
        else:
            rim, body, hl = palette["white_rim"], palette["white"], palette["white_hl"]

        pygame.draw.circle(ps, rim, (r, r), r)
        pygame.draw.circle(ps, body, (r, r), int(r * 0.94))
        pygame.draw.circle(ps, rim, (r, r), int(r * 0.78), 1)

        hl_r = int(r * 0.4)
        hl_x = r - int(r * 0.28)
        hl_y = r - int(r * 0.28)
        hs = pygame.Surface((hl_r * 2, hl_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(hs, (*hl, 100), (hl_r, hl_r), hl_r)
        ps.blit(hs, (hl_x - hl_r, hl_y - hl_r))

        if self.is_king():
            pts = []
            n = 10
            for i in range(n):
                angle = -math.pi / 2 + (i / n) * 2 * math.pi
                rad = r * (0.58 if i % 2 == 0 else 0.30)
                pts.append((r + rad * math.cos(angle), r + rad * math.sin(angle)))
            pygame.draw.polygon(ps, palette["gold"], pts)
            pygame.draw.polygon(ps, palette["gold_dark"], pts, 2)
            pygame.draw.circle(ps, palette["gold_dark"], (r, r), int(r * 0.12))

        ps.set_alpha(int(255 * alpha_mult))
        surface.blit(ps, (self.x - r, self.y - r - y_offset))


# ============================================================
# Главный класс GUI
# ============================================================
class CheckersGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Checkers — Interactive Edition")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("georgia", 38, bold=True)
        self.font_med = pygame.font.SysFont("georgia", 22, bold=True)
        self.font_small = pygame.font.SysFont("georgia", 16)

        self.theme_keys = list(THEMES.keys())
        self.theme_idx = 0
        self.theme = THEMES[self.theme_keys[self.theme_idx]]

        self.reset_game()

    def reset_game(self):
        self.game = CheckersGame()
        self.history = []
        self.pieces = {}
        self.sync_pieces_from_game()
        self.selected = None
        self.valid_moves = []
        self.last_path = None
        self.winner = None
        self.message = ""
        self.message_time = 0.0
        self.continuation = None

    def sync_pieces_from_game(self):
        new_pieces = {}
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                sym = self.game.board[r][c]
                if sym != CheckersGame.EMPTY:
                    key = (r, c)
                    if key in self.pieces:
                        p = self.pieces[key]
                        p.symbol = sym
                        p.target_row = r
                        p.target_col = c
                        new_pieces[key] = p
                    else:
                        new_pieces[key] = DrawPiece(sym, r, c)
        self.pieces = new_pieces

    def show_message(self, text):
        self.message = text
        self.message_time = time.time()

    def save_state(self):
        snap = [row.copy() for row in self.game.board]
        self.history.append((snap, self.game.current_player))

    def click_to_square(self, pos):
        x, y = pos
        if not (BOARD_X <= x < BOARD_X + BOARD_W and
                BOARD_Y <= y < BOARD_Y + BOARD_H):
            return None
        return (int((y - BOARD_Y) // SQUARE), int((x - BOARD_X) // SQUARE))

    def handle_click(self, mouse_pos):
        if self.winner:
            self.reset_game()
            return

        sq = self.click_to_square(mouse_pos)
        if sq is None:
            return

        row, col = sq
        current = self.game.current_player

        # Multi-jump continuation
        if self.continuation is not None:
            cr, cc = self.continuation
            if (row, col) != (cr, cc):
                path = self.find_path((cr, cc), (row, col), self.valid_moves)
                if path:
                    self.execute_path(path)
            return

        # Ничего не выбрано
        if self.selected is None:
            p = self.pieces.get((row, col))
            if p and p.player() == current:
                self.select_piece(row, col, p)
            return

        # Клик по той же шашке — снять выбор
        if (row, col) == self.selected:
            self.deselect()
            return

        # Попытка хода
        path = self.find_path(self.selected, (row, col), self.valid_moves)
        if path:
            self.execute_path(path)
            return

        # Выбор другой своей шашки
        p = self.pieces.get((row, col))
        self.deselect()
        if p and p.player() == current:
            self.select_piece(row, col, p)

    def select_piece(self, row, col, piece):
        self.selected = (row, col)
        piece.set_selected(True)
        piece.press()

        # Соберём все допустимые пути
        all_moves = self.collect_all_moves(self.game.current_player)
        own = [m for m in all_moves if m[0] == (row, col)]
        has_capture = any(self.is_capture_path(m) for m in own)

        if has_capture:
            self.valid_moves = [m for m in own if self.is_capture_path(m)]
        else:
            self.valid_moves = own

    def deselect(self):
        if self.selected:
            p = self.pieces.get(self.selected)
            if p:
                p.set_selected(False)
        self.selected = None
        self.valid_moves = []

    def find_path(self, frm, to, paths):
        for path in paths:
            if path[0] == frm and path[-1] == to:
                return path
        return None

    def is_capture_path(self, path):
        return len(path) > 2 or abs(path[0][0] - path[1][0]) == 2

    def collect_all_moves(self, color):
        """Возвращает список всех допустимых путей для игрока color.
        Игнорирует current_player, чтобы избежать переключения."""
        return [tuple(tuple(p) for p in m) for m in self.compute_moves_for(color)]

    def compute_moves_for(self, color):
        """Считаем ходы для color, временно подменив current_player."""
        saved = self.game.current_player
        self.game.current_player = color
        moves = self.game.get_moves()
        self.game.current_player = saved
        return moves

    def execute_path(self, path):
        """Главное исправление: НЕ трогаем current_player руками —
        пусть CheckersGame.make_move сам корректно его переключит."""
        self.save_state()

        moving_piece = self.pieces.get(path[0])
        if not moving_piece:
            return

        self.deselect()

        # Превращаем в algebraic-нотацию и даём существующей логике сделать всё сама
        move_text = self.path_to_algebraic(path)
        try:
            self.game.make_move(move_text)
        except ValueError as exc:
            self.show_message(f"Illegal: {exc}")
            self.history.pop()
            return

        # Запускаем визуальные анимации: capture исчезновение
        for i in range(1, len(path)):
            prev = path[i - 1]
            cur = path[i]
            if abs(prev[0] - cur[0]) == 2:
                mr, mc = (prev[0] + cur[0]) // 2, (prev[1] + cur[1]) // 2
                victim = self.pieces.get((mr, mc))
                if victim:
                    victim.start_capture()

        # Перемещаем шашку
        moving_piece.start_move(path[-1][0], path[-1][1])
        moving_piece.symbol = self.game.board[path[-1][0]][path[-1][1]]
        self.pieces[path[-1]] = moving_piece
        if path[0] in self.pieces:
            del self.pieces[path[0]]

        self.last_path = path

        # Multi-jump для того же игрока?
        last_pos = path[-1]
        if any(self.is_capture_path(m) for m in
               [tuple(tuple(p) for p in x) for x in
                self.compute_moves_for(self.game.opponent())  # смотрим ходы СЛЕДУЮЩЕГО игрока
               ] if m[0] == last_pos):
            pass

        # Правильная проверка: может ли ТОЛЬКО-ЧТО-ХОДИВШИЙ игрок продолжить серию
        player_just_moved = self.game.opponent()  # т.к. make_move уже переключил
        # А нам нужно проверить старого игрока. Запомним его до make_move.
        # Проще: сохраним ДО make_move:
        # (см. save_state + restored ниже)

        # Чтобы корректно проверить multi-jump, считаем ходы для только-что-ходившего игрока
        just_moved = self.game.opponent()  # make_move уже переключил current_player
        continuation_moves = [
            tuple(tuple(p) for p in m)
            for m in self.compute_moves_for(just_moved)
            if tuple(tuple(p) for p in m)[0] == last_pos
            and self.is_capture_path(tuple(tuple(p) for p in m))
        ]

        if continuation_moves:
            self.continuation = last_pos
            self.selected = last_pos
            moving_piece.set_selected(True)
            self.valid_moves = continuation_moves
            self.show_message("Continue jumping!")
            return

        self.continuation = None
        self.check_game_over()

    def path_to_algebraic(self, path):
        tokens = [self.game.coords_to_algebraic(p) for p in path]
        return "x".join(tokens)

    def check_game_over(self):
        if self.game.is_game_over():
            self.winner = self.game.winner()
            if self.winner:
                self.show_message(f"Winner: {self.winner.upper()}")
            else:
                self.show_message("Draw!")

    def undo(self):
        if not self.history:
            self.show_message("Nothing to undo")
            return
        snap, player = self.history.pop()
        self.game.board = snap
        self.game.current_player = player
        self.sync_pieces_from_game()
        self.deselect()
        self.continuation = None
        self.winner = None
        self.last_path = None
        self.show_message("Undone")

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        hovered = self.click_to_square((mx, my))

        for (r, c), p in list(self.pieces.items()):
            p.update(dt)
            if p.is_dead():
                del self.pieces[(r, c)]
                continue
            can_select = (p.player() == self.game.current_player)
            if self.continuation is not None:
                can_select = can_select and (r, c) == self.continuation
            p.set_hover(hovered == (r, c) and can_select)

    def draw(self):
        pal = self.theme
        self.screen.fill(pal["bg"])
        self.draw_panel()
        self.draw_board()
        self.draw_valid_moves()
        self.draw_pieces()
        self.draw_winner()

    def draw_panel(self):
        pal = self.theme
        title = self.font_big.render("CHECKERS", True, pal["gold"])
        self.screen.blit(title, title.get_rect(center=(WINDOW_W // 2, 45)))

        subtitle = self.font_small.render("Interactive Edition", True, pal["dim"])
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_W // 2, 80)))

        turn_text = "White's turn" if self.game.current_player == "w" else "Black's turn"
        ts = self.font_med.render(turn_text, True, pal["text"])
        self.screen.blit(ts, (30, 110))

        col = pal["white"] if self.game.current_player == "w" else pal["black"]
        rim = pal["white_rim"] if self.game.current_player == "w" else pal["rim"]
        pygame.draw.circle(self.screen, col, (230, 121), 12)
        pygame.draw.circle(self.screen, rim, (230, 121), 12, 2)

        b_left = sum(1 for r in range(8) for c in range(8)
                     if self.game.board[r][c] in ("b", "B"))
        w_left = sum(1 for r in range(8) for c in range(8)
                     if self.game.board[r][c] in ("w", "W"))
        eaten_w = 12 - w_left
        eaten_b = 12 - b_left
        cap = f"Captured  W:{eaten_w}   B:{eaten_b}"
        cs = self.font_small.render(cap, True, pal["dim"])
        self.screen.blit(cs, (WINDOW_W - cs.get_width() - 30, 115))

        th = self.font_small.render(f"Theme: {pal['name']}  (T)", True, pal["dim"])
        self.screen.blit(th, th.get_rect(center=(WINDOW_W // 2, 110)))

        hints = [
            ("Click", "move"),
            ("U", "undo"),
            ("R", "restart"),
            ("T", "theme"),
            ("ESC", "quit"),
        ]
        total_w = sum(self.font_small.size(f"{k}: {v}")[0] + 20 for k, v in hints)
        x = (WINDOW_W - total_w) // 2
        y = WINDOW_H - 40
        for k, v in hints:
            txt = self.font_small.render(f"{k}: {v}", True, pal["dim"])
            self.screen.blit(txt, (x, y))
            x += txt.get_width() + 20

        if self.message and time.time() - self.message_time < 2.5:
            ms = self.font_med.render(self.message, True, pal["gold"])
            self.screen.blit(ms, ms.get_rect(center=(WINDOW_W // 2, WINDOW_H - 75)))

    def draw_board(self):
        pal = self.theme
        border = pygame.Rect(BOARD_X - 7, BOARD_Y - 7, BOARD_W + 14, BOARD_H + 14)
        pygame.draw.rect(self.screen, pal["panel"], border, border_radius=8)

        highlight_squares = set()
        if self.last_path:
            for p in self.last_path:
                highlight_squares.add(p)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = BOARD_X + c * SQUARE
                y = BOARD_Y + r * SQUARE
                rect = pygame.Rect(x, y, SQUARE, SQUARE)
                is_dark = (r + c) % 2 == 1
                color = pal["dark"] if is_dark else pal["light"]
                if (r, c) in highlight_squares:
                    color = pal["hint"]
                pygame.draw.rect(self.screen, color, rect)

        pygame.draw.rect(self.screen, pal["gold_dark"], border, 2, border_radius=8)

    def draw_valid_moves(self):
        pal = self.theme
        pulse = (math.sin(time.time() * 4) + 1) / 2
        for path in self.valid_moves:
            r, c = path[-1]
            x = BOARD_X + c * SQUARE + SQUARE // 2
            y = BOARD_Y + r * SQUARE + SQUARE // 2
            if self.is_capture_path(path):
                pygame.draw.circle(self.screen, pal["capture"], (x, y), SQUARE // 3, 4)
                pygame.draw.circle(self.screen, pal["capture"], (x, y), int(SQUARE // 4), 2)
            else:
                radius = int(8 + pulse * 4)
                surf = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*pal["valid"], 220), (radius + 3, radius + 3), radius)
                self.screen.blit(surf, (x - radius - 3, y - radius - 3))

    def draw_pieces(self):
        pal = self.theme
        living = [p for p in self.pieces.values() if not p.dying]
        dying = [p for p in self.pieces.values() if p.dying]
        for p in living:
            p.draw(self.screen, pal)
        for p in dying:
            p.draw(self.screen, pal)

    def draw_winner(self):
        if not self.winner:
            return
        pal = self.theme
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text = "White Wins!" if self.winner == "w" else "Black Wins!"
        ws = self.font_big.render(text, True, pal["gold"])
        self.screen.blit(ws, ws.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 25)))

        sub = self.font_med.render("Click to play again", True, pal["text"])
        self.screen.blit(sub, sub.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 25)))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.handle_click(ev.pos)
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if ev.key == pygame.K_r:
                        self.reset_game()
                    if ev.key == pygame.K_u:
                        self.undo()
                    if ev.key == pygame.K_t:
                        self.theme_idx = (self.theme_idx + 1) % len(self.theme_keys)
                        self.theme = THEMES[self.theme_keys[self.theme_idx]]
                        self.show_message(f"Theme: {self.theme['name']}")

            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    CheckersGUI().run()
