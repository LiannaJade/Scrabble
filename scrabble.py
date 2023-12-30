import json
import random
import os

# TODO
# game setup
# player handling
# game loop
# game ending


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


class Host:
    def __init__(self, host_player, lang="en"):
        self._started = False
        self.players = []
        self.add_player(host_player)
        self.player_count = None
        # gets tiles
        self.tiles = TilePool(lang)
        # gets words
        self.words = []
        if os.path.exists("Dictionaries/"+lang+".txt"):
            file = open("Dictionaries/"+lang+".txt", "r")
            self.words = file.readlines()
            file.close()
        for i in range(len(self.words)):
            self.words[i] = self.words[i].replace("\n", "")
        #

    def add_player(self, player):
        # add a player to the game
        # returns 1 if successful, else 0
        # this may need redoing when real multiplayer is made
        if not self._started:
            player_host = PlayerHost(player)
            self.players.append(player_host)
            return True
        else:
            return False

    def start_game(self):
        # starting
        self._started = True
        self.player_count = len(self.players)
        # draws tiles to decide order
        for i, j in zip(range(self.player_count), self.tiles.draw(self.player_count)):
            self.players[i].tiles.append(j)
        self.players.sort(key=lambda n: n.tiles[0])
        for i in range(self.player_count):
            self.players[i].order = i
            self.players[i].send("order {0}, tile: {1}".format(i, self.players[i].tiles.pop(0))) # change to actual command
        # takes 7 tiles per player
        for player in self.players:
            player.tiles = self.tiles.take(7)
            player.send("tiles: {0}".format(player.tiles))
        # start game loop


class PlayerHost:
    # class used by the host to handle players
    def __init__(self, player):
        self.player = player
        self.tiles = []
        self.order = None

    def send(self, command):
        # update to actual code
        self.player.receive(command)


class PlayerClient:
    def __init__(self, name):
        self.name = name

    def receive(self, command):
        # update to actual code
        print(self.name, command)


if __name__ == "__main__":
    player1 = PlayerClient("player 1")
    host = Host(player1)
    player2 = PlayerClient("player 2")
    host.add_player(player2)
    host.start_game()
