from game import Game

def main():
    game = Game()

    while not game.shouldStop():
        game.update()

if __name__ == "__main__":
    main()