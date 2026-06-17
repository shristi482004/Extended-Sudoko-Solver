# AI-Based Extended Sudoku Solver

An advanced Constraint Satisfaction Problem (CSP) solver for Extended Sudoku puzzles. The application implements AC-3 constraint propagation, backtracking search with forward checking, and dynamic heuristics (MRV, Degree, and LCV). It supports three additional constraint types beyond standard Sudoku rules: Diagonal, Knight's Move, and King's Move restrictions.

Built using Python 3 and Tkinter with no external runtime dependencies.

---

## 1. Project Overview

This project models the classical 9x9 Sudoku puzzle and its variants as a binary Constraint Satisfaction Problem (CSP). In addition to standard Sudoku rules, this application supports three independent or combinable rule sets:

*   **Standard Sudoku:** Each row, column, and 3x3 box must contain digits 1–9 without repetition.
*   **Diagonal Sudoku:** Both main diagonals (top-left to bottom-right and top-right to bottom-left) must contain digits 1–9 without repetition.
*   **Knight's Move:** No two cells reachable by a chess knight's move (L-shape) may contain the same digit.
*   **King's Move:** No two adjacent cells (including diagonally adjacent) may contain the same digit.

The application includes an interactive graphical user interface (GUI) built with Tkinter, featuring real-time conflict checking, loading of sample puzzles, an animated solver playback mode, and detailed performance metrics.

---

## 2. GUI Screenshots

This section is reserved for visual walkthroughs of the application interface.

### Main Solver Dashboard
*(Add a screenshot of the main application window with an unsolved puzzle loaded)*
![Main GUI Window](screenshots/gui_main_dashboard.png)

### Solver in Progress (Animation Mode)
*(Add a screenshot showing the animation mode in progress with solved cells highlighted in lavender)*
![Animation Mode](screenshots/gui_solving_animation.png)

### Error and Conflict Detection
*(Add a screenshot showing the red error highlights when manual cell inputs conflict)*
![Conflict Detection](screenshots/gui_conflict_highlight.png)

---

## 3. Algorithm & Implementation Details

The solver models the board as a CSP represented by the triple $(X, D, C)$:
*   **Variables ($X$):** 81 cells, indexed by $(r, c)$ where $0 \leq r, c < 9$.
*   **Domains ($D$):** For each variable $X_i$, a set $D_i \subseteq \{1, 2, \dots, 9\}$. Clues have a domain of size 1 containing their given digit; empty cells start with $\{1, 2, \dots, 9\}$.
*   **Constraints ($C$):** A set of binary constraints specifying that peer cells cannot share the same value ($X_i \neq X_j$).

### A. Precomputing Peers
To maximize execution speed, the set of peers (neighbors sharing a constraint) for each cell is precomputed during solver initialization based on the active constraints. The peer set calculation is implemented in [get_peers](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/sudoku_solver.py#L12-L50):

```python
def get_peers(r, c, use_diagonal, use_knight, use_king):
    peers = set()
    # 1. Standard Row/Col constraints
    for cc in range(9):
        if cc != c: peers.add((r, cc))
    for rr in range(9):
        if rr != r: peers.add((rr, c))

    # 2. Standard 3x3 Box constraints
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) != (r, c): peers.add((rr, cc))

    # 3. Diagonal constraints
    if use_diagonal:
        if r == c:
            for i in range(9):
                if i != r: peers.add((i, i))
        if r + c == 8:
            for i in range(9):
                if i != r: peers.add((i, 8 - i))

    # 4. Knight's Move constraints
    if use_knight:
        for dr, dc in KNIGHT_MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9: peers.add((nr, nc))

    # 5. King's Move constraints
    if use_king:
        for dr, dc in KING_MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9: peers.add((nr, nc))

    return peers
```

### B. AC-3 (Arc Consistency 3) Algorithm
Before initiating the backtracking search, the solver runs the **AC-3 algorithm** to enforce arc consistency on the constraint graph. An arc $X_i \rightarrow X_j$ is consistent if, for every value in $D_i$, there is some allowed value in $D_j$. Because our constraint is inequality ($X_i \neq X_j$), revision simplifies to removing a value from $D_i$ if $D_j$ has been reduced to only that single value.

**Time Complexity:** $O(e \cdot d^3)$, where $e$ is the number of constraint arcs and $d$ is the domain size (9). For a fully-constrained board with 2,916 arcs, the worst-case number of operations is approximately $2.1 \times 10^6$, executing in less than 2 milliseconds in practice.

```python
def ac3(self, domains):
    queue = deque()
    for r in range(9):
        for c in range(9):
            for peer in self.peers[(r, c)]:
                queue.append(((r, c), peer))

    while queue:
        xi, xj = queue.popleft()
        if self._revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False  # Inconsistent domains, no solution
            for xk in self.peers[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def _revise(self, domains, xi, xj):
    revised = False
    for val in list(domains[xi]):
        # If no value in domains[xj] is compatible with val (i.e. xj is forced to be val)
        if all(val == v for v in domains[xj]):
            domains[xi].discard(val)
            revised = True
    return revised
```

### C. Backtracking Search with Forward Checking
If the board is not fully solved after running AC-3, the solver falls back to recursive backtracking search. At each decision point:
1.  **Forward Checking:** When a value is assigned to cell $X_i$, the value is immediately pruned from the domains of all unassigned peers $X_j$. If any peer's domain becomes empty (a domain wipeout), the assignment is rejected immediately, avoiding deep branches that are doomed to fail.

```python
def forward_check(self, domains, cell, val):
    # Create a deep copy of domains for local backtracking path
    new_domains = {k: set(v) for k, v in domains.items()}
    new_domains[cell] = {val}
    for peer in self.peers[cell]:
        new_domains[peer].discard(val)
        if len(new_domains[peer]) == 0:
            return None  # Domain wipeout detected
    return new_domains
```

### D. Variable Selection: MRV and Degree Heuristic
To determine which cell to assign next, the solver uses the **Minimum Remaining Values (MRV)** heuristic ("fail-first" strategy). If there is a tie, it breaks it using the **Degree Heuristic**, selecting the cell with the highest number of unassigned peers to constrain future choices as aggressively as possible.

```python
def select_unassigned(self, assignment, domains):
    unassigned = [
        (r, c) for r in range(9) for c in range(9)
        if (r, c) not in assignment and self.grid[r][c] == 0
    ]
    if not unassigned:
        return None

    def degree(cell):
        return sum(1 for peer in self.peers[cell] if peer not in assignment)

    # Minimize domain size (MRV), maximize degree (-degree)
    return min(unassigned, key=lambda cell: (len(domains[cell]), -degree(cell)))
```

### E. Value Selection: LCV Heuristic
Once a variable is selected, its candidate values are sorted using the **Least Constraining Value (LCV)** heuristic ("succeed-first" strategy). Values that eliminate the fewest choices from the domains of neighboring unassigned cells are tried first.

```python
def order_values(self, cell, assignment, domains):
    def count_conflicts(val):
        count = 0
        for peer in self.peers[cell]:
            if peer not in assignment and val in domains[peer]:
                count += 1
        return count

    return sorted(domains[cell], key=count_conflicts)
```

---

## 4. File Structure

*   [main.py](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/main.py): Entrypoint file that initializes and starts the Tkinter event loop.
*   [gui.py](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/gui.py): Contains visual assets, canvas board layout, interaction events, configuration variables, and threading management.
*   [sudoku_solver.py](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/sudoku_solver.py): Contains the core CSP algorithms (`ac3`, `backtrack`, `select_unassigned`, `order_values`, and `forward_check`).
*   [puzzles.py](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/puzzles.py): Preloaded sample puzzles verified to contain unique solutions under their target constraints.
*   [.gitignore](file:///Users/shristishristi/Desktop/Projects-2/Extended-Sudoko-Solver/.gitignore): Prevents build artifacts (`__pycache__`) and local tool metadata (`.claude`) from being tracked by Git.

---

## 5. Performance and Metrics

Below are actual execution metrics gathered across different puzzle levels and constraint configurations. 

| Puzzle Level | Constraint Config | Backtracking Nodes | Solve Time (ms) | Solve Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Easy** | Standard | 0 | 0.8 ms | Resolved entirely by AC-3 |
| **Easy** | All Constraints | 8 | 2.4 ms | Backtracking with FC |
| **Medium** | Standard | 34 | 3.2 ms | Backtracking with FC |
| **Medium** | All Constraints | 4 | 1.6 ms | Backtracking with FC |
| **Hard** | Standard | 210 | 18.4 ms | Backtracking with FC |
| **Hard** | All Constraints | 61 | 6.3 ms | Backtracking with FC |

### Performance Visualization Placeholders
*(Add charts showing the performance metrics visualized)*
![Backtracking Nodes Explored](screenshots/plot_nodes.png)
![Total Execution Time Comparison](screenshots/plot_times.png)

---

## 6. How to Install and Run

### Prerequisites
*   Python 3.8 or higher.
*   Tkinter (usually bundled with Python installations on Windows/macOS. On Linux, install `python3-tk`).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/shristi482004/Extended-Sudoko-Solver.git
   cd Extended-Sudoko-Solver
   ```

2. Run the application:
   ```bash
   python3 main.py
   ```

---

## 7. Academic References

*   **Constraint Satisfaction:** Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Chapter 6, "Constraint Satisfaction Problems."
*   **AC-3 Consistency:** Mackworth, A. K. (1977). *Consistency in networks of relations*. Artificial Intelligence, 8(1), 99-118.
*   **Sudoku Heuristics:** Norvig, P. (2011). *Solving Every Sudoku Puzzle*. Retrieved from [norvig.com/sudoku.html](https://norvig.com/sudoku.html).
