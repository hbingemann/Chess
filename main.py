# ---------------------------------------------------
# |                    CHESS                        |
# ---------------------------------------------------

import pygame

SIZE = WIDTH, HEIGHT = 800, 800
FPS = 60
SQUARE_SIZE = WIDTH // 8


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
        # self.pieces = [class, class, class ...]

    def mouse_down(self, pos, button):
        if button != 1:  # not left click
            return None
        for piece in self.pieces:
            if piece.get_rect().collidepoint(pos):
                return piece
        return None

    def remove_at(self, caller_piece, pos):
        for piece in self.pieces:
            if (piece.x, piece.y) == pos and piece != caller_piece:
                self.pieces.remove(piece)
                return

    def get_available_squares(self, caller_piece, squares):
        # make sure squares are on board
        for square in squares:
            if not 0 <= square[0] < 8 or not 0 <= square[1] < 8:
                squares.remove(square)
        # define variables
        pos = caller_piece.x, caller_piece.y
        collision_squares = []
        taking_squares = []
        blocked_squares = []
        # check if a square is on a piece
        for piece in self.pieces:
            if (piece.x, piece.y) in squares:
                collision_squares.append((piece.x, piece.y))
                if piece.color != caller_piece.color:
                    taking_squares.append((piece.x, piece.y))
        # check if squares are blocked
        for square in collision_squares:
            # calculate what direction the square is from the original position
            change = square[0] - pos[0], square[1] - pos[1]
            move_dir_x = change[0] // abs(change[0]) if change[0] != 0 else 0
            move_dir_y = change[1] // abs(change[1]) if change[1] != 0 else 0
            # then disallow all squares behind that square
            for i in range(1, 8):
                blocked_square = square[0] + move_dir_x * i, square[1] + move_dir_y * i
                if blocked_square in squares:
                    blocked_squares.append(blocked_square)
        # remove squares behind other pieces
        for square in blocked_squares:
            if square in squares:
                squares.remove(square)
        # remove squares where collisions occur
        for square in collision_squares:
            if square in squares:
                squares.remove(square)
        # add squares where collisions occur but a piece takes
        for square in taking_squares:
            if square not in squares and square not in blocked_squares:
                squares.append(square)
        # check for special pawn rules
        if isinstance(caller_piece, Pawn):
            temp_squares = []
            for square in squares:
                # getting change
                change = abs(square[0] - pos[0]), abs(square[1] - pos[1])
                if change == (1, 1):  # if moving on a diagonal
                    if square in taking_squares:  # if its a taking square and not creating a duplicate
                        temp_squares.append(square)  # add it
                elif change == (0, 1) or change == (0, 2):  # its moving on a straight
                    if square not in taking_squares:
                        temp_squares.append(square)
            squares = temp_squares
        return squares

    # Board:
    # - keeps track of piece locations
    # - tells piece if move is legal / possible (not blocked by other piece)


class Piece:
    def __init__(self, image, color, start):
        self.color = color
        self.available_squares = []
        self.image = pygame.image.load(image)
        self.moves = self.get_moves()
        self._pixel_x, self._pixel_y = (i * 100 for i in start)
        self._x, self._y = start
        self.picked_up_pos = self.x, self.y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val
        self._pixel_x = val * SQUARE_SIZE

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
        self._pixel_y = val * SQUARE_SIZE

    @property
    def pixel_x(self):
        return self._pixel_x

    @pixel_x.setter
    def pixel_x(self, val):
        self._pixel_x = val
        self._x = val // SQUARE_SIZE

    @property
    def pixel_y(self):
        return self._pixel_y

    @pixel_y.setter
    def pixel_y(self, val):
        self._pixel_y = val
        self._y = val // SQUARE_SIZE

    def get_moves(self):
        raise NotImplementedError

    def get_rect(self):
        return pygame.Rect(self.pixel_x, self.pixel_y, self.image.get_width(), self.image.get_height())

    def pick_up(self, board):
        # create list of all positions it can move to
        # give board that list
        # board returns all places it can move to
        # keep track of current (later original) location / show possible moves
        legal_squares = [(self.x + change_x, self.y + change_y) for change_x, change_y in
                         self.moves]  # before check with board
        self.available_squares = board.get_available_squares(self, legal_squares)  # after check with board
        self.picked_up_pos = self.x, self.y
        pass

    def drop(self, pos, board):
        grid_pos = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        if grid_pos in self.available_squares:
            self.x, self.y = grid_pos
            if isinstance(self, Pawn):
                if (0, -2) in self.moves:  # white pawn
                    self.moves.remove((0, -2))
                elif (0, 2) in self.moves:  # black pawn
                    self.moves.remove((0, 2))
            board.remove_at(self, (self.x, self.y))
        else:
            self.x, self.y = self.picked_up_pos

    # Piece
    # - knows where it can move towards based off of its own moving possibilities (e.g: bishop on diagonals)
    # - kills itself if it has been taken
    # - keeps track of mouse clicks then asks board if ok


class Pawn(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_pawn.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        if self.color == "white":
            return [(0, -1), (0, -2), (1, -1), (-1, -1)]
        else:
            return [[(0, 1), (0, 2), (1, 1), (-1, 1)]]

    # Individual Pieces:
    # - tells piece class its moving constraints
    # - its start
    # -


class Rook(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_rook.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = []
        for x in range(-7, 8):
            moves.append((x, 0))
            moves.append((0, x))
        return moves


class Knight(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_knight.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        return moves


class Bishop(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_bishop.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = []
        for i in range(-7, 8):
            moves.append((i, i))
            moves.append((-i, i))
        return moves


class Queen(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_queen.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = []
        for i in range(-7, 8):
            moves.append((i, i))
            moves.append((-i, i))
        for x in range(-7, 8):
            moves.append((x, 0))
            moves.append((0, x))
        return moves


class King(Piece):
    def __init__(self, color, start):
        self.image = "img/" + color + "_king.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        return moves


def draw_board(surface):
    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:  # to make checkered pattern
                col = "#61a055"  # green
            else:
                col = "#ebf2d2"  # white
            pygame.draw.rect(surface, col, (x * SQUARE_SIZE, y * SQUARE_SIZE, WIDTH, HEIGHT))


def default_setup():
    whites = []
    blacks = []
    # pawns
    for i in range(8):
        whites.append(Pawn("white", (i, 6)))
        blacks.append(Pawn("black", (i, 1)))
    # knights
    whites.append(Knight("white", (1, 7)))
    whites.append(Knight("white", (6, 7)))
    blacks.append(Knight("black", (1, 0)))
    blacks.append(Knight("black", (6, 0)))
    # rooks
    whites.append(Rook("white", (0, 7)))
    whites.append(Rook("white", (7, 7)))
    blacks.append(Rook("black", (0, 0)))
    blacks.append(Rook("black", (7, 0)))
    # bishops
    whites.append(Bishop("white", (2, 7)))
    whites.append(Bishop("white", (5, 7)))
    blacks.append(Bishop("black", (2, 0)))
    blacks.append(Bishop("black", (5, 0)))
    # king and queen
    whites.append(Queen("white", (3, 7)))
    whites.append(King("white", (4, 7)))
    blacks.append(Queen("black", (3, 0)))
    blacks.append(King("black", (4, 0)))

    return whites, blacks


if __name__ == '__main__':  # running the game
    # setting some values that will be useful
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('CHESS')

    draw_board(screen)

    board = Board()
    white_pieces, black_pieces = default_setup()
    board.pieces = white_pieces + black_pieces

    piece_following_mouse = None

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

            # mouse down
            elif event.type == pygame.MOUSEBUTTONDOWN:
                piece = board.mouse_down(event.pos, event.button)
                if piece is not None:
                    piece_following_mouse = piece
                    piece.pick_up(board)

            # mouse up
            elif event.type == pygame.MOUSEBUTTONUP:
                if piece_following_mouse is not None:
                    piece_following_mouse.drop(event.pos, board)
                    piece_following_mouse = None

        # if dragging a piece
        if piece_following_mouse is not None:
            piece_following_mouse.pixel_x = pygame.mouse.get_pos()[0] - piece_following_mouse.image.get_width() // 2
            piece_following_mouse.pixel_y = pygame.mouse.get_pos()[1] - piece_following_mouse.image.get_height() // 2

        # update screen
        draw_board(screen)
        screen.blits((piece.image, piece.get_rect()) for piece in board.pieces if piece is not piece_following_mouse)
        if piece_following_mouse is not None:
            screen.blit(piece_following_mouse.image, piece_following_mouse.get_rect())
        pygame.display.update()

    pygame.quit()
