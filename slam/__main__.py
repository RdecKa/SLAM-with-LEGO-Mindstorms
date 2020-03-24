import tkinter as tk
import slam.gui.window as window

if __name__ == '__main__':
    root = tk.Tk()
    app = window.Window(master=root)
    app.mainloop()
