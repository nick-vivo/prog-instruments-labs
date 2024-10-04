# https://vc.ru/dev/638343-tri-krutye-igry-na-python-s-ishodnikami

import sys
import random

from PyQt5.QtGui import QPainter, QColor

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal

from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication


class Tetris(QMainWindow):
    """
    The main class for the Tetris game.

    This class inherits from QMainWindow and implements the main game logic.
    """

    def __init__(self):
        """
        Initializes the Tetris game.

        Calls the parent class constructor and initializes the game interface.

        Note:
            This method is the constructor for the class.
        """
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the game interface.

        Creates the game board, sets it as the central widget,
        configures the status bar, and starts the game.

        Note:
            This method is responsible for setting up the game interface.
        """
        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        self.statusbar = self.statusBar()
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.tboard.start()

        self.resize(180, 380)
        self.center()
        self.setWindowTitle('Tetris')
        self.show()

    def center(self):
        """
        Centers the game window on the screen.

        Calculates the screen center coordinates and moves the game window
        to that position.

        Note:
            This method is used to position the game window on the screen.
        """
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width()-size.width())/2),
                  int((screen.height()-size.height())/2))


class Board(QFrame):
    """
    Represents a Tetris game board.

    Attributes:
        msg2Statusbar (pyqtSignal): Signal emitted to update the status bar.
        board_width (int): The width of the game board.
        board_height (int): The height of the game board.
        speed (int): The speed of the game.

    Methods:
        __init__(parent): Initializes the game board with the given parent.
        init_board(): Initializes the game board state.
        shape_at(x, y): Returns the shape at the given coordinates.
        set_shape_at(x, y, shape): Sets the shape at the given coordinates.
        square_width(): Returns the width of a square on the board.
        square_height(): Returns the height of a square on the board.
        start(): Starts the game.
        pause(): Pauses or resumes the game.
        paintEvent(event): Handles painting of the game board.
        keyPressEvent(event): Handles key press events.
        timerEvent(event): Handles timer events.
        clear_board(): Clears the game board.
        drop_down(): Drops the current piece down.
        one_line_down(): Moves the current piece down one line.
        piece_dropped(): Handles the piece being dropped.
        remove_full_lines(): Removes full lines from the game board.
        new_piece(): Creates a new piece.
        try_move(new_piece, newX, newY): Tries to move the piece to a
        new position.
        draw_square(painter, x, y, shape): Draws a square on the game board.
    """

    msg2Statusbar = pyqtSignal(str)

    board_width = 10
    board_height = 22
    speed = 300

    def __init__(self, parent):
        """
        Initializes the game board with the given parent.

        Args:
            parent: The parent widget of the game board.
        """

        super().__init__(parent)
        self.init_board()

    def init_board(self):
        """
        Initializes the game board state.
        """

        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clear_board()

    def shape_at(self, x, y):
        """
        Returns the shape at the given coordinates.

        Args:
            x (int): The x-coordinate of the shape.
            y (int): The y-coordinate of the shape.

        Returns:
            int: The shape at the given coordinates.
        """

        return self.board[(y * Board.board_width) + x]

    def set_shape_at(self, x, y, shape):
        """
        Sets the shape at the given coordinates.

        Args:
            x (int): The x-coordinate of the shape.
            y (int): The y-coordinate of the shape.
            shape (int): The shape to set.
        """

        self.board[(y * Board.board_width) + x] = shape

    def square_width(self):
        """
        Returns the width of a square on the board.

        Returns:
            int: The width of a square on the board.
        """

        return self.contentsRect().width() // Board.board_width

    def square_height(self):
        """
        Returns the height of a square on the board.

        Returns:
            int: The height of a square on the board.
        """

        return self.contentsRect().height() // Board.board_height

    def start(self):
        """
        Starts the game.
        """

        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clear_board()

        self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.new_piece()
        self.timer.start(Board.speed, self)

    def pause(self):
        """
        Pauses or resumes the game.
        """

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")

        else:
            self.timer.start(Board.speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update()

    def paintEvent(self, event):
        """
        Handles painting of the game board.

        Args:
            event: The paint event.
        """

        painter = QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.board_height * self.square_height()

        for i in range(Board.board_height):
            for j in range(Board.board_width):
                shape = self.shape_at(j, Board.board_height - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.draw_square(painter,
                                    rect.left() + j * self.square_width(),
                                    boardTop + i * self.square_height(), shape)

            if self.curPiece.shape() != Tetrominoe.NoShape:

                for i in range(4):

                    x = self.curX + self.curPiece.x(i)
                    y = self.curY - self.curPiece.y(i)

                    self.draw_square(painter,
                                    rect.left() + x * self.square_width(),
                                    boardTop + (Board.board_height - y - 1) * self.square_height(),
                                    self.curPiece.shape())

    def keyPressEvent(self, event):
        """
        Handles key press events.

        Args:
            event: The key press event.
        """

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.try_move(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.try_move(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Down:
            self.try_move(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_Up:
            self.try_move(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_Space:
            self.drop_down()

        elif key == Qt.Key_D:
            self.one_line_down()

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):
        """
        Handles timer events.

        Args:
            event: The timer event.

        If the event is triggered by the game timer, it either starts a new
        piece or moves the current piece down.
        """

        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.new_piece()
            else:
                self.one_line_down()

        else:
            super(Board, self).timerEvent(event)

    def clear_board(self):
        """
        Clears the game board by setting all shapes to NoShape.
        """

        for i in range(Board.board_height * Board.board_width):
            self.board.append(Tetrominoe.NoShape)

    def drop_down(self):
        """
        Drops the current piece down as far as possible.
        """

        newY = self.curY

        while newY > 0:

            if not self.try_move(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.piece_dropped()

    def one_line_down(self):
        """
        Moves the current piece down one line.
        """

        if not self.try_move(self.curPiece, self.curX, self.curY - 1):
            self.piece_dropped()

    def piece_dropped(self):
        """
        Handles the piece being dropped.

        Sets the shape of the dropped piece on the board, removes full lines,
        and starts a new piece if necessary.
        """

        for i in range(4):

            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.set_shape_at(x, y, self.curPiece.shape())

        self.remove_full_lines()

        if not self.isWaitingAfterLine:
            self.new_piece()

    def remove_full_lines(self):
        """
        Removes full lines from the board.

        Shifts down all lines above the full lines and updates the number of
        removed lines.
        """

        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.board_height):

            n = 0
            for j in range(Board.board_width):
                if not self.shape_at(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:

            for k in range(m, Board.board_height):

                for j in range(Board.board_width):
                    self.set_shape_at(j, k, self.shape_at(j, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0:

            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    def new_piece(self):
        """
        Starts a new piece.

        Creates a new random piece and sets its position on the board.
        """

        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.board_width // 2 + 1
        self.curY = Board.board_height - 1 + self.curPiece.minY()

        if not self.try_move(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")

    def try_move(self, new_piece, newX, newY):
        """
        Tries to move the piece to a new position.

        Args:
            new_piece: The new piece to move.
            newX (int): The new x-coordinate of the piece.
            newY (int): The new y-coordinate of the piece.

        Returns:
            bool: True if the move is successful, False otherwise.
        """

        for i in range(4):

            x = newX + new_piece.x(i)
            y = newY - new_piece.y(i)

            if (x < 0 or x >= Board.board_width or
                    y < 0 or y >= Board.board_height):

                return False

            if self.shape_at(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = new_piece
        self.curX = newX
        self.curY = newY
        self.update()

        return True

    def draw_square(self, painter, x, y, shape):
        """
        Draws a square on the board.

        Args:
            painter: The painter to use.
            x (int): The x-coordinate of the square.
            y (int): The y-coordinate of the square.
            shape (int): The shape of the square.

        Draws a square on the board with the specified shape and color.
        """

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())

        painter.drawLine(x + 1, y + self.square_height() - 1,
                         x + self.square_width() - 1,
                         y + self.square_height() - 1)

        painter.drawLine(x + self.square_width() - 1,
                         y + self.square_height() - 1,
                         x + self.square_width() - 1,
                         y + 1)


class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):

    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):

        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)


    def shape(self):
        return self.pieceShape


    def setShape(self, shape):

        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape


    def setRandomShape(self):
        self.setShape(random.randint(1, 7))


    def x(self, index):
        return self.coords[index][0]


    def y(self, index):
        return self.coords[index][1]


    def setX(self, index, x):
        self.coords[index][0] = x


    def setY(self, index, y):
        self.coords[index][1] = y


    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m



    def maxX(self):

            m = self.coords[0][0]
            for i in range(4):
                m = max(m, self.coords[i][0])

            return m


    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m


    def maxY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m


    def rotateLeft(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result


    def rotateRight(self):

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


if __name__ == '__main__':

    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())