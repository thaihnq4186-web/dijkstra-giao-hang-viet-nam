import sys
import tkinter as tk
from tkinter import messagebox
from app import WarehouseApp


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    root = tk.Tk()
    try:
        WarehouseApp(root)
    except (OSError, ValueError) as error:
        messagebox.showerror('Lỗi dữ liệu', str(error))
        root.destroy()
        raise
    root.mainloop()


if __name__ == '__main__':
    main()
