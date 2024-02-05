import json
import random
import os
import threading
import time


# TODO
# game setup
# player handling
# game loop
# game ending


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

    def get_value(self, tile):
        return self.values[tile]

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
            player.send("tiles: {0}".format("".join(player.tiles)))  # change to actual command
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
                        sender.score += self.calculate_score(board)
                        sender.tiles = list(rack) + self.tiles.take(7 - len(rack))
                        sender.send("tiles: {0}".format("".join(sender.tiles)))
                        self.current_player = (self.current_player + 1) % self.player_count
                        self.board = board
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
            counter = xs[0] + 1
            while counter < xs[-1]:
                if counter in xs or board[ys[0]][counter] != " ":
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

    def calculate_score(self, board):
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
        # add scoring
        return 1


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


if __name__ == "__main__":
    player1 = PlayerClient("player 1")
    host = Host(player1)
    player2 = PlayerClient("player 2")
    host.add_player(player2)
    host.start_game()

    time.sleep(2)

    while True:
        exec(input("->"))
