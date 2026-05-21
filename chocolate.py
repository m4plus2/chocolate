# Chocolate NES Emulator
# Built in Python with Tkinter

from loader import ROM
from cpu import CPU
from ram import RAM
from ppu import PPU

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.title("Chocolate v0.1.0")
root.geometry("800x600")

menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)

debug_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Debugging Tools", menu=debug_menu)

SCALE = 3

canvas = tk.Canvas(
    root,
    width=256 * SCALE,
    height=240 * SCALE,
    bg="black",
    highlightthickness=0
)

canvas.pack(pady=20)

image = tk.PhotoImage(
    width=256 * SCALE,
    height=240 * SCALE
)

canvas.create_image((0, 0), image=image, anchor="nw")

cpu = None
ppu = None


def show_cpu():
    if not cpu:
        return

    debug_window = tk.Toplevel(root)
    debug_window.title("CPU Debugger")
    debug_window.geometry("300x200")

    label = tk.Label(
        debug_window,
        font=("Consolas", 12),
        justify="left"
    )

    label.pack(padx=10, pady=10)

    def update_debug():
        if not cpu:
            return

        info = (
            f"A: {hex(cpu.a)}\n"
            f"X: {hex(cpu.x)}\n"
            f"Y: {hex(cpu.y)}\n"
            f"SP: {hex(cpu.sp)}\n"
            f"PC: {hex(cpu.pc)}\n"
            f"STATUS: {hex(cpu.status)}"
        )

        label.config(text=info)

        debug_window.after(100, update_debug)

    update_debug()


debug_menu.add_command(label="CPU Debugger", command=show_cpu)


def render_chr():
    if not ppu:
        return

    colors = [
        "#000000",
        "#555555",
        "#AAAAAA",
        "#FFFFFF"
    ]

    for py in range(128):
        row = []

        tile_y = py // 8
        pixel_y = py % 8

        for px in range(128):
            tile_x = px // 8
            pixel_x = px % 8

            tile = tile_y * 16 + tile_x

            color = ppu.get_tile_pixel(
                tile,
                pixel_x,
                pixel_y
            )

            row.append(colors[color])

        scaled_row = []

        for color in row:
            for i in range(SCALE):
                scaled_row.append(color)

        row_data = "{" + " ".join(scaled_row) + "}"

        for sy in range(SCALE):
            image.put(
                row_data,
                to=(0, py * SCALE + sy)
            )


def open_rom():
    global cpu
    global ppu

    path = filedialog.askopenfilename(
        filetypes=[("NES ROMs", "*.nes")]
    )

    if not path:
        return

    rom = ROM(path)
    ram = RAM()

    ppu = PPU(rom)
    cpu = CPU(rom, ram, ppu)

    render_chr()

    print("ROM loaded!")


file_menu.add_command(label="Open", command=open_rom)


def tick():
    if cpu:
        for i in range(100):
            cpu.step()

    root.after(1, tick)


tick()

root.mainloop()