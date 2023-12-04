import tkinter as tk
import tkinter.ttk as ttk
import json


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scrabble")
        self.geometry("360x420")
        self.create_theme()
        try:
            file = open("config.json", "r")
            self.config = json.loads(file.readlines()[0])
            file.close()
            print("configs found", self.config)
        except:
            self.config = {}
            self.config["full screen"] = 1
            print("configs not found")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=1)
        self.frames = {}
        for frame in (MainMenu, SettingsPage, GameSetupPage):
            self.frames[frame] = frame(container, self)
        self.set_frame(MainMenu)
        self.mainloop()

    def set_frame(self, frame):
        for F in self.frames.values():
            F.place_forget()
        self.frames[frame].place(relx=0.5, rely=0, anchor="n")

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


class SettingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        settings_label = ttk.Label(self, text="Settings",
                                   style="title.TLabel")
        settings_label.grid(row=0, column=1)
        self.fs_var = tk.IntVar(self, value=controller.config["full screen"])
        full_screen_option = ttk.Checkbutton(self, text="Full screen", variable=self.fs_var)
        full_screen_option.invoke() if self.get_option("full screen") else None
        full_screen_option.grid(row=1, column=1)
        menu_button = ttk.Button(self, text="Back to Menu",
                                 command=self.back_to_menu)
        menu_button.grid(row=10, column=1)
        apply_button = ttk.Button(self, text="Apply",
                                  command=self.apply)
        apply_button.grid(row=10, column=2)

    def apply(self):
        self.set_option("full screen", self.fs_var.get())

    def back_to_menu(self):
        file = open("config.json", "w")
        file.write(json.dumps(self.controller.config))
        file.close()
        self.controller.set_frame(MainMenu)
        print(self.controller.config)

    def set_option(self, option, value):
        self.controller.config[option] = value
        print("set {0}  to {1}".format(option, value))

    def get_option(self, option):
        return self.controller.config[option]


class GameSetupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        setup_label = ttk.Label(self, text="Game Setup",
                                style="title.TLabel")
        setup_label.grid(row=0, column=1)
        back_to_menu_button = ttk.Button(self, text="Back to Menu",
                                         command=lambda: controller.set_frame(MainMenu))
        back_to_menu_button.grid(row=1, column=1)


if __name__ == "__main__":
    App()
