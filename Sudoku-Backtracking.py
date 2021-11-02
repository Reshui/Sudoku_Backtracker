
import pygame
import sys
import requests

from pygame.locals import *

screen_size = 11 * 60
square_length = screen_size // 11
FPS = 60  # 30

default_text_color = (0, 0, 0)
false_path_color = (255, 140, 38)
background_color = (233, 233, 233)
attempted_path_color = (125, 114, 122)
user_input_color = (203, 153, 190)
selected_square_color = (161, 218, 232)
pygame.init()

used_font = pygame.font.SysFont('Comic Sans MS', 35)
button_font = pygame.font.SysFont('Comic Sans MS', 27)

# Numbers 0-9 on keyboard
valid_numbers = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
                 pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3,
                 pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7,
                 pygame.K_KP8, pygame.K_KP9]

board_gen_number = 0


def update_screen(images):
    pygame.display.update(images)
    clock.tick(FPS)


class NewPuzzle:

    def __init__(self, screen, squares=None):

        self.generate_board()
        self.board_values(True)
        self.possible_paths = self.return_possible_numbers()
        self.screen = screen
        self.new_square_values(squares)
        self.path = []
        self.create_solutions()

    def board_values(self, initiate_original):
        '''
            Returns dictionary of items within self.board that have non-zero values
        '''
        values = {(col, row, self.return_block_number((col, row))): self.board[row][col] for row in range(
            len(self.board)) for col in range(len(self.board[row])) if self.board[row][col] != 0}

        if initiate_original:
            self.original_board_values = values
        else:
            return values

    def create_solutions(self):
        '''
            Solves the Sudoku board and stores each squares solution in a dictionary
        '''
        original_board = self.board.copy()
        # This will change values in self.board
        self.solve_sudoku(self.possible_paths, False)

        self.correct_solutions = self.board_values(False)

        self.board = original_board

    def generate_board(self):

        global board_gen_number

        board_gen_number += 1

        if board_gen_number == 1:

            self.board = [
                [0, 6, 0, 0, 0, 8, 0, 9, 0],
                [1, 0, 0, 0, 5, 9, 6, 0, 0],
                [0, 0, 9, 1, 0, 0, 0, 0, 0],
                [0, 0, 4, 0, 0, 6, 7, 0, 0],
                [0, 0, 0, 0, 9, 2, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [8, 0, 1, 0, 7, 5, 0, 0, 0],
                [0, 7, 0, 2, 8, 0, 0, 1, 4]]

        else:
            response = requests.get(
                url="https://sugoku.herokuapp.com/board?difficulty=hard")

            if response.ok == True:
                board = list(response.json()['board'])

            self.board = board

    def new_square_values(self, square_dict=None):
        '''Generates a dictionary containing every square within the self.board'''

        if square_dict == None:
            # Create new square objects and draw them on the screen aking with lines
            self.squares = {coord: PuzzleSquare(coord, self.board[coord[1]][coord[0]], screen, coord in self.possible_paths)
                            for k in (self.possible_paths, self.original_board_values) for coord in k}

            draw_board(self.squares, self.screen)

        else:
            # Edit the existing values for each square on the gui.... used for generating new puzzles

            updated_portion = []
            new_squares = {}

            for square_key, square in square_dict.items():

                new_value = self.board[square.coordinate[1]
                                       ][square.coordinate[0]]

                updated_portion.extend(square.update_square(
                    new_value, background_color, False))

                new_squares[square_key] = square

            else:

                updated_portion.extend(draw_lines(self.screen))

                pygame.display.update(updated_portion)

                self.squares = new_squares

    def return_block_number(self, coord):
        ''' returns which 3x3 block the current coordinate is in'''
        block_number = (coord[0] // 3) + (3 * (coord[1] // 3))

        return block_number

    def return_possible_numbers(self, queried_points=None, input_coord=(), used_number=None):
        '''Returns a dictionary compiled of possible sets of numbers for unfilled coordinates.
        Returns a boolean for if completion of puzzle is possible with current board'''

        gen_dict = {}

        if queried_points != None:

            row = input_coord[1]
            col = input_coord[0]
            group = input_coord[2]

            for key, set_data in queried_points.items():
                # if the coordinate is affected by the input_coord square being updated to used_number
                # remove val from the set of its possible values if present
                # {s for s in set_data if s != val}
                if not key == input_coord:

                    gen_dict[key] = set_data.copy()

                    if key[0] == col or key[1] == row or key[2] == group:

                        gen_dict[key].discard(used_number)

                        if len(gen_dict[key]) == 0:

                            # An empty set of values is available for coordinate key. solution not possible
                            return gen_dict, False

            return gen_dict, True

        else:
            # This if statement is run only when possible numbers for each square are unknown
            available_numbers = set(range(1, 10))
            # Place set of numbers that follow the rules of Sudoku for each number inside a dictionary
            # key is (x,y,block_number)
            gen_dict = {(col, row, self.return_block_number((col, row))):
                        available_numbers.difference(self.used_set(row, col))
                        for row in range(len(self.board)) for col in range(len(self.board[row]))
                        if self.board[row][col] == 0}
            return gen_dict

    def used_set(self, row, col):
        '''Returns a set of invalid values for the given coordinate'''

        # game board is a 9x9 grid denoted into blocks of 3x3

        col_start = (col // 3)*3

        row_start = (row // 3)*3

        col_block = range(col_start, col_start+3)
        row_block = range(row_start, row_start + 3)

        used_block = {self.board[yb][xb]
                      for yb in row_block for xb in col_block if self.board[yb][xb] != 0}

        used_horizontal = {s for s in self.board[row] if s != 0}

        used_vertical = {s[col] for s in self.board if s[col] != 0}

        return used_horizontal.union(used_vertical).union(used_block)

    def draw_false(self, square_to_update, key, show_step, wrong_value):
        '''Draw the board with the false answer then replace with an empty value'''

        row = key[1]
        col = key[0]

        rects_to_update = []

        for img, clr in enumerate([false_path_color, background_color]):

            if img == 1:
                wrong_value = 0

            if show_step:

                rects_to_update = square_to_update.update_square(
                    wrong_value, clr)
                # draw_board(board,False,key[0:2], reverse_decision= True)
                update_screen(rects_to_update)

    def solve_sudoku(self, path_sets, show_steps):
        '''
        Recursive function that solves sudoku puzzles for NewPuzzle classes stored in a variable called "game" 
        Optionally show path on screen
        '''
        # Loop values corresponding to the square with the smallest number of possible values
        key = sorted(path_sets,
                     key=lambda x: len(path_sets[x]))[0]

        #  Retrieve graphical object representing the selected point on the board
        if show_steps:
            gui_square = self.squares[key]

        for value in path_sets[key]:

            if check_events(True) == True:
                return False, True

            if show_steps:
                update_screen(gui_square.update_square(
                    value, attempted_path_color))

            # Returns remaining possible values for the other squares on the board as a dictionary
            # Value_is_valid is True if using [value] on the board doesn't generate an empty set of possible values for another square
            new_value_sets, value_is_valid = self.return_possible_numbers(
                path_sets, key, value)

            col = key[0]
            row = key[1]

            if len(new_value_sets) == 0:
                # Recursive Exit condition
                self.board[row][col] = value
                return True, False
            elif value_is_valid:
                # Solution is still theoretically possible [0 Non-Empty sets of values for remaining squares ]
                solution_found, system_interrupt = self.solve_sudoku(
                    new_value_sets, show_steps)

                if system_interrupt:
                    # Exit Loop if user clicks New Puzzle or Show Solution
                    return False, True
                elif solution_found:

                    self.board[row][col] = value
                    return True, False

            if show_steps:
                # If algorithm reaches this conditional then a solution wasn't possible with the attempted value
                self.draw_false(gui_square, key, show_steps, value)
        else:
            # Possible values with the given board have been exhausted ... go back and try a different solution path
            return False, False


class ActionButton:

    def __init__(self, text, height, width, x, y, color, surface):
        self.text = text
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.color = color
        self.shape = Rect(self.x, self.y, self.width, self.height)
        self.surface = surface
        self.text_color = default_text_color
        self.text_location = (self.x + 17, self.y + 5)


class PuzzleSquare:

    text_color = (0, 0, 0)

    def __init__(self, coordinate, value, surface, allow_user_edit):

        self.allow_user_edit = allow_user_edit
        self.coordinate = coordinate
        self.x = (coordinate[0] + 1) * square_length
        self.y = (coordinate[1] + 1) * square_length
        self.value = value
        self.surface = surface
        self.location = (self.x, self.y)
        if value != 0:
            self.text_value = str(value)
        else:
            self.text_value = ""

        self.square = Rect(self.x, self.y, square_length, square_length)
        self.square_color = background_color

        self.text_color = default_text_color
        self.text_location = (self.x + 17, self.y + 5)

    def update_square(self, value, new_square_color, redraw_lines=True):
        '''Redraws the square onto the board
           Doesn't change values in self.board'''
        try:
            self.value = int(value)
        except ValueError:
            return []

        if self.value != 0:
            self.text_value = str(value)
        else:
            self.text_value = ""

        self.square_color = new_square_color

        updated_square = pygame.draw.rect(
            self.surface, self.square_color, self.square)

        updated_text = self.surface.blit(used_font.render(
            self.text_value, True, self.text_color), self.text_location)

        new_images = [updated_square, updated_text]

        if redraw_lines:
            new_images.extend(draw_lines(self.surface))

        return new_images


def draw_lines(surface):

    rects_to_update = []

    for i in range(0, 10):  # Draw horizontal and Vertical lines

        if i % 3 == 0:
            line_width = 6
        else:
            line_width = 2
        # vertical line
        v1 = pygame.draw.line(surface, (0, 0, 0), (square_length + square_length * i, square_length),
                              (square_length + square_length*i, screen_size - square_length), line_width)
        # horizontal line
        h1 = pygame.draw.line(surface, (0, 0, 0), (square_length, square_length + square_length * i),
                              (screen_size - square_length, square_length + square_length*i), line_width)

        rects_to_update.append(v1)
        rects_to_update.append(h1)

    return rects_to_update


def draw_buttons(buttons):

    for button in buttons:

        pygame.draw.rect(button.surface, button.color, button.shape)

        button.surface.blit(button_font.render(
            button.text, True, button.text_color), button.text_location)

    pygame.display.update()


def draw_board(square_set, surface):

    surface.fill(background_color)
    for square in square_set.values():
        if square.value != 0:
            square.update_square(square.value, background_color, False)

    draw_lines(surface)

    pygame.display.update()


def check_events(execute_solve_algorithm, selected_square=None, puzzle_solved=False):

    global game

    exit_algo_loop = True
    enter_algo_loop = True

    for event in pygame.event.get():

        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):

            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Test if user clicked on a button, puzzle square or empty space
            if puzzle_solved == False and not execute_solve_algorithm and initiate_algo.shape.collidepoint(pygame.mouse.get_pos()):
                # Show steps to solve Sudoku puzzle if the Solve Puzzle button is pressed
                selected_square = None
                return enter_algo_loop, selected_square, puzzle_solved

            elif generate_new_puzzle.shape.collidepoint(pygame.mouse.get_pos()):

                puzzle_solved = False
                selected_square = None
                game = NewPuzzle(screen, game.squares.copy())

                if execute_solve_algorithm:
                    return exit_algo_loop
                else:
                    return not enter_algo_loop, selected_square, puzzle_solved

            elif show_solution.shape.collidepoint(pygame.mouse.get_pos()):

                puzzle_solved = True

                for key, value in game.correct_solutions.items():
                    # If statement is to ensure that original board colors aren't changed
                    if not key in game.original_board_values:
                        game.squares[key].update_square(
                            value, attempted_path_color, False)

                draw_lines(screen)

                pygame.display.update()

                if execute_solve_algorithm:
                    return exit_algo_loop
                else:
                    return not enter_algo_loop, selected_square, puzzle_solved

            elif execute_solve_algorithm == False and puzzle_solved == False:

                previous_square_available = True if selected_square != None else False

                for square_key, puzzle_square in game.squares.items():
                    # Only return a square on the board if it is clicked and doesn't hold the original non-zero numbers
                    if puzzle_square.square.collidepoint(pygame.mouse.get_pos()):

                        user_selected_same_square = True if square_key == selected_square else False

                        update_previous_square = True if not user_selected_same_square and previous_square_available else False

                        if not square_key in game.original_board_values:

                            if update_previous_square:

                                square_color = background_color if game.squares[
                                    selected_square].value == 0 else user_input_color

                                update_screen(game.squares[selected_square].update_square(
                                    game.squares[selected_square].value, square_color, True))

                            if not user_selected_same_square:
                                # Change the square color to blue to signify that it has been clicked
                                selected_square = square_key

                                update_screen(game.squares[selected_square].update_square(
                                    game.squares[selected_square].value, selected_square_color, True))

                        return not enter_algo_loop, selected_square, puzzle_solved
                # user has clicked on an empty space so remove reference key if they attempt to type a number

                if previous_square_available and game.squares[
                        selected_square].value == 0:
                    # User pressed a square within the board and then an empty space
                    # Change previous square to white if empty
                    update_screen(game.squares[selected_square].update_square(
                        game.squares[selected_square].value, background_color, True))

                return not enter_algo_loop, None, puzzle_solved

        elif event.type == pygame.KEYDOWN:

            if event.key in valid_numbers and selected_square != None and not execute_solve_algorithm:
                # User has pressed a number on their keyboard
                user_input = (valid_numbers.index(event.key)) % 10

                input_color = background_color if user_input == 0 else user_input_color

                update_screen(game.squares[selected_square].update_square(
                    user_input, input_color, True))

    if execute_solve_algorithm == False:
        return not enter_algo_loop, selected_square, puzzle_solved
    else:
        return not exit_algo_loop


if __name__ == "__main__":

    screen = pygame.display.set_mode(
        (screen_size + square_length * 7, screen_size + square_length))

    clock = pygame.time.Clock()
    pygame.display.set_caption("Sudoku")

    game = NewPuzzle(screen)

    # Button that when pressed will visibly show the steps taken solve the sudoku
    initiate_algo = ActionButton("Solve Puzzle", square_length, 20 + square_length*4,
                                 game.squares[(8, 0, 2)].x + square_length*3, game.squares[(8, 0, 2)].y, attempted_path_color, screen)

    generate_new_puzzle = ActionButton("New Puzzle", initiate_algo.height, initiate_algo.width, initiate_algo.x,
                                       initiate_algo.y + initiate_algo.height + 30, attempted_path_color, screen)

    show_solution = ActionButton("Show Solution", generate_new_puzzle.height, generate_new_puzzle.width, generate_new_puzzle.x,
                                 generate_new_puzzle.y + generate_new_puzzle.height + 30, attempted_path_color, screen)

    draw_buttons([initiate_algo, generate_new_puzzle, show_solution])

    puzzle_solved = False
    execute_solve_algorithm = False
    # if not None then it references to a coordinate key within a dictionary holding pygame.Rect objects
    selected_square = None

    while True:

        execute_solve_algorithm, selected_square, puzzle_solved = check_events(
            execute_solve_algorithm, selected_square, puzzle_solved)

        if not puzzle_solved and execute_solve_algorithm == True:

            puzzle_solved = game.solve_sudoku(game.possible_paths, True)[0]
            execute_solve_algorithm = False
