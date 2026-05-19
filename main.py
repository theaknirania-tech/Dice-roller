# ============================================================
#  🎲 Python Dice Roller — Tkinter Project
#  Beginner-Friendly | Dark UI | Animation | Sound
# ============================================================
#
#  Install dependencies first:
#    pip install Pillow playsound
#
#  Run:
#    python dice_roller.py
# ============================================================

import tkinter as tk
from tkinter import ttk, font
import random
import threading
import time
import os

# Try importing optional libraries
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow not found. Using canvas dice instead.")

try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("playsound not found. Sounds disabled.")


# ─── Constants ───────────────────────────────────────────────
BG_COLOR       = "#0d0d14"   # Dark background
CARD_COLOR     = "#1a1a2e"   # Card surface
ACCENT_COLOR   = "#7c3aed"   # Purple accent
TEXT_COLOR     = "#ffffff"   # White text
MUTED_COLOR    = "#6b7280"   # Gray muted text
HIGHLIGHT      = "#a78bfa"   # Light purple highlight
MAX_HISTORY    = 10          # Maximum rolls to remember
ANIMATION_STEPS = 18         # How many frames during roll
ANIMATION_DELAY = 55         # Milliseconds between frames


# ─── Draw a single die face on a Canvas ──────────────────────
DOT_POSITIONS = {
    1: [(50, 50)],
    2: [(28, 28), (72, 72)],
    3: [(28, 28), (50, 50), (72, 72)],
    4: [(28, 28), (72, 28), (28, 72), (72, 72)],
    5: [(28, 28), (72, 28), (50, 50), (28, 72), (72, 72)],
    6: [(28, 25), (72, 25), (28, 50), (72, 50), (28, 75), (72, 75)],
}

def draw_die(canvas, value, x=0, y=0, size=100, color="#7c3aed"):
    """Draw a die face with rounded corners and dots."""
    canvas.delete("all")

    # Die body with rounded rectangle
    r = int(size * 0.18)   # corner radius
    canvas.create_polygon(
        x+r, y,
        x+size-r, y,
        x+size, y+r,
        x+size, y+size-r,
        x+size-r, y+size,
        x+r, y+size,
        x, y+size-r,
        x, y+r,
        smooth=True,
        fill=color,
        outline="#a78bfa",
        width=2,
    )

    # Shine highlight (top-left triangle effect)
    canvas.create_oval(
        x+5, y+5,
        x+size//2, y+size//2,
        fill="", outline="white", width=0,
        stipple="gray25",
    )

    # Draw dots
    dot_r = int(size * 0.09)
    positions = DOT_POSITIONS.get(value, [])
    scale = size / 100

    for (cx, cy) in positions:
        px = int(x + cx * scale)
        py = int(y + cy * scale)
        canvas.create_oval(
            px - dot_r, py - dot_r,
            px + dot_r, py + dot_r,
            fill="white",
            outline="",
        )


# ─── Sound Effect ────────────────────────────────────────────
def play_roll_sound():
    """Play dice rolling sound in a background thread."""
    if not SOUND_AVAILABLE:
        return
    sound_file = os.path.join(os.path.dirname(__file__), "dice_roll.mp3")
    if os.path.exists(sound_file):
        thread = threading.Thread(
            target=playsound, args=(sound_file,), daemon=True
        )
        thread.start()
    else:
        print("Sound file 'dice_roll.mp3' not found.")


# ─── Dice Roller Logic ───────────────────────────────────────
def roll_dice(num_dice: int = 1) -> tuple[list[int], int]:
    """
    Roll num_dice standard 6-sided dice.
    Returns a list of results and the total sum.
    """
    results = [random.randint(1, 6) for _ in range(num_dice)]
    total   = sum(results)
    return results, total


# ─── Main Application Class ──────────────────────────────────
class DiceRollerApp:
    """
    A beginner-friendly Tkinter Dice Roller application.
    Features: dark UI, animated dice, sound effects, roll history.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎲 Python Dice Roller")
        self.root.geometry("750x650")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # State variables
        self.num_dice      = tk.IntVar(value=2)
        self.is_rolling    = False
        self.roll_count    = 0
        self.history: list[dict] = []
        self.die_canvases: list[tk.Canvas] = []
        self.anim_step     = 0
        self.current_vals  = [1, 1]

        self._build_ui()
        self._center_window()

    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        """Build all UI widgets."""
        # ── Title bar ─────────────────────────────────────
        title_frame = tk.Frame(self.root, bg=CARD_COLOR, pady=12)
        title_frame.pack(fill="x", padx=0, pady=0)

        tk.Label(
            title_frame, text="🎲  PYTHON DICE ROLLER",
            font=("Courier New", 18, "bold"),
            bg=CARD_COLOR, fg=HIGHLIGHT,
        ).pack()
        tk.Label(
            title_frame, text="Tkinter Project  ·  Beginner Friendly",
            font=("Courier New", 9),
            bg=CARD_COLOR, fg=MUTED_COLOR,
        ).pack()

        # ── Main content ──────────────────────────────────
        content = tk.Frame(self.root, bg=BG_COLOR)
        content.pack(fill="both", expand=True, padx=16, pady=10)

        # Left side: dice + controls
        left = tk.Frame(content, bg=BG_COLOR)
        left.pack(side="left", fill="both", expand=True)

        # Right side: history
        right = tk.Frame(content, bg=CARD_COLOR, relief="flat", bd=0)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.configure(width=210)
        right.pack_propagate(False)
        self._build_history_panel(right)

        # Dice count selector
        self._build_dice_selector(left)

        # Dice canvas area
        self._build_dice_area(left)

        # Result label
        self.result_label = tk.Label(
            left, text="Press Roll to start!",
            font=("Courier New", 14, "bold"),
            bg=BG_COLOR, fg=MUTED_COLOR,
        )
        self.result_label.pack(pady=(8, 4))

        self.sub_label = tk.Label(
            left, text="",
            font=("Courier New", 9),
            bg=BG_COLOR, fg=MUTED_COLOR,
        )
        self.sub_label.pack()

        # Roll button
        self._build_roll_button(left)

        # Stats row
        self._build_stats(left)

        # Keyboard shortcut hint
        tk.Label(
            left, text="Tip: Press [Space] to roll quickly",
            font=("Courier New", 8),
            bg=BG_COLOR, fg=MUTED_COLOR,
        ).pack(pady=(6, 0))

        # Bind spacebar
        self.root.bind("<space>", lambda e: self._roll())

    def _build_dice_selector(self, parent):
        """Build the num-dice toggle buttons."""
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.pack(pady=(6, 4))

        tk.Label(
            frame, text="Number of Dice:",
            font=("Courier New", 9, "bold"),
            bg=BG_COLOR, fg=MUTED_COLOR,
        ).pack(side="left", padx=(0, 8))

        self._dice_btns = []
        for n in range(1, 5):
            btn = tk.Button(
                frame, text=str(n), width=3,
                font=("Courier New", 9, "bold"),
                bg=CARD_COLOR, fg=MUTED_COLOR,
                activebackground=ACCENT_COLOR,
                activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=lambda v=n: self._set_dice_count(v),
            )
            btn.pack(side="left", padx=2)
            self._dice_btns.append(btn)

        self._set_dice_count(2)

    def _set_dice_count(self, n: int):
        """Change number of dice and rebuild canvas grid."""
        if self.is_rolling:
            return
        self.num_dice.set(n)
        self.current_vals = [1] * n

        # Update button highlights
        for i, btn in enumerate(self._dice_btns):
            if i + 1 == n:
                btn.configure(bg=ACCENT_COLOR, fg="white")
            else:
                btn.configure(bg=CARD_COLOR, fg=MUTED_COLOR)

        # Rebuild dice area
        for c in self.die_canvases:
            c.master.destroy()
        self.die_canvases.clear()

        size = 95 if n <= 2 else 75
        for i in range(n):
            frame = tk.Frame(self.dice_frame, bg=BG_COLOR, padx=4, pady=4)
            frame.pack(side="left")
            c = tk.Canvas(
                frame, width=size, height=size,
                bg=BG_COLOR, highlightthickness=0,
            )
            c.pack()
            draw_die(c, 1, size=size)
            self.die_canvases.append(c)

        self.result_label.config(text="Ready!", fg=MUTED_COLOR)
        self.sub_label.config(text="")

    def _build_dice_area(self, parent):
        """Build the frame that holds the dice canvases."""
        wrapper = tk.Frame(
            parent, bg=CARD_COLOR,
            relief="flat", bd=0,
            pady=16, padx=16,
        )
        wrapper.pack(fill="x", pady=6, padx=8)

        self.dice_frame = tk.Frame(wrapper, bg=CARD_COLOR)
        self.dice_frame.pack()

        self._set_dice_count(self.num_dice.get())

    def _build_roll_button(self, parent):
        """Build the big Roll button."""
        self.roll_btn = tk.Button(
            parent,
            text="🎲  ROLL DICE!",
            font=("Courier New", 14, "bold"),
            bg=ACCENT_COLOR, fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            relief="flat", bd=0,
            padx=30, pady=10,
            cursor="hand2",
            command=self._roll,
        )
        self.roll_btn.pack(pady=10)

        # Hover effects
        self.roll_btn.bind("<Enter>", lambda e: self.roll_btn.config(bg="#6d28d9"))
        self.roll_btn.bind("<Leave>", lambda e: self.roll_btn.config(bg=ACCENT_COLOR))

    def _build_stats(self, parent):
        """Build the stats row (total rolls, best, average)."""
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.pack(pady=4)

        self.stat_rolls_var = tk.StringVar(value="0")
        self.stat_best_var  = tk.StringVar(value="—")
        self.stat_avg_var   = tk.StringVar(value="—")

        for label, var, color in [
            ("ROLLS",   self.stat_rolls_var, HIGHLIGHT),
            ("BEST",    self.stat_best_var,  "#818cf8"),
            ("AVERAGE", self.stat_avg_var,   "#60a5fa"),
        ]:
            col = tk.Frame(frame, bg=BG_COLOR, padx=14)
            col.pack(side="left")
            tk.Label(col, textvariable=var, font=("Courier New", 16, "bold"),
                     bg=BG_COLOR, fg=color).pack()
            tk.Label(col, text=label, font=("Courier New", 7),
                     bg=BG_COLOR, fg=MUTED_COLOR).pack()

    def _build_history_panel(self, parent):
        """Build the roll history panel."""
        tk.Label(
            parent, text="📜 ROLL HISTORY",
            font=("Courier New", 9, "bold"),
            bg=CARD_COLOR, fg=HIGHLIGHT,
            pady=8,
        ).pack(fill="x")

        tk.Frame(parent, bg=ACCENT_COLOR, height=1).pack(fill="x")

        self.history_frame = tk.Frame(parent, bg=CARD_COLOR)
        self.history_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self._no_history_label = tk.Label(
            self.history_frame,
            text="No rolls yet…\nStart rolling!",
            font=("Courier New", 9),
            bg=CARD_COLOR, fg=MUTED_COLOR,
            justify="center",
        )
        self._no_history_label.pack(expand=True, pady=30)

    # ── Rolling Logic ────────────────────────────────────────
    def _roll(self):
        """Start the dice rolling animation."""
        if self.is_rolling:
            return

        self.is_rolling  = True
        self.anim_step   = 0

        # Disable button
        self.roll_btn.config(
            text="Rolling…", bg="#2a2a3e",
            fg=MUTED_COLOR, state="disabled",
        )
        self.result_label.config(text="🎲  Rolling…", fg=HIGHLIGHT)
        self.sub_label.config(text="")

        # Play sound in background
        play_roll_sound()

        # Start animation loop
        self._animate()

    def _animate(self):
        """One frame of the rolling animation."""
        n = self.num_dice.get()
        size = 95 if n <= 2 else 75

        # Show random values during animation
        for i, canvas in enumerate(self.die_canvases):
            temp = random.randint(1, 6)
            draw_die(canvas, temp, size=size)

        self.anim_step += 1

        if self.anim_step < ANIMATION_STEPS:
            # Slow down as animation progresses
            delay = ANIMATION_DELAY + self.anim_step * 8
            self.root.after(delay, self._animate)
        else:
            # Show final result
            self._finish_roll()

    def _finish_roll(self):
        """Display the final roll result and update history."""
        n = self.num_dice.get()
        size = 95 if n <= 2 else 75

        results, total = roll_dice(n)
        self.current_vals = results

        for i, canvas in enumerate(self.die_canvases):
            draw_die(canvas, results[i], size=size)

        # Update labels
        self.result_label.config(
            text=f"Total: {total}",
            fg="white",
            font=("Courier New", 18, "bold"),
        )
        if n > 1:
            breakdown = " + ".join(str(v) for v in results)
            self.sub_label.config(
                text=f"[ {breakdown} ]  =  {total}",
                fg=MUTED_COLOR,
            )

        # Update stats
        self.roll_count += 1
        self.history.insert(0, {"dice": results, "total": total})
        self.history = self.history[:MAX_HISTORY]
        self._update_history()
        self._update_stats()

        # Re-enable button
        self.roll_btn.config(
            text="🎲  ROLL DICE!", bg=ACCENT_COLOR,
            fg="white", state="normal",
        )
        self.is_rolling = False

    def _update_stats(self):
        """Refresh the stats row."""
        self.stat_rolls_var.set(str(self.roll_count))
        if self.history:
            best = max(r["total"] for r in self.history)
            avg  = sum(r["total"] for r in self.history) / len(self.history)
            self.stat_best_var.set(str(best))
            self.stat_avg_var.set(f"{avg:.1f}")

    def _update_history(self):
        """Rebuild the history panel with current history list."""
        # Clear old entries
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.history:
            self._no_history_label = tk.Label(
                self.history_frame,
                text="No rolls yet…\nStart rolling!",
                font=("Courier New", 9),
                bg=CARD_COLOR, fg=MUTED_COLOR,
                justify="center",
            )
            self._no_history_label.pack(expand=True, pady=30)
            return

        for i, record in enumerate(self.history):
            row = tk.Frame(
                self.history_frame,
                bg="#12121f" if i == 0 else CARD_COLOR,
                pady=4, padx=4,
            )
            row.pack(fill="x", pady=1)

            dice_str = "  ".join(
                ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][v - 1]
                for v in record["dice"]
            )
            tk.Label(
                row, text=dice_str,
                font=("Courier New", 12),
                bg=row["bg"], fg=HIGHLIGHT if i == 0 else "white",
            ).pack(side="left")

            tk.Label(
                row, text=f"= {record['total']}",
                font=("Courier New", 10, "bold"),
                bg=row["bg"], fg=HIGHLIGHT if i == 0 else MUTED_COLOR,
            ).pack(side="right")


# ─── Entry Point ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = DiceRollerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
