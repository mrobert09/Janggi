# Description: The backbone of a Janggi (Korean Chess) game. Some differences from normal Janggi, namely that
# players can not change their Elephant or Horse position. Also any Draw conditions are disabled.
# Main class method used by the program is the make_move() method. Blue goes first.

class JanggiGame:
    """
    Main game class. Keeps track of the state of the board, including validating game state and
    making moves through make_move(). Board is displayed visually in the program output for debug
    purposes. Piece positions are maintained through a dictionary called _filled_spaces. Upon a checkmate
    scenario, game will update the _game_state variable to declare winner. Turns are automatically
    swapped back and forth, with checks in place preventing players from taking a turn out of order.
    """
    def __init__(self):
        self._game_state = "UNFINISHED"
        self._player_turn = "BLUE"
        self._board_positions = []
        self._board_coords = []

        # Main database of piece objects and positions.
        self._filled_spaces = {}

        # Total possible move positions, does not include staying still. Used in checks.
        self._total_red_targets = []
        self._total_blue_targets = []

        # Boolean flags for state of check
        self._blue_check = False
        self._red_check = False
        self._check_test = False
        self._last_killed = None  # storage for last piece removed, in case it needs to be put back

        # Debug flag, enables free movement of pieces
        self._debug = 0

        # Setup method to take care of running other starting methods.
        self.setup()

    def setup(self):
        """
        Setup method for board state and other maintenance items. Purpose of method is to clean up
        the class __init__ method a little. Runs the following methods:
        generate_coord_list(): Fills list with every coordinate on board.
        generate_equivalencies(): Creates an equivalent coordinate system.
        generate_dict(): Initially fills board dictionary with "None" in each position.
        generate_pieces(): Creates class objects for each piece and places them on the board.
        generate_board_state(): Starting valid moves for each piece.
        :return: None
        """
        self.generate_coord_list()
        self.generate_equivalencies()
        self.generate_dict()
        self.generate_pieces()
        self.generate_board_state()

    def generate_coord_list(self):
        """
        Fills list with every coordinate on board. Used for iterating through board positions.
        :return: None
        """
        for x in range(9):
            for y in range(10):
                self._board_coords.append((x, y))

    def generate_equivalencies(self):
        """
        Generates a dictionary holding equivalent coordinates for cells.
        :return: None
        """
        self.equiv = PositionEquivalents()

    def generate_dict(self):
        """
        Initially fills board dictionary with "None" in each position.
        :return: None
        """
        for x in range(9):
            for y in range(10):
                self.set_filled_spaces((x, y), None)

    def generate_pieces(self):
        """
        Manually sets up every piece on the board by initializing objects specific for each piece type.
        Each piece object accepts 5 parameters:
        Game class object: self
        Team: "RED" or "BLUE"
        Starting position: (x, y)
        Piece name: Uses xYy# naming structure, where x: color, Yy: piece, #: piece number
        Type: The type of piece it is.
        :return:
        """

        # Red Team
        self._rCh1 = Chariot(self, "RED", (0, 0), "rCh1", "Chariot")
        self._rCh2 = Chariot(self, "RED", (8, 0), "rCh2", "Chariot")
        self._rEl1 = Elephant(self, "RED", (1, 0), "rEl1", "Elephant")
        self._rEl2 = Elephant(self, "RED", (6, 0), "rEl2", "Elephant")
        self._rHo1 = Horse(self, "RED", (2, 0), "rHo1", "Horse")
        self._rHo2 = Horse(self, "RED", (7, 0), "rHo2", "Horse")
        self._rGu1 = Guard(self, "RED", (3, 0), "rGu1", "Guard")
        self._rGu2 = Guard(self, "RED", (5, 0), "rGu2", "Guard")
        self._rGen = General(self, "RED", (4, 1), "rGen", "General")
        self._rCa1 = Cannon(self, "RED", (1, 2), "rCa1", "Cannon")
        self._rCa2 = Cannon(self, "RED", (7, 2), "rCa2", "Cannon")
        self._rSo1 = Soldier(self, "RED", (0, 3), "rSo1", "Soldier")
        self._rSo2 = Soldier(self, "RED", (2, 3), "rSo2", "Soldier")
        self._rSo3 = Soldier(self, "RED", (4, 3), "rSo3", "Soldier")
        self._rSo4 = Soldier(self, "RED", (6, 3), "rSo4", "Soldier")
        self._rSo5 = Soldier(self, "RED", (8, 3), "rSo5", "Soldier")

        # Blue Team
        self._bCh1 = Chariot(self, "BLUE", (0, 9), "bCh1", "Chariot")
        self._bCh2 = Chariot(self, "BLUE", (8, 9), "bCh2", "Chariot")
        self._bEl1 = Elephant(self, "BLUE", (1, 9), "bEl1", "Elephant")
        self._bEl2 = Elephant(self, "BLUE", (6, 9), "bEl2", "Elephant")
        self._bHo1 = Horse(self, "BLUE", (2, 9), "bHo1", "Horse")
        self._bHo2 = Horse(self, "BLUE", (7, 9), "bHo2", "Horse")
        self._bGu1 = Guard(self, "BLUE", (3, 9), "bGu1", "Guard")
        self._bGu2 = Guard(self, "BLUE", (5, 9), "bGu2", "Guard")
        self._bGen = General(self, "BLUE", (4, 8), "bGen", "General")
        self._bCa1 = Cannon(self, "BLUE", (1, 7), "bCa1", "Cannon")
        self._bCa2 = Cannon(self, "BLUE", (7, 7), "bCa2", "Cannon")
        self._bSo1 = Soldier(self, "BLUE", (0, 6), "bSo1", "Soldier")
        self._bSo2 = Soldier(self, "BLUE", (2, 6), "bSo2", "Soldier")
        self._bSo3 = Soldier(self, "BLUE", (4, 6), "bSo3", "Soldier")
        self._bSo4 = Soldier(self, "BLUE", (6, 6), "bSo4", "Soldier")
        self._bSo5 = Soldier(self, "BLUE", (8, 6), "bSo5", "Soldier")

    def generate_board_state(self):
        """
        Method that refreshes the state of the board after every turn. Checks the available moves
        for every piece still remaining. The piece method move_check() adds these moves to data members
        _total_red_targets and _total_blue_targets. Move_check() will also set flags for check conditions.
        :return:
        """

        # Resets piece list and check flags
        self._blue_check = False
        self._red_check = False
        self._total_blue_targets.clear()
        self._total_red_targets.clear()

        # Local variable used for debugging loop iterations.
        debug_count = 0

        # Initial pass to set up all possible moves
        for from_x in range(9):
            for from_y in range(10):
                debug_count += 1  # used for breakpoint debugging

                piece = self.check_square((from_x, from_y))
                if piece != None:

                    # Repopulate list of possible move targets
                    piece.reset_possible_targets()
                    for coord in self._board_coords:
                        piece.move_check((from_x, from_y), coord)

    def check_square(self, coord):
        """
        Method to check if a space is occupied.
        :param coord: (x, y) coordinate from board.
        :return: None if space is empty. Piece object if space is occupied.
        """
        return self._filled_spaces[coord]

    def set_filled_spaces(self, coord, name):
        """
        Adds contents to space on board.
        :param coord: (x, y) coordinate from board.
        :param name: None if space is now empty. Piece object if space is occupied.
        :return: None
        """
        self._filled_spaces[coord] = name

    def get_filled_spaces(self):
        """
        Retrieves contents of _filled_spaces dictionary. Used for debugging.
        :return: _filled_spaces dictionary.
        """
        return self._filled_spaces

    def get_game_state(self):
        """
        Returns current state of game.
        :return: "UNFINISHED" if game is unfinished. "BLUE_WIN" or "RED_WIN" if somebody has won.
        """
        return self._game_state

    def is_in_check(self, color):
        """
        Returns the status of check for a certain team.
        Uses lowercase 'blue' and 'red' to fit with test conditions on Gradescope.
        :param color: 'blue' or 'red'
        :return: True if team is in check, False otherwise.
        """
        if color == 'blue':
            return self._blue_check
        if color == 'red':
            return self._red_check

    def set_check_flag(self, color):
        """
        Sets boolean flag for check state for each team.
        :param color: "BLUE" or "RED"
        :return: None
        """
        if color == "BLUE":
            self._blue_check = True
        if color == "RED":
            self._red_check = True

    def set_check_test_flag(self):
        """
        Used by piece classes to set check flag when determining checkmate status.
        :return: None
        """
        self._check_test = True

    def get_total_targets(self, color):
        """
        Returns total valid targets for a given team. Used in logic for many piece classes.
        :param color: "BLUE" or "RED"
        :return: All target options for a team.
        """
        if color == "BLUE":
            return self._total_blue_targets
        if color == "RED":
            return self._total_red_targets

    def set_total_targets(self, coord, color):
        """
        Appends total target list for a team with a newly verified valid move.
        :param coord: (x, y) coordinate from board.
        :param color: "BLUE" or "RED"
        :return: None
        """
        if color == "BLUE":
            self._total_blue_targets.append(coord)
        if color == "RED":
            self._total_red_targets.append(coord)

    def remove_total_targets(self, coord, color):
        """
        Removes from total target list for a team a move determined to be invalid.
        Needed as there are some situations (such as a self-check) where an initially valid move
        is later determined to be invalid.
        :param coord: (x, y) coordinate from board.
        :param color: "BLUE" or "RED"
        :return: None
        """
        if color == "BLUE":
            self._total_blue_targets.remove(coord)
        if color == "RED":
            self._total_red_targets.remove(coord)

    def make_move(self, p_from, p_to):
        """
        Main method called by user. Tests for a couple universal conditions to see if move is valid.
        Verifies that the move being attempted is a pre-determined valid move for that piece.
        Ensures a self-check doesn't happen and will reset the board to previous state if it does.
        Ends with a checkmate test.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is is successful. False otherwise.
        """

        # Ensures game is in progress and player is attempting to move pieces within the board.
        if self._game_state != "UNFINISHED":
            return False
        if p_from not in self.equiv.get_equivalents() or \
                p_to not in self.equiv.get_equivalents():
            return False

        # Setting up some local variables for easier human readability.
        pos_from = self.get_equiv(p_from)
        pos_to = self.get_equiv(p_to)
        moving = self._filled_spaces
        piece = moving[pos_from]

        # Test code for showing moves on GradeScope
        if piece != None:
            if moving[pos_to] != None:
                print("# Attempting move:", piece.get_team(), piece.get_type(), "=>",
                      moving[pos_to].get_team(), moving[pos_to].get_type())
            else:
                print("# Attempting move:", piece.get_team(), piece.get_type(), "=>",
                      "Empty space.")
        else:
            print("# Moving: Empty square.")
        print("g.make_move(\"" + p_from + "\", \"" + p_to + "\")")

        # Checks if piece exists.
        if piece == None:
            return False

        # Checks if correct player turn. Debug option from __init__ would skip this check.
        if self._debug == 0:
            if piece.get_team() != self._player_turn:
                return False

        # Verifies that piece is trying to move into position previously generated by generate_board_state().
        if pos_to in piece.get_possible_targets():

            # Stores enemy unit in case it needs to be restored.
            self._last_killed = self.check_square(pos_to)

            # Move piece to its new location and clear the space it came from.
            self.set_filled_spaces(pos_from, None)
            piece.set_square(pos_to)
            self.set_filled_spaces(pos_to, piece)

            # Check the current state of the board for next turn.
            self.generate_board_state()

            # Can't end your turn in check. If it's determined a player has self-checked,
            # resets whatever move happened and has them go again.
            if self._player_turn == "BLUE" and self._blue_check:
                piece.set_square(pos_from)
                self.set_filled_spaces(pos_from, piece)
                self.set_filled_spaces(pos_to, self._last_killed)
                self._last_killed = None
                return False
            if self._player_turn == "RED" and self._red_check:
                piece.set_square(pos_from)
                self.set_filled_spaces(pos_from, piece)
                self.set_filled_spaces(pos_to, self._last_killed)
                self._last_killed = None
                return False

            # If move didn't result in self-check, change turn and print board.
            self._last_killed = None
            self.change_turn()
            # self.print_board()

            # Upon new player turn, test for checkmate condition.
            if self._player_turn == "BLUE" and self._blue_check:
                self.test_check_mate("BLUE")
            if self._player_turn == "RED" and self._red_check:
                self.test_check_mate("RED")

            return True
        return False

    def test_check_mate(self, color):
        """
        Checkmate test that is triggered if a team starts their turn in check.
        Runs a deep search into all possible board states that could result from any move performed by
        team currently in check. For purposes of comment clarity and readability, the current team (the one
        in check) is referred to as friendly, while the attacking team is referred to as the enemy. Method also
        sets the game state should a checkmate be determined. Uses several short-circuit techniques to end
        the deep search should a certain state be realized.
        :param color: "BLUE" or "RED"
        :return: True if checkmate. False otherwise.
        """

        # Local variables used for debugging loop iterations.
        debug_count = 0
        debug_count2 = 0

        # Resets valid move list of friendly team for re-evaluation.
        if color == "BLUE":
            self._total_blue_targets = []
        if color == "RED":
            self._total_red_targets = []

        # Iterates through board looking for a friendly piece.
        for from_x in range(9):
            for from_y in range(10):
                debug_count += 1  # used for breakpoint debugging
                pos_from = (from_x, from_y)
                piece = self.check_square(pos_from)
                if piece != None and piece.get_team() == color:

                    # Resets valid move list for friendly piece for re-evaluation.
                    piece.reset_possible_targets()

                    # Checks all possible moves for friendly piece.
                    for coord in self._board_coords:
                        self._check_test = False
                        if piece.move_check(pos_from, coord):

                            # Move friendly piece to its new location and clear the space it came from.
                            self._last_killed = self.check_square(coord)
                            self.set_filled_spaces(pos_from, None)
                            self.set_filled_spaces(coord, piece)
                            piece.set_square(coord)

                            # Checks all enemy moves available for new potentially valid position found above.
                            # Has a short-circuit system to exit the following loop in the event of a check.
                            # Finding a check means that friendly move position is invalid as it would leave
                            # friendly General still in a check position.
                            for new_from_x in range(9):
                                if self._check_test == True:  # short-circuit in case of a check
                                    break
                                for new_from_y in range(10):
                                    if self._check_test == True:  # short-circuit in case of a check
                                        break
                                    debug_count2 += 1  # used for breakpoint debugging
                                    new_pos = (new_from_x, new_from_y)
                                    piece2 = self.check_square(new_pos)
                                    if piece2 != None and piece2.get_team() != color:  # != color == enemy team

                                        # If the friendly piece would kill the target piece. Special case.
                                        if piece2.get_square() == coord:
                                            break

                                        # Checks all potential moves of this enemy piece.
                                        # Enemy piece's move_check() will set _check_test flag if check occurs.
                                        for coord2 in self._board_coords:
                                            piece2.move_check(new_pos, coord2)
                                            if self._check_test == True:  # short-circuit in case of a check

                                                # If check is found, remove friendly pieces move as it is invalid.
                                                piece.remove_possible_targets(coord)
                                                self.remove_total_targets(coord, color)

                                                # Reset the state of the board to check next friendly move.
                                                self.set_filled_spaces((from_x, from_y), piece)
                                                self.set_filled_spaces(coord, self._last_killed)
                                                piece.set_square((from_x, from_y))
                                                break

                            # If no check was found for given friendly move, then no checkmate has occurred.
                            # This is true because there is at least 1 friendly move that does not end in check.
                            if self._check_test == False:
                                self.set_filled_spaces((from_x, from_y), piece)
                                self.set_filled_spaces(coord, self._last_killed)
                                piece.set_square((from_x, from_y))

        # If after checking all possible moves, friendly team has no valid targets, then checkmate is declared.
        if color == "BLUE" and self._total_blue_targets == []:
            self._game_state = "RED_WON"
            print("Red wins.")
            return True
        if color == "RED" and self._total_red_targets == []:
            self._game_state = "BLUE_WON"
            print("Blue wins.")
            return True

    def change_turn(self):
        """
        Simple method for swapping player turns.
        :return: None
        """
        if self._player_turn == "BLUE":
            self._player_turn = "RED"
        elif self._player_turn == "RED":
            self._player_turn = "BLUE"

    def print_board(self):
        """
        Prints board into the output. Utilizes a nested list for easy checkerboard layout.
        Also uses some custom print statements for readability. Used in conjunction with generate_board().
        :return: None
        """
        self.generate_board()
        print("      A       B       C       D       E       F       G       H       I")
        print("    ----------------------------------------------------------------------")
        num = 1
        for element in self._board_positions:
            if num < 10:
                print(num, "", element, num)
                print("    ----------------------------------------------------------------------")
            if num == 10:
                print(num, element, num)
                print("    ----------------------------------------------------------------------")
                print("      A       B       C       D       E       F       G       H       I")
            num += 1

    def generate_board(self):
        """
        Generates board data used visuals.
        :return: None
        """
        temp = []
        self._board_positions = []
        for y in range(10):
            for x in range(9):
                if self._filled_spaces[(x, y)] == None:
                    temp.append("    ")  # used to make visual board of positions
                else:
                    temp.append(self._filled_spaces[(x, y)].get_name())
            self._board_positions.append(temp)
            temp = []

    def get_equiv(self, val):
        """
        Simplified get method to return the equivalent value of a square. For example,
        10 returns 'b1' and 'c1' returns 20. Note: 'b1' is a string, but 10 is an int.
        :param val: Original square name.
        :return: Equivalent name for square.
        """
        return self.equiv.pos_equivalent(val)


class PositionEquivalents:
    """
    Class used to build an equivalent coordinate database. Could have been built into main game class
    as a method, but opted for this for some increased modularization and readability.
    """
    def __init__(self):
        self._position_dict = {}
        self.generate_dict()

    def generate_dict(self):
        """
        Fills position dictionary with equivalent coordinates.
        :return: None
        """
        count = 1
        letter = 97

        for y in range(10):
            for x in range(9):
                let = chr(letter)
                num = str(count)
                coords = (x, y)
                self._position_dict[let + num] = coords
                self._position_dict[coords] = let + num
                letter += 1
            count += 1
            letter = 97

    def pos_equivalent(self, val):
        """
        Returns the equivalent coordinate for a specific square. Converts both ways.
        :param val: Coordinate to be converted. Can be in form "a1" or "(x, y)"
        :return: Equivalent coordinate form.
        """
        if val in self._position_dict:
            return self._position_dict[val]

    def get_equivalents(self):
        """
        Returns list of equivalent coordinate systems. Mostly for debugging purposes.
        :return: Equivalents dictionary.
        """
        return self._position_dict


class Piece:
    """
    Parent class for all pieces in the game. Has basic get methods for name and team.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Chariot #1 = rCh1
    """
    def __init__(self, game, team, coord, name, type):
        self._game = game
        self._team = team
        self._pos = coord
        self._name = name
        self._type = type
        self._possible_targets = []
        self.place_piece()  # Places piece in starting location upon creation.

    def get_name(self):
        """
        Gets piece name. Names are in xYy# format described earlier in program.
        Exception: Generals follow xYyy format.
        :return: Piece's name in xYy# format. Example: "bSo4" or "rGen".
        """
        return self._name

    def get_type(self):
        """
        Gets piece type.
        :return: Piece's type. Example: "Chariot" or "General".
        """
        return self._type

    def get_team(self):
        """
        Gets team color.
        :return: "BLUE" or "RED"
        """
        return self._team

    def set_square(self, pos):
        """
        Updates record of piece's location. Does NOT move the piece according to the game.
        This is merely used in addition for data.
        :param pos: (x, y) coordinate from board.
        :return: None
        """
        self._pos = pos

    def get_square(self):
        """
        Gets location of piece on board.
        :return: (x, y) coordinate from board where piece is located.
        """
        return self._pos

    def place_piece(self):
        """
        Method used upon initialization of piece. Places it in default position given.
        :return: None
        """
        self._game.set_filled_spaces(self._pos, self)

    def reset_possible_targets(self):
        """
        Used by game class to reset database of possible valid moves piece has.
        Useful in checkmate method from game class.
        :return: None
        """
        self._possible_targets.clear()

    def get_possible_targets(self):
        """
        Retrieves all valid moves piece has.
        :return: List of possible coordinates piece can move to.
        """
        return self._possible_targets

    def remove_possible_targets(self, coord):
        """
        Removes individual targets from possible move list. Used if previously valid position is
        determined to be invalid.
        :param coord: (x, y) coordinate from board.
        :return: None
        """
        self._possible_targets.remove(coord)


class Soldier(Piece):
    """
    Child class for Soldiers in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Soldier #1 = rSo1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Soldier staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some one square Soldier movements
        move_up = p_from[1] - 1 == p_to[1] and p_from[0] == p_to[0]
        move_down = p_from[1] + 1 == p_to[1] and p_from[0] == p_to[0]
        move_left = p_from[0] - 1 == p_to[0] and p_from[1] == p_to[1]
        move_right = p_from[0] + 1 == p_to[0] and p_from[1] == p_to[1]
        move_upleft = p_from[1] - 1 == p_to[1] and p_from[0] - 1 == p_to[0]
        move_upright = p_from[1] - 1 == p_to[1] and p_from[0] + 1 == p_to[0]
        move_downleft = p_from[1] + 1 == p_to[1] and p_from[0] - 1 == p_to[0]
        move_downright = p_from[1] + 1 == p_to[1] and p_from[0] + 1 == p_to[0]

        # Blue Soldier
        if team == "BLUE":

            # Setting up special Red palace diagonal move conditions
            diag_squares = [(3, 0), (3, 2), (4, 1), (5, 0), (5, 2)]
            diagonal_check = p_from in diag_squares and p_to in diag_squares and (move_upleft or move_upright)

            # Is Soldier trying to move a valid distance?
            if diagonal_check or move_up or move_left or move_right:

                # Is there a piece where the Soldier is moving?
                if attacking != None:

                    # Is it on the Soldiers's team?
                    if attacking.get_team() == team:
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    # If building move database.
                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                # If building move database.
                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False

        # Red Soldier
        if team == "RED":

            # Setting up special Blue palace diagonal move conditions
            diag_squares = [(3, 7), (3, 9), (4, 8), (5, 7), (5, 9)]
            diagonal_check = p_from in diag_squares and p_to in diag_squares and (move_downleft or move_downright)

            # Is Soldier trying to move a valid distance?
            if diagonal_check or move_down or move_left or move_right:

                # Is there a piece where the Soldier is moving?
                if attacking != None:

                    # Is it on the Soldiers's team?
                    if attacking.get_team() == team:
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    # If building move database.
                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                # If building move database.
                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False


class Cannon(Piece):
    """
    Child class for Cannons in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Cannon #1 = rCa1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions. Calls collision_check() method.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Cannon staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some Cannon movements
        move_up = p_from[0] == p_to[0] and p_from[1] > p_to[1]
        move_down = p_from[0] == p_to[0] and p_from[1] < p_to[1]
        move_left = p_from[1] == p_to[1] and p_from[0] > p_to[0]
        move_right = p_from[1] == p_to[1] and p_from[0] < p_to[0]
        move_diagonal = p_from[0] != p_to[0] and p_from[1] != p_to[1]

        # Setting up special palace diagonal move conditions
        # Ignores middle squares in palace as Cannon can never get there.
        red_diag_squares = [(3, 0), (3, 2), (5, 0), (5, 2)]
        blue_diag_squares = [(3, 7), (3, 9), (5, 7), (5, 9)]
        in_red_palace = p_from in red_diag_squares and p_to in red_diag_squares
        in_blue_palace = p_from in blue_diag_squares and p_to in blue_diag_squares
        diagonal_check = move_diagonal and (in_red_palace or in_blue_palace)

        # Is the Cannon trying to move a valid distance?
        if diagonal_check or move_up or move_down or move_left or move_right:

            # Does the Cannon collide with anything if moving > 1 square?
            # Only proceed if not testing soft checks.
            if self.collision_check(move_up, move_down, move_left, move_right, diagonal_check, p_from, p_to):

                # Is there a piece where the Cannon is moving?
                if attacking != None:

                    # Is it on the Cannon's team?
                    if attacking.get_team() == team:
                        return False

                    # Is it attacking an enemy Cannon?
                    if attacking.get_type() == "Cannon":
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # If jump is invalid.
            else:
                return False

        # If trying to move to invalid location.
        else:
            return False

    def collision_check(self, up, down, left, right, diagonal, p_from, p_to):
        """
        Helper function that checks if collision has occurred. For Cannon's, this function returns True
        if exactly 1 piece is jumped over and that piece is not another Cannon. Otherwise, it will return false.
        :param up: True / False
        :param down: True / False
        :param left: True / False
        :param right: True / False
        :param diagonal: True / False
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if jump is valid, False is jump is not.
        """
        v_distance = abs(p_from[1] - p_to[1])
        h_distance = abs(p_from[0] - p_to[0])
        collisions = 0
        cannon_list = ["rCa1", "rCa2", "bCa1", "bCa2"]

        # Each direction below is very similar in logic. It calculates the absolute value of the distance
        # being traveled, then runs a loop to check each position between p_from and p_to. Returns False
        # if it sees another Cannon, and returns True if the number of collisions == 1.
        if up:
            for pos in range(v_distance - 1):
                coord = (p_from[0], p_from[1] - (pos + 1))
                block_check = self._game.check_square(coord)
                if block_check != None:
                    if block_check.get_name() in cannon_list:
                        return False
                    collisions += 1
        if down:
            for pos in range(v_distance - 1):
                coord = (p_from[0], p_from[1] + pos + 1)
                block_check = self._game.check_square(coord)
                if block_check != None:
                    if block_check.get_name() in cannon_list:
                        return False
                    collisions += 1
        if left:
            for pos in range(h_distance - 1):
                coord = (p_from[0] - (pos + 1), p_from[1])
                block_check = self._game.check_square(coord)
                if block_check != None:
                    if block_check.get_name() in cannon_list:
                        return False
                    collisions += 1
        if right:
            for pos in range(h_distance - 1):
                coord = (p_from[0] + pos + 1, p_from[1])
                block_check = self._game.check_square(coord)
                if block_check != None:
                    if block_check.get_name() in cannon_list:
                        return False
                    collisions += 1
        if diagonal:
            # Easy coord math to see if in Red or Blue palace.
            # Because the x + y for the two palace spots are mutually exclusive...:
            if p_from[0] + p_from[1] < 8:  # Red Palace
                if self._game.check_square((4, 1)) != None:  # If something is in center of Red Palace
                    if self._game.check_square((4, 1)).get_name() in cannon_list:
                        return False
                    return True
                else:
                    return False
            if p_from[0] + p_from[1] > 9:  # Blue Palace
                if self._game.check_square((4, 8)) != None:  # If something is in center of Blue Palace
                    if self._game.check_square((4, 8)).get_name() in cannon_list:
                        return False
                    return True

        # Returns true only if collisions found were exactly 1.
        if collisions == 1:
            return True
        else:
            return False


class General(Piece):
    """
    Child class for Generals in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red General = rGen
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Defining some one square General movements
        move_up = p_from[1] - 1 == p_to[1] and p_from[0] == p_to[0]
        move_down = p_from[1] + 1 == p_to[1] and p_from[0] == p_to[0]
        move_left = p_from[0] - 1 == p_to[0] and p_from[1] == p_to[1]
        move_right = p_from[0] + 1 == p_to[0] and p_from[1] == p_to[1]
        move_upleft = p_from[0] - 1 == p_to[0] and p_from[1] - 1 == p_to[1]
        move_upright = p_from[0] + 1 == p_to[0] and p_from[1] - 1 == p_to[1]
        move_downleft = p_from[0] - 1 == p_to[0] and p_from[1] + 1 == p_to[1]
        move_downright = p_from[0] + 1 == p_to[0] and p_from[1] + 1 == p_to[1]
        move_diagonal = move_upleft or move_upright or move_downleft or move_downright

        # Blue General
        if team == "BLUE":

            # Setting up special palace diagonal move conditions
            diag_squares = [(3, 7), (3, 9), (4, 8), (5, 7), (5, 9)]
            diagonal_check = p_from in diag_squares and move_diagonal

            # Is the General trying to leave the palace?
            if p_to[0] > 5 or p_to[0] < 3 or p_to == (3, 6) or p_to == (4, 6) or p_to == (5, 6):
                return False

            # Is the General staying still?
            if attacking == self:
                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # Is the General trying to move a valid distance?
            if diagonal_check or move_up or move_down or move_left or move_right:

                # Is there a piece where the General is moving?
                if attacking != None:

                    # Is it on the General's team?
                    if attacking.get_team() == "BLUE":
                        return False

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False

        # Red General
        if team == "RED":

            # Setting up special palace diagonal move conditions
            diag_squares = [(3, 0), (3, 2), (4, 1), (5, 0), (5, 2)]
            diagonal_check = p_from in diag_squares and move_diagonal

            # Is the General trying to leave the palace?
            if p_to[0] > 5 or p_to[0] < 3 or p_to == (3, 3) or p_to == (4, 3) or p_to == (5, 3):
                return False

            # Is the General staying still?
            if attacking == self:
                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # Is the General trying to move a valid distance?
            if move_up or move_down or move_left or move_right or diagonal_check:

                # Is there a piece where the General is moving?
                if attacking != None:

                    # Is it on the General's team?
                    if attacking.get_team() == "RED":
                        return False

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False


class Chariot(Piece):
    """
    Child class for Chariots in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Chariot #1 = rCh1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions. Calls collision_check() method.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Chariot staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some Chariot movements
        move_up = p_from[0] == p_to[0] and p_from[1] > p_to[1]
        move_down = p_from[0] == p_to[0] and p_from[1] < p_to[1]
        move_left = p_from[1] == p_to[1] and p_from[0] > p_to[0]
        move_right = p_from[1] == p_to[1] and p_from[0] < p_to[0]
        move_diagonal = p_from[0] != p_to[0] and p_from[1] != p_to[1]

        # Setting up special palace diagonal move conditions
        red_diag_squares = [(3, 0), (3, 2), (4, 1), (5, 0), (5, 2)]
        blue_diag_squares = [(3, 7), (3, 9), (4, 8), (5, 7), (5, 9)]
        in_red_palace = p_from in red_diag_squares and p_to in red_diag_squares
        in_blue_palace = p_from in blue_diag_squares and p_to in blue_diag_squares
        diagonal_check = move_diagonal and (in_red_palace or in_blue_palace)

        # Is the Chariot trying to move a valid distance?
        if diagonal_check or move_up or move_down or move_left or move_right:

            # Does the Chariot collide with anything if moving > 1 square?
            if self.collision_check(move_up, move_down, move_left, move_right, diagonal_check, p_from, p_to):

                # Is there a piece where the Chariot is moving?
                if attacking != None:

                    # Is it on the Chariot's team?
                    if attacking.get_team() == team:
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # If path is blocked.
            else:
                return False
        # If trying to move to invalid location.
        else:
            return False

    def collision_check(self, up, down, left, right, diagonal, p_from, p_to):
        """
        Helper function that checks if collision has occurred. Returns False if collision detected.
        :param up: True / False
        :param down: True / False
        :param left: True / False
        :param right: True / False
        :param diagonal: True / False
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        v_distance = abs(p_from[1] - p_to[1])
        h_distance = abs(p_from[0] - p_to[0])
        if up:
            for pos in range(v_distance - 1):
                coord = (p_from[0], p_from[1] - (pos + 1))
                block_check = self._game.check_square(coord)
                if block_check != None:
                    return False
        if down:
            for pos in range(v_distance - 1):
                coord = (p_from[0], p_from[1] + pos + 1)
                block_check = self._game.check_square(coord)
                if block_check != None:
                    return False
        if left:
            for pos in range(h_distance - 1):
                coord = (p_from[0] - (pos + 1), p_from[1])
                block_check = self._game.check_square(coord)
                if block_check != None:
                    return False
        if right:
            for pos in range(h_distance - 1):
                coord = (p_from[0] + pos + 1, p_from[1])
                block_check = self._game.check_square(coord)
                if block_check != None:
                    return False

        if diagonal:
            # Easy coord math to see if in Red or Blue palace.
            # Because the x + y for the two palace spots are mutually exclusive...:
            # If Chariot is in center, it can only move 1 space. No need to check collision.

            # Moving down right in Palace
            if p_from[0] < p_to[0] and p_from[1] < p_to[1]:
                if p_to[0] != 4:  # not targeting center square. Must try to move two squares.
                    coord = (p_from[0] + 1, p_from[1] + 1)
                    block_check = self._game.check_square(coord)
                    if block_check != None:
                        return False

            # Moving up right in Palace
            if p_from[0] < p_to[0] and p_from[1] > p_to[1]:
                if p_to[0] != 4:  # not targeting center square. Must try to move two squares.
                    coord = (p_from[0] + 1, p_from[1] - 1)
                    block_check = self._game.check_square(coord)
                    if block_check != None:
                        return False

            # Moving down left in Palace
            if p_from[0] > p_to[0] and p_from[1] < p_to[1]:
                if p_to[0] != 4:  # not targeting center square. Must try to move two squares.
                    coord = (p_from[0] - 1, p_from[1] + 1)
                    block_check = self._game.check_square(coord)
                    if block_check != None:
                        return False

            # Moving up left in Palace
            if p_from[0] > p_to[0] and p_from[1] > p_to[1]:
                if p_to[0] != 4:  # not targeting center square. Must try to move two squares.
                    coord = (p_from[0] - 1, p_from[1] - 1)
                    block_check = self._game.check_square(coord)
                    if block_check != None:
                        return False
        return True


class Elephant(Piece):
    """
    Child class for Elephants in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Elephant #1 = rEl1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions. Calls collision_check() method.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Elephant staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some Elephant movements
        move_upleft = p_from[0] == p_to[0] + 2 and p_from[1] == p_to[1] + 3
        move_upright = p_from[0] == p_to[0] - 2 and p_from[1] == p_to[1] + 3
        move_rightup = p_from[0] == p_to[0] - 3 and p_from[1] == p_to[1] + 2
        move_rightdown = p_from[0] == p_to[0] - 3 and p_from[1] == p_to[1] - 2
        move_downright = p_from[0] == p_to[0] - 2 and p_from[1] == p_to[1] - 3
        move_downleft = p_from[0] == p_to[0] + 2 and p_from[1] == p_to[1] - 3
        move_leftdown = p_from[0] == p_to[0] + 3 and p_from[1] == p_to[1] - 2
        move_leftup = p_from[0] == p_to[0] + 3 and p_from[1] == p_to[1] + 2

        # Is the Elephant trying to move a valid distance?
        if move_upright or move_upleft or move_rightup or move_rightdown \
                or move_downright or move_downleft or move_leftdown or move_leftup:

            # Does the Elephant collide with anything in it's path?
            if self.collision_check(move_upright, move_upleft, move_rightup, move_rightdown,
                                    move_downright, move_downleft, move_leftdown, move_leftup,  p_from):

                # Is there a piece where the Elephant is moving?
                if attacking != None:

                    # Is it on the Elephant's team?
                    if attacking.get_team() == team:
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # If path is blocked.
            else:
                return False

        # If trying to move to invalid location.
        else:
            return False

    def collision_check(self, upright, upleft, rightup, rightdown, downright, downleft,
                        leftdown, leftup, p_from):
        """
        Helper function that checks if collision has occurred. Returns False if collision detected.
        :param upright: True / False
        :param upleft: True / False
        :param rightup: True / False
        :param rightdown: True / False
        :param downright: True / False
        :param downleft: True / False
        :param leftdown: True / False
        :param leftup: True / False
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :return: True if move is valid. False otherwise.
        """
        if upright or upleft:
            coord = (p_from[0], p_from[1] - 1)
            if self._game.check_square(coord) != None:
                return False
            if upright:
                coord = (p_from[0] + 1, p_from[1] - 2)
                if self._game.check_square(coord) != None:
                    return False
            if upleft:
                coord = (p_from[0] - 1, p_from[1] - 2)
                if self._game.check_square(coord) != None:
                    return False
            return True
        if rightup or rightdown:
            coord = (p_from[0] + 1, p_from[1])
            if self._game.check_square(coord) != None:
                return False
            if rightup:
                coord = (p_from[0] + 2, p_from[1] - 1)
                if self._game.check_square(coord) != None:
                    return False
            if rightdown:
                coord = (p_from[0] + 2, p_from[1] + 1)
                if self._game.check_square(coord) != None:
                    return False
            return True
        if downright or downleft:
            coord = (p_from[0], p_from[1] + 1)
            if self._game.check_square(coord) != None:
                return False
            if downright:
                coord = (p_from[0] + 1, p_from[1] + 2)
                if self._game.check_square(coord) != None:
                    return False
            if downleft:
                coord = (p_from[0] - 1, p_from[1] + 2)
                if self._game.check_square(coord) != None:
                    return False
            return True
        if leftdown or leftup:
            coord = (p_from[0] - 1, p_from[1])
            if self._game.check_square(coord) != None:
                return False
            if leftdown:
                coord = (p_from[0] - 2, p_from[1] + 1)
                if self._game.check_square(coord) != None:
                    return False
            if leftup:
                coord = (p_from[0] - 2, p_from[1] - 1)
                if self._game.check_square(coord) != None:
                    return False
            return True


class Horse(Piece):
    """
    Child class for Horses in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Horse #1 = rHo1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)

    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions. Calls collision_check() method.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Horse staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some Horse movements
        move_upleft = p_from[0] == p_to[0] + 1 and p_from[1] == p_to[1] + 2
        move_upright = p_from[0] == p_to[0] - 1 and p_from[1] == p_to[1] + 2
        move_rightup = p_from[0] == p_to[0] - 2 and p_from[1] == p_to[1] + 1
        move_rightdown = p_from[0] == p_to[0] - 2 and p_from[1] == p_to[1] - 1
        move_downright = p_from[0] == p_to[0] - 1 and p_from[1] == p_to[1] - 2
        move_downleft = p_from[0] == p_to[0] + 1 and p_from[1] == p_to[1] - 2
        move_leftdown = p_from[0] == p_to[0] + 2 and p_from[1] == p_to[1] - 1
        move_leftup = p_from[0] == p_to[0] + 2 and p_from[1] == p_to[1] + 1

        # Is the Horse trying to move a valid distance?
        if move_upright or move_upleft or move_rightup or move_rightdown \
                or move_downright or move_downleft or move_leftdown or move_leftup:

            # Does the Horse collide with anything in it's path?
            if self.collision_check(move_upright, move_upleft, move_rightup, move_rightdown,
                                    move_downright, move_downleft, move_leftdown, move_leftup,  p_from):

                # Is there a piece where the Horse is moving?
                if attacking != None:

                    # Is it on the Horse's team?
                    if attacking.get_team() == team:
                        return False

                    # Is the enemy General in check?
                    if attacking.get_type() == "General":
                        self._game.set_check_flag(attacking.get_team())
                        self._game.set_check_test_flag()

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            # If path is blocked.
            else:
                return False

        # If trying to move to invalid location.
        else:
            return False

    def collision_check(self, upright, upleft, rightup, rightdown, downright, downleft,
                        leftdown, leftup, p_from):
        """
        Helper function that checks if collision has occurred. Returns False if collision detected.
        :param upright: True / False
        :param upleft: True / False
        :param rightup: True / False
        :param rightdown: True / False
        :param downright: True / False
        :param downleft: True / False
        :param leftdown: True / False
        :param leftup: True / False
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :return: True if move is valid. False otherwise.
        """
        if upright or upleft:
            coord = (p_from[0], p_from[1] - 1)
            if self._game.check_square(coord) != None:
                return False
            return True
        if rightup or rightdown:
            coord = (p_from[0] + 1, p_from[1])
            if self._game.check_square(coord) != None:
                return False
            return True
        if downright or downleft:
            coord = (p_from[0], p_from[1] + 1)
            if self._game.check_square(coord) != None:
                return False
            return True
        if leftdown or leftup:
            coord = (p_from[0] - 1, p_from[1])
            if self._game.check_square(coord) != None:
                return False
            return True


class Guard(Piece):
    """
    Child class for Guards in the game. Has move_check method used to check collision and valid movements.
    :param game: Game class creating this.
    :param team: Team color assigned. Valid inputs: "BLUE" or "RED"
    :param coord: Coordinate where piece is to be initially placed. Uses (x, y) tuples.
    :param name: Name of piece as it will appear in the piece database. Example: Red Guard #1 = rGu1
    """
    def __init__(self, game, team, coord, name, type):
        super().__init__(game, team, coord, name, type)


    def move_check(self, p_from, p_to):
        """
        Checks piece specific move conditions.
        :param p_from: (x, y) coordinate from board where piece is moving from.
        :param p_to: (x, y) coordinate from board where piece is moving to.
        :return: True if move is valid. False otherwise.
        """
        attacking = self._game.check_square(p_to)
        team = self.get_team()

        # Is the Guard staying still?
        if attacking == self:
            self._possible_targets.append(p_to)
            self._game.set_total_targets(p_to, team)
            return True

        # Defining some one square Guard movements
        move_up = p_from[1] - 1 == p_to[1] and p_from[0] == p_to[0]
        move_down = p_from[1] + 1 == p_to[1] and p_from[0] == p_to[0]
        move_left = p_from[0] - 1 == p_to[0] and p_from[1] == p_to[1]
        move_right = p_from[0] + 1 == p_to[0] and p_from[1] == p_to[1]
        move_upleft = p_from[0] - 1 == p_to[0] and p_from[1] - 1 == p_to[1]
        move_upright = p_from[0] + 1 == p_to[0] and p_from[1] - 1 == p_to[1]
        move_downleft = p_from[0] - 1 == p_to[0] and p_from[1] + 1 == p_to[1]
        move_downright = p_from[0] + 1 == p_to[0] and p_from[1] + 1 == p_to[1]
        move_diagonal = move_upleft or move_upright or move_downleft or move_downright

        # Blue Guards
        if team == "BLUE":

            # Setting up special palace diagonal move conditions
            diag_squares = [(3, 7), (3, 9), (4, 8), (5, 7), (5, 9)]
            diagonal_check = p_from in diag_squares and move_diagonal

            # Is the Guard trying to leave the palace?
            if p_to[0] > 5 or p_to[0] < 3 or p_to == (3, 6) or p_to == (4, 6) or p_to == (5, 6):
                return False

            # Is the Guard trying to move a valid distance?
            if move_up or move_down or move_left or move_right or diagonal_check:

                # Is there a piece where the Guard is moving?
                if attacking != None:

                    # Is it on the Guard's team?
                    if attacking.get_team() == "BLUE":
                        return False

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False

        # Red Guard
        if team == "RED":

            # Setting up special palace diagonal move conditions
            diag_squares = [(3, 0), (3, 2), (4, 1), (5, 0), (5, 2)]
            diagonal_check = p_from in diag_squares and move_diagonal

            # Is the Guard trying to leave the palace?
            if p_to[0] > 5 or p_to[0] < 3 or p_to == (3, 3) or p_to == (4, 3) or p_to == (5, 3):
                return False

            # Is the Guard trying to move a valid distance?
            if move_up or move_down or move_left or move_right or diagonal_check:

                # Is there a piece where the Guard is moving?
                if attacking != None:

                    # Is it on the Guard's team?
                    if attacking.get_team() == "RED":
                        return False

                    self._possible_targets.append(p_to)
                    self._game.set_total_targets(p_to, team)
                    return True

                self._possible_targets.append(p_to)
                self._game.set_total_targets(p_to, team)
                return True

            else:
                return False


def main():
    """
    Main function to run if file is called directly.
    :return: None
    """

if __name__ == '__main__':
    main()
