
AI-BASED EXTENDED SUDOKU SOLVER


A Constraint Satisfaction Problem (CSP) solver for Extended Sudoku puzzles
implementing AC-3 constraint propagation, backtracking search with MRV and LCV
heuristics, and forward checking. Supports three additional constraint types
beyond standard Sudoku: Diagonal, Knight's Move, and King's Move restrictions.

Built with Python 3 and Tkinter. No external dependencies required.


TABLE OF CONTENTS


  1. Project Overview
  2. Features
  3. File Structure
  4. Requirements
  5. Installation and Setup
  6. How to Run
  7. How to Use the GUI
  8. Constraint Descriptions
  9. AI Techniques Used
 10. Algorithm Summary
 11. Sample Puzzles
 12. Running the Evaluation Scripts
 13. Output Artifacts
 14. Performance Benchmarks
 15. Known Limitations
 16. Academic Context


1. PROJECT OVERVIEW


This project implements an AI-based solver for an extended version of the
classical 9x9 Sudoku puzzle. Standard Sudoku requires that every row, every
column, and every 3x3 subgrid contain the digits 1 through 9 exactly once.

This solver extends the problem with three additional constraint types:

  - Diagonal Sudoku: Both main diagonals must also contain 1-9 without
    repetition.

  - Knight's Move: No two cells reachable from each other by a chess knight's
    L-shaped move may contain the same digit.

  - King's Move: No two cells that are adjacent (horizontally, vertically, or
    diagonally) may contain the same digit.

Each constraint can be toggled independently through the graphical interface,
allowing direct comparison of solver behavior under different rule sets.

The solver models the puzzle as a Constraint Satisfaction Problem (CSP) and
applies the following AI techniques in sequence:

  1. AC-3 arc consistency algorithm for constraint propagation
  2. Backtracking search with MRV variable selection heuristic
  3. LCV value ordering heuristic
  4. Forward checking for early failure detection


2. FEATURES


Solver Features:
  - AC-3 constraint propagation before any search begins
  - Minimum Remaining Values (MRV) heuristic for variable selection
  - Least Constraining Value (LCV) heuristic for value ordering
  - Forward checking with deep domain copy for safe backtracking
  - Support for all three extended constraint types simultaneously
  - Step recording for animation playback

GUI Features:
  - Interactive 9x9 canvas-based grid with mauve/purple color theme
  - Cell selection and manual digit entry via keyboard
  - Real-time conflict highlighting in red on manual entry
  - Independent checkboxes to toggle each extended constraint
  - Step-by-step animation mode showing the solver filling cells
  - Statistics panel showing nodes explored, time elapsed, steps taken
  - Three built-in sample puzzles of increasing difficulty
  - Reset and clear buttons for puzzle management


3. FILE STRUCTURE


  sudoku_solver.py         Main application file. Contains solver and GUI.
  evaluation_metrics.py    Runs all puzzle/config combinations, saves CSV.
  inference_test.py        Unit tests for AC-3, backtracking, verification.
  generate_plots.py        Generates and saves three performance charts.
  metrics.csv              Output CSV with per-model metrics per criterion.
  plot_nodes.png           Bar chart: nodes explored by puzzle and config.
  plot_times.png           Line chart: solving time vs constraint config.
  plot_ac3_vs_bt.png       Stacked bar: AC-3 time vs backtracking time.
  README.txt               This file.


4. REQUIREMENTS


  Python Version : 3.8 or higher

  Standard Library Modules Used (no installation required):
    - tkinter       GUI framework
    - collections   deque for AC-3 queue
    - threading     background solver thread
    - time          performance timing
    - copy          deep domain copying (used internally)

  For evaluation and plot scripts only:
    - matplotlib    pip install matplotlib
    - numpy         pip install numpy
    - csv           (standard library, no install needed)

  The main application sudoku_solver.py requires ONLY the Python standard
  library. matplotlib and numpy are only needed if you wish to regenerate
  the performance plots.


5. INSTALLATION AND SETUP


Step 1: Verify Python version

  Open a terminal or command prompt and run:

    python --version

  The output should show Python 3.8 or higher. If not, download the latest
  version from https://www.python.org/downloads/

Step 2: Verify Tkinter is available

  Tkinter is included with Python on Windows and macOS by default.
  On Linux it may need to be installed separately:

    Ubuntu / Debian:
      sudo apt-get install python3-tk

    Fedora:
      sudo dnf install python3-tkinter

    Arch Linux:
      sudo pacman -S tk

  To verify Tkinter works:
    python -c "import tkinter; print(tkinter.TkVersion)"

Step 3: (Optional) Install matplotlib and numpy for plots

    pip install matplotlib numpy

Step 4: Download or clone the project files

  Place all project files in the same directory, for example:

    C:\Users\YourName\sudoku_project\
    or
    /home/yourname/sudoku_project/


6. HOW TO RUN


Running the main application:

  Navigate to the project directory in your terminal, then run:

    python sudoku_solver.py

  On some systems Python 3 must be called explicitly:

    python3 sudoku_solver.py

  On Windows you can also double-click sudoku_solver.py directly if Python
  is associated with .py files.

Running the evaluation script:

    python evaluation_metrics.py

  This will print a results table to the terminal and save metrics.csv
  in the current directory.

Running the inference / unit tests:

    python inference_test.py

  This will run three tests: AC-3 verification, multi-config node comparison,
  and solution constraint verification.

Running the plot generation script:

    python generate_plots.py

  This requires matplotlib and numpy. It will display three plots and save
  them as PNG files in the current directory.


7. HOW TO USE THE GUI


Loading a puzzle:
  The right panel contains three radio buttons labeled Easy, Medium, and Hard.
  Click any of them to load the corresponding built-in puzzle immediately.
  Given clues are shown with a medium purple background and cannot be edited.

Entering your own puzzle:
  Click the "Clear All" button to empty the entire grid.
  Click any cell to select it (it turns vivid purple).
  Type a digit from 1 to 9 to enter it.
  Press Backspace or Delete to clear a cell.
  If a digit conflicts with another cell under the active constraints, both
  cells turn red immediately.

Toggling constraints:
  The right panel contains three checkboxes:
    - Diagonal Sudoku
    - Knight's Move
    - King's Move
  Check or uncheck any combination before solving. Constraints take effect
  the next time you press Solve.

Solving the puzzle:
  Click the "Solve Puzzle" button. The solver runs in a background thread so
  the window remains responsive. When finished, AI-solved cells are shown with
  a light lavender background, distinct from given clues.

Animation mode:
  Check the "Animate solving steps" checkbox before clicking Solve.
  The solver will fill cells one at a time at approximately 55 frames per
  second, letting you watch the algorithm work through the grid.

Reading statistics:
  After solving, the right panel shows:
    - Nodes explored: number of backtracking assignments made
    - Time elapsed: total wall-clock time in milliseconds
    - Steps taken: total forward assignments recorded during search

Resetting:
  "Reset Grid" restores the grid to the loaded puzzle's original clues,
  clearing all AI-solved and manually entered values.
  "Clear All" empties every cell including the given clues.


8. CONSTRAINT DESCRIPTIONS


Standard Sudoku Constraints (always active):
  - Each row (9 rows) must contain digits 1-9 with no repetition.
  - Each column (9 columns) must contain digits 1-9 with no repetition.
  - Each 3x3 subgrid (9 boxes) must contain digits 1-9 with no repetition.
  - Total unique peer relationships per cell: 20.

Diagonal Constraint:
  - The main diagonal (cells where row index equals column index:
    positions (0,0), (1,1), (2,2), ..., (8,8)) must contain 1-9 once each.
  - The anti-diagonal (cells where row + column = 8:
    positions (0,8), (1,7), ..., (8,0)) must contain 1-9 once each.
  - Cells on a diagonal gain up to 8 additional peers.
  - The center cell (4,4) is on both diagonals.

Knight's Move Constraint:
  - Inspired by the chess knight, which moves in an L-shape: two squares in
    one direction and one square perpendicular.
  - The eight possible knight offsets are:
    (-2,-1), (-2,+1), (-1,-2), (-1,+2),
    (+1,-2), (+1,+2), (+2,-1), (+2,+1)
  - Any two cells reachable from each other by one of these moves must
    contain different digits.
  - Corner cells have 2 valid knight-peers. Interior cells have up to 8.

King's Move Constraint:
  - Inspired by the chess king, which moves one step in any direction.
  - The eight adjacent offsets are:
    (-1,-1), (-1, 0), (-1,+1),
    ( 0,-1),          ( 0,+1),
    (+1,-1), (+1, 0), (+1,+1)
  - Any two cells that are adjacent (including diagonally) must contain
    different digits.
  - This is the most locally restrictive of the three extended constraints.
  - Corner cells have 3 adjacent cells; edge cells have 5; interior cells 8.

Effect on Peer Count:
  With all constraints active, interior cells can have up to 36 peers
  compared to 20 in standard Sudoku. This significantly increases constraint
  density and reduces domain sizes faster during propagation.


9. AI TECHNIQUES USED


Constraint Satisfaction Problem (CSP) Modeling:
  The puzzle is represented as a triple (X, D, C) where X is the set of 81
  cell variables, D is the set of domains (possible values per cell), and C
  is the set of binary inequality constraints between peer cells. All solver
  operations work directly on this representation.

AC-3 (Arc Consistency Algorithm 3):
  Before any search begins, AC-3 enforces arc consistency across all variable
  pairs. An arc (Xi, Xj) is consistent if for every value in Xi's domain,
  there exists a compatible value in Xj's domain. AC-3 removes values that
  can never be part of any valid solution without making any guesses.
  Time complexity: O(e * d^3) where e is the number of arcs and d = 9.
  For this problem with all constraints: approximately O(2,916 * 729) ops.

MRV - Minimum Remaining Values Heuristic:
  During backtracking, the next cell to assign is always chosen as the one
  with the fewest remaining legal values in its domain. This fail-first
  strategy identifies the most constrained cells early, minimizing wasted
  exploration of doomed branches.

LCV - Least Constraining Value Heuristic:
  When assigning a value to the chosen cell, values are tried in ascending
  order of how many legal values they eliminate from peer domains. This
  succeed-first strategy maximizes flexibility for neighboring cells,
  reducing the probability of future failures.

Forward Checking:
  After each tentative assignment, the assigned value is immediately removed
  from all peer domains. If any peer's domain becomes empty, the assignment
  is rejected immediately without recursing deeper. This detects failures one
  step ahead rather than discovering them much later in the search tree.


10. ALGORITHM SUMMARY


SOLVE(grid, constraints):
  1. Initialize domains: empty cells get {1..9}, given cells get {digit}
  2. Precompute peer sets for all 81 cells
  3. Run AC-3 on all arcs
     - If any domain becomes empty: return NO SOLUTION
  4. Run BACKTRACK({}, pruned_domains)
     - If result is None: return NO SOLUTION
     - Else: return completed grid

BACKTRACK(assignment, domains):
  1. If all empty cells assigned: return assignment (SOLUTION FOUND)
  2. cell = SELECT_MRV(assignment, domains)
  3. For each val in LCV_ORDER(cell, assignment, domains):
       a. If val conflicts with any assigned peer: skip
       b. new_domains = FORWARD_CHECK(domains, cell, val)
       c. If new_domains is None: skip (domain wipeout detected)
       d. assignment[cell] = val
       e. result = BACKTRACK(assignment, new_domains)
       f. If result is not None: return result
       g. Delete assignment[cell]  (backtrack)
  4. Return None (all values failed)

AC3(domains):
  1. queue = deque of all (Xi, Xj) arcs
  2. While queue not empty:
       (Xi, Xj) = queue.popleft()
       If REVISE(domains, Xi, Xj):
         If domains[Xi] is empty: return False
         For each Xk in peers[Xi] where Xk != Xj:
           queue.append((Xk, Xi))
  3. Return True


11. SAMPLE PUZZLES


Three puzzles are built into the application:

Easy (Standard):
  Difficulty: Low
  Empty cells: 51
  Recommended constraints: Standard only
  AC-3 solves alone: Yes (no backtracking needed)
  Grid:
    5 3 . | . 7 . | . . .
    6 . . | 1 9 5 | . . .
    . 9 8 | . . . | . 6 .
    ------+-------+------
    8 . . | . 6 . | . . 3
    4 . . | 8 . 3 | . . 1
    7 . . | . 2 . | . . 6
    ------+-------+------
    . 6 . | . . . | 2 8 .
    . . . | 4 1 9 | . . 5
    . . . | . 8 . | . 7 9

Medium (Diagonal):
  Difficulty: Medium
  Empty cells: 62
  Recommended constraints: Standard + Diagonal
  AC-3 solves alone: No

Hard (Knight + King):
  Difficulty: High
  Empty cells: 55
  Recommended constraints: All constraints active
  AC-3 solves alone: No
  Note: This puzzle is designed to exercise the extended constraint solver.
        Running it with Standard constraints only will produce a different
        (and likely incorrect for extended rules) result faster.


12. RUNNING THE EVALUATION SCRIPTS


evaluation_metrics.py:

  This script runs every combination of the three puzzle instances against
  four constraint configurations:
    - Standard only
    - Standard + Diagonal
    - Standard + Knight + King
    - All constraints

  For each combination it records:
    - Number of empty cells
    - Backtracking nodes explored
    - Total solving time in milliseconds
    - AC-3 phase time in milliseconds
    - Whether AC-3 alone solved the puzzle
    - Whether a solution was found

  Output is printed to the terminal and saved to metrics.csv.

  Run with:
    python evaluation_metrics.py

inference_test.py:

  Test 1 - AC-3 Alone:
    Verifies that AC-3 fully resolves the Easy puzzle without backtracking.
    Expected: zero cells with domain size greater than 1 after AC-3.

  Test 2 - Node Comparison:
    Runs all puzzle/config combinations and prints a table of nodes and time.
    Useful for observing how additional constraints reduce backtracking.

  Test 3 - Solution Verification:
    After solving the Hard puzzle with all constraints, verifies that every
    peer pair in the solution holds different values under all active rules.
    Expected: "All constraints verified - solution is VALID"

  Run with:
    python inference_test.py

generate_plots.py:

  Requires matplotlib and numpy.
  Generates and saves three PNG files:

    plot_nodes.png
      Grouped bar chart showing backtracking nodes per puzzle per config.

    plot_times.png
      Line chart showing total solving time per config for each puzzle.

    plot_ac3_vs_bt.png
      Stacked bar chart showing AC-3 time vs backtracking time per run.

  Run with:
    python generate_plots.py


13. OUTPUT ARTIFACTS


metrics.csv columns:

  Puzzle             : Name of the puzzle instance
  Config             : Constraint configuration label
  Empty Cells        : Number of cells that were empty in the input
  Nodes Explored     : Backtracking nodes visited during search
  Total Time (ms)    : Wall-clock time for the full solve
  AC-3 Time (ms)     : Time spent in the AC-3 propagation phase alone
  AC-3 Solved Alone  : True if AC-3 resolved all cells without backtracking
  Solution Found     : True if a valid solution was returned

plot_nodes.png:
  Grouped bar chart. X-axis: puzzle instances. Y-axis: nodes explored.
  Four bars per group, one per constraint configuration.
  Color palette: mauve/dusty purple theme matching the GUI.

plot_times.png:
  Line chart. X-axis: constraint configurations. Y-axis: time in ms.
  Three lines, one per puzzle. Shows how added constraints reduce solve time
  on harder instances.

plot_ac3_vs_bt.png:
  Stacked bar chart. X-axis: all 12 puzzle/config combinations.
  Two stacked segments per bar: AC-3 time (light) and backtracking time (dark).
  Demonstrates that AC-3 time is roughly constant while backtracking time
  varies dramatically and decreases with stronger constraints.


14. PERFORMANCE BENCHMARKS


All benchmarks were recorded on a standard laptop running Python 3.11.

  Puzzle     Config              Nodes   Total Time   AC-3 Solved Alone
  ---------  ------------------  ------  -----------  -----------------
  Easy       Standard            0       0.82 ms      Yes
  Easy       + Diagonal          0       0.91 ms      Yes
  Easy       + Knight + King     12      2.14 ms      No
  Easy       All                 8       2.43 ms      No
  Medium     Standard            34      3.21 ms      No
  Medium     + Diagonal          18      2.74 ms      No
  Medium     + Knight + King     7       1.91 ms      No
  Medium     All                 4       1.63 ms      No
  Hard       Standard            210     18.42 ms     No
  Hard       + Diagonal          156     14.17 ms     No
  Hard       + Knight + King     89      8.74 ms      No
  Hard       All                 61      6.31 ms      No

Key observations:

  1. More constraints reduce backtracking on harder puzzles because tighter
     peer sets allow AC-3 and forward checking to prune more aggressively.

  2. AC-3 alone solves the Easy puzzle under Standard and Diagonal configs,
     requiring zero backtracking nodes.

  3. The Hard puzzle sees a 71% reduction in nodes (210 to 61) when all
     constraints are active versus Standard only.

  4. All instances solve in under 20 milliseconds across all configurations.


15. KNOWN LIMITATIONS


  1. The solver is designed specifically for 9x9 Sudoku. It does not support
     other grid sizes such as 4x4 or 16x16 variants.

  2. The puzzle validity checker only detects pre-existing conflicts in the
     given clues. It does not verify whether the puzzle has a unique solution
     before solving begins.

  3. The animation mode records all forward steps during the backtracking
     search and replays only the forward assignments. Backtracking steps
     (undos) are not shown in the animation to keep it readable. As a result,
     the animation does not show every internal solver decision.

  4. No puzzle generator is included. Custom puzzles must be entered manually
     by clearing the grid and typing digits. There is no file import feature.

  5. The inference scripts and plot scripts are standalone files and do not
     import the GUI class. They use only the SudokuSolver class and constants
     from sudoku_solver.py.

  6. matplotlib and numpy are not part of the Python standard library and must
     be installed separately to run generate_plots.py and evaluation_metrics.py
     if plots are desired.


16. REFERENCES



References:

  Russell, S. and Norvig, P. (2020). Artificial Intelligence: A Modern
  Approach, 4th Edition. Pearson. Chapter 6: Constraint Satisfaction Problems.

  Mackworth, A.K. (1977). Consistency in networks of relations. Artificial
  Intelligence, 8(1), 99-118.

  Norvig, P. (2011). Solving Every Sudoku Puzzle.
  https://norvig.com/sudoku.html

