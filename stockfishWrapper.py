from stockfish import Stockfish
import os


class StockfishWrapper(Stockfish):
    def __init__(self, location=os.path.join("Stockfish/src", "stockfish")):
        self.think_time = 200
        super().__init__(location)

    def set_computer_think_time(self, time: int):
        """

        :param time:
            an integer in milliseconds of time that the computer will think for
        :return:
            nothing
        """
        self.think_time = time

    def get_algebraic_notation(self, piece, move_from: tuple, move_to: tuple) -> str:
        """

        :param piece:
            the piece class that moved
        :param move_from:
            tuple (x, y) position from 0 to 7 starting in top left
        :param move_to:
            same as move from, but ending position
        :return:
            move in algebraic notation as str
        """
        letters = [val for val in "abcdefgh"]
        column_from = letters[move_from[0]]
        row_from = 8 - move_from[1]
        column_to = letters[move_to[0]]
        row_to = 8 - move_to[1]
        move = str(column_from) + str(row_from) + str(column_to) + str(row_to)
        if piece.get_initial() == "P":
            if move_to[1] in (0, 7):
                move += "q"  # the promotion value
        return move

    def get_coordinate_notation(self, move: str):
        letters = [val for val in "abcdefgh"]
        column_from = letters.index(move[0])
        row_from = 8 - int(move[1])
        column_to = letters.index(move[2])
        row_to = 8 - int(move[3])
        move_from = column_from, row_from
        move_to = column_to, row_to
        return move_from, move_to

    def get_fen_notation(self, pieces: list) -> str:
        """

        :param pieces:
            a list of piece classes
        :return:
            fen string notation
        """
        result = ""
        board_matrix = [[" " for col in range(8)] for row in range(8)]
        for piece in pieces:
            board_matrix[piece.x][piece.y] = piece.get_initial_code()
        for row in board_matrix:
            blanks = 0
            for val in row:
                if val == " ":
                    blanks += 1
                else:  # val = initial
                    if blanks != 0:
                        result += str(blanks)
                        blanks = 0
                    result += val
            if blanks != 0:
                result += str(blanks)
            result += "/"

        return result
