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
        if state:
            self.overrideredirect(True)
            self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        else:
            self.overrideredirect(False)
            self.geometry("360x420+{0}+{1}".format(int(self.winfo_screenwidth()/2-180),
                                                   int(self.winfo_screenheight()/2-210)))
        print("set full screen to {0}".format(state))

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
        setup_label = ttk.Label(self, text="Game Setup",
                                style="title.TLabel")
        setup_label.grid(row=0, column=1, columnspan=2)
        back_to_menu_button = ttk.Button(self, text="Back to Menu",
                                         command=lambda: controller.set_frame(MainMenu))
        back_to_menu_button.grid(row=1, column=1)
        start_game_button = ttk.Button(self, text="Start Game",
                                       command=self.start_game)
        start_game_button.grid(row=1, column=2)

    def start_game(self):
        self.controller.start_game()

    def on_switch(self):
        pass


class GameCanvas(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.canvas = tk.Canvas(self, width=640, height=360)
        self.canvas.pack()
        # key binds
        self.canvas.bind_all("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind_all("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind_all("<Motion>", self.on_mouse_motion)
        # creates frame images
        self.canvas.create_image(320, 0, anchor="n", image=self.controller.assets["board"], tag="board")
        self.canvas.create_image(320, 360, anchor="s", image=self.controller.assets["rack"], tag="rack")
        bbox = self.canvas.bbox("rack")
        for i in range(7):
            self.canvas.create_image(bbox[0]+5+i*20, bbox[1], anchor="nw",
                                     image=self.controller.assets["tile"], tags=["tile", (i, "R")])

        print("wee woo")

    def on_switch(self):
        if not self.controller.app_config["full screen"]:
            self.controller.geometry("640x360")
        player = scrabble.PlayerClient("player1")
        host = scrabble.Host(player)
        # temp code
        player2 = scrabble.PlayerClient("player2")
        host.add_player(player2)
        player.host = host
        player2.host = host
        host.start_game()

    def find_anchor(self, x, y):
        """checks if (x, y) is within the range of an anchor
        and returns which anchor is valid"""
        for image in self.canvas.find_overlapping(x, y, x, y):
            # check game board
            if "board" in self.canvas.gettags(image):
                bbox = self.canvas.bbox("board")
                x, y = int((x-bbox[0])/(bbox[2]-bbox[0])*15), int((y-bbox[1])/(bbox[3]-bbox[1])*15)
                if x == 15:
                    x = 14
                if y == 15:
                    y = 14
                # x, y now shows the tile with 0, 0 being the top left
                return x, y
            # check rack
            elif "rack" in self.canvas.gettags(image):
                bbox = self.canvas.bbox("rack")
                x, y = (x-bbox[0]-5)/(bbox[2]-bbox[0]-10)*7, "R"
                if x < 0:
                    x = 0
                elif x >= 7:
                    x = 6
                # returns n, "R" where n is the order of the rack space and "R" inidicates it is on the rack
                return int(x), y
            else:
                return None, None

    def on_left_click(self, event):
        # if there is a tile where clicked, then give tile move tag
        if "tile" in self.canvas.gettags("current"):
            self.canvas.addtag_withtag("move", "current")

    def on_left_release(self, event):
        bbox = self.canvas.bbox("move")
        # if bbox is not none than there is a tile currently being moved
        if bbox is not None:
            # finds the nearest anchor point
            x, y = (bbox[0] + bbox[2])/2, (bbox[1]+bbox[3])/2
            anchor = self.find_anchor(x, y)
            # if the anchor point is empty, tile assign that place, removes all tags that aren't "tile"
            if len(self.canvas.find_withtag(anchor)) == 0 and anchor != (None, None):
                self.canvas.addtag_withtag(anchor, "move")
                for tag in self.canvas.gettags("move"):
                    if tag not in ["current", "move", "tile", str(anchor[0]) + " " + str(anchor[1])]:
                        self.canvas.dtag(anchor, tag)
            anchor = self.canvas.gettags("move")
            for i in anchor:
                if i not in ["tile", "move", "current"]:
                    anchor = i.split(" ")
                    anchor = int(anchor[0]), int(anchor[1]) if anchor[1].isnumeric() else anchor[1]
            # now that the anchor to move the tile to is found, is then move
            if anchor[1] == "R":
                bbox = self.canvas.bbox("rack")
                x, y = bbox[0] + 5 + anchor[0] * 20, bbox[1]
            else:
                bbox = self.canvas.bbox("board")
                x = bbox[0] + anchor[0]*(bbox[2] - bbox[0])/15
                y = bbox[1] + anchor[1]*(bbox[3] - bbox[1])/15
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


if __name__ == "__main__":
    app = App()
