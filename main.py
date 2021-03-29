# ---------------------------------------------------
# |                    CHESS                        |
# ---------------------------------------------------

import pygame
import os
from stockfishWrapper import StockfishWrapper

# initialize packages
pygame.font.init()
stockfish = StockfishWrapper()

# global constants
SIZE = WIDTH, HEIGHT = 1000, 800
FPS = 60
SQUARE_SIZE = 100
AVAILABLE_MOVE_CIRCLE_COLOR = (50, 50, 50, 100)  # last num is alpha value
AVAILABLE_MOVE_CIRCLE_RADIUS = 18 * 0.01 * SQUARE_SIZE
MENU_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("img", "chess_background.jpg")), SIZE)
LIGHT_GREY = (150, 150, 150, 100)
BLACK = (0, 0, 0, 50)
BLUE = (0, 0, 200)
WHITE = (220, 220, 220)


# TODO:
#  - en passant (special pawn move)
#  - add stockfish
#  - create menu
#  - checkmate returns to menu
#  - add a puzzle database
#  - create endgame scenarios


class Board:
    def __init__(self):
        self.pieces = []
        # self.pieces = [class, class, class ...]
        self.circles = []
        # self.circles = [circle_center, circle_center ... ]
        self.moves = []
        # self.moves = ["e2e4", "e7e5", ...
        self.turn = "white"

    def new_circles(self, squares):
        self.circles = []
        for square in squares:
            self.circles.append(
                (square[0] * SQUARE_SIZE + SQUARE_SIZE // 2, square[1] * SQUARE_SIZE + SQUARE_SIZE // 2))

    def mouse_down(self, pos, button):
        if button != 1:  # not left click
            return None  # then exit because it should be left click
        for piece in self.pieces:
            if piece.get_rect().collidepoint(pos) and piece.color == self.turn:
                return piece
        return None

    def remove_at(self, caller_piece):
        for piece in self.pieces:
            if (piece.x, piece.y) == (caller_piece.x, caller_piece.y) and piece.color != caller_piece.color:
                self.pieces.remove(piece)
                return

    def get_available_squares(self, caller_piece, squares):  # if its moves are legal
        squares = self.get_possible_squares(caller_piece, squares)
        squares = self.check_for_castling(caller_piece, squares)
        # check if putting own king in check
        temp_squares = squares.copy()
        for square in temp_squares:
            if self.does_move_become_check(caller_piece, square):
                squares.remove(square)
        return squares

    def check_for_castling(self, caller_piece, squares):
        if isinstance(caller_piece, King):
            castle_moves = [square for square in squares if abs(square[0] - caller_piece.x) == 2]
            # remove squares and append later if allowed
            for square in castle_moves:
                squares.remove(square)
            # look for rooks
            rooks = [piece for piece in self.pieces if
                     isinstance(piece, Rook) and piece.color == caller_piece.color and not piece.has_moved]
            y_pos = 0 if caller_piece.color == "black" else 7
            # look for rooks on right and left
            rook_right = next((rook for rook in rooks if (rook.x, rook.y) == (7, y_pos)), None)
            rook_left = next((rook for rook in rooks if (rook.x, rook.y) == (0, y_pos)), None)
            if len(castle_moves) > 0 and len(rooks) > 0:
                if rook_right is not None and (caller_piece.x + 1, caller_piece.y) in rook_right.get_possible_squares(
                        self):
                    # possible to castle right
                    # legal to castle right? (not put in check)
                    legal = True
                    for i in range(1, 3):
                        if self.does_move_become_check(caller_piece, (caller_piece.x + i, caller_piece.y)):
                            legal = False
                            break
                    if legal:
                        squares.append((caller_piece.x + 2, caller_piece.y))
                if rook_left is not None and (caller_piece.x - 1, caller_piece.y) in rook_left.get_possible_squares(
                        self):
                    # possible to castle left
                    # legal to castle left?
                    legal = True
                    for i in range(-2, 0):
                        if self.does_move_become_check(caller_piece, (caller_piece.x + i, caller_piece.y)):
                            legal = False
                            break
                    if legal:
                        squares.append((caller_piece.x - 2, caller_piece.y))
        return squares

    def get_possible_squares(self, caller_piece, squares):  # just if its moves are physically possible
        # make sure squares are on board
        temp_squares = squares.copy()
        for square in temp_squares:
            if square[0] > 7 or square[0] < 0 or square[1] > 7 or square[1] < 0:
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
                    if square in taking_squares:  # if its a taking square
                        temp_squares.append(square)  # add it
                elif change == (0, 1) or change == (0, 2):  # its moving on a straight
                    if square not in taking_squares:  # if its not a taking square
                        temp_squares.append(square)
            squares = temp_squares
        return squares

    def king_in_check(self, color):
        # color is color of king that could be in check
        king_pos = [(piece.x, piece.y) for piece in self.pieces if isinstance(piece, King) and piece.color == color]
        king_pos = king_pos[0] if len(king_pos) > 0 else None
        for piece in self.pieces:
            if piece.color != color:
                for square in piece.get_possible_squares(self):
                    if king_pos == square:
                        return True
        return False

    def does_move_become_check(self, moving_piece, move_to_position):
        prev_position = moving_piece.x, moving_piece.y
        # temporarily create a new board
        moving_piece.x, moving_piece.y = move_to_position
        taken_piece = None
        for piece in self.pieces:
            if (piece.x, piece.y) == move_to_position and piece is not moving_piece:
                taken_piece = piece
                self.pieces.remove(piece)
                break
        # test if this temporary board sets king in check
        is_in_check = self.king_in_check(moving_piece.color)
        if taken_piece is not None:
            self.pieces.append(taken_piece)
        # reset back to original board
        moving_piece.x, moving_piece.y = prev_position
        # return whether that would set own king in check
        return is_in_check

    def insufficient_material(self):  # check for insufficient material ex: king and king
        pieces = [piece for piece in self.pieces if not isinstance(piece, King)]
        piece_initials = [piece.__str__()[10] for piece in pieces]
        if len(pieces) == 0:  # king and king
            return True
        if len(pieces) == 1:  # only one piece (besides kings)
            if "B" in piece_initials:  # just a bishop cannot checkmate
                return True
            if "K" in piece_initials:  # just a knight cannot checkmate
                return True
        elif len(pieces) == 2:  # there are two pieces (besides king)
            if piece_initials == ["B", "B"]:  # bishop vs. bishop cannot checkmate if bishops are on same color square
                if pieces[0].color != pieces[1].color and (pieces[0].x + pieces[0].y) % 2 != (
                        pieces[1].x + pieces[1].y) % 2:
                    return True
        # these are the only insufficient materials
        # so we can otherwise assume there is enough material to checkmate
        return False

    def add_move(self, move):
        self.moves.append(move)
        stockfish.set_position(self.moves)
        end = "\n" if self.turn == "black" else " "
        print(move, end=end)
        self.turn = "black" if self.turn == "white" else "white"  # swap turn

    def move_piece_at_to(self, move_from, move_to):
        for piece in self.pieces:
            if (piece.x, piece.y) == move_from:
                piece.pick_up(self)
                piece.drop(move_to, self)
                break


class Piece:
    def __init__(self, image, color, start):
        self.color = color
        self.available_squares = []
        self.image = pygame.image.load(os.path.join("img", image))
        self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        self.moves = self.get_moves()
        self._pixel_x, self._pixel_y = (i * SQUARE_SIZE for i in start)
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

    def get_initial(self):
        raise NotImplementedError

    def get_initial_code(self):
        if self.color == "white":
            return self.get_initial().upper()
        else:
            return self.get_initial().lower()

    def get_rect(self):
        return pygame.Rect(self.pixel_x, self.pixel_y, self.image.get_width(), self.image.get_height())

    def pick_up(self, board):
        # create list of all positions it can move to
        # give board that list
        # board returns all places it can move to
        # keep track of current (later original) location / show possible moves
        self.available_squares = self.get_available_squares(board)
        board.new_circles(self.available_squares)
        self.picked_up_pos = self.x, self.y
        pass

    def drop(self, pos, board):
        board.circles = []
        if pos in self.available_squares:
            self.x, self.y = pos
            board.remove_at(self)
            if isinstance(self, Pawn):
                self.delete_moves()  # delete double move
                if self.y == 0 or self.y == 7:
                    new_piece = Queen(self.color, (self.x, self.y))
                    board.pieces.append(new_piece)
                    board.pieces.remove(self)
            elif isinstance(self, King):
                self.delete_moves()  # delete castling move
                # if just did a castle
                # move the rook that castled with
                y_pos = 0
                if self.color == "white":
                    y_pos = 7
                if pos[0] - self.picked_up_pos[0] == 2:
                    # moved right
                    for piece in board.pieces:
                        if isinstance(piece, Rook) and (piece.x, piece.y) == (7, y_pos):
                            piece.x = 5
                elif pos[0] - self.picked_up_pos[0] == -2:
                    # moved left
                    for piece in board.pieces:
                        if isinstance(piece, Rook) and (piece.x, piece.y) == (0, y_pos):
                            piece.x = 3
            elif isinstance(self, Rook):
                self.has_moved = True
            board.add_move(stockfish.get_algebraic_notation(self, self.picked_up_pos, pos))
        else:
            self.x, self.y = self.picked_up_pos

    def get_available_squares(self, board):
        legal_squares = [(self.x + change_x, self.y + change_y) for change_x, change_y in self.moves]
        final_squares = board.get_available_squares(self, legal_squares)
        return final_squares

    def get_possible_squares(self, board):
        legal_squares = [(self.x + change_x, self.y + change_y) for change_x, change_y in self.moves]
        squares = board.get_possible_squares(self, legal_squares)
        return squares


class Pawn(Piece):
    def __init__(self, color, start):
        self.image = color + "_pawn.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        if self.color == "white":
            return [(0, -1), (0, -2), (1, -1), (-1, -1)]
        else:  # color = black
            return [(0, 1), (0, 2), (1, 1), (-1, 1)]

    def delete_moves(self):
        if (0, -2) in self.moves:  # white pawn
            self.moves.remove((0, -2))
        elif (0, 2) in self.moves:  # black pawn
            self.moves.remove((0, 2))

    def get_initial(self):
        return "P"

    # Individual Pieces:
    # - tells piece class its moving constraints
    # - its start
    # -


class Rook(Piece):
    def __init__(self, color, start):
        self.image = color + "_rook.png"
        self.has_moved = False
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = []
        for x in range(-7, 8):
            moves.append((x, 0))
            moves.append((0, x))
        return moves

    def get_initial(self):
        return "R"


class Knight(Piece):
    def __init__(self, color, start):
        self.image = color + "_knight.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        return moves

    def get_initial(self):
        return "N"


class Bishop(Piece):
    def __init__(self, color, start):
        self.image = color + "_bishop.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = []
        for i in range(-7, 8):
            moves.append((i, i))
            moves.append((-i, i))
        return moves

    def get_initial(self):
        return "B"


class Queen(Piece):
    def __init__(self, color, start):
        self.image = color + "_queen.png"
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

    def get_initial(self):
        return "Q"


class King(Piece):
    def __init__(self, color, start):
        self.image = color + "_king.png"
        super().__init__(self.image, color, start)

    def get_moves(self):
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0)]
        return moves

    def delete_moves(self):
        if (2, 0) in self.moves:
            self.moves.remove((2, 0))
            self.moves.remove((-2, 0))

    def get_initial(self):
        return "K"


def draw_board(surface):
    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:  # to make checkered pattern
                col = "#61a055"  # green
            else:
                col = "#ebf2d2"  # white
            pygame.draw.rect(surface, col, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_circles(surface, circles):
    s = pygame.Surface(SIZE, pygame.SRCALPHA)
    for circle_pos in circles:
        pygame.draw.circle(s, AVAILABLE_MOVE_CIRCLE_COLOR, circle_pos, AVAILABLE_MOVE_CIRCLE_RADIUS)
    surface.blit(s, (0, 0))


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


def normal_game(screen, computer=False):
    # setting some values that will be useful

    draw_board(screen)

    board = Board()
    white_pieces, black_pieces = default_setup()
    board.pieces = white_pieces + black_pieces

    piece_following_mouse = None

    # game loop
    run = True
    quit_window = False
    clock = pygame.time.Clock()
    while run:
        # regulate game speed
        clock.tick(FPS)

        # check events
        for event in pygame.event.get():

            # close window
            if event.type == pygame.QUIT:
                run = False
                quit_window = True

            # mouse click/down
            elif event.type == pygame.MOUSEBUTTONDOWN:
                piece = board.mouse_down(event.pos, event.button)
                if piece is not None:
                    if not (board.turn == "black" and computer):
                        piece_following_mouse = piece
                        piece.pick_up(board)

            # mouse release/up
            elif event.type == pygame.MOUSEBUTTONUP:
                if piece_following_mouse is not None:
                    mouse_grid_pos = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                    piece_following_mouse.drop(mouse_grid_pos, board)
                    piece_following_mouse = None
                    # see if there is checkmate
                    pieces_with_moves = [piece for piece in board.pieces if piece.color == board.turn
                                         and len(piece.get_available_squares(board)) > 0]
                    if len(pieces_with_moves) == 0:
                        # there are no pieces with moves
                        # it is either checkmate or stalemate
                        if board.king_in_check(board.turn):
                            winner = "White" if board.turn == "black" else "Black"
                            print("\n Checkmate!! \n " + winner + " wins!!")
                        else:
                            print("\n Stalemate. \n It's a draw.")
                    if board.insufficient_material():
                        print("\n Insufficient Material. \n It's a draw.")

        # if dragging a piece then move piece to mouse
        if piece_following_mouse is not None:
            piece_following_mouse.pixel_x = pygame.mouse.get_pos()[0] - piece_following_mouse.image.get_width() // 2
            piece_following_mouse.pixel_y = pygame.mouse.get_pos()[1] - piece_following_mouse.image.get_height() // 2

        # draw background/board
        draw_board(screen)
        # draw all pieces
        screen.blits((piece.image, piece.get_rect()) for piece in board.pieces if piece is not piece_following_mouse)
        # draw available move circles
        draw_circles(screen, board.circles)
        # draw currently held piece
        if piece_following_mouse is not None:
            screen.blit(piece_following_mouse.image, piece_following_mouse.get_rect())
        # update screen
        pygame.display.update()

        # after we updated the graphic let computer go
        if computer and board.turn == "black":  # playing against computer
            move = stockfish.get_best_move_time(200)
            move_from, move_to = stockfish.get_coordinate_notation(move)
            board.move_piece_at_to(move_from, move_to)

    # if quitting window
    if quit_window:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    return


class Slider:
    def __init__(self, screen, background_image, pos, size, minimum, maximum, text, callback):
        self.screen = screen
        self.pos = self.x, self.y = pos
        self.font = pygame.font.SysFont("loma", 48, True)
        self.size = self.width, self.height = 300, 60  # hier hier hier hier ist size
        self.background_image = pygame.transform.scale(pygame.image.load(background_image), self.size)
        self.text = text
        self.callback = callback
        self.max = maximum
        self.min = minimum
        self.value = minimum
        self.following_mouse = False
        self.num_increments = self.max - self.min + 1  # plus one because max and min included
        self.increment_size = self.width / self.num_increments
        self.line_size = self.line_width, self.line_height = self.width - 40, 5

    def draw(self):
        # background
        self.screen.blit(self.background_image, self.get_rect())
        # always want to be following mouse if supposed to
        self.follow_mouse()
        # add text
        text = self.font.render(self.text + str(self.value), True, (20, 20, 20))
        text_y = self.y - 10
        text_x = self.x + self.width // 2 - text.get_width() // 2
        self.screen.blit(text, (text_x, text_y))
        # add the slider part
        line_start = (self.x + (self.line_width - self.width) // 2, self.y + text.get_height())
        line_end = (self.x + self.width - (self.line_width - self.width) // 2, self.y + text.get_height())
        pygame.draw.line(self.screen, WHITE, line_start, line_end, self.line_height)
        # add the circle indicator
        circle_x = self.x + (self.value - self.min) * self.increment_size
        circle_y = self.y + text.get_height()
        pygame.draw.circle(self.screen, BLUE, (circle_x, circle_y), 15)

    def mouse_down(self, mouse_pos):
        if pygame.Rect.collidepoint(self.get_rect(), mouse_pos):
            self.following_mouse = True

    def mouse_up(self, mouse_pos):
        self.following_mouse = False
        self.callback(self.value)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def follow_mouse(self):
        if self.following_mouse and pygame.Rect.collidepoint(self.get_rect(), pygame.mouse.get_pos()):
            mouse_x = pygame.mouse.get_pos()[0]
            self.value = int((mouse_x - self.x) // self.increment_size + self.min)
        elif self.following_mouse:
            mouse_x = pygame.mouse.get_pos()[0]
            if mouse_x < self.x:
                self.value = self.min
            elif mouse_x > self.x + self.width:
                self.value = self.max


class Button:
    def __init__(self, screen, image, pos, size, text, callback):
        self.screen = screen
        self.image = pygame.transform.scale(pygame.image.load(image), size)
        self.pos = self.x, self.y = pos
        self.font = pygame.font.SysFont("loma", 48, True)
        self.size = self.width, self.height = size
        self.text = text
        self.callback = callback

    def mouse_up(self, mouse_pos):
        pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def mouse_down(self, mouse_pos):
        if pygame.Rect.collidepoint(self.get_rect(), mouse_pos):
            self.callback()

    def draw(self):
        self.screen.blit(self.image, self.pos)
        text = self.font.render(self.text, True, (20, 20, 20))
        text_x = self.x + self.width // 2 - text.get_width() // 2
        text_y = self.y + self.height // 2 - text.get_height() // 2
        self.screen.blit(text, (text_x, text_y))
        if pygame.Rect.collidepoint(self.get_rect(), pygame.mouse.get_pos()):
            s = pygame.Surface(SIZE, pygame.SRCALPHA)
            pygame.draw.rect(s, BLACK, self.get_rect())
            self.screen.blit(s, (0, 0))


class Menu:
    def __init__(self, screen):
        self.widgets = []
        self.title = None
        self.title_pos = None
        self.screen = screen

    def draw(self):
        for widget in self.widgets:
            widget.draw()
        self.screen.blit(self.title, self.title_pos)

    def back(self):
        pass

    def add_button(self, text, callback):
        num_widgets = len(self.widgets)
        button_size = 300, 60
        button_file = os.path.join("img", "widget" + str(num_widgets % 5 + 1) + ".png")
        pos = 130, 100 * num_widgets + 170
        button = Button(self.screen, button_file, pos, button_size, text, callback)
        self.widgets.append(button)

    def add_slider(self, text, callback, minimum, maximum):
        num_widgets = len(self.widgets)
        slider_size = 200, 50
        slider_background = os.path.join("img", "widget" + str(num_widgets % 5 + 1) + ".png")
        pos = 130, 100 * num_widgets + 170
        slider = Slider(self.screen, slider_background, pos, slider_size, minimum, maximum, text, callback)
        self.widgets.append(slider)

    def add_dropdown(self):
        pass

    def add_title(self, text):
        font = pygame.font.SysFont("Ubuntu", 96)
        title = font.render(text, True, (220, 220, 220))
        pos = 260 - title.get_width() // 2, 30
        self.title = title
        self.title_pos = pos

    def mouse_down(self, mouse_pos):
        for widget in self.widgets:
            widget.mouse_down(mouse_pos)

    def mouse_up(self, mouse_pos):
        for widget in self.widgets:
            widget.mouse_up(mouse_pos)


class GameState:
    def __init__(self):
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption('CHESS')
        # initialize menus
        self.main_menu = Menu(self.screen)
        self.settings_menu = Menu(self.screen)
        # add menu widgets
        self.add_main_menu_widgets()
        self.add_settings_menu_widgets()
        # begin loop
        self.active_menu = self.main_menu
        self.menu_loop(self.screen)

    def add_main_menu_widgets(self):
        menu = self.main_menu
        button_info = {"Human": lambda: normal_game(self.screen),
                       "Computer": lambda: normal_game(self.screen, computer=True),
                       "Settings": lambda: self.set_active_menu(self.settings_menu),
                       "Quit": lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
                       }
        slider_info = {"Difficulty: ": (lambda x: stockfish.set_skill_level(x), 2, 25),
                       }
        for name, callback in button_info.items():
            menu.add_button(name, callback)
        for name, (callback, minimum, maximum) in slider_info.items():
            menu.add_slider(name, callback, minimum, maximum)
        menu.add_title("Chess")

    def add_settings_menu_widgets(self):
        menu = self.settings_menu
        button_info = {"Back": lambda: self.set_active_menu(self.main_menu),
                       "Quit": lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
                       }
        for name, callback in button_info.items():
            menu.add_button(name, callback)
        menu.add_title("Settings")

    def set_active_menu(self, menu):
        self.active_menu = menu

    def menu_loop(self, screen):

        # start main loop
        clock = pygame.time.Clock()
        run = True
        while run:  # main loop guckt nach mouse clicks und so und lauft die game loops

            # regulate fps
            clock.tick(FPS)

            # check events
            for event in pygame.event.get():

                # close window
                if event.type == pygame.QUIT:
                    run = False

                # mouse click/down
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.active_menu.mouse_down(event.pos)

                # mouse release/up
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.active_menu.mouse_up(event.pos)

                # mouse move
                elif event.type == pygame.MOUSEMOTION:
                    pass

            # update screen
            screen.blit(MENU_BACKGROUND, (0, 0))
            self.active_menu.draw()
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    gamestate = GameState()
