import copy
import itertools


class HexBoard:
    """Hexs essentially have three dimensions, w/o reference to real math let's say A B C are  NW/SE NE/SW N/S"""

# four or five to a side
    def __init__(self, size = 4, coords=None, ax_coords=None) -> None:
        if coords is None:
            coords = []
        if ax_coords is None:
            ax_coords = []
        first_row_length = size
        self.rows_no = (size * 2) - 1
        self.max_coord = self.rows_no // 2
        self.max_slice_length = first_row_length + self.max_coord
        middle_row_length = self.max_slice_length
        self.rows = [
            [(i, j) in coords for j in range(i)] for i in itertools.chain(
                range(first_row_length, middle_row_length + 1),
                range(middle_row_length - 1, first_row_length - 1, -1))
        ]
        self.center = (size-1, size-1)
        for coord in coords:
            row = coord[0]
            col = coord[1]
            self.rows[row][col] = True
        for axcoord in ax_coords:
            self.set_axial(*axcoord, True)
        self.cells = 0
        for row in self.rows:
            self.cells += len(row)

    # q + r + s = 0
    # def axial_to_index(self, q:int=None, r:int=None, s:int=None):
    #     if [q,r,s].count(None) >= 2:
    #         raise RuntimeError("Require 2 or more coordinates")
    #     row = r + self.max_coord
    #     q_index

    def axial_to_index(self, q, r, s):
        # -3:0 -2: -1  -1 -2 0:-3, 1:-3, 2:-3
        row = r + self.max_coord
        if row < self.max_coord:
            q_index = row + q
        else:
            q_index = q + self.max_coord

        return row, q_index

    def index_to_axial(self, row, col):
        r = row - self.max_coord
        q = col - row
        s = -q -r
        return (q,r,s)

    def get_index(self, row, col):
        return self.rows[row][col]

    def set_index(self, row, col, val):
        self.rows[row][col] = val

    def get_axial(self, q, r, s):
        coords = self.axial_to_index(q,r,s)
        row = coords[0]
        col = coords[1]
        return self.rows[row][col]

    def set_axial(self, q, r, s, value):
        coords = self.axial_to_index(q, r, s)
        row = coords[0]
        col = coords[1]
        self.rows[row][col] = value

    def toggle_axial(self, q, r, s):
        self.set_axial(q,r,s, not self.get_axial(q, r, s))

    def ci(self, c:int, i:int):
        return self.rows[c][i]

    def ai(self, a:int, i:int):
        expected_row_length_at_i = len(self.rows[0]) + i
        actual_row_length_at_i = len(self.rows[i])
        delta = expected_row_length_at_i - actual_row_length_at_i
        actual_index = i - (delta // 2)
        return self.rows[i][actual_index]

    def neighbors_axial(self, q, r, s):
        pos_neighbors = [
            (q, r+1, s-1),
            (q, r-1, s+1),
            (q+1, r, s-1),
            (q-1, r, s+1),
            (q+1, r-1, s),
            (q-1, r+1, s)
                ]
        return list(filter(lambda coord: self.in_bounds(*coord), pos_neighbors))

    def index_neighbors_from_axial(self, q, r, s):
        return list(map(lambda coords: self.axial_to_index(*coords), self.neighbors_axial(q,r,s)))

    def is_finished(self): # check al cells have the same value
        target = self.get_index(0, 0)
        for row in self.rows:
            for value in row:
                if value is not target:
                    return False
        return True

    def length_of_slice_at_offset(self, offset):
        if offset > self.max_coord:
            raise IndexError("")
        return self.max_slice_length - offset

    def in_bounds(self, q, r, s):
        return -self.max_coord <= q <= self.max_coord and -self.max_coord <= r <= self.max_coord and -self.max_coord <= s <= self.max_coord

    def touch(self, q, r, s):
        new_board = copy.deepcopy(self)
        neighbors = self.neighbors_axial(q, r, s)
        new_board.toggle_axial(q,r,s)
        for n in neighbors:
            new_board.toggle_axial(*n)
        return new_board

    def touch_index(self, row, index):
        return self.touch(*self.index_to_axial(row, index))

    def hash(self):
        hash_sum = 0
        i = 0
        flat_list = [item for sublist in self.rows for item in sublist]
        for bool_item in flat_list:
            hash_sum += (bool_item << i)
            i += 1
        return hash_sum


    def bfs(self):
        queue = [self]
        opened = []
        log_interval = self.cells
        score = (self.cells // 2) * (self.cells // 2)
        while len(queue) > 0:
            head = queue.pop(0)
            if str(head) not in opened:
                opened.append(str(head))
                score = min(score, head.score())
                print("opening {}:\n{}".format(head.hash(), head))
                if head.is_finished():
                    print("we did it")
                    break
                elif len(opened) % log_interval == 0:
                    print("opened {} nodes, score {}.".format(len(opened), head.score()))
                # touch all new things
                for i in range(len(head.rows)):
                    for row_index in range(len(head.rows[i])):
                        next_node = head.touch_index(i, row_index)
                        if next_node not in opened:
                            queue.append(next_node)


    def filled(self):
        count = 0
        for row in self.rows:
            for value in row:
                if value:
                    count += 1
        return count

    def score(self):
        count = self.filled()
        return count * (self.cells - count)


    def __str__(self) -> str:
        out_str = ""
        for row in self.rows:
            need_space = self.rows_no - len(row)
            out_str += " " * need_space
            for cell in row:
                if cell:
                    out_str += "*"
                else:
                    out_str += "-"
                out_str += " "
            out_str += "\n"
        return out_str

def print_value(board, q, r, s):
    print("value of {}, {}, {} is {}.".format(q,r,s, board.get_axial(q,r,s)))

def print_touch(board, q, r, s):
    print("after touching {}, board is \n{}".format((q,r,s), board.touch(q,r,s)))

if __name__ == '__main__':
   # board = HexBoard(ax_coords=[(0,0,0), (1,0,-1), (0,-1,1), (1,-3,2)])
    board = HexBoard(size=2, ax_coords=[(0,0,0), (1,0,-1), (0,-1,1)])
    print(board)
    print_value(board, 0,0,0)
    print_value(board, 1,0,-1)
    print_value(board, 1,-3,-1)
    print_value(board, 0, -1, 1)
    print_value(board, -1,0,1)
    print ("neightbors of 0, 0, 0 are {}, AKA {}".format(board.neighbors_axial(0,0,0), board.index_neighbors_from_axial(0,0,0)))
    print_touch(board, 0,0,0)
    board.bfs()

