from checkers import CheckersGame

WELCOME = '''
Checkers CLI
Enter moves in algebraic notation, e.g. b6-a5 or b6xc4.
Capture moves are enforced when available.
Type 'exit' or 'quit' to leave the game.
'''


def main() -> None:
    game = CheckersGame()
    print(WELCOME)
    while True:
        print(game.render())
        if game.is_game_over():
            winner = game.winner()
            if winner:
                print(f"Game over. Winner: {winner.upper()}")
            else:
                print("Game over. Draw.")
            break
        print(f"Current player: {game.current_player}")
        move = input('Your move: ').strip()
        if move.lower() in {'exit', 'quit'}:
            print('Exiting game.')
            break
        try:
            game.make_move(move)
        except ValueError as exc:
            print(f'Error: {exc}')
            continue


if __name__ == '__main__':
    main()
