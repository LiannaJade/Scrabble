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
                    self.nodes[current_node][char] = (len(self.nodes), index == len(string)-1)
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
            num = random.randint(0, len(self.tiles)-1)
            rtn.append(self.tiles.pop(num))
        return rtn

    def draw(self, count):
        # returns a list of random tiles from the pool without taking them
        rtn = set()
        while len(rtn) < count:
            rtn.add(random.randint(0, len(self.tiles)-1))
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
        # gets tiles
        self.tiles = TilePool(lang)
        # gets words (possibly change to a GADDAG or DAWG)
        self.words = []
        if os.path.exists("Dictionaries/"+lang+".txt"):
            file = open("Dictionaries/"+lang+".txt", "r")
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
            self.players[i].send("order: {0}; order_tile: {1}".format(i, self.players[i].tiles.pop(0)))  # change to actual command
        # takes 7 tiles per player
        for player in self.players:
            player.tiles = self.tiles.take(7)
            player.send("tiles: {0}".format(player.tiles))  # change to actual command
        # start game loop
        self.start()

    def run(self):
        self.game_loop()

    def game_loop(self):
        for player_index in range(self.player_count):
            # tells all players the current player
            for player in self.players:
                player.send("current_player: {0}".format(player_index))
            # waiting for response from player
            waiting = True
            while waiting:
                if len(self.inputs) > 0:
                    print("woooooo working {0}".format(self.inputs.pop(0)))
                time.sleep(1)


class PlayerHost:
    # class used by the host to handle players
    def __init__(self, player, host):
        self.player = player
        self.host = host
        self.tiles = []
        self.order = None

    def send(self, command):
        # update to actual code
        self.player.receive(command)

    def receive(self, string):
        self.host.inputs.append(string)


class PlayerClient:
    def __init__(self, name, update=lambda: None):
        self.name = name
        self.order = None
        self.board = None
        self.tiles = None
        self.player_count = None
        self.player_turn = None
        self.update = update

        self.host = None  # temp variable until implementation

    def receive(self, command):
        # update to actual code
        try:
            commands = command.split(";")
            for command in commands:
                opcode, operand = command.split(":")
                if opcode == "order":
                    self.order = int(operand)
                elif opcode == "order_tile":
                    print(operand)
                elif opcode == "tiles":
                    print(operand)
                    self.tiles = operand.replace("'", "").replace("[", "").replace("]", "").split(", ")
        except:
            pass
        self.update()
        print(self.name, command)

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
