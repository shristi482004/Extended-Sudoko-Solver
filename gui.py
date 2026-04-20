import tkinter as tk
from tkinter import messagebox
import time
import threading

from puzzles import SAMPLE_PUZZLES
from sudoku_solver import SudokuSolver, get_peers

# ─────────────────────────────────────────────
#  COLOR PALETTE  (mauve / dusty purple theme)
# ─────────────────────────────────────────────
BG_MAIN        = "#2D1F3D"
BG_PANEL       = "#3D2B50"
BG_CELL        = "#F5F0FA"
BG_GIVEN       = "#C9B8E8"
BG_SOLVED      = "#E8D5F5"
BG_SELECTED    = "#9B72CF"
BG_HIGHLIGHT   = "#DDD0F0"
BG_ERROR       = "#E57373"
BG_BTN_PRI     = "#7B5EA7"
BG_BTN_PRI_HOV = "#9B7DC7"
BG_BTN_SEC     = "#4A3560"
BG_BTN_SEC_HOV = "#5A4570"
BG_BTN_ACC     = "#6D4A7C"
BG_BTN_ACC_HOV = "#8B5A9C"
BG_THICK_LINE  = "#7B5EA7"
BG_THIN_LINE   = "#C5B0E0"

FG_MAIN        = "#F5F0FA"
FG_GIVEN       = "#2D1F3D"
FG_SOLVED      = "#5A3080"
FG_LABEL       = "#D0B8E8"
FG_TITLE       = "#E8D5F5"
FG_BTN         = "#000000"

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_CELL   = ("Segoe UI", 20, "bold")
FONT_SMALL  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_STATUS = ("Segoe UI", 10)

CELL_SIZE = 56
GRID_PAD  = 4

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Extended Sudoku Solver")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.selected = None
        self.given    = set()
        self.solving  = False
        self.anim_steps = []
        self.anim_idx   = 0

        self.var_diag   = tk.BooleanVar(value=True)
        self.var_knight = tk.BooleanVar(value=True)
        self.var_king   = tk.BooleanVar(value=True)
        self.var_anim   = tk.BooleanVar(value=False)

        self.cell_vals = [[0]*9 for _ in range(9)]
        self.cell_state = [["empty"]*9 for _ in range(9)]

        self._build_ui()
        self._load_puzzle("Easy (Standard)")
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=BG_PANEL, pady=10)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="AI Extended Sudoku Solver",
                 font=FONT_TITLE, bg=BG_PANEL, fg=FG_TITLE).pack()
        tk.Label(title_frame, text="Constraint Propagation  ·  Backtracking  ·  MRV + LCV + Forward Checking",
                 font=FONT_STATUS, bg=BG_PANEL, fg=FG_LABEL).pack()

        body = tk.Frame(self, bg=BG_MAIN, padx=16, pady=12)
        body.pack()

        left = tk.Frame(body, bg=BG_MAIN)
        left.grid(row=0, column=0, padx=(0, 16))
        self._build_grid(left)

        right = tk.Frame(body, bg=BG_PANEL, padx=16, pady=16)
        right.grid(row=0, column=1, sticky="n")
        self._build_controls(right)

        self.status_var = tk.StringVar(value="Load a puzzle or click a cell to begin.")
        status_bar = tk.Frame(self, bg=BG_PANEL, pady=6)
        status_bar.pack(fill=tk.X)
        tk.Label(status_bar, textvariable=self.status_var,
                 font=FONT_STATUS, bg=BG_PANEL, fg=FG_LABEL).pack()

    def _build_grid(self, parent):
        canvas_size = CELL_SIZE * 9 + GRID_PAD * 2 + 4
        self.canvas = tk.Canvas(parent, width=canvas_size, height=canvas_size,
                                bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack()

        self.cell_rects = {}
        self.cell_texts = {}

        for r in range(9):
            for c in range(9):
                x0 = GRID_PAD + c * CELL_SIZE + (c//3) * 2
                y0 = GRID_PAD + r * CELL_SIZE + (r//3) * 2
                x1 = x0 + CELL_SIZE - 1
                y1 = y0 + CELL_SIZE - 1
                rect = self.canvas.create_rectangle(x0, y0, x1, y1,
                                                    fill=BG_CELL,
                                                    outline=BG_THIN_LINE,
                                                    width=1, tags=f"cell_{r}_{c}")
                text = self.canvas.create_text((x0+x1)//2, (y0+y1)//2,
                                               text="",
                                               font=FONT_CELL,
                                               fill=FG_GIVEN,
                                               tags=f"text_{r}_{c}")
                self.cell_rects[(r,c)] = rect
                self.cell_texts[(r,c)] = text

        for br in range(3):
            for bc in range(3):
                x0 = GRID_PAD + bc*3*CELL_SIZE + bc*2
                y0 = GRID_PAD + br*3*CELL_SIZE + br*2
                x1 = x0 + CELL_SIZE*3 - 1
                y1 = y0 + CELL_SIZE*3 - 1
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             outline=BG_THICK_LINE,
                                             width=3, fill="")

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.bind("<Key>", self._on_key)

    def _build_controls(self, parent):
        tk.Label(parent, text="Load Puzzle", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w")
        self.puzzle_var = tk.StringVar(value="Easy (Standard)")
        for name in SAMPLE_PUZZLES:
            rb = tk.Radiobutton(parent, text=name, variable=self.puzzle_var,
                                value=name, font=FONT_LABEL,
                                bg=BG_PANEL, fg=FG_LABEL,
                                selectcolor=BG_BTN_SEC,
                                activebackground=BG_PANEL,
                                activeforeground=FG_MAIN,
                                command=lambda n=name: self._load_puzzle(n))
            rb.pack(anchor="w", pady=1)

        self._sep(parent)

        tk.Label(parent, text=" Extra Constraints", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w")
        for var, label, icon in [
            (self.var_diag,   "Diagonal Sudoku", "↗"),
            (self.var_knight, "Knight's Move",   "♞"),
            (self.var_king,   "King's Move",     "♚"),
        ]:
            cb = tk.Checkbutton(parent, text=f"{icon}  {label}",
                                variable=var,
                                font=FONT_LABEL,
                                bg=BG_PANEL, fg=FG_LABEL,
                                selectcolor=BG_BTN_SEC,
                                activebackground=BG_PANEL,
                                activeforeground=FG_MAIN)
            cb.pack(anchor="w", pady=1)

        self._sep(parent)

        tk.Label(parent, text="Options", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w")
        tk.Checkbutton(parent, text="Animate solving steps",
                       variable=self.var_anim,
                       font=FONT_LABEL, bg=BG_PANEL, fg=FG_LABEL,
                       selectcolor=BG_BTN_SEC,
                       activebackground=BG_PANEL, activeforeground=FG_MAIN
                       ).pack(anchor="w", pady=1)

        self._sep(parent)

        tk.Label(parent, text="Actions", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w", pady=(0,6))

        self._btn(parent, "Solve Puzzle",  BG_BTN_ACC, BG_BTN_ACC_HOV, self._solve)
        self._btn(parent, "Reset Grid",   BG_BTN_ACC, BG_BTN_ACC_HOV, self._reset)
        self._btn(parent, "Clear All",    BG_BTN_ACC, BG_BTN_ACC_HOV, self._clear)

        self._sep(parent)

        tk.Label(parent, text="Statistics", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w")
        self.stat_nodes = tk.StringVar(value="Nodes explored: —")
        self.stat_time  = tk.StringVar(value="Time elapsed: —")
        self.stat_steps = tk.StringVar(value="Steps taken: —")
        for sv in [self.stat_nodes, self.stat_time, self.stat_steps]:
            tk.Label(parent, textvariable=sv, font=FONT_STATUS,
                     bg=BG_PANEL, fg=FG_LABEL).pack(anchor="w")

        self._sep(parent)

        tk.Label(parent, text="Legend", font=FONT_HEAD,
                 bg=BG_PANEL, fg=FG_TITLE).pack(anchor="w")
        for color, label in [
            (BG_GIVEN,   "Given clue"),
            (BG_SOLVED,  "AI-solved"),
            (BG_SELECTED,"Selected"),
            (BG_ERROR,   "Conflict"),
        ]:
            row = tk.Frame(parent, bg=BG_PANEL)
            row.pack(anchor="w", pady=1)
            tk.Label(row, bg=color, width=2, height=1, relief=tk.FLAT).pack(side=tk.LEFT, padx=(0,6))
            tk.Label(row, text=label, font=FONT_STATUS,
                     bg=BG_PANEL, fg=FG_LABEL).pack(side=tk.LEFT)

    def _sep(self, parent):
        tk.Frame(parent, bg=BG_THICK_LINE, height=1).pack(fill=tk.X, pady=8)

    def _btn(self, parent, text, bg, hover_bg, cmd):
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                        bg=bg, fg=FG_BTN,
                        activebackground=hover_bg, activeforeground=FG_BTN,
                        relief=tk.FLAT, padx=12, pady=8,
                        cursor="hand2", command=cmd)
        btn.pack(pady=3, fill=tk.X)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _cell_xy(self, r, c):
        x0 = GRID_PAD + c * CELL_SIZE + (c//3) * 2
        y0 = GRID_PAD + r * CELL_SIZE + (r//3) * 2
        return x0, y0, x0+CELL_SIZE-1, y0+CELL_SIZE-1

    def _draw_cell(self, r, c, force_color=None):
        val   = self.cell_vals[r][c]
        state = self.cell_state[r][c]

        if force_color:
            color = force_color
        elif self.selected == (r, c):
            color = BG_SELECTED
        elif state == "given":
            color = BG_GIVEN
        elif state == "solved":
            color = BG_SOLVED
        elif state == "error":
            color = BG_ERROR
        else:
            color = BG_CELL

        fg = FG_GIVEN if state in ("given","empty") else FG_SOLVED
        if self.selected == (r, c):
            fg = "#FFFFFF"

        self.canvas.itemconfig(self.cell_rects[(r,c)], fill=color)
        self.canvas.itemconfig(self.cell_texts[(r,c)],
                               text=str(val) if val else "",
                               fill=fg)

    def _redraw_all(self):
        for r in range(9):
            for c in range(9):
                self._draw_cell(r, c)

    def _on_canvas_click(self, event):
        if self.solving:
            return
        for r in range(9):
            for c in range(9):
                x0, y0, x1, y1 = self._cell_xy(r, c)
                if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                    prev = self.selected
                    self.selected = (r, c)
                    if prev:
                        self._draw_cell(*prev)
                    self._draw_cell(r, c)
                    self.focus_set()
                    return

    def _on_key(self, event):
        if self.solving or self.selected is None:
            return
        r, c = self.selected
        if (r, c) in self.given:
            return
        if event.char in "123456789":
            self.cell_vals[r][c] = int(event.char)
            self.cell_state[r][c] = "empty"
            self._draw_cell(r, c)
            self._check_conflicts()
        elif event.keysym in ("BackSpace", "Delete", "0"):
            self.cell_vals[r][c] = 0
            self.cell_state[r][c] = "empty"
            self._draw_cell(r, c)
            self._check_conflicts()

    def _check_conflicts(self):
        for r in range(9):
            for c in range(9):
                if self.cell_state[r][c] == "error":
                    self.cell_state[r][c] = "empty"

        for r in range(9):
            for c in range(9):
                val = self.cell_vals[r][c]
                if val == 0:
                    continue
                peers = get_peers(r, c,
                                  self.var_diag.get(),
                                  self.var_knight.get(),
                                  self.var_king.get())
                for pr, pc in peers:
                    if self.cell_vals[pr][pc] == val:
                        self.cell_state[r][c] = "error"
                        self.cell_state[pr][pc] = "error"
        self._redraw_all()

    def _load_puzzle(self, name):
        if self.solving:
            return
        puzzle = SAMPLE_PUZZLES[name]
        self.given = set()
        for r in range(9):
            for c in range(9):
                v = puzzle[r][c]
                self.cell_vals[r][c]  = v
                self.cell_state[r][c] = "given" if v else "empty"
                if v:
                    self.given.add((r, c))
        self.selected = None
        self._redraw_all()
        self.status_var.set(f"Loaded: {name} — press ⚡ Solve to run the AI solver.")
        self.stat_nodes.set("Nodes explored: —")
        self.stat_time.set("Time elapsed: —")
        self.stat_steps.set("Steps taken: —")

    def _reset(self):
        if self.solving:
            return
        for r in range(9):
            for c in range(9):
                if (r, c) not in self.given:
                    self.cell_vals[r][c]  = 0
                    self.cell_state[r][c] = "empty"
        self.selected = None
        self._redraw_all()
        self.status_var.set("Grid reset to original clues.")

    def _clear(self):
        if self.solving:
            return
        self.given = set()
        for r in range(9):
            for c in range(9):
                self.cell_vals[r][c]  = 0
                self.cell_state[r][c] = "empty"
        self.selected = None
        self._redraw_all()
        self.status_var.set("Grid cleared — enter your own puzzle!")

    def _solve(self):
        if self.solving:
            return

        grid = [[self.cell_vals[r][c] for c in range(9)] for r in range(9)]

        for r in range(9):
            for c in range(9):
                v = grid[r][c]
                if v == 0:
                    continue
                peers = get_peers(r, c,
                                  self.var_diag.get(),
                                  self.var_knight.get(),
                                  self.var_king.get())
                for pr, pc in peers:
                    if grid[pr][pc] == v:
                        messagebox.showerror("Invalid Puzzle",
                                             f"Conflict at ({r+1},{c+1})! "
                                             "Please fix the puzzle first.")
                        return

        self.solving = True
        self.status_var.set("🔄  AI solver running…  (AC-3 → MRV+LCV+Backtracking)")
        self.update()

        def run():
            solver = SudokuSolver(grid,
                                  use_diagonal=self.var_diag.get(),
                                  use_knight=self.var_knight.get(),
                                  use_king=self.var_king.get())
            t0  = time.perf_counter()
            sol = solver.solve()
            elapsed = time.perf_counter() - t0
            self.after(0, lambda: self._on_solved(sol, solver, elapsed))

        threading.Thread(target=run, daemon=True).start()

    def _on_solved(self, sol, solver, elapsed):
        if sol is None:
            self.solving = False
            self.status_var.set("No solution found with current constraints.")
            messagebox.showwarning("No Solution",
                                   "The puzzle has no valid solution\nwith the selected constraints.")
            return

        if self.var_anim.get() and solver.steps:
            fwd = [(r,c,v) for r,c,v in solver.steps if v != 0]
            self._anim_steps = fwd
            self._anim_sol   = sol
            self._anim_solver = solver
            self._anim_elapsed = elapsed
            self._anim_idx = 0
            self._animate_step()
        else:
            self._apply_solution(sol, solver, elapsed)

    def _animate_step(self):
        if self._anim_idx < len(self._anim_steps):
            r, c, v = self._anim_steps[self._anim_idx]
            if (r,c) not in self.given:
                self.cell_vals[r][c]  = v
                self.cell_state[r][c] = "solved"
                self._draw_cell(r, c)
            self._anim_idx += 1
            self.after(18, self._animate_step)
        else:
            self._apply_solution(self._anim_sol, self._anim_solver, self._anim_elapsed)

    def _apply_solution(self, sol, solver, elapsed):
        for r in range(9):
            for c in range(9):
                if (r,c) not in self.given:
                    self.cell_vals[r][c]  = sol[r][c]
                    self.cell_state[r][c] = "solved"
        self.selected = None
        self._redraw_all()
        self.solving = False

        constraints = []
        if self.var_diag.get():   constraints.append("Diagonal")
        if self.var_knight.get(): constraints.append("Knight")
        if self.var_king.get():   constraints.append("King")
        c_str = " + ".join(constraints) if constraints else "Standard only"

        self.stat_nodes.set(f"Nodes explored: {solver.nodes:,}")
        self.stat_time.set(f"Time elapsed:   {elapsed*1000:.1f} ms")
        self.stat_steps.set(f"Steps taken:    {len([s for s in solver.steps if s[2]!=0]):,}")
        self.status_var.set(f"Solved in {elapsed*1000:.1f} ms  |  Constraints: {c_str}")
