import itertools
import random
import ansi_colors as ac


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    
    def get_cells(self):
        return self.cells
    
    def get_count(self):
        return self.count

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        """ if len(self.cells) == len(self.mines):
            return self.cells
        else:
            return set() """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        """ if len(self.cells) == len(self.safes):
            return self.cells
        else:
            return set() """
        return self.safes


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            self.mines.add(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.safes.add(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_nearby(self, cell):
        nearby = set()
        # Get adjacent cells.
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Add cell if within boundaries and not already characterized
                if (0 <= i < self.height and
                    0 <= j < self.width and
                    (i, j) not in self.moves_made and
                    (i, j) not in self.mines and
                    (i, j) not in self.safes):
                    nearby.add((i, j))
        return nearby

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        # Get cells for new sentence.
        sentence_cells = self.get_nearby(cell)
        # Create new sentence.
        self.knowledge.append(Sentence(sentence_cells, count))

        # Check for new information.
        print("Checking sentences:")
        for sentence in self.knowledge:
            print(f"  sentence: {sentence}")
            get_cells = sentence.get_cells()
            get_count = sentence.get_count()
            # Remove sentences with no cells.
            if len(get_cells) == 0:
                print(ac.BRIGHT_MAGENTA + "  removing sentence with no cells" + ac.RESET)
                self.knowledge.remove(sentence)
                continue
            if get_count == 0:
                print(f"    count is 0, sentence: {get_cells}, {get_count}")
                to_mark = []
                for c in get_cells:
                    to_mark.append(c)
                for item in to_mark:
                    self.mark_safe(item)
                # Remove sentence if it has no cells.
                if len(get_cells) == 0:
                    print("    removing sentence with no cells.")
                    self.knowledge.remove(sentence)
                    continue
            # Check for mines.
            if len(get_cells) == get_count:
                print(ac.BRIGHT_RED + f"    potential miner sentence: {sentence},  length: {len(get_cells)}" + ac.RESET)
                for c in get_cells:
                    print(f"nearby: {self.get_nearby(c)}")
                    if self.get_nearby(c) == 0:
                        print(ac.BRIGHT_RED + f"{c} is a mine" + ac.RESET)
                        to_mark = []
                        for c in get_cells:
                            to_mark.append(c)
                        for item in to_mark:
                            self.mark_mine(item)
                    else:
                        print(ac.BRIGHT_RED + f"{c} is not a mine" + ac.RESET)
                    
        print(f"move: {cell}")
        print(f"count: {count}")
        # print(f"sentence_cells: {sentence_cells}")
        print(f"known safe moves: {self.safes.difference(self.moves_made, self.mines)}")
        # print(f"moves_made: {self.moves_made}")
        print(ac.BRIGHT_GREEN + f"mines: {self.mines}\n" + ac.RESET)

        # Check for subsets in pairs of sentences.
        """ # Create list of sentences in knowledge.
        sentence_list = [sentence for sentence in self.knowledge] 
        # Get list of all permutations taken 2 at a time.
        perms = list(itertools.combinations(sentence_list, 2))
        for perm in perms:
            cells1 = perm[0].get_cells()
            count1 = perm[0].get_count()
            cells2 = perm[1].get_cells()
            count2 = perm[1].get_count()
            # If subset, create new sentence.
            if cells1 and cells2 and cells1 < cells2 and cells1.issubset(cells2):
                print("cells1 is subset")
                self.knowledge.append(Sentence(cells2.difference(cells1), count2 - count1))
            if cells1 and cells2 and cells2 < cells1 and cells2.issubset(cells1):
                print("cells2 is subset")
                self.knowledge.append(Sentence(cells1.difference(cells2), count1 - count2)) """

        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Use a safe cell, if available and not previously used for a moves.
        if self.safes:
            for c in self.safes:
                if c not in self.moves_made:
                    return c
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        choices = []
        # List the cells that can be used for a move.
        for i in range(self.height):
            for j in range(self.width):
                if  (i, j) not in self.moves_made and (i, j) not in self.mines:
                    choices.append((i, j))
        if len(choices) > 0:
            return random.choice(choices)
        else:
            return None
