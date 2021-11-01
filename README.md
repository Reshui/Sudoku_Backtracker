# Sudoku_Backtracker

pygame installation is necessary to run this .py file

Pressing the Solve Puzzle Button will allow you to visualize the steps used by Python to solve the puzzle.
Attempted numbers will appear in purple and will flash orange if a solution isn't possible with the curent values before 
then disappearing.

Pressing the new puzzle key will return a new puzzle with values from the API: "https://sugoku.herokuapp.com/board?difficulty=hard"

Pressing a square within the board will select the square and highlight it in blue. Once selected numbers 0-9 will be accepted as input.
If 0 the square will empty its self of value and turn the square white.
