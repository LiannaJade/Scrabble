import tkinter as tk
import tkinter.ttk as ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scrabble")
        self.geometry("360x420")
        self.create_theme()
        container = ttk.Frame(self)
        container.pack(fill="both", expand=1)
        self.frames = {}
        for frame in (MainMenu, SettingsPage):
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
                                       command=lambda: print("implement me"))  # implementation needed
        start_game_button.grid(row=1, column=1)
        settings_button = ttk.Button(self, text="Settings",
                                     command=lambda: controller.set_frame(SettingsPage))
        settings_button.grid(row=2, column=1)


class SettingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        settings_label = ttk.Label(self, text="Settings",
                                   style="title.TLabel")
        settings_label.grid(row=0, column=1)
        menu_button = ttk.Button(self, text="Back to Menu",
                                 command=lambda: controller.set_frame(MainMenu))
        menu_button.grid(row=10, column=1)


if __name__ == "__main__":
    App()
