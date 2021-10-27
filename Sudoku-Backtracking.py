
from tkinter import *

#root= Tk()

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

def return_possible_numbers(game,queried_points=None,input_coord=()):

    ''' returns a dictionary compiled of possible sets of numbers for unfilled coordinates'''
    available_numbers=set(range(1,10))

    if queried_points != None:
        
        input_coord_block=return_block_number(input_coord)

        for key in queried_points:
            #if the coordinate is affected by the input_coord being applied
            if key[0] == input_coord[0] or key[1] == input_coord[1] or return_block_number(key) == input_coord_block:
            
                queried_points[key] = available_numbers.difference(used_set(key[1],key[0],game))

        return queried_points    

    else:

        coord_dict = {(col,row):available_numbers.difference(used_set(row,col,game)) for row in range(len(game)) for col in range(len(game[row])) if game[row][col] == 0}
        #Numbers that follow the rules of Sudoku
        return coord_dict 

def solution_possible(value_sets):

    ''' Returns True if Every Null value has a Non-Empty set of possible values '''
    
    for val in value_sets.values():
        if len(val)==0:
            return False
    else:
        return True

def play_sudoku(board, value_sets=None ): #recursive function

    if value_sets==None:
        value_sets = return_possible_numbers(board) # set of possible values for each coordinate
    
    sorted_keys = sorted(value_sets, key = lambda x: len(value_sets[x])) # prioritize numbers with the least number of possibilities
    
    for key in sorted_keys:
        col = key[0]
        row = key[1]
        i=0     #iterator to determine if all values within set have been parsed

        for value in value_sets[key]: 

            board[row][col] = value

            i+=1
            
            updated_value_sets = value_sets.copy()

            del updated_value_sets[(col,row)]

            updated_value_sets = return_possible_numbers(board,updated_value_sets,key)    # available numbers after the board has been update
            
            if len(updated_value_sets) ==0:

                return board , updated_value_sets  

            elif solution_possible(updated_value_sets) == True: #check if every point still has a possible value
                
                board , updated_value_sets = play_sudoku(board,updated_value_sets)          #recursive call

                if len(updated_value_sets) ==0:    #board may have been solved
                    return board , updated_value_sets
                else:
                    board[row][col]= 0
                    
                    if i == len(value_sets[key]):   #game completion not possible with current board values
                        return board , value_sets
            else:

                board[row][col] = 0

                if i == len(value_sets[key]):   #game completion not possible with current board values
                    return board ,value_sets               # go back and choose a different value

    return board, updated_value_sets

'''
original_board = [
[8,0,7,9,4,0,3,1,0],
[0,3,1,0,7,6,4,0,0],
[0,0,0,1,0,0,0,5,0],
[9,0,0,5,0,0,0,0,0],
[0,0,0,0,0,0,1,6,0],
[1,0,5,3,0,7,0,2,4],
[0,0,3,0,0,2,6,9,1],
[0,1,0,6,9,3,0,4,0],
[4,0,0,7,0,0,2,3,8]]
'''

'''original_board=[
[1,0,0,0,6,0,9,0,0],
[0,0,9,0,7,0,0,3,0],
[0,0,0,0,0,0,4,0,1],
[0,0,5,0,0,2,0,6,0],
[0,0,1,0,0,4,0,0,0],
[3,0,0,0,0,8,0,4,2],
[0,8,0,0,0,6,0,9,0],
[0,0,3,0,5,0,0,2,0],
[0,0,0,0,0,0,0,0,0]]'''

'''original_board=[
[0,5,6,9,0,0,0,7,0],
[0,0,0,0,1,0,0,0,8],
[4,0,0,0,0,0,0,0,0],
[9,0,0,0,0,0,0,4,0],
[2,0,0,3,0,0,0,0,0],
[0,4,3,0,0,8,0,0,7],
[0,0,0,0,0,9,6,0,0],
[0,0,2,0,0,0,0,0,0],
[0,3,7,6,0,0,0,5,0],
]'''

original_board=[
    [6,0,9,0,0,0,0,0,4],
    [0,8,0,3,0,6,0,0,0],
    [0,0,0,0,5,7,0,0,6],
    [0,0,1,0,0,0,0,4,7],
    [0,0,0,0,1,0,0,0,0],
    [8,5,0,0,0,0,2,0,0],
    [1,0,0,6,2,0,0,0,0],
    [0,0,0,5,0,8,0,7,0],
    [2,0,0,0,0,0,6,0,3]]

solved_board=play_sudoku(original_board)[0]

print(solved_board)
