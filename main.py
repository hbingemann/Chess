# ---------------------------------------------------
# |                    CHESS                        |
# ---------------------------------------------------

import pygame

SIZE = WIDTH, HEIGHT = 800, 800
FPS = 60


# - drag and drop of pieces if move is legal
# - every piece has it's own individual moves
# - define move possibilities as a function?
# - checking for legal move:
#   - each piece has a list of tuples
#   - tuples represent changes in x, y that they can do
#   - ex: pawn (x + 0, y + 1)
# - take pieces
# - promote pawns
# - look for checks / checkmate
# - look for stalemate / draw


class Board:
    def __init__(self):
        pass

    # Board:
    # - keeps track of piece locations
    # - tells piece if move is legal / possible (not blocked by other piece)


class Piece:
    def __init__(self, image, color, start):
        self.image = pygame.image.load(image)

    # Piece
    # - knows where it can move towards based off of its own moving possibilities (e.g: bishop on diagonals)
    # - kills itself if it has been taken
    # - keeps track of mouse clicks then asks board if ok


class Pawn(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_pawn.png"
        self.start = start
        super().__init__(self.image, color, self.start)

    # Individual Pieces:
    # - tells piece class its moving constraints
    # - its start
    # -


class Rook(Piece):
    def __init__(self):
        super().__init__()


class Knight(Piece):
    def __init__(self):
        super().__init__()


class Bishop(Piece):
    def __init__(self):
        super().__init__()


class Queen(Piece):
    def __init__(self):
        super().__init__()


class King(Piece):
    def __init__(self):
        super().__init__()


def draw_board(surface):
    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:  # to make checkered pattern
                col = "#61a055"  # green
            else:
                col = "#ebf2d2"  # white
            pygame.draw.rect(surface, col, (x * WIDTH // 8, y * WIDTH // 8, WIDTH, HEIGHT))


if __name__ == '__main__':  # running the game
    # setting some values that will be useful
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('CHESS')

    draw_board(screen)

    # game loop
    run = True
    clock = pygame.time.Clock()
    while run:
        # regulate game speed and calculate some elapsed time for inputs
        clock.tick(FPS)

        # check events
        for event in pygame.event.get():

            # close window
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()
