import random
import os
import threading
import queue
import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
import playsound

# ---------------- VOICE QUEUE ---------------- #

voice_queue = queue.Queue()

def voice_worker():
    while True:
        item = voice_queue.get()

        if item is None:
            break
        text, callback = item

        try:
            tts = gTTS(text=text, lang="en", slow=False)
            file = "temp.mp3"
            tts.save(file)
            playsound.playsound(file)
            if os.path.exists(file):
                os.remove(file)

        except Exception as e:
            print("Voice Error:", e)

        finally:
            voice_queue.task_done()
            if callback:
                root.after(1000, callback)   # 3 sec delay

threading.Thread(target=voice_worker, daemon=True).start()


def speak(text, callback=None):
    voice_queue.put((text, callback))

# ---------------- MAIN WINDOW ---------------- #

root = tk.Tk()
root.title("Smart Voice Number Caller")
root.geometry("600x780")
root.resizable(False, False)


# ---------------- STATE ---------------- #

started = False
paused = False
dark_mode = False

numbers = []
history = []


# ---------------- THEMES ---------------- #

LIGHT_THEME = {
    "bg": "white",
    "fg": "black",
    "board": "white",
    "btn": "#dddddd"
}

DARK_THEME = {
    "bg": "#1e1e1e",
    "fg": "white",
    "board": "#2b2b2b",
    "btn": "#444444"
}


# ---------------- MAIN DISPLAY ---------------- #

main_label = tk.Label(
    root,
    text="READY",
    font=("Arial Black", 50)
)

main_label.pack(pady=15)

# ---------------- BUTTON FRAME ---------------- #

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

# ---------------- NUMBER SYSTEM ---------------- #

def reset_numbers():
    global numbers, history
    numbers = list(range(1, 91))
    random.shuffle(numbers)
    history.clear()


reset_numbers()


# ---------------- BOARD ---------------- #

board_frame = tk.Frame(root)
board_frame.pack(pady=10)
cells = {}

n = 1

for r in range(9):
    for c in range(10):
        if n <= 90:
            lbl = tk.Label(
                board_frame,
                text=str(n),
                width=4,
                height=2,
                font=("Arial", 10),
                borderwidth=1,
                relief="solid"
            )

            lbl.grid(row=r, column=c, padx=2, pady=2)
            cells[n] = lbl

            n += 1


# ---------------- THEME SYSTEM ---------------- #

def apply_theme():
    theme = DARK_THEME if dark_mode else LIGHT_THEME
    root.configure(bg=theme["bg"])
    main_label.config(bg=theme["bg"], fg=theme["fg"])
    btn_frame.config(bg=theme["bg"])
    board_frame.config(bg=theme["bg"])

    for btn in [start_btn, reset_btn, retry_btn, quit_btn, theme_btn]:
        btn.config(
            bg=theme["btn"],
            fg=theme["fg"],
            activebackground=theme["board"]
        )

    for i in cells:
        if cells[i]["bg"] not in ["green", "purple"]:
            cells[i].config(
                bg=theme["board"],
                fg=theme["fg"]
            )


def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        theme_btn.config(text="LIGHT MODE")
    else:
        theme_btn.config(text="DARK MODE")

    apply_theme()


# ---------------- GAME FUNCTIONS ---------------- #

def show_popup(num):
    messagebox.showinfo("Number Called", f"Number: {num}")


def start_game():
    global started
    if not started:
        started = True
        start_btn.config(state="disabled")
        call_number()


def reset_game():
    global started, paused
    started = False
    paused = False
    main_label.config(text="READY", fg="blue")
    reset_numbers()
    start_btn.config(state="normal")
    apply_theme()


def toggle_pause():
    global paused
    paused = not paused

    if paused:
        main_label.config(text="PAUSED", fg="orange")
    else:
        main_label.config(text="READY", fg="blue")


def retry_last():
    if history:
        last = history[-1]
        main_label.config(text=str(last), fg="purple")
        speak(f"The number is {last}")


def quit_game():
    voice_queue.put(None)
    root.destroy()

# ---------------- MAIN LOGIC ---------------- #

def call_number():
    if not started:
        return

    if paused:
        root.after(500, call_number)
        return

    if not numbers:
        main_label.config(text="FINISHED", fg="red")
        messagebox.showinfo("Game Over", "All numbers completed!")
        speak("Game finished")
        return

    num = numbers.pop()
    history.append(num)
    main_label.config(text=str(num), fg="green")
    cells[num].config(bg="green", fg="white")
    show_popup(num)
    speak(f"The number is {num}", callback=call_number)

# ---------------- BUTTONS ---------------- #

start_btn = tk.Button(
    btn_frame,
    text="START",
    width=10,
    font=("Arial", 12),
    command=start_game
)

reset_btn = tk.Button(
    btn_frame,
    text="RESET",
    width=10,
    font=("Arial", 12),
    command=reset_game
)

retry_btn = tk.Button(
    btn_frame,
    text="RETRY",
    width=10,
    font=("Arial", 12),
    command=retry_last
)

quit_btn = tk.Button(
    btn_frame,
    text="QUIT",
    width=10,
    font=("Arial", 12),
    command=quit_game
)

theme_btn = tk.Button(
    btn_frame,
    text="DARK MODE",
    width=12,
    font=("Arial", 12),
    command=toggle_theme
)

start_btn.grid(row=0, column=0, padx=8, pady=5)
reset_btn.grid(row=0, column=1, padx=8, pady=5)
retry_btn.grid(row=1, column=0, padx=8, pady=5)
quit_btn.grid(row=1, column=1, padx=8, pady=5)
theme_btn.grid(row=2, column=0, columnspan=2, pady=8)

# ---------------- KEY SHORTCUTS ---------------- 

root.bind("p", lambda e: toggle_pause())   # Pause
root.bind("q", lambda e: quit_game())      # Quit
root.bind("t", lambda e: toggle_theme())   # Theme


# ---------------- START APP ----------------

apply_theme()
root.mainloop()
