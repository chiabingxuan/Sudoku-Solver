# Sudoku Solver

## Introduction: Modelling the Problem
This project was inspired by CS50's course on "Introduction to Artificial Intelligence with Python".

We can model Sudoku as a constraint satisfaction problem (CSP), in the form of an undirected graph with 81 nodes. Each of the 81 cells (or "boxes" as written in the code) in the puzzle corresponds to a unique node in the graph. Also, the "neighbours" of a given cell are defined to be the cells in either the same row, column or square as that cell (excluding the cell itself). Then, any two neighbours in the graph will be joined by an edge, which represents the binary constraint that no two neighbours are equal to each other. For each cell, the unary constraint is that the cell must contain an integer value between 1 and 9 inclusive.

## General Idea
Having modelled the Sudoku puzzle as a CSP, we can then make use of existing CSP algorithms to solve this problem. In `sudoku_solver.py`, we first enforce node consistency on the graph, based on the unary constraints of each cell. Then, we carry out the AC-3 algorithm to ensure that the graph is arc consistent, using the binary constraints of each <neighbour, neighbour> pair. Finally, we carry out a Backtracking Search to find a suitable assignment of values for each of the 81 cells.

Additional improvements are made in `backtrack()` to speed up the solving process:  
* An unassigned cell is selected using the minimum remaining value (MRV) heuristic, and then the degree heuristic to break ties
* After choosing an unassigned cell, we assign values to the cell in an ordered sequence, based on the least-constraining values heuristic
* After a value is assigned to a cell, we call the `inference()` method to make more inferences about the values in other cells, based on this new assignment. This involves carrying out the AC-3 algorithm, which would allow us to maintain the arc consistency of the graph each time an assignment is made

## How to Use
When `sudoku_solver.py` is being run, it requires the user to input a file path corresponding to a .txt file that contains an unsolved Sudoku puzzle. Empty cells are represented by underscores ("_") and cells in the same row are separated by commas (","). An example of a possible .txt file, named `sample_puzzle.txt`, is provided in this repository. Following this, the program will print out a solution to this puzzle (if there are multiple solutions, it will print out only one of the possible solutions). If there are no solutions, the program will simply print out the message "No solution".
