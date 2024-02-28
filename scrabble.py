import json
import random
import os
import threading
import time


class DAWG:
    """the basic idea of a DAWG, made to be more "python-friendly"
    the saved structure is still stored as an automata"""

    def __init__(self, strings):
        strings.sort()
        self.nodes = [{}]
        for string in strings:
            current_node = 0
            for char, index in zip(string, range(len(string))):
                if char in self.nodes[current_node].keys():
                    current_node = self.nodes[current_node][char][0]
                else:
                    self.nodes[current_node][char] = (len(self.nodes), index == len(string) - 1)
                    current_node = len(self.nodes)
                    self.nodes.append({})

    def contains(self, string):
        current_node = 0
        for char, index in zip(string, range(len(string))):
            if char in self.nodes[current_node].keys():
                if index == len(string) - 1 and self.nodes[current_node][char][1]:
                    return True
                else:
                    current_node = self.nodes[current_node][char][0]
            else:
                return False

    def find(self, string, node=0):
        string = string.upper()
        if len(string) == 1:
            if string == "*":
                return [i.lower() for i in filter(lambda x: self.nodes[node][x][1], self.nodes[node].keys())]
            elif string in self.nodes[node].keys() and self.nodes[node][string][1]:
                return [string]
            else:
                return []
        else:
            if string[0] == "*":
                letters = [chr(i) for i in range(ord("A"), ord("Z")+1)]  # modify this for use with other languages
            else:
                letters = [string[0]]
            rtn = []
            for letter in letters:
                if letter in self.nodes[node].keys():
                    if string[0] == "*":
                        rtn += [letter.lower() + i for i in self.find(string[1:], node=self.nodes[node][letter][0])]
                    else:
                        rtn += [letter + i for i in self.find(string[1:], node=self.nodes[node][letter][0])]

            return rtn


class TilePool:
    def __init__(self, lang):
        file = open("tiles.json", "r")
        tiles = json.loads("".join(file.readlines()))[lang]
        file.close()
        self.tiles = []
        for i in tiles.items():
            for j in range(i[1][0]):
                self.tiles.append(i[0])
        self.values = {}
        for i in tiles.items():
            self.values[i[0]] = i[1][1]

    def take(self, count):
        # takes tiles from tile pool ///(what if count > tile pool size)
        rtn = []
        if count > self.count:
            count = self.count
        for i in range(count):
            num = random.randint(0, len(self.tiles) - 1)
            rtn.append(self.tiles.pop(num))
        return rtn

    def draw(self, count):
        # returns a list of random tiles from the pool without taking them
        rtn = set()
        while len(rtn) < count:
            rtn.add(random.randint(0, len(self.tiles) - 1))
        rtn = list(rtn)
        for i in range(len(rtn)):
            rtn[i] = self.tiles[rtn[i]]
        random.shuffle(rtn)
        return rtn

    def swap(self, tiles):
        # swaps a set of tiles
        count = len(tiles)
        self.tiles += tiles
        tiles = self.take(count)
        return tiles

    def get_value(self, word):
        value = 0
        for letter in word:
            if letter in self.values.keys():
                value += self.values[letter]
        return value

    @property
    def count(self):
        return len(self.tiles)


class Host(threading.Thread):
    def __init__(self, host_player, lang="en"):
        super().__init__()
        self.inputs = []
        self._game_started = False
        self.players = []
        self.add_player(host_player)
        self.player_count = None
        self.board = [[" " for j in range(15)] for i in range(15)]
        self.current_player = 0
        self.bonus_tiles = {"DW": [(1, 1), (2, 2), (3, 3), (4, 4),
                                   (13, 1), (12, 2), (11, 3), (10, 4),
                                   (1, 13), (2, 12), (3, 11), (4, 10),
                                   (13, 13), (12, 12), (11, 11), (10, 10)],
                            "DL": [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14),
                                   (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11),
                                   (8, 2), (8, 6), (8, 8), (8, 12),
                                   (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)],
                            "TW": [(0, 0), (7, 0), (14, 0), (14, 7),
                                   (14, 14), (7, 14), (0, 14), (0, 7)],
                            "TL": [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13),
                                   (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)]}
        # gets tiles
        self.tiles = TilePool(lang)
        # gets words (possibly change to a GADDAG or DAWG)
        self.words = []
        if os.path.exists("Dictionaries/" + lang + ".txt"):
            file = open("Dictionaries/" + lang + ".txt", "r")
            self.words = file.readlines()
            file.close()
        for i in range(len(self.words)):
            self.words[i] = self.words[i].replace("\n", "")
        self.words = DAWG(self.words)

    def add_player(self, player):
        # add a player to the game
        # returns 1 if successful, else 0
        # this may need redoing when real multiplayer is made
        if not self._game_started:
            player_host = PlayerHost(player, self)
            self.players.append(player_host)
            player.host = player_host  # update this temp thing
            return True
        else:
            return False

    def start_game(self):
        # starting
        self._game_started = True
        self.player_count = len(self.players)
        # draws tiles to decide order
        for i, j in zip(range(self.player_count), self.tiles.draw(self.player_count)):
            self.players[i].tiles.append(j)
        self.players.sort(key=lambda n: n.tiles[0])
        for i in range(self.player_count):
            self.players[i].order = i
            self.players[i].send(
                "order: {0}; order_tile: {1}; player_count: {2}".format(i, self.players[i].tiles.pop(0),
                                                                        self.player_count))
        # takes 7 tiles per player
        for player in self.players:
            player.tiles = self.tiles.take(7)
            player.send("tiles: {0}; current_player: {1}".format("".join(player.tiles), self.current_player))  # change to actual command
        # start game loop
        self.start()

    def run(self):
        self.game_loop()

    def game_loop(self):
        # waiting for response from player
        playing = True
        while playing:
            if len(self.inputs) > 0:
                command = self.inputs.pop(0)
                sender, command = command
                if command[:7] == "place: ":
                    # splits incoming command
                    board, rack = command[7:].split("/")
                    board = list(board)
                    board = [board[i * 15:i * 15 + 15] for i in range(15)]
                    rack = list(rack)

                    # plays turn if valid
                    if self.is_valid_move(board):
                        illegal_words = self.find_illegal_words(board)
                        if len(illegal_words) != 0:
                            sender.send("error1: illegal word")
                            continue
                        sender.score += self.calculate_score(board, rack)
                        sender.tiles = list(rack) + self.tiles.take(7 - len(rack))
                        sender.send("tiles: {0}".format("".join(sender.tiles)))
                        self.current_player = (self.current_player + 1) % self.player_count
                        self.set_board(board)
                        for player in self.players:
                            player.send("board: {0}".format("".join(["".join(i) for i in self.board])))
                            player.send("score: {0}/{1}".format(sender.order, sender.score))
                            player.send("current_player: {0}".format(self.current_player))
                    else:
                        sender.send("error1: oh no")

                print("completed {0}".format(command))
            time.sleep(1)

    @staticmethod
    def find_words(board):
        words, roots = [], []
        for x in range(15):
            word, root = "", None
            for y in range(15):
                # scans over each letter of a row
                if board[x][y] == " ":
                    # if current space is blank add word if valid
                    if len(word) >= 2:
                        words.append(word)
                        roots.append(root)
                    word, root = "", None
                else:
                    if root is None:
                        root = (x, y, True)
                    word += board[x][y]
            if len(word) >= 2:
                words.append(word)
                roots.append(root)
        for y in range(15):
            word, root = "", None
            for x in range(15):
                # scans over each letter of a row
                if board[x][y] == " ":
                    # if current space is blank add word if valid
                    if len(word) >= 2:
                        words.append(word)
                        roots.append(root)
                    word, root = "", None
                else:
                    if root is None:
                        root = (x, y, False)
                    word += board[x][y]
            if len(word) >= 2:
                words.append(word)
                roots.append(root)

        return words, roots

    def is_valid_move(self, board):
        # gets the difference between the two boards
        diff = [[" " for x in range(15)] for y in range(15)]
        new_letters_at = []
        for x in range(15):
            for y in range(15):
                if self.board[x][y] != board[x][y]:
                    diff[x][y] = board[x][y]
                    new_letters_at.append((x, y))
        # validity check
        xs, ys = list(set([i[0] for i in new_letters_at])), list(set([i[1] for i in new_letters_at]))
        xs.sort()
        ys.sort()
        if len(xs) != 1 and len(ys) != 1:
            # if all new tiles don't fall on to the same line then false
            return False
        # checks that new tiles are consecutive
        elif len(xs) == 1:
            counter = ys[0] + 1
            while counter < ys[-1]:
                if counter in ys or board[xs[0]][counter] != " ":
                    counter += 1
                else:
                    return False
        elif len(ys) == 1:
            print(xs, ys)
            counter = xs[0] + 1
            while counter < xs[-1]:
                if counter in xs or board[counter][ys[0]] != " ":
                    counter += 1
                else:
                    return False
        # if there is a tile on the center tile then legal always
        if (7, 7) in new_letters_at:
            if len(new_letters_at) > 1:
                return True
        # checks new tiles touch at least one old tile
        for tile in new_letters_at:
            if tile[0] > 0 and self.board[tile[0] - 1][tile[1]] != " ":
                return True
            if tile[0] < 14 and self.board[tile[0] + 1][tile[1]] != " ":
                return True
            if tile[1] > 0 and self.board[tile[0]][tile[1] - 1] != " ":
                return True
            if tile[1] < 14 and self.board[tile[0]][tile[1] + 1] != " ":
                return True
        return False

    def calculate_score(self, board, rack):
        # needs finishing
        words, roots = self.find_words(board)
        old_words, old_roots = self.find_words(self.board)
        new_words, new_roots = [], []
        for word, root in zip(words, roots):
            if word not in old_words:
                new_words.append(word)
                new_roots.append(root)
            else:
                index = old_words.index(word)
                if old_roots[index] != root:
                    new_words.append(word)
                    new_roots.append(root)
        print(new_words, new_roots)
        value = 0
        # gets the score of each word modified
        for word, root in zip(new_words, new_roots):
            # finds the word multiplier
            multiplier = 1
            bonus_letters = ""
            for i in range(len(word)):
                # find the current tile
                if root[2]:
                    tile = (root[0], root[1] + i)
                else:
                    tile = (root[0] + i, root[1])
                # applies any bonuses the tile may have
                if self.board[tile[1]][tile[0]] == " ":
                    if tile in self.bonus_tiles["DW"]:
                        multiplier *= 2
                    elif tile in self.bonus_tiles["TW"]:
                        multiplier *= 3
                    elif tile in self.bonus_tiles["DL"]:
                        bonus_letters += word[i]
                    elif tile in self.bonus_tiles["TL"]:
                        bonus_letters += word[i] * 2
            value += self.tiles.get_value(word + bonus_letters) * multiplier
            # 50 point bonus for using all available tiles
            if len(rack) == 0:
                value += 50
        return value

    def set_board(self, board):
        has_blanks = True if True in [True if "*" in i else False for i in board] else False
        if has_blanks:
            words, roots = self.find_words(board)
            for word, root in zip(words, roots):
                if "*" in word:
                    new_word = random.choice(self.words.find(word))
                    tile = list(root)
                    for old_letter, new_letter in zip(word, new_word):
                        if old_letter != new_letter:
                            print(tile, new_letter, board)
                            board[tile[0]][tile[1]] = new_letter
                            print(board)
                        if tile[2]:
                            tile[1] += 1
                        else:
                            tile[0] += 1

        self.board = board

    def find_illegal_words(self, board):
        illegal_words = []
        words, roots = self.find_words(board)
        for word in words:
            if len(self.words.find(word)) == 0:
                illegal_words.append(word)
        return illegal_words


class PlayerHost:
    # class used by the host to handle players
    def __init__(self, player, host):
        self.player = player
        self.host = host
        self.tiles = []
        self.order = None
        self.score = 0

    def send(self, command):
        # update to actual code
        self.player.receive(command)

    def receive(self, string):
        self.host.inputs.append([self, string])
        print("server received: {0}".format(string))


class PlayerClient:
    def __init__(self, name, update=lambda types: None):
        self.name = name
        self.order = None
        self.board = None
        self.tiles = None
        self.player_count = None
        self.current_player = 0
        self.update = update
        self.scores = [0] * 4

        self.host = None  # temp variable until implementation

    def receive(self, command):
        # update to actual code
        updated = []
        print(command)
        try:
            commands = command.split("; ")
            for command in commands:
                opcode, operand = command.split(": ")
                if opcode == "order":
                    self.order = int(operand)
                elif opcode == "order_tile":
                    pass
                elif opcode == "tiles":
                    self.tiles = list(operand)
                elif opcode == "score":
                    player, score = operand.split("/")
                    player, score = int(player), int(score)
                    self.scores[player] = score
                    print("scores now {0}".format(self.scores))
                elif opcode == "board":
                    self.board = [[operand[j * 15 + i] for i in range(15)] for j in range(15)]
                    updated.append("board")
                elif opcode == "player_count":
                    self.player_count = int(operand)
                elif opcode == "current_player":
                    self.current_player = int(operand)
                updated.append(opcode)
        except:
            raise
        if self.update is not None:
            self.update(updated)

    def send(self, string):
        # update to actual code
        self.host.receive(string)


class BotV1(PlayerClient):
    """This is the first BOt based on a paper by Andrew W. Appel AND Guy J. Jacobson in May 1988
    it uses a DAWG structure in it's methodology and finds The highest value next move"""
    def __init__(self, dictionary=None, update=None):
        super().__init__(self, "Bot")
        self.update = self.do_turn
        self.secondary_update = update
        self.cross_checks = {}
        self.letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        self.board = [[" " for x in range(15)] for y in range(15)]
        self.potential_anchors = set([])
        # creates new english dictionary if none is passed in
        if dictionary is None:
            lang = "en"
            if os.path.exists("Dictionaries/" + lang + ".txt"):
                file = open("Dictionaries/" + lang + ".txt", "r")
                words = file.readlines()
                file.close()
            for i in range(len(words)):
                words[i] = words[i].replace("\n", "")
            self.DAWG = DAWG(words)
        else:
            self.DAWG = dictionary

    def do_turn(self, types):
        if "current_player" in types and self.current_player == self.order:
            move = self.find_move()
            print(move, "aaaaaaaaaaaaaaaaaaaaaah")
            if move is not None:
                board = "".join(["".join(i) for i in self.board])  # converts board into a string of all the letters
                rack = "".join(self.tiles)
                self.send("place: {0}/{1}".format(board, rack))
            else:
                pass  # swap tile code
        if self.secondary_update is not None:
            self.secondary_update(types)
        # send move to host

    def find_move(self):
        # compute cross checks (change so it only computes places with changes)
        if self.board is not None:
            # find anchors
            self.potential_anchors = set([])
            for i in range(15):
                for j in range(15):
                    if self.board[i][j] == " ":
                        if i > 0 and self.board[i - 1][j] != " ":
                            self.potential_anchors.add((j, i))
                        elif i < 14 and self.board[i + 1][j] != " ":
                            self.potential_anchors.add((j, i))
                        elif j > 0 and self.board[i][j - 1] != " ":
                            self.potential_anchors.add((j, i))
                        elif j < 14 and self.board[i][j + 1] != " ":
                            self.potential_anchors.add((j, i))
            # does cross checks (cross checks only need to happen on potential anchors)
            self.cross_checks = {}
            for i in self.potential_anchors:
                # gets column and row of anchor
                line_x = list(self.board[i[1]])
                line_x[i[0]] = "*"
                line_y = [line[i[0]] for line in self.board]
                line_y[i[1]] = "*"
                # removes spaces that don't connect to anchor
                x = i[0] - 1
                while x >= 0:
                    if line_x[x] == " ":
                        line_x = line_x[x + 1:]
                        x = -1
                    else:
                        x -= 1
                x = 1
                while x < len(line_x):
                    if line_x[x] == " ":
                        line_x = line_x[:x]
                        x = 15
                    else:
                        x += 1
                y = i[1] - 1
                while y >= 0:
                    if line_y[y] == " ":
                        line_y = line_y[y + 1:]
                        y = -1
                    else:
                        y -= 1
                y = 1
                while y < len(line_y):
                    if line_y[y] == " ":
                        line_y = line_y[:y]
                        y = 15
                    else:
                        y += 1
                # converts list into string with all upper case
                line_x, line_y = "".join(line_x).upper(), "".join(line_y).upper()
                # finds the letters that the anchor could be based on the row
                if line_x != "*":
                    index = line_x.index("*")
                    words = self.DAWG.find(line_x)
                    letters = [word[index].upper() for word in words]
                    self.cross_checks[i] = set(letters)
                # finds the letters teh anchor could be based on the column and does the intersection with found letters
                if line_y != "*":
                    index = line_y.index("*")
                    words = self.DAWG.find(line_y)
                    letters = [word[index].upper() for word in words]
                    if i in self.cross_checks.keys():
                        self.cross_checks[i] = self.cross_checks[i].intersection(letters)
                    else:
                        self.cross_checks[i] = set(letters)
        # find left side


        # temp version
        if len(self.potential_anchors) == 0:
            self.board[7][7] = self.tiles[0]
            self.tiles = self.tiles[1:]
            return self.find_move()
        for anchor in self.potential_anchors:
            playable = self.cross_checks[anchor].intersection(self.tiles)
            if len(playable) != 0:
                tile = random.choice(list(playable))
                self.board[anchor[1]][anchor[0]] = tile
                self.tiles.remove(tile)
                return self.board
        return None


if __name__ == "__main__":
    player1 = PlayerClient("player 1")
    host = Host(player1)
    player2 = PlayerClient("player 2")
    host.add_player(player2)
    host.start_game()

    time.sleep(2)

    while True:
        exec(input("->"))
