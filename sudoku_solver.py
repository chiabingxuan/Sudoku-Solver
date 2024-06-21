import copy


class Box(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.square = self.get_square_num(row, col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col, self.square))

    def get_square_num(self, row, col):
        if row < 3:
            if col < 3:
                return 0
            if col < 6:
                return 1
            return 2
        if row < 6:
            if col < 3:
                return 3
            if col < 6:
                return 4
            return 5
        if col < 3:
            return 6
        if col < 6:
            return 7
        return 8


class SudokuSolver(object):
    def __init__(self, filename):
        self.board = self.read_board(filename)
        self.domains = dict()
        self.squares = {num: set() for num in range(9)}
        for row in range(9):
            for col in range(9):
                new_box = Box(row, col)
                self.domains[new_box] = {1, 2, 3, 4, 5, 6, 7, 8, 9}
                self.squares[new_box.square].add(new_box)

    def read_board(self, filename):
        with open(filename, "r", encoding="utf-8") as text:
            lines = text.readlines()
            board = list()
            for line in lines:
                row = line.strip().split(",")
                casted_row = list()
                for item in row:
                    if item == "_":
                        casted_row.append(0)
                    else:
                        casted_row.append(int(item))
                board.append(casted_row)
            return board

    def print_solution(self):
        print("Solution:")
        for row in self.board:
            print(row)

    def get_neighbours(self, box):
        neighbours = set()
        row = box.row
        col = box.col
        square = box.square
        for count in range(9):
            neighbours.add(Box(row, count))
            neighbours.add(Box(count, col))
        square_neighbours = self.squares[square]
        neighbours = neighbours.union(square_neighbours)
        neighbours.remove(box)
        return neighbours

    def fill_box(self, box, entry):
        if not self.board[box.row][box.col]:
            self.board[box.row][box.col] = entry

    def enforce_node_consistency(self):
        for box in self.domains:
            entry = self.board[box.row][box.col]
            if entry:
                self.domains[box] = {entry}

    def revise(self, editing_box, basis_box):
        editing_box_domain = self.domains[editing_box]
        basis_box_domain = self.domains[basis_box]
        new_editing_box_domain = set()
        for possible_entry in editing_box_domain:
            for basis_box_entry in basis_box_domain:
                if possible_entry != basis_box_entry:
                    new_editing_box_domain.add(possible_entry)
                    break
        if len(new_editing_box_domain) < len(editing_box_domain):
            self.domains[editing_box] = new_editing_box_domain
            return True
        return False

    def ac3(self, arcs=None):
        if arcs is None:
            queue = list()
            for box in self.domains:
                box_neighbours = self.get_neighbours(box)
                for neighbour in box_neighbours:
                    queue.append((box, neighbour))
        else:
            queue = arcs
        while queue:
            front_arc = queue.pop(0)
            editing_box, basis_box = front_arc[0], front_arc[1]
            editing_box_neighbours = self.get_neighbours(editing_box)
            if self.revise(editing_box, basis_box):
                if len(self.domains[editing_box]) == 0:
                    return False
                for editing_box_neighbour in editing_box_neighbours:
                    if editing_box_neighbour != basis_box:
                        queue.append((editing_box_neighbour, editing_box))
        return True

    def inference(self, assignment, box_assigned):
        arcs = list()
        box_assigned_neighbours = self.get_neighbours(box_assigned)
        self.domains[box_assigned] = {assignment[box_assigned]}
        for neighbour in box_assigned_neighbours:
            arcs.append((neighbour, box_assigned))
        if not self.ac3(arcs=arcs):
            return None
        inferences = dict()
        for box in self.domains:
            if box not in assignment and len(self.domains[box]) == 1:
                inferences[box] = self.domains[box].pop()
                self.domains[box].add(inferences[box])
        return inferences

    def assignment_complete(self, assignment):
        return len(assignment) == len(self.domains)

    def consistent(self, assignment):
        for box, assigned_value in assignment.items():
            entry = self.board[box.row][box.col]
            if entry and assigned_value != entry:
                return False
        boxes = list(assignment.keys())
        for index in range(len(boxes)):
            box = boxes[index]
            for moving_index in range(index + 1, len(boxes)):
                moving_box = boxes[moving_index]
                if moving_box in self.get_neighbours(box) and assignment[box] == assignment[moving_box]:
                    return False
        return True

    def order_domain_values(self, box, assignment):
        box_domains = list(self.domains[box])
        box_neighbours = self.get_neighbours(box)

        def constrain(possible_assignment_to_box):
            choices_eliminated = 0
            for neighbour in box_neighbours:
                if neighbour not in assignment:
                    neighbour_domains = self.domains[neighbour]
                    for possible_assignment_to_neighbour in neighbour_domains:
                        if possible_assignment_to_box == possible_assignment_to_neighbour:
                            choices_eliminated += 1
            return choices_eliminated

        box_domains.sort(key=constrain)
        return box_domains

    def select_unassigned_box(self, assignment):
        unassigned_boxes = list()
        for box in self.domains:
            if box not in assignment:
                unassigned_boxes.append(box)
        unassigned_boxes.sort(key=lambda box_variable: len(self.get_neighbours(box_variable)), reverse=True)
        unassigned_boxes.sort(key=lambda box_variable: len(self.domains[box_variable]))
        return unassigned_boxes[0]

    def backtrack(self, assignment):
        if self.assignment_complete(assignment):
            return assignment
        box = self.select_unassigned_box(assignment)
        box_domain = self.order_domain_values(box, assignment)
        for value in box_domain:
            assignment[box] = value
            if self.consistent(assignment):
                old_domains = copy.deepcopy(self.domains)
                inferences = self.inference(assignment, box)
                if isinstance(inferences, dict):
                    for box_inferred in inferences:
                        assignment[box_inferred] = inferences[box_inferred]
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
                    for box_inferred in inferences:
                        del assignment[box_inferred]
                self.domains = old_domains
            del assignment[box]
        return None

    def solve(self):
        self.enforce_node_consistency()
        self.ac3()
        final_assignment = self.backtrack(dict())
        if not final_assignment:
            print("No solution found.")
            return
        for box, assigned_value in final_assignment.items():
            self.fill_box(box, assigned_value)
        self.print_solution()


if __name__ == "__main__":
    filename = input("Enter file name of a Sudoku puzzle (in .txt format): ")
    solver = SudokuSolver(filename)
    solver.solve()
    end = input("Enter any key to quit: ")
