import tkinter as tk
import tkinter.ttk as ttk
import json


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scrabble")
        self.create_theme()
        self.open_configs()
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
        self.config = json.loads(file.readlines()[0])
        file.close()
        print("configs found", self.config)
        # apply configs
        self.set_full_screen(self.config["full screen"])

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
        self.fs_var = tk.IntVar(self, value=controller.config["full screen"])
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
        file.write(json.dumps(self.controller.config))
        file.close()

    def set_option(self, option, value):
        self.controller.config[option] = value

    def get_option(self, option):
        return self.controller.config[option]

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
        test_label = ttk.Label(self, text="test", style="title.TLabel")
        test_label.pack()
        print("wee woo")

    def on_switch(self):
        pass


if __name__ == "__main__":
    App()
