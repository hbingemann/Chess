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


# Noch so ein paar Ideen...
#
# Game Klasse
# - koordiniert den Ablauf
# - zum Beispiel die Uhr
# - oder die Maus Klicks
# - ruft dann die Animationen auf
# - baut ein neues Spiel auf
# - startet das Spiel (die Uhr)
# - ruft den Computer auf einen Zug zu machen
#
#
# Board Klasse
# - weiss wo alle Figuren stehen
# - und welche noch da sind
# - schaut auch welche der erlaubten Züge noch möglich sind (da da keine anderen Figuren stehen)
# - kann auch entscheiden. ob ein Maus Klick auf einem bestimmten Pixel ein e Figure trifft und wen ja, welche
#
# Piece Klasse
# - alles, was alle Figuren gemeinsam haben
# - so als eine Art Platzhalter fuer spaeter
# - wissen wo sie stehen
# - haben eine Liste mit erlaubten Zügen (relativ zu ihrem Standort)
# - aber man muss auch Besonderheiten erlauben, wie zum Beispiel den ersten Zug vom Bauern... Oder die Rochade... Oder en passant...
# - koennen auch sagen, auf welche Felder sie von ihren Standort aus gehen können (geben eine Liste zurueck)
# - sind schwarz oder weiss
# - haben ein Bild
# - koennen sich bewegen von A nach B mit einem netten huebsch aussehenden coolen Move
# - koennen explodieren, wenn sie geschlagen werden
#
# Einzelne Figuren Klassen
# - besetzen die Platzhalter in "Piece" entsprechend
# - zum Beispiel, welche spezifischen Zuege der Bauer machen kann - alle Bauern haben die gleichen Zuege - das ist so eine Art Klassen Variable, fuer alle gleich
# - manche Platzhalter von "Piece" werden erst mit den eigentlichen "Instanzen" besetzt (zum Beispiel wo sie stehen), das ist von Bauer zu Bauer verschieden
#
#
# - zum Beispiel, das Spiel "sieht" wohin die Maus geklickt hat - fragt das Board, ob das eine Figur ist. 
# - wenn ja, dann Sagt das Spiel dem Board, dass diese Figur bewegt werden soll
# - Board fragt dann die Figur, wohin sie denn so laufen kann
# - Board checked dann welche von den legalen Felder denn so moeglich sind (da dort noch nix steht)
# - das gibt eine kuerzere Liste von moeglichen Feldern
# - sagt dann dem Spiel, wohin die Figur laufen kann (und gibt dem Spiel auch die Figur fuer drag and drop)
# - Spiel malt dann die Punkte auf die Felder, wohin die Figur eigentlich nur hin laufen kann
# - Spiel schaut dann, wohin der Spieler zum zweiten mal clickt - oder drag and drop macht
# - wenn drag and drop, dann muss das Spiel die Figur mit bewegen
# - wenn der zweite Klick oder der Drag and Drop auf einem Punkt-Feld landet, dann ruft das Spiel die Animation auf
# - Spiel sagt der Figur, sich von A nach B zu bewegen
# - Figure macht das dann
# - Spiel sagt dann dem Board, dass die Figur nun auf dem neuen Platz steht
# - Board checked ob das eine andere Figur geschlagen hat
# - sagt dies dem Spiel dann, falss dem so ist
# - Spiel sagt dann der geschlagenen Figur doch bitte zu explodieren
#
# oder so aehnlich?


class Board:
    def __init__(self):
        self.pieces = []
        # self.pieces = [(knight, (pos.x, pos.y)), (pawn, (pos.x, pos.y))]

    # Board:
    # - keeps track of piece locations
    # - tells piece if move is legal / possible (not blocked by other piece)


class Piece:
    def __init__(self, image, color, start, moves):
        self.image = pygame.image.load(image)
        self.moves = moves
        self.x, self.y = start

    def get_rect(self):
        return self.x * WIDTH // 8, self.y * WIDTH // 8, self.image.get_width(), self.image.get_height()

    # Piece
    # - knows where it can move towards based off of its own moving possibilities (e.g: bishop on diagonals)
    # - kills itself if it has been taken
    # - keeps track of mouse clicks then asks board if ok

    # vielleicht x und y als grid coordinaten speichern (0, 1, 2, 3 ...
    # und wenn der pygame es "malen" will dann gibt mann den die grid
    # coordinaten * 100 (oder WIDTH // 8) zurueck
    # - daher kommt die get_rect function


class Pawn(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_pawn.png"
        super().__init__(self.image, color, start, self.get_moves)

    def get_moves(self):
        return [(0, 1), (0, 2), (1, 1, "takes")]

    # Individual Pieces:
    # - tells piece class its moving constraints
    # - its start
    # -


class Rook(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_rook.png"
        super().__init__(self.image, color, start, self.get_moves)

    def get_moves(self):
        moves = []
        for x in range(-7, 7):
            moves.append((x, 0))
        for y in range(-7, 7):
            moves.append((0, y))
        return moves


class Knight(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_knight.png"
        super().__init__(self.image, color, start, self.get_moves)

    def get_moves(self):
        moves = []
        return moves


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


def default_setup():
    whites = []
    blacks = []
    # pawns
    for i in range(8):
        whites.append(Pawn("white", (i, 6)))
    # knights
    whites.append(Knight("white", (1, 7)))
    whites.append(Knight("white", (6, 7)))
    # rooks
    whites.append(Rook("white", (0, 7)))
    whites.append(Rook("white", (7, 7)))

    return whites, blacks


if __name__ == '__main__':  # running the game
    # setting some values that will be useful
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('CHESS')

    draw_board(screen)

    board = Board()
    white_pieces, black_pieces = default_setup()

    # game loop
    run = True
    clock = pygame.time.Clock()
    while run:
        # regulate game speed
        clock.tick(FPS)

        # check events
        for event in pygame.event.get():

            # close window
            if event.type == pygame.QUIT:
                run = False

        pawn = Pawn("white", (1, 0))
        screen.blits((piece.image, piece.get_rect()) for piece in white_pieces)
        screen.blits((piece.image, piece.get_rect()) for piece in black_pieces)
        pygame.display.update()

    pygame.quit()
