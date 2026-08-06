"""Perfect-maze generation on a rectangular grid wrapped around a cylinder."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from types import MappingProxyType
from typing import Mapping, TypeAlias


Cell: TypeAlias = tuple[int, int]
Edge: TypeAlias = tuple[Cell, Cell]


def _edge(first: Cell, second: Cell) -> Edge:
    return (first, second) if first < second else (second, first)


def cylindrical_neighbors(cell: Cell, rows: int, columns: int) -> tuple[Cell, ...]:
    """Return orthogonal neighbors with circumferential column wraparound."""
    row, column = cell
    if not 0 <= row < rows or not 0 <= column < columns:
        raise ValueError(f"cell {cell} is outside a {rows}x{columns} maze")

    neighbors = [(row, (column - 1) % columns), (row, (column + 1) % columns)]
    if row > 0:
        neighbors.append((row - 1, column))
    if row + 1 < rows:
        neighbors.append((row + 1, column))
    return tuple(neighbors)


@dataclass(frozen=True)
class Maze:
    rows: int
    columns: int
    seed: int
    edges: frozenset[Edge]
    entry: Cell
    exit: Cell
    solution: tuple[Cell, ...]

    @property
    def adjacency(self) -> Mapping[Cell, tuple[Cell, ...]]:
        graph: dict[Cell, list[Cell]] = {
            (row, column): []
            for row in range(self.rows)
            for column in range(self.columns)
        }
        for first, second in self.edges:
            graph[first].append(second)
            graph[second].append(first)
        return MappingProxyType(
            {cell: tuple(sorted(neighbors)) for cell, neighbors in graph.items()}
        )


@dataclass(frozen=True, slots=True)
class MazeMetrics:
    solution_steps: int
    turns: int
    dead_ends: int
    challenge_score: float


@dataclass(frozen=True, slots=True)
class MazeSelection:
    maze: Maze
    metrics: MazeMetrics
    candidate_count: int


def _path_from_parents(
    parents: Mapping[Cell, Cell | None], start: Cell, end: Cell
) -> tuple[Cell, ...]:
    path = [end]
    while path[-1] != start:
        parent = parents[path[-1]]
        if parent is None:
            raise ValueError(f"no path from {start} to {end}")
        path.append(parent)
    path.reverse()
    return tuple(path)


def _breadth_first_tree(
    adjacency: Mapping[Cell, tuple[Cell, ...]], start: Cell
) -> tuple[dict[Cell, Cell | None], dict[Cell, int]]:
    parents: dict[Cell, Cell | None] = {start: None}
    distances = {start: 0}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for neighbor in adjacency[cell]:
            if neighbor not in parents:
                parents[neighbor] = cell
                distances[neighbor] = distances[cell] + 1
                queue.append(neighbor)
    return parents, distances


def generate_perfect_maze(rows: int, columns: int, seed: int) -> Maze:
    """Generate a deterministic spanning-tree maze and select a far axial exit."""
    if rows < 2:
        raise ValueError("rows must be at least 2")
    if columns < 3:
        raise ValueError("columns must be at least 3 for cylindrical wraparound")

    rng = random.Random(seed)
    entry: Cell = (0, 0)
    visited = {entry}
    stack = [entry]
    edges: set[Edge] = set()

    while stack:
        current = stack[-1]
        candidates = [
            neighbor
            for neighbor in cylindrical_neighbors(current, rows, columns)
            if neighbor not in visited
        ]
        if not candidates:
            stack.pop()
            continue

        rng.shuffle(candidates)
        next_cell = candidates[0]
        edges.add(_edge(current, next_cell))
        visited.add(next_cell)
        stack.append(next_cell)

    provisional = Maze(
        rows=rows,
        columns=columns,
        seed=seed,
        edges=frozenset(edges),
        entry=entry,
        exit=(rows - 1, 0),
        solution=(),
    )
    parents, distances = _breadth_first_tree(provisional.adjacency, entry)
    exit_cell = max(
        ((rows - 1, column) for column in range(columns)),
        key=lambda cell: (distances[cell], -cell[1]),
    )
    solution = _path_from_parents(parents, entry, exit_cell)
    return Maze(
        rows=rows,
        columns=columns,
        seed=seed,
        edges=frozenset(edges),
        entry=entry,
        exit=exit_cell,
        solution=solution,
    )


def count_simple_paths(maze: Maze, start: Cell, end: Cell, limit: int = 2) -> int:
    """Count simple graph paths up to ``limit`` for an independent uniqueness check."""
    if limit < 1:
        raise ValueError("limit must be positive")

    count = 0
    stack: list[tuple[Cell, frozenset[Cell]]] = [(start, frozenset({start}))]
    while stack and count < limit:
        current, seen = stack.pop()
        if current == end:
            count += 1
            continue
        for neighbor in maze.adjacency[current]:
            if neighbor not in seen:
                stack.append((neighbor, seen | {neighbor}))
    return count


def _movement_direction(first: Cell, second: Cell, columns: int) -> str:
    row_delta = second[0] - first[0]
    if row_delta:
        return "axial+" if row_delta > 0 else "axial-"
    clockwise = (second[1] - first[1]) % columns
    return "clockwise" if clockwise == 1 else "counterclockwise"


def measure_maze(maze: Maze) -> MazeMetrics:
    """Measure physical puzzle characteristics used for candidate selection."""
    solution_steps = len(maze.solution) - 1
    directions = [
        _movement_direction(first, second, maze.columns)
        for first, second in zip(maze.solution, maze.solution[1:])
    ]
    turns = sum(first != second for first, second in zip(directions, directions[1:]))
    dead_ends = sum(len(neighbors) == 1 for neighbors in maze.adjacency.values())

    node_count = maze.rows * maze.columns
    path_ratio = solution_steps / max(node_count - 1, 1)
    turn_ratio = turns / max(solution_steps - 1, 1)
    dead_end_ratio = dead_ends / node_count
    challenge_score = min(
        1.0,
        0.65 * path_ratio + 0.25 * turn_ratio + 0.10 * dead_end_ratio,
    )
    return MazeMetrics(
        solution_steps=solution_steps,
        turns=turns,
        dead_ends=dead_ends,
        challenge_score=challenge_score,
    )


def generate_maze_for_difficulty(
    rows: int,
    columns: int,
    seed: int,
    difficulty: int,
    candidates: int = 24,
) -> MazeSelection:
    """Select a difficulty quantile from deterministic perfect-maze candidates."""
    if not 1 <= difficulty <= 10:
        raise ValueError("difficulty must be between 1 and 10")
    if candidates < 2:
        raise ValueError("at least two candidates are required")

    ranked: list[tuple[MazeMetrics, Maze]] = []
    for index in range(candidates):
        candidate = generate_perfect_maze(rows, columns, seed + index * 104729)
        ranked.append((measure_maze(candidate), candidate))
    ranked.sort(
        key=lambda item: (
            item[0].challenge_score,
            item[0].solution_steps,
            item[0].turns,
            item[0].dead_ends,
            item[1].seed,
        )
    )
    quantile = (difficulty - 1) / 9.0
    selected_index = round(quantile * (len(ranked) - 1))
    metrics, maze = ranked[selected_index]
    return MazeSelection(maze=maze, metrics=metrics, candidate_count=candidates)
