#!/usr/bin/env python3
import threading
import tkinter as tk
from tkinter import ttk

import pyautogui
from pynput import keyboard


BLOCKED_KEYS = {"/", "esc", "enter", "tab", "f1", "f2", "f3", "f4"}


class AutoPiano:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPiano")
        self.root.resizable(False, False)
        self.root.configure(bg="#eef3f2")

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#eef3f2")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#176b87", foreground="#ffffff",
                        font=("DejaVu Sans", 18, "bold"))
        style.configure("Subtitle.TLabel", background="#176b87", foreground="#c9e6e7",
                        font=("DejaVu Sans", 9))
        style.configure("Section.TLabel", background="#ffffff", foreground="#243746",
                        font=("DejaVu Sans", 10, "bold"))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#6a7c80",
                        font=("DejaVu Sans", 9))
        style.configure("Value.TLabel", background="#e8f2f1", foreground="#176b87",
                        font=("DejaVu Sans", 9, "bold"), padding=(8, 4))
        style.configure("Primary.TButton", background="#e56b55", foreground="#ffffff",
                        font=("DejaVu Sans", 9, "bold"), padding=(12, 8))
        style.map("Primary.TButton", background=[("active", "#c95543")])
        style.configure("Action.TButton", background="#dce8e7", foreground="#243746",
                        font=("DejaVu Sans", 9, "bold"), padding=(12, 8))
        style.map("Action.TButton", background=[("active", "#c4d8d6")])
        style.configure("Loop.TButton", background="#176b87", foreground="#ffffff",
                        font=("DejaVu Sans", 9, "bold"), padding=(12, 8))
        style.map("Loop.TButton", background=[("active", "#0f536a")])
        style.configure("Horizontal.TScale", background="#ffffff", troughcolor="#dce8e7",
                        sliderthickness=16)

        self.active = False
        self.paused = False
        self.loop = False
        self.delay = tk.IntVar(value=120)
        self.delay_dash = tk.IntVar(value=1000)
        self.worker = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.hotkey_listener = keyboard.GlobalHotKeys({
            "<f5>": self.toggle_loop_from_hotkey,
            "<f6>": self.toggle_pause_from_hotkey,
            "<f7>": self.stop_from_hotkey,
            "<f8>": self.start_from_hotkey,
        })

        frame = ttk.Frame(root, padding=0, style="App.TFrame")
        frame.grid()
        header = ttk.Frame(frame, padding=(20, 16), style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.configure(style="Header.TFrame")
        style.configure("Header.TFrame", background="#176b87")
        ttk.Label(header, text="AUTOPIANO", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Reproductor de partituras", style="Subtitle.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 0))

        editor = ttk.Frame(frame, padding=(20, 18, 20, 12), style="Card.TFrame")
        editor.grid(row=1, column=0, sticky="ew")
        ttk.Label(editor, text="PARTITURA", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(editor, text="Escribe notas, guiones y acordes entre corchetes", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 8))
        self.score = tk.Text(editor, width=58, height=9, wrap="word", undo=True,
                             bg="#f7faf9", fg="#243746", insertbackground="#e56b55",
                             relief="flat", bd=0, padx=10, pady=10,
                             font=("DejaVu Sans Mono", 10))
        self.score.grid(row=2, column=0, sticky="ew")

        settings = ttk.Frame(frame, padding=(20, 10, 20, 8), style="Card.TFrame")
        settings.grid(row=2, column=0, sticky="ew")
        ttk.Label(settings, text="CONFIGURACION", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(settings, text="Velocidad de notas", style="Muted.TLabel").grid(row=1, column=0, sticky="w")
        self.speed = ttk.Scale(settings, from_=20, to=400, variable=self.delay,
                               command=self.update_speed)
        self.speed.configure(style="Horizontal.TScale")
        self.speed.grid(row=2, column=0, padx=(0, 12), sticky="ew")
        self.speed_value = ttk.Label(settings, text="120 ms", width=8, style="Value.TLabel")
        self.speed_value.grid(row=2, column=1, sticky="e")

        ttk.Label(settings, text="Duracion de pausa (-)", style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.dash_speed = ttk.Scale(settings, from_=100, to=3000,
                                    variable=self.delay_dash, command=self.update_dash_speed)
        self.dash_speed.configure(style="Horizontal.TScale")
        self.dash_speed.grid(row=4, column=0, padx=(0, 12), sticky="ew")
        self.dash_value = ttk.Label(settings, text="1000 ms", width=8, style="Value.TLabel")
        self.dash_value.grid(row=4, column=1, sticky="e")
        settings.columnconfigure(0, weight=1)

        footer = ttk.Frame(frame, padding=(20, 10, 20, 18), style="Card.TFrame")
        footer.grid(row=3, column=0, sticky="ew")
        self.status = ttk.Label(footer, text="●  Detenido", style="Muted.TLabel")
        self.status.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Button(footer, text="INICIAR  F8", style="Primary.TButton", command=self.start).grid(row=1, column=0, sticky="ew")
        ttk.Button(footer, text="PAUSA  F6", style="Action.TButton", command=self.toggle_pause).grid(row=1, column=1, padx=6, sticky="ew")
        ttk.Button(footer, text="DETENER  F7", style="Action.TButton", command=self.stop).grid(row=1, column=2, sticky="ew")
        self.loop_button = ttk.Button(footer, text="BUCLE INFINITO: OFF  F5", style="Loop.TButton", command=self.toggle_loop)
        self.loop_button.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        for column in range(3):
            footer.columnconfigure(column, weight=1)

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.hotkey_listener.start()

    def update_speed(self, value):
        amount = int(float(value))
        self.delay.set(amount)
        self.speed_value.config(text=f"{amount} ms")

    def update_dash_speed(self, value):
        amount = int(float(value))
        self.delay_dash.set(amount)
        self.dash_value.config(text=f"{amount} ms")

    def start_from_hotkey(self):
        self.root.after(0, self.start)

    def toggle_pause_from_hotkey(self):
        self.root.after(0, self.toggle_pause)

    def stop_from_hotkey(self):
        self.root.after(0, self.stop)

    def toggle_loop_from_hotkey(self):
        self.root.after(0, self.toggle_loop)

    def start(self):
        if self.active:
            return
        self.active = True
        self.paused = False
        self.stop_event.clear()
        self.pause_event.clear()
        self.status.config(text="●  Reproduciendo", foreground="#2d8a69")
        score = self.score.get("1.0", "end-1c")
        self.worker = threading.Thread(target=self.play, args=(score,), daemon=True)
        self.worker.start()

    def play(self, score):
        while not self.stop_event.is_set():
            index = 0
            while index < len(score) and not self.stop_event.is_set():
                self.pause_event.wait()
                character = score[index]

                if character.isspace():
                    index += 1
                    continue
                if character == "-":
                    self.wait(self.delay_dash.get() / 1000)
                    index += 1
                    continue
                if character == "[":
                    end = score.find("]", index + 1)
                    chord = score[index + 1:] if end == -1 else score[index + 1:end]
                    for key in chord:
                        if key.lower() not in BLOCKED_KEYS and not key.isspace():
                            pyautogui.keyDown(key)
                    self.wait(0.04)
                    for key in chord:
                        if key.lower() not in BLOCKED_KEYS and not key.isspace():
                            pyautogui.keyUp(key)
                    self.wait(self.delay.get() / 1000)
                    index = len(score) if end == -1 else end + 1
                    continue

                if character.lower() not in BLOCKED_KEYS:
                    pyautogui.press(character)
                    self.wait(self.delay.get() / 1000)
                index += 1

            if not self.loop:
                break

        self.root.after(0, self.playback_finished)

    def wait(self, seconds):
        self.stop_event.wait(seconds)

    def toggle_pause(self):
        if not self.active:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_event.clear()
            self.status.config(text="●  Pausado", foreground="#c77b22")
        else:
            self.pause_event.set()
            self.status.config(text="●  Reproduciendo", foreground="#2d8a69")

    def stop(self):
        self.stop_event.set()
        self.pause_event.set()
        self.paused = False
        if not self.active:
            self.status.config(text="●  Detenido", foreground="#6a7c80")

    def toggle_loop(self):
        self.loop = not self.loop
        state = "ON" if self.loop else "OFF"
        self.loop_button.config(text=f"Bucle infinito: {state} (F5)")

    def playback_finished(self):
        self.active = False
        self.paused = False
        self.status.config(text="●  Detenido", foreground="#6a7c80")

    def close(self):
        self.stop()
        self.hotkey_listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    pyautogui.PAUSE = 0
    app_root = tk.Tk()
    AutoPiano(app_root)
    app_root.mainloop()
