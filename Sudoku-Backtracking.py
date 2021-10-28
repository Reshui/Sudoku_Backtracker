
import pygame,sys,requests

from pygame.locals import *

screen_size = 11 * 60 # number should be divisible by 11
square_length = screen_size // 11

original_board_colors = (0,0,0)
wrong_number_color = (245,0,0)
possible_number_color = (64,201,30)
FPS= 40

clock=pygame.time.Clock()

pygame.init()

used_font=pygame.font.SysFont('Comic Sans MS', 35 )

screen = pygame.display.set_mode((screen_size,screen_size))

pygame.display.set_caption("Sudoku Solver")

def check_events():
    for event in pygame.event.get():

        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE ):

            pygame.quit()
            sys.exit()

def draw_board(current_board,initial_board_gen,attempted_coord= None, permit_backtrack = False):

    if initial_board_gen == True:
        color_selection = original_board_colors
    elif permit_backtrack == True:
        color_selection=wrong_number_color
        #rectangle_color= (255,255,255)
    else:
        color_selection =possible_number_color

    if initial_board_gen: #draw lines

        screen.fill((255,255,255))

        for i in range(0,10):

            if i % 3 ==0:
                line_width=4
            else:
                line_width=2

            pygame.draw.line(screen, (0,0,0) , (square_length + square_length *i , square_length) , ( square_length + square_length*i , screen_size - square_length ),line_width)#vertical line

            pygame.draw.line(screen, (0,0,0) , ( square_length, square_length + square_length *i) , (screen_size - square_length , square_length + square_length*i),line_width)#horizontal line

        numbers_for_screen = []

        for row in range(len(current_board)):

            for col in range(len(current_board[0])):

                if current_board[row][col] != 0:

                    draw_location =  ( (col + 1) * square_length + 17, (row+1) * square_length + 5 )

                    drawn_number = used_font.render(str(board[row][col]), True, color_selection)

                    numbers_for_screen.append((drawn_number,draw_location))

        else:
            screen.blits(numbers_for_screen, False)

        pygame.display.update()

    else:
        row = attempted_coord[1]
        col = attempted_coord[0]
        rc= []
        val= board[row][col]

        if val !=0 :
            val= str(val)
        else:
            val=" "

        x_coord=(col + 1) * square_length 
        y_coord= (row+1) * square_length

        rc.append(pygame.draw.rect(screen,(255,255,255),Rect(x_coord + 4 ,y_coord + 4, square_length -8,square_length -8) ))

        draw_location =  ( x_coord + 17, y_coord + 5 )

        drawn_number = used_font.render(val, True, color_selection)

        rc.append(screen.blit(drawn_number,draw_location))

        pygame.display.update(rc)

    clock.tick(FPS)

def used_set(row,col,current_board):
    ''' returns a set of invalid values for the given coordinate'''

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

    ''' returns a dictionary compiled of possible sets of numbers for unfilled coordinates'''
    
    available_numbers=set(range(1,10))

    if queried_points != None:

        row = input_coord[1]
        col = input_coord[0]
        group = input_coord[2]

        for key, set_data in queried_points.items():
            #if the coordinate is affected by the input_coord being applied then
            #remove val from the set of its possible values if present
            if key[0] == col or key[1] == row or key[2] == group:
               
                '''k = set_data.copy()
                k.discard(val)

                d = available_numbers.difference(used_set(key[1],key[0],game))

                if k != d:
                    i+=1'''
                if val in set_data:
                    queried_points[key] = {s for s in set_data if s != val}
                    #set_data.discard(val)

                if len(queried_points[key]) == 0:
                    return queried_points , False

        return queried_points ,True 

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

def solve_sudoku(board, value_sets=None ): #recursive function

    if value_sets==None:
        value_sets = return_possible_numbers(board)[0] # set of possible values for each coordinate

    sorted_keys = sorted(value_sets, key = lambda x: len(value_sets[x])) # prioritize numbers with the least number of possibilities
    
    key = sorted_keys[0]

    col = key[0]
    row = key[1]
    i=0     #iterator to determine if all values within set have been parsed

    for value in value_sets[key]: # for each member of the target set

        check_events()

        board[row][col] = value

        draw_board(board,False,key[0:2], False)

        i+=1
        
        updated_value_sets = value_sets.copy()

        del updated_value_sets[key]         #necessary to view possibilities with current board

        updated_value_sets, continue_attempt = return_possible_numbers(board,updated_value_sets,key,value)    # available numbers after the board has been update
        
        if len(updated_value_sets) ==0:

            return board , updated_value_sets

        elif continue_attempt == True: #check if every point still has a possible value
            
            board , updated_value_sets = solve_sudoku(board,updated_value_sets)          #recursive call

            if len(updated_value_sets) == 0:    #board may have been solved
                return board , updated_value_sets
            else:

                draw_board(board,False,key[0:2], True)
                board[row][col] = 0
                draw_board(board,False,key[0:2], True)
                
                if i == len(value_sets[key]):   #game completion not possible with current board values
                    return board , value_sets
        else:

            draw_board(board,False,key[0:2], True)
            board[row][col] = 0
            draw_board(board,False,key[0:2], True)

            if i == len(value_sets[key]):   #game completion not possible with current board values
                return board ,value_sets               # go back and choose a different value

    return board, updated_value_sets

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

    response=requests.get(url="https://sugoku.herokuapp.com/board?difficulty=hard")

    if response.ok == True:
        board = list ( response.json()['board'] )

    return board

if __name__ == "__main__":

    board = generate_board()

    draw_board(board,True)

    solve_sudoku(board)

    while 1:
        check_events()
        
