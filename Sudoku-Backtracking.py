
import pygame,sys,requests

from pygame.locals import *

screen_size = 11 * 60 # number should be divisible by 11
square_length = screen_size // 11

FPS= 30

default_text_color = (0,0,0)

false_path_color = (135,209,236)
background_color = (255,255,255)
attempted_path_color = (159,162,162)

pygame.init()

used_font = pygame.font.SysFont('Comic Sans MS', 35 )
button_font = pygame.font.SysFont('Comic Sans MS', 27 )

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

    square_length = screen_size // 11
    text_color = (0,0,0) 

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
        
        self.square =  Rect(self.x, self.y, square_length, square_length) 
        self.square_color = background_color

        self.text_color = default_text_color
        self.text_location = (self.x + 17, self.y + 5 )

    def update_square(self, value, new_square_color, redraw_lines = True):

        try:
            self.value = int(value)
        except ValueError:
            return []
        
        if self.value != 0:
            self.text_value = str(value)
        else:
            self.text_value = ""

        self.square_color = new_square_color

        updated_square = pygame.draw.rect(self.surface, self.square_color, self.square)

        updated_text = self.surface.blit(used_font.render(self.text_value, True, self.text_color), self.text_location)

        new_images = [updated_square, updated_text] 
        if redraw_lines:
            new_images.extend(draw_lines(self.surface))

        return new_images

def draw_lines(surface):

    rects_to_update = []

    for i in range(0,10):       #Draw horizontal and Vertical lines

        if i % 3 ==0:
            line_width = 6
        else:
            line_width = 2
        #vertical line
        v1=pygame.draw.line(surface, (0,0,0) , (square_length + square_length *i , square_length) , ( square_length + square_length*i , screen_size - square_length ),line_width)
        #horizontal line
        h1=pygame.draw.line(surface, (0,0,0) , ( square_length, square_length + square_length *i) , (screen_size - square_length , square_length + square_length*i),line_width)
        
        rects_to_update.append(v1)
        rects_to_update.append(h1)

    return rects_to_update

def check_events(use_solving_algorithm):

    for event in pygame.event.get():

        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE ):

            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if SolveSudoku.shape.collidepoint(pygame.mouse.get_pos()):
                use_solving_algorithm = True

    return use_solving_algorithm

def draw_board(square_set, surface, buttons):

    surface.fill(background_color)

    for square in square_set.values():
        if square.value != 0:
            square.update_square( square.value, background_color, False)
    
    for button in buttons:

        pygame.draw.rect(button.surface, button.color, button.shape)

        button.surface.blit(button_font.render(button.text, True, button.text_color), button.text_location)

    draw_lines(surface)

    pygame.display.update()

def update_screen(images):
    pygame.display.update(images)
    clock.tick(FPS)

def used_set(row,col,current_board):
    '''Returns a set of invalid values for the given coordinate'''

    blocks = [ range(3) , range(3,6) , range(6,9)] #game board is a 9x9 grid denoted into blocks of 3x3 
    
    for block in blocks:

        if row in block:
            row_block = block
        if col in block:
            col_block = block

    used_block = { current_board[yb][xb] for yb in row_block for xb in col_block if current_board[yb][xb] != 0}
    
    used_horizontal = {s for s in current_board[row] if s != 0}

    used_vertical = {s[col] for s in current_board if s[col] != 0}

    return used_horizontal.union(used_vertical).union(used_block)

def return_block_number(coord):
    
    ''' returns which block the current coordinate is in'''
    block_number= (coord[0] // 3) + (3 * (coord[1] // 3))

    return block_number

def return_possible_numbers(game,queried_points=None,input_coord=(), val =None):

    '''Returns a dictionary compiled of possible sets of numbers for unfilled coordinates.
       Returns a boolean for if completion of puzzle is possible with current board'''
    
    available_numbers=set(range(1,10))

    if queried_points != None:

        row = input_coord[1]
        col = input_coord[0]
        group = input_coord[2]

        gen_dict = {}

        for key, set_data in queried_points.items():
            #if the coordinate is affected by the input_coord being applied then
            #remove val from the set of its possible values if present
            gen_dict[key] = set_data.copy()#{s for s in set_data if s != val}
            
            if key[0] == col or key[1] == row or key[2] == group:
               
                gen_dict[key].discard(val)

                if len(gen_dict[key]) == 0:
                    
                    #An empty set of values is available for coordinate key. solution not possible
                    return gen_dict , False

        return gen_dict ,True 

    else:
        
        coord_dict = {(col,row,return_block_number((col,row))):available_numbers.difference(used_set(row,col,game)) for row in range(len(game)) for col in range(len(game[row])) if game[row][col] == 0}
        #Numbers that follow the rules of Sudoku
        # key is (x,y,block_number)
        return coord_dict , True

def solution_possible(value_sets):

    ''' Returns True if Every Null value has a Non-Empty set of possible values '''
    
    for val in value_sets.values():
        if val == None or len(val)==0:
            return False
    else:
        return True

def solve_sudoku(board, value_sets=None, draw_each_step = False ): #recursive function

    if value_sets==None:
        value_sets = return_possible_numbers(board)[0] # set of possible values for each coordinate

    sorted_keys = sorted(value_sets, key = lambda x: len(value_sets[x])) # prioritize numbers with the least number of possibilities
    
    key = sorted_keys[0]

    col = key[0]
    row = key[1]

    for item_num ,value in enumerate(value_sets[key]): # for each member of the target set

        check_events()

        board[row][col] = value

        if draw_each_step:
            draw_board(board,False,key[0:2], False)     #update the board with the given number in green
        
        updated_value_sets = value_sets.copy()

        del updated_value_sets[key]         #necessary to view possibilities with current board

        updated_value_sets, continue_attempt = return_possible_numbers(board,updated_value_sets,key,value)    # available numbers after the board has been update
        
        if len(updated_value_sets) ==0:

            return board , updated_value_sets

        elif continue_attempt == True: #check if every point still has a possible value
            
            board , updated_value_sets = solve_sudoku(board,updated_value_sets,draw_each_step)          #recursive call

            if len(updated_value_sets) == 0:    #board may have been solved
                return board , updated_value_sets
            else:

                board=draw_false(board,row,col,key,draw_each_step) 
                
                if item_num == len(value_sets[key]):   #game completion not possible with current board values
                    return board , value_sets
        else:

            board=draw_false(board,row,col,key,draw_each_step)

            if item_num == len(value_sets[key]):   #game completion not possible with current board values
                return board ,value_sets               

    return board, updated_value_sets

def draw_false(square_to_update,board,key,show_step):
    '''Draw the board with the false answer then replace with an empty value'''
    
    row=key[1]
    col=key[0]

    rects_to_update = []

    for img, clr in enumerate([false_path_color, background_color]):

        if img == 1:
            board[row][col] = 0

        if show_step:
            
            rects_to_update = square_to_update.update_square(board[row][col], clr)
            #draw_board(board,False,key[0:2], reverse_decision= True)
            update_screen(rects_to_update)

    return board

def generate_board():

    '''return [[0,0,0,0,0,0,0,0,5],
    [1,2,0,5,6,0,0,0,0],
    [4,0,8,2,0,9,0,0,0],
    [0,1,0,0,5,0,0,0,0],
    [0,6,9,0,0,0,0,0,4],
    [0,0,0,0,0,0,0,0,6],
    [0,0,0,0,0,1,0,4,2],
    [0,0,0,9,2,5,0,0,0],
    [0,0,0,0,0,0,8,5,0]]'''

    '''return [
    [0,0,0,7,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0],
    [0,0,0,4,3,0,2,0,0],
    [0,0,0,0,0,0,0,0,6],
    [0,0,0,5,0,9,0,0,0],
    [0,0,0,0,0,0,4,1,8],
    [0,0,0,0,8,1,0,0,0],
    [0,0,2,0,0,0,0,5,0],
    [0,4,0,0,0,0,3,0,0]]'''

    response=requests.get(url="https://sugoku.herokuapp.com/board?difficulty=hard")

    if response.ok == True:
        board = list ( response.json()['board'] )

    return board

if __name__ == "__main__":

    screen = pygame.display.set_mode((screen_size + square_length * 7,screen_size+ square_length ))
    
    clock=pygame.time.Clock()

    pygame.display.set_caption("Sudoku Solver")

    board = generate_board()

    show_steps=True#int(input("Input 1 to show each step otherwise enter 0:\t"))

    if show_steps ==1:
        show_steps= True
    else:
        show_steps = False

    square_dict = {}
    value_sets = return_possible_numbers(board)[0] 

    # Generate Class objects for each square

    original_board = { (col,row,return_block_number((col,row) ) ): board[row][col]  for row in range(len(board)) for col in range(len(board[row])) if board[row][col] != 0 }

    for k in (value_sets, original_board):
        for coord in k:
            square_dict[coord] = PuzzleSquare(coord,board[coord[1]][coord[0]], screen, coord in value_sets)
            #square_dict[k2] = PuzzleSquare(k,board[k[1]][k[0]], screen, False)

    SolveSudoku = ActionButton("Solving Algorithm", square_length, 20 + square_length*4, \
                                square_dict[(8,0,2)].x + square_length*3, square_dict[(8,0,2)].y, attempted_path_color, screen)
    
    if show_steps == True:
        draw_board(square_dict, screen,[SolveSudoku])
    #Dictionary containing the set of all possible values for each Empty space on the board

    current_path = []

    continue_attempt = True
    use_alternate_path = False

    puzzle_solved = False
    solve_puzzle = False

    while 1:

        solve_puzzle = check_events(solve_puzzle)

        if not puzzle_solved and solve_puzzle == True:

            if use_alternate_path == True:

                previous_path = current_path.pop()

                key = previous_path[0]

                value_sets = previous_path[2]
                
                used_from_set = previous_path[1]

            else:

                sorted_keys = sorted(value_sets, key = lambda x: len(value_sets[x]))

                key = sorted_keys[0]
                used_from_set = set()

            current_square = square_dict[key]

            if use_alternate_path:  # Show that the current path is False
                board = draw_false(current_square, board, key, show_steps)

            for item_number ,value in enumerate(value_sets[key]): #loop through every value to determine possible solution path

                if use_alternate_path == False or (use_alternate_path == True and value not in used_from_set) :
                    
                    new_value_sets = value_sets.copy()

                    del new_value_sets[key]

                    col = key[0]
                    row = key[1]

                    board[row][col] = value

                    used_from_set.add(value)

                    if show_steps:

                        update_screen(current_square.update_square( value, attempted_path_color))

                    new_value_sets, continue_attempt = return_possible_numbers(board,new_value_sets,key,value)    # available numbers after the board has been update
                    
                    if len(new_value_sets) == 0:

                        puzzle_solved = True
                        break

                    elif continue_attempt == True: 
                        
                        use_alternate_path = False

                        current_path.append([key,   used_from_set,    value_sets.copy()])
                        
                        value_sets = new_value_sets 
                        break

                    else:
                        # Show that the board isn't solvable with the current value 
                        board = draw_false(current_square, board, key, show_steps)

                        if len(value_sets[key].difference(used_from_set))==0:
                            use_alternate_path = True
                            break

                    
