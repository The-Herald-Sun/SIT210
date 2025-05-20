import tkinter as tk
from FrontEnd import UI
from Db import CowDataAccess

if __name__ == "__main__":
    root = tk.Tk()
    ui = UI(root, cow_data_access=CowDataAccess())
    root.mainloop()