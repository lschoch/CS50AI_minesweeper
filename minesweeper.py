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
                # Add cell if within boundaries and not safe or move made.
                if (0 <= i < self.height and
                    0 <= j < self.width and
                    (i, j) not in self.safes and 
                    (i, j) not in self.moves_made
                    ):
                    nearby.add((i, j))
        return nearby

    def check_knowledge(self, knowledge):
        # Check for new inferendes.
        flag = True
        while flag:
            flag = False
            print("printing sentences in knowledge:")
            for sentence in knowledge:
                print(sentence)
            for sentence in knowledge:
                get_cells = sentence.get_cells()
                get_count = sentence.get_count()
                if get_count == 0:
                    print("count 0")
                    for c in get_cells.copy():
                        self.mark_safe(c)
                    # Remove the sentence since all cells have been removed.
                    knowledge.remove(sentence)
                    self.check_knowledge(knowledge) 
                    # flag = True

                # Check for mines.
                if len(get_cells) == get_count and get_count > 0:
                    print(ac.BRIGHT_GREEN + "len = count" + ac.RESET)
                    for c in get_cells.copy():
                        self.mark_mine(c)
                    # Remove the sentence since all cells have been removed.
                    knowledge.remove(sentence)
                    self.check_knowledge(knowledge)
                    # flag = True

            # Check for subsets in pairs of sentences.
            if len(knowledge) > 1:
                combo_list = list(itertools.combinations(knowledge, 2))
                for combo in combo_list:
                    set0 = combo[0].get_cells()
                    count0 = combo[0].get_count()
                    set1 = combo[1].get_cells()
                    count1 = combo[1].get_count()
                    if set0 and set1:
                        print(ac.BRIGHT_YELLOW + f"set0: {set0}, set1: {set1}" + ac.RESET)
                        if set1 < set0:
                            print(ac.BRIGHT_RED + f"set1<set0: set0: {set0} set1: {set1}" + ac.RESET)
                            knowledge.append(Sentence(set0 - set1, count0 - count1))
                            if combo[0] in knowledge:
                                knowledge.remove(combo[0])
                            if combo[1] in knowledge:
                                knowledge.remove(combo[1])
                            self.check_knowledge(knowledge)
                            # flag = True
                        elif set0 < set1:
                            print(ac.BRIGHT_RED + f"set0<set1: set0: {set0} set1: {set1}" + ac.RESET)
                            knowledge.append(Sentence(set1 - set0, count1 - count0))
                            if combo[0] in knowledge:
                                knowledge.remove(combo[0])
                            if combo[1] in knowledge:
                                knowledge.remove(combo[1])
                            self.check_knowledge(knowledge)    
                            # flag = True
            

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
        print(ac.BRIGHT_MAGENTA + f"move: {cell}, count: {count}" + ac.RESET)
        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.check_knowledge(self.knowledge)
        # Get cells for new sentence.
        sentence_cells = self.get_nearby(cell)

        # If there are cells in sentence_cells, create new sentence.
        if sentence_cells:
            self.knowledge.append(Sentence(sentence_cells, count))
        # Check for inferences.
        self.check_knowledge(self.knowledge)
        print(ac.BRIGHT_MAGENTA + f"miners: {self.mines}\n" + ac.RESET)

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
