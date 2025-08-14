import tkinter as tk
import tkinter.ttk as ttk
import json
import scrabble
import os


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scrabble")
        self.app_config = {}
        self.assets = {}
        self.create_theme()
        self.open_configs()
        self.open_assets()
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=1)
        # creates all the different pages for the menu
        self.frames = {}
        for frame in (MainMenu, SettingsPage, GameSetupPage):
            self.frames[frame] = frame(self.container, self)
        self.set_frame(MainMenu)
        self.mainloop()

    def start_game(self):
        self.frames[GameCanvas] = GameCanvas(self.container, self)
        self.set_frame(GameCanvas)

    def set_frame(self, frame):
        for i in self.frames.values():
            i.place_forget()
        self.frames[frame].place(relx=0.5, rely=0, anchor="n")
        self.frames[frame].on_switch()

    def open_configs(self):
        file = open("config.json", "r")
        self.app_config = json.loads(file.readlines()[0])
        file.close()
        print("configs found", self.app_config)
        # apply configs
        self.set_full_screen(self.app_config["full screen"])

    def open_assets(self):
        for image in os.scandir("assets"):
            if image.name[-4:] == ".png":
                self.assets[image.name[:-4]] = tk.PhotoImage(file=image.path)

    def set_full_screen(self, state):
        if state is None:
            state = self.app_config["full screen"]
        if state:
            self.overrideredirect(True)
            self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        else:
            self.overrideredirect(False)
            self.geometry("360x420+{0}+{1}".format(int(self.winfo_screenwidth() / 2 - 180),
                                                   int(self.winfo_screenheight() / 2 - 210)))

    @staticmethod
    def create_theme():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("title.TLabel", font=("Times", 36, "bold"))


class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        title_label = ttk.Label(self, text="Scrabble", style="title.TLabel")
        title_label.grid(row=0, column=1)
        start_game_button = ttk.Button(self, text="Start Game",
                                       command=lambda: controller.set_frame(GameSetupPage))
        start_game_button.grid(row=1, column=1)
        settings_button = ttk.Button(self, text="Settings",
                                     command=lambda: controller.set_frame(SettingsPage))
        settings_button.grid(row=2, column=1)
        quit_button = ttk.Button(self, text="Quit",
                                 command=controller.destroy)
        quit_button.grid(row=3, column=1)

    def on_switch(self):
        pass


class SettingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        settings_label = ttk.Label(self, text="Settings",
                                   style="title.TLabel")
        settings_label.grid(row=0, column=1, columnspan=2)
        self.fs_var = tk.IntVar(self, value=controller.app_config["full screen"])
        full_screen_option = ttk.Checkbutton(self, text="Full screen", variable=self.fs_var)
        full_screen_option.grid(row=1, column=1)
        menu_button = ttk.Button(self, text="Back to Menu",
                                 command=lambda: controller.set_frame(MainMenu))
        menu_button.grid(row=10, column=1)
        apply_button = ttk.Button(self, text="Apply",
                                  command=self.apply)
        apply_button.grid(row=10, column=2)

    def apply(self):
        # If full screen option has changed, then run method to change window size
        if self.fs_var.get() != self.get_option("full screen"):
            self.set_option("full screen", self.fs_var.get())
            self.controller.set_full_screen(self.get_option("full screen"))
        # Saves configs to the file
        file = open("config.json", "w")
        file.write(json.dumps(self.controller.app_config))
        file.close()

    def set_option(self, option, value):
        self.controller.app_config[option] = value

    def get_option(self, option):
        return self.controller.app_config[option]

    def on_switch(self):
        self.fs_var.set(self.get_option("full screen"))


class GameSetupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.observer_mode = tk.IntVar()
        setup_label = ttk.Label(self, text="Game Setup", style="title.TLabel")
        setup_label.grid(row=0, column=1, columnspan=2)
        observer_tick_box = ttk.Checkbutton(self, text="Observer Mode", variable=self.observer_mode)
        observer_tick_box.grid(row=1, column=1, columnspan=2)
        ai_count_label = ttk.Label(self, text="Number of AI:")
        ai_count_label.grid(row=2, column=1, sticky="E")
        ai_count_entry = ttk.Spinbox(self, from_=0, to=3, width=10)
        ai_count_entry.set(1)
        ai_count_entry.grid(row=2, column=2, sticky="W")
        self.ai_count = ai_count_entry
        back_to_menu_button = ttk.Button(self, text="Back   to Menu",
                                         command=lambda: controller.set_frame(MainMenu))
        back_to_menu_button.grid(row=10, column=1)
        start_game_button = ttk.Button(self, text="Start Game",
                                       command=self.start_game)
        start_game_button.grid(row=10, column=2)

    def start_game(self):
        self.controller.start_game()

    def on_switch(self):
        pass


class GameCanvas(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.player = None
        self.canvas = tk.Canvas(self, width=640, height=360)
        self.canvas.pack()
        # key binds
        self.canvas.bind_all("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind_all("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind_all("<Motion>", self.on_mouse_motion)
        # creates frame images
        self.canvas.create_image(320, 0, anchor="n", image=self.controller.assets["board"], tag="board")
        self.canvas.create_image(320, 360, anchor="s", image=self.controller.assets["rack"], tag="rack")
        self.canvas.create_text(20, 300, anchor="w", text="End Turn", tags=["button", "end_turn"])
        self.canvas.create_text(170, 320, anchor="w", tag="error_line", font=("Helvetica", 20, "bold"))
        self.canvas.create_text(20, 20, anchor="w", tag="tile_pool")
        self.canvas.create_rectangle(20, 40, 100, 120, tag="tile_bag")
        self.canvas.create_text(20, 130, anchor="w", text="Swap Tiles", tags=["button", "swap_tiles"])
        self.canvas.create_text(480, 20, anchor="w", tags=["button", "exit_game"], font=("Helvetica", 16, "bold"),
                                text="Exit to Menu")
        self.canvas.create_text(20, 320, anchor="w", text="Pass", tags=["button", "pass"])

    def set_tiles(self, tiles):
        # removes tiles currently in the rack
        tile_textures = self.canvas.find_withtag("tile")
        for tile in tile_textures:
            tags = list(self.canvas.gettags(tile))
            tags.remove("tile")
            loc = list(filter(lambda x: False if x[:5] == "text_" else True, tags))[0]
            if loc[-1] == "R":
                text = int(list(filter(lambda x: True if x[:5] == "text_" else False, tags))[0][5:])
                self.canvas.delete(text)
                self.canvas.delete(tile)
        # replaces all rack tiles
        bbox = self.canvas.bbox("rack")
        for i, k in zip(range(7), tiles):
            j = self.canvas.create_text(bbox[0] + 15 + i * 20, bbox[1] + 8, anchor="c", fill="red",
                                        text=k, tags=["tile_text", (i, "R")], font=("Courier", 10))
            self.canvas.create_image(bbox[0] + 5 + i * 20, bbox[1], anchor="nw",
                                     image=self.controller.assets["tile"], tags=["tile", (i, "R"), "text_" + str(j)])
            self.canvas.tag_raise(j)

    def set_board(self):
        # removes all current board tiles
        tile_textures = self.canvas.find_withtag("tile")
        for tile in tile_textures:
            tags = list(self.canvas.gettags(tile))
            tags.remove("tile")
            loc = list(filter(lambda x: False if x[:5] == "text_" else True, tags))[0]
            if loc[-1] != "R":
                text = int(list(filter(lambda x: True if x[:5] == "text_" else False, tags))[0][5:])
                self.canvas.delete(text)
                self.canvas.delete(tile)

        # replaces all board tiles
        bbox = self.canvas.bbox("board")
        for x in range(15):
            for y in range(15):
                if self.player.board[y][x] != " ":
                    x1 = bbox[0] + x * (bbox[2] - bbox[0]) / 15
                    y1 = bbox[1] + y * (bbox[3] - bbox[1]) / 15
                    num = self.canvas.create_text(x1 + 10, y1 + 8, anchor="c", font=("Courier", 10),
                                                  text=self.player.board[y][x], tags=["tile_text", (x, y)])
                    self.canvas.create_image(x1, y1, anchor="nw",
                                             image=self.controller.assets["tile"],
                                             tags=["tile", (x, y), "text_" + str(num), "played"])
                    self.canvas.tag_raise(num)

    def set_error_line(self, error=" "):
        error_line = self.canvas.find_withtag("error_line")
        for i in error_line:
            self.canvas.itemconfigure(i, text=error)

    def set_tile_pool(self):
        tile_pool = self.canvas.find_withtag("tile_pool")
        for i in tile_pool:
            self.canvas.itemconfigure(i, text="tile pool {0}".format(self.player.tile_pool))

    def create_player_list(self):
        for i in range(self.player.player_count):
            if i == self.player.order:
                name = "you {0}".format(self.player.scores[i])
            else:
                name = "player{0} {1}".format(i, self.player.scores[i])
            if i == self.player.current_player:
                name = "- " + name
            self.canvas.create_text(20, 240+i*15, anchor="w", text=name, tags=["player_list", i],
                                    font=("Helvetica", 10))

    def update_player_list(self):
        player_list = self.canvas.find_withtag("player_list")
        for player in player_list:
            num = int(list(filter(lambda x: x.isnumeric(), self.canvas.gettags(player)))[0])
            if num == self.player.order:
                name = "you {0}".format(self.player.scores[num])
            else:
                name = "player{0} {1}".format(num, self.player.scores[num])
            if num == self.player.current_player:
                name = "- " + name
            self.canvas.itemconfigure(player, text=name)

    def find_anchor(self, x, y):
        """checks if (x, y) is within the range of an anchor
        and returns which anchor is valid"""
        for image in self.canvas.find_overlapping(x, y, x, y):
            # check game board
            if "board" in self.canvas.gettags(image):
                bbox = self.canvas.bbox("board")
                x, y = int((x - bbox[0]) / (bbox[2] - bbox[0]) * 15), int((y - bbox[1]) / (bbox[3] - bbox[1]) * 15)
                if x == 15:
                    x = 14
                if y == 15:
                    y = 14
                # x, y now shows the tile with 0, 0 being the top left
                return x, y
            # check rack
            elif "rack" in self.canvas.gettags(image):
                bbox = self.canvas.bbox("rack")
                x, y = (x - bbox[0] - 5) / (bbox[2] - bbox[0] - 10) * 7, "R"
                if x < 0:
                    x = 0
                elif x >= 7:
                    x = 6
                # returns n, "R" where n is the order of the rack space and "R" inidicates it is on the rack
                return int(x), y
            else:
                return None, None

    def get_board(self):
        # finds all tiles
        tiles = self.canvas.find_withtag("tile_text")
        # gets tile tags
        letter = [self.canvas.itemcget(i, "text") for i in tiles]
        tiles = [self.canvas.gettags(i) for i in tiles]
        for i in range(len(tiles)):
            for j in tiles[i]:
                if j not in ["tile_text", "not played", "played"]:
                    tiles[i] = [j, letter[i]]
        board = [[" " for j in range(15)] for i in range(15)]
        rack = []
        for tile in tiles:
            # converts the tile location to ints
            loc = tile[0].split(" ")
            if loc[1] == "R":
                loc[0] = int(loc[0])
            else:
                loc[0], loc[1] = int(loc[0]), int(loc[1])
            # places tiles on board
            if loc[1] != "R":
                board[loc[1]][loc[0]] = tile[1]
            else:
                rack.append(tile[1])
        return board, rack

    def on_switch(self):
        if not self.controller.app_config["full screen"]:
            self.controller.geometry("640x360")
        if self.controller.frames[GameSetupPage].observer_mode.get() == 0:
            # if not observer mode
            self.player = scrabble.PlayerClient("host", update=self.on_update)
            host = scrabble.Host(self.player)
            self.player.host = host.players[-1]
            self.player.host_main = host
            for i in range(int(self.controller.frames[GameSetupPage].ai_count.get())):
                player = scrabble.BotV1(dictionary=host.words)
                host.add_player(player)
                player.host = host.players[-1]
                player.host_main = host
            host.start_game()
        else:
            # if observer mode
            self.player = scrabble.BotV1(update=self.on_update)
            host = scrabble.Host(self.player)
            self.player.host = host.players[-1]
            self.player.host_main = host
            for i in range(int(self.controller.frames[GameSetupPage].ai_count.get())):
                player = scrabble.BotV1(dictionary=host.words)
                host.add_player(player)
                player.host = host.players[-1]
                player.host_main = host
            host.start_game()

    def on_update(self, types):
        for opcode, operand in types:
            if opcode == "tiles" and self.player.tiles is not None:
                self.set_tiles(self.player.tiles)
            elif opcode == "board" and self.player.board is not None:
                self.set_board()
            elif opcode == "player_count":
                self.create_player_list()
            elif opcode == "tile_pool":
                self.set_tile_pool()
            elif opcode in ["current_player", "score"]:
                self.update_player_list()
                self.set_error_line()
            elif opcode == "error1":
                self.set_error_line(error="Invalid Tile Placement")
            elif opcode == "error2":
                self.set_error_line(error="Invalid Word \"{0}\"".format(operand.capitalize()))
            elif opcode == "winner":
                if operand.isnumeric() and int(operand) == self.player.order:
                    self.set_error_line(error="You Won")
                else:
                    self.set_error_line(error="Winner Player{0}".format(operand))

    def on_left_click(self, event):
        # if there is a tile where clicked, then give tile move tag
        for i in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            if "tile" in self.canvas.gettags(i) and "played" not in self.canvas.gettags(i):
                self.canvas.addtag_withtag("move", i)
                for tag in self.canvas.gettags(i):
                    if tag[:5] == "text_":
                        self.canvas.addtag_withtag("move", int(tag[5:]))
            elif "button" in self.canvas.gettags(i):
                if "end_turn" in self.canvas.gettags(i):
                    self.complete_turn()
                elif "pass" in self.canvas.gettags(i):
                    self.player.send("pass: ")
                    self.set_board()
                    self.set_tiles(self.player.tiles)
                elif "swap_tiles" in self.canvas.gettags(i):
                    ids = list(self.canvas.find_withtag("swap"))  # finds the ids of all tiles on the swap pad
                    if len(ids) == 0:
                        self.set_error_line("No tiles selected to swap")
                    else:
                        tiles = []
                        # gets all the tile text items
                        for item in ids:
                            if "tile_text" in self.canvas.gettags(item):
                                tiles.append(item)
                        # finds text on tile, tiles is now a list of letters
                        for tile, index in zip(tiles, range(len(tiles))):
                            tiles[index] = self.canvas.itemcget(tile, "text")
                        # deletes tiles
                        for item in ids:
                            self.canvas.delete(item)
                        # sends command to server
                        self.player.send("swap: {0}".format("".join(tiles)))
                elif "exit_game" in self.canvas.gettags(i):
                    # exits to main menu and deletes self from pages
                    self.player.host_main.playing = False
                    self.controller.set_frame(MainMenu)
                    self.controller.frames.pop(GameCanvas)
                    self.controller.set_full_screen(None)
        self.canvas.tag_raise("move")

    def on_left_release(self, event):
        bbox = self.canvas.bbox("move")
        # if bbox is not none than there is a tile currently being moved
        if bbox is not None:
            # gets the centre of the held tile
            x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            # if the held tile is over tile tile bag, it is dropped without moving it
            tile_bag_pos = self.canvas.bbox(self.canvas.find_withtag("tile_bag")[0])
            if tile_bag_pos[0] < x < tile_bag_pos[2] and tile_bag_pos[1] < y < tile_bag_pos[3]:
                self.canvas.addtag_withtag("swap", "move")
                self.canvas.dtag("move", "move")
            else:
                # finds the nearest anchor point on board or rack to tile position
                anchor = self.find_anchor(x, y)
                # if the anchor point is empty, tile assign that place, removes all tags that aren't "tile"
                if len(self.canvas.find_withtag(anchor)) == 0 and anchor != (None, None):
                    self.canvas.addtag_withtag(anchor, "move")
                    for tag in self.canvas.gettags("move"):
                        if tag not in ["current", "move", "tile", str(anchor[0]) + " " + str(anchor[1])] and tag[:5] != "text_":
                            self.canvas.dtag(anchor, tag)
                anchor = self.canvas.gettags("move")
                for i in anchor:
                    if i not in ["tile", "move", "current", "swap"] and i[:5] != "text_":
                        anchor = i.split(" ")
                        anchor = int(anchor[0]), int(anchor[1]) if anchor[1].isnumeric() else anchor[1]
                # now that the anchor to move the tile to is found, is then move
                if anchor[1] == "R":
                    bbox = self.canvas.bbox("rack")
                    x, y = bbox[0] + 5 + anchor[0] * 20, bbox[1]
                else:
                    bbox = self.canvas.bbox("board")
                    x = bbox[0] + anchor[0] * (bbox[2] - bbox[0]) / 15
                    y = bbox[1] + anchor[1] * (bbox[3] - bbox[1]) / 15
                self.canvas.moveto("move", x, y)
                self.canvas.dtag("move", "move")

    def on_mouse_motion(self, event):
        x, y = event.x - 10, event.y - 10
        if x < 0:
            x = 0
        elif x > 620:
            x = 620
        if y < 0:
            y = 0
        elif y > 340:
            y = 340
        self.canvas.moveto("move", x, y)

    def complete_turn(self):
        board, rack = self.get_board()
        board = "".join(["".join(i) for i in board])  # converts board into a string of all the letters
        rack = "".join(rack)
        self.player.send("place: {0}/{1}".format(board, rack))


if __name__ == "__main__":
    app = App()
