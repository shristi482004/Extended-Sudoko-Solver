"""Sudoku solver module.

This module exposes the SudokuSolver class and peer generation logic.
"""

from collections import deque

KNIGHT_MOVES = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
KING_MOVES   = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]


def get_peers(r, c, use_diagonal, use_knight, use_king):
    """Return all cells that (r,c) must differ from, given active constraints."""
    peers = set()
    for cc in range(9):
        if cc != c:
            peers.add((r, cc))
    for rr in range(9):
        if rr != r:
            peers.add((rr, c))

    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) != (r, c):
                peers.add((rr, cc))

    if use_diagonal:
        if r == c:
            for i in range(9):
                if i != r:
                    peers.add((i, i))
        if r + c == 8:
            for i in range(9):
                if i != r:
                    peers.add((i, 8 - i))

    if use_knight:
        for dr, dc in KNIGHT_MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9:
                peers.add((nr, nc))

    if use_king:
        for dr, dc in KING_MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9:
                peers.add((nr, nc))

    return peers


class SudokuSolver:
    def __init__(self, grid, use_diagonal=True, use_knight=True, use_king=True):
        self.grid = [row[:] for row in grid]
        self.use_diagonal = use_diagonal
        self.use_knight = use_knight
        self.use_king = use_king
        self.nodes = 0
        self.solution = None
        self.steps = []

        self.domains = {}
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    self.domains[(r, c)] = set(range(1, 10))
                else:
                    self.domains[(r, c)] = {grid[r][c]}

        self.peers = {}
        for r in range(9):
            for c in range(9):
                self.peers[(r, c)] = get_peers(r, c, use_diagonal, use_knight, use_king)

    def ac3(self, domains):
        # Time complexity: O(e * d^3) where e = number of arcs (≈2916 with all constraints active), d = max domain size = 9
        queue = deque()
        for r in range(9):
            for c in range(9):
                for peer in self.peers[(r, c)]:
                    queue.append(((r, c), peer))

        while queue:
            xi, xj = queue.popleft()
            if self._revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False
                for xk in self.peers[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains, xi, xj):
        revised = False
        for val in list(domains[xi]):
            if all(val == v for v in domains[xj]):
                domains[xi].discard(val)
                revised = True
        return revised

    def select_unassigned(self, assignment, domains):
        unassigned = [
            (r, c)
            for r in range(9)
            for c in range(9)
            if (r, c) not in assignment and self.grid[r][c] == 0
        ]
        if not unassigned:
            return None

        def degree(cell):
            return sum(1 for peer in self.peers[cell] if peer not in assignment)

        return min(unassigned, key=lambda cell: (len(domains[cell]), -degree(cell)))

    def order_values(self, cell, assignment, domains):
        def count_conflicts(val):
            count = 0
            for peer in self.peers[cell]:
                if peer not in assignment and val in domains[peer]:
                    count += 1
            return count

        return sorted(domains[cell], key=count_conflicts)

    def forward_check(self, domains, cell, val):
        new_domains = {k: set(v) for k, v in domains.items()}
        new_domains[cell] = {val}
        for peer in self.peers[cell]:
            new_domains[peer].discard(val)
            if len(new_domains[peer]) == 0:
                return None
        return new_domains

    def backtrack(self, assignment, domains):
        if len(assignment) == sum(
            1
            for r in range(9)
            for c in range(9)
            if self.grid[r][c] == 0
        ):
            return assignment

        cell = self.select_unassigned(assignment, domains)
        if cell is None:
            return assignment

        self.nodes += 1

        for val in self.order_values(cell, assignment, domains):
            consistent = True
            for peer in self.peers[cell]:
                if assignment.get(peer) == val:
                    consistent = False
                    break
            if not consistent:
                continue

            new_domains = self.forward_check(domains, cell, val)
            if new_domains is None:
                continue

            assignment[cell] = val
            self.steps.append((cell[0], cell[1], val))

            result = self.backtrack(assignment, new_domains)
            if result is not None:
                return result

            del assignment[cell]
            self.steps.append((cell[0], cell[1], 0))

        return None

    def solve(self):
        domains = {k: set(v) for k, v in self.domains.items()}
        if not self.ac3(domains):
            return None

        assignment = {}
        result = self.backtrack(assignment, domains)
        if result is None:
            return None

        sol = [row[:] for row in self.grid]
        for (r, c), val in result.items():
            sol[r][c] = val
        self.solution = sol
        return sol

    def count_solutions(self, limit=2):
        """Count solutions up to `limit`, stopping early once reached.

        Runs as an isolated search — does not touch self.solution/self.steps.
        """
        domains = {k: set(v) for k, v in self.domains.items()}
        if not self.ac3(domains):
            return 0

        total_unassigned = sum(
            1 for r in range(9) for c in range(9) if self.grid[r][c] == 0
        )
        count = 0

        def backtrack(assignment, domains):
            nonlocal count
            if count >= limit:
                return
            if len(assignment) == total_unassigned:
                count += 1
                return

            cell = self.select_unassigned(assignment, domains)
            if cell is None:
                count += 1
                return

            for val in self.order_values(cell, assignment, domains):
                if count >= limit:
                    return
                consistent = True
                for peer in self.peers[cell]:
                    if assignment.get(peer) == val:
                        consistent = False
                        break
                if not consistent:
                    continue

                new_domains = self.forward_check(domains, cell, val)
                if new_domains is None:
                    continue

                assignment[cell] = val
                backtrack(assignment, new_domains)
                del assignment[cell]

                if count >= limit:
                    return

        backtrack({}, domains)
        return count
