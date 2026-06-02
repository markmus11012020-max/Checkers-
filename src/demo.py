from checkers import CheckersGame


def run_demo() -> None:
    game = CheckersGame()
    print('Initial board:')
    print(game.render())

    # simple move
    print('\nMake move: b6-a5')
    game.make_move('b6-a5')
    print(game.render())

    # set up a capture scenario
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
    print('\nCapture scenario board:')
    print(game.render())
    print('\nMake capture: b6-d4')
    game.make_move('b6-d4')
    print(game.render())

    # promotion scenario
    game = CheckersGame()
    game.board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'b', '.', '.', '.', '.', '.', '.'],
    ]
    game.current_player = 'b'
    print('\nPromotion scenario board:')
    print(game.render())
    print('\nMake move: b2-a1 (promotion)')
    # b2 -> a1 in algebraic where b2 corresponds to (row 6,col1) but ensure move legal
    try:
        game.make_move('b2-a1')
    except Exception as e:
        print('Promotion move failed:', e)
    print(game.render())


if __name__ == '__main__':
    run_demo()
