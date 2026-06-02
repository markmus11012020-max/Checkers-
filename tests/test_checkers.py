import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from checkers import CheckersGame


def test_initial_board_has_pieces() -> None:
    game = CheckersGame()
    assert game.get_piece(game.algebraic_to_coords('a7')) == 'b'
    assert game.get_piece(game.algebraic_to_coords('b2')) == 'w'


def test_simple_move() -> None:
    game = CheckersGame()
    game.make_move('b6-a5')
    assert game.get_piece(game.algebraic_to_coords('a5')) == 'b'
    assert game.get_piece(game.algebraic_to_coords('b6')) == '.'
    assert game.current_player == 'w'


def test_capture_move() -> None:
    game = CheckersGame()
    game.board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'b', '.', '.', '.', '.', '.', '.'],
        ['.', '.', 'w', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
    ]
    game.current_player = 'b'
    game.make_move('b6-d4')
    assert game.get_piece(game.algebraic_to_coords('d4')) == 'b'
    assert game.get_piece(game.algebraic_to_coords('c5')) == '.'


def test_forced_capture() -> None:
    game = CheckersGame()
    game.board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', 'b', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'w', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
    ]
    game.current_player = 'b'
    try:
        game.make_move('d6-c5')
        assert False, 'Expected capture requirement'
    except ValueError as exc:
        assert 'capture' in str(exc).lower()
