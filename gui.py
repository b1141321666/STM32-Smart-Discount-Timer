import tkinter as tk
from tkinter import ttk
import serial
import threading
import queue

PORT = "COM5"
BAUDRATE = 115200

data_queue = queue.Queue()
running = True


def read_serial():
    global running

    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        data_queue.put(("status", "Connected: COM5"))

        while running:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if line.startswith("TIME="):
                data_queue.put(("data", line))

        ser.close()

    except serial.SerialException as e:
        data_queue.put(("status", f"Connection error: {e}"))


def update_gui():
    while not data_queue.empty():
        kind, value = data_queue.get_nowait()

        if kind == "status":
            status_label.config(text=value)

        elif kind == "data":
            try:
                values = {}

                for item in value.split(","):
                    key, val = item.split("=", 1)
                    values[key] = val

                time_label.config(text=values["TIME"] + " s")
                error_label.config(text=values["ERROR"] + " s")
                discount_label.config(text=values["DISCOUNT"] + " 折")

                status_label.config(text="Challenge completed!")

            except (ValueError, KeyError):
                status_label.config(text="Invalid UART data")

    if running:
        root.after(100, update_gui)


def on_close():
    global running
    running = False
    root.destroy()


root = tk.Tk()
root.title("10 秒計時折扣機")
root.geometry("450x380")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="10 秒折扣大挑戰",
    font=("Microsoft JhengHei", 22, "bold")
)
title_label.pack(pady=20)

tk.Label(root, text="Time", font=("Arial", 14)).pack()
time_label = tk.Label(root, text="-- s", font=("Arial", 23, "bold"))
time_label.pack(pady=5)

tk.Label(root, text="Error", font=("Arial", 14)).pack()
error_label = tk.Label(root, text="-- s", font=("Arial", 23, "bold"))
error_label.pack(pady=5)

tk.Label(root, text="Discount", font=("Arial", 14)).pack()
discount_label = tk.Label(
    root,
    text="-- 折",
    font=("Microsoft JhengHei", 27, "bold"),
    fg="blue"
)
discount_label.pack(pady=10)

status_label = tk.Label(
    root,
    text="Connecting to COM5...",
    font=("Arial", 11),
    fg="gray"
)
status_label.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)

serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

root.after(100, update_gui)
root.mainloop()