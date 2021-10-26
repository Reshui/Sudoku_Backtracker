
def block_set(x,y,current_board):
    ''' Returns a set of values from the current block depending on the current x,y coordinate'''
    
    x_block = None
    y_block = None
    
    blocks = [ range(3) , range(3,6) , range(6,9)] #game board is a 9x9 grid denoted into blocks of 3x3 
    
    t = 0
    
    while (x_block != None and y_block != None) == False: #loop until range iterators are found
        if x in blocks[t]:
            x_block = blocks[t]
        if y in blocks[t]:
            y_block = blocks[t]
        t += 1

    returned_block_set = { current_board[yb][xb] for yb in y_block for xb in x_block if current_board[yb][xb] > 0}
    
    return  returned_block_set

def used_set(row_number,column_number,game):
    ''' returns a set of invalid values for the given coordinate'''

    used_horizontal = {s for s in game[row_number] if s > 0}

    used_vertical = {s[column_number] for s in game if s[column_number] > 0}

    used_block = block_set(column_number,row_number,game)

    return used_horizontal.union(used_vertical).union(used_block)

def return_possible_numbers(game):

    ''' returns a dictionary compiled of possible sets of numbers for unfilled coordinates'''
    available_numbers=set(range(1,10))
    coord_dict = {}

    for row in range(len(game)):     # Loop values to find available numbers

        for column in range(len(game[row])):

            if game[row][column] == 0:  #if equal to 0 then the number hasn't been filled

                useable_numbers = available_numbers.difference(used_set(row,column,game))
                #set of numbers available for the current coordinate
                
                coord_dict[(column,row)] = useable_numbers.copy()

                useable_numbers.clear()

    return coord_dict 

def solution_possible(game,values):

    ''' Returns True if Every value that is 0 has a non empty set of possible values '''

    for row in range(len(game)):

        for column in range(len(game)):

            if game[row][column] == 0 and (not (column,row) in values or len(values[(column,row)]) == 0):

                return False
    else:
        return True

def play_sudoku(board,cd=None): #recursive function

    if cd==None:
        cd = return_possible_numbers(board) # set of possible values for each coordinate
    
    sorted_keys = sorted(cd, key= lambda x: len(cd[x])) # prioritize numbers with the least number of possibilities
    
    for key in sorted_keys:
        column = key[0]
        row = key[1]
        i=0     #iterator to determine if all values within set have been parsed

        for value in cd[key]: 

            board[row][column] = value
            i+=1
            cd2 = return_possible_numbers(board)    # available numbers after board update

            if solution_possible(board,cd2) == True: # break out of current values and try next point
                
                board = play_sudoku(board,cd2)          #recursive call

                if len(return_possible_numbers(board)) ==0:     
                    return board
                else:
                    board[row][column]= 0
                    
                    if i == len(cd[key]):   #game completion not possible with current board values
                        return board
            else:

                board[row][column]= 0

                if i == len(cd[key]):   #game completion not possible with current board values
                    return board
                 
    return board

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

original_board=[
[1,0,0,0,6,0,9,0,0],
[0,0,9,0,7,0,0,3,0],
[0,0,0,0,0,0,4,0,1],
[0,0,5,0,0,2,0,6,0],
[0,0,1,0,0,4,0,0,0],
[3,0,0,0,0,8,0,4,2],
[0,8,0,0,0,6,0,9,0],
[0,0,3,0,5,0,0,2,0],
[0,0,0,0,0,0,0,0,0]]

#Logs which numbers are changeable by program
#bool_mask = [[False if y > 0 else True for y in x ] for x in original_board]

solved_board=play_sudoku(original_board)

print(solved_board)
