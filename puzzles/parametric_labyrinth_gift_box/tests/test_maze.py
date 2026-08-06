from collections import deque
import unittest

from labyrinth_box.maze import (
    count_simple_paths,
    cylindrical_neighbors,
    generate_maze_for_difficulty,
    generate_perfect_maze,
    measure_maze,
)


class MazeGenerationTests(unittest.TestCase):
    def test_cylindrical_neighbors_wrap_across_seam(self) -> None:
        neighbors = set(cylindrical_neighbors((1, 0), rows=3, columns=8))

        self.assertIn((1, 7), neighbors)
        self.assertIn((1, 1), neighbors)
        self.assertIn((0, 0), neighbors)
        self.assertIn((2, 0), neighbors)

    def test_seeded_generation_is_deterministic(self) -> None:
        first = generate_perfect_maze(rows=6, columns=12, seed=42)
        second = generate_perfect_maze(rows=6, columns=12, seed=42)

        self.assertEqual(first, second)

    def test_generated_maze_is_connected_spanning_tree(self) -> None:
        maze = generate_perfect_maze(rows=7, columns=14, seed=9)
        expected_cells = maze.rows * maze.columns

        self.assertEqual(len(maze.edges), expected_cells - 1)

        seen = {maze.entry}
        queue = deque([maze.entry])
        while queue:
            cell = queue.popleft()
            for neighbor in maze.adjacency[cell]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)

        self.assertEqual(len(seen), expected_cells)

    def test_entry_and_exit_have_exactly_one_solution_path(self) -> None:
        maze = generate_perfect_maze(rows=8, columns=16, seed=1234)

        self.assertEqual(maze.entry[0], 0)
        self.assertEqual(maze.exit[0], maze.rows - 1)
        self.assertEqual(maze.solution[0], maze.entry)
        self.assertEqual(maze.solution[-1], maze.exit)
        self.assertEqual(count_simple_paths(maze, maze.entry, maze.exit, limit=2), 1)

    def test_different_seeds_change_the_tree(self) -> None:
        first = generate_perfect_maze(rows=6, columns=12, seed=1)
        second = generate_perfect_maze(rows=6, columns=12, seed=2)

        self.assertNotEqual(first.edges, second.edges)

    def test_maze_metrics_describe_solution_and_dead_ends(self) -> None:
        maze = generate_perfect_maze(rows=6, columns=12, seed=81)

        metrics = measure_maze(maze)

        self.assertEqual(metrics.solution_steps, len(maze.solution) - 1)
        self.assertGreater(metrics.dead_ends, 0)
        self.assertGreaterEqual(metrics.turns, 0)
        self.assertGreaterEqual(metrics.challenge_score, 0.0)
        self.assertLessEqual(metrics.challenge_score, 1.0)

    def test_higher_difficulty_selects_harder_candidate_on_same_grid(self) -> None:
        easy = generate_maze_for_difficulty(
            rows=8, columns=16, seed=100, difficulty=1, candidates=20
        )
        hard = generate_maze_for_difficulty(
            rows=8, columns=16, seed=100, difficulty=10, candidates=20
        )

        self.assertGreaterEqual(
            hard.metrics.challenge_score, easy.metrics.challenge_score
        )
        self.assertEqual(count_simple_paths(hard.maze, hard.maze.entry, hard.maze.exit), 1)
        self.assertEqual(hard.candidate_count, 20)


if __name__ == "__main__":
    unittest.main()
