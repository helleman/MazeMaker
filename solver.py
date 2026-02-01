#!/usr/bin/env python3
import sys
from typing import List, Tuple
from collections import deque
import time
import os

def read_maze(filename: str) -> Tuple[List[List[str]], int, int]:
    """Read and validate maze file from disk

    Args:
        filename: Path to maze file (.txt format)

    Returns:
        Tuple of (grid: List[List[str]], height: int, width: int)

    Raises:
        FileNotFoundError: File doesn't exist
        ValueError: Invalid maze format or content
        IOError: File access problems
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found.")
    except IOError as e:
        raise IOError(f"Cannot read file '{filename}': {e}")

    if not lines:
        raise ValueError("Empty maze file.")

    # Remove trailing newlines and validate structure
    grid = [line.rstrip('\n') for line in lines]
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    # Check all lines have same length (rectangular grid)
    if any(len(line) != width for line in grid):
        raise ValueError("Inconsistent line lengths in maze - must be rectangular.")

    # Validate character set
    valid_chars = set(' -|.|SF')
    for i, row in enumerate(grid):
        for j, char in enumerate(row):
            if char not in valid_chars:
                raise ValueError(f"Invalid character '{char}' at position ({i}, {j}) in maze.")

    # Find start (S) and finish (F) positions
    start_pos = None
    finish_pos = None
    for i in range(height):
        for j in range(width):
            if grid[i][j] == 'S':
                if start_pos:
                    raise ValueError("Multiple 'S' positions found in maze.")
                start_pos = (i, j)
            elif grid[i][j] == 'F':
                if finish_pos:
                    raise ValueError("Multiple 'F' positions found in maze.")
                finish_pos = (i, j)

    if not start_pos:
        raise ValueError("No start position ('S') found in maze.")
    if not finish_pos:
        raise ValueError("No finish position ('F') found in maze.")

    # Basic border validation (allow openings for paths)
    if not all(c in ' -|.' for c in grid[0]):
        print(f"Warning: Top border contains unexpected characters")
    if not all(c in ' -|.' for c in grid[height-1]):
        print(f"Warning: Bottom border contains unexpected characters")

    # Left and right should mostly be '|' and '.'
    left_col = ''.join(row[0] for row in grid)
    right_col = ''.join(row[width-1] for row in grid)
    if not all(c in ' -|.' for c in left_col):
        print(f"Warning: Left border contains unexpected characters")
    if not all(c in ' -|.' for c in right_col):
        print(f"Warning: Right border contains unexpected characters")

    return [list(row) for row in grid], height, width

def solve_maze(grid: List[List[str]], start: Tuple[int, int],
               finish: Tuple[int, int], height: int, width: int) -> List[Tuple[int, int]]:
    """Solve maze using Breadth-First Search (BFS) for shortest path

    Args:
        grid: 2D maze grid (mutable - will be modified with path)
        start: (row, col) tuple for start position
        finish: (row, col) tuple for finish position
        height: Number of rows in grid
        width: Number of columns in grid

    Returns:
        List of (row, col) tuples representing the shortest path from start to finish

    Raises:
        ValueError: If no path exists from start to finish
    """
    # Directions: North, South, East, West
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    # BFS setup
    queue = deque([start])
    visited = set([start])
    parent = {start: None}  # Track path reconstruction

    # Valid characters for movement
    walkable_chars = set(' SF')

    # BFS exploration
    found_finish = False
    while queue:
        current = queue.popleft()
        r, c = current

        # Check if we've reached the finish
        if current == finish:
            found_finish = True
            break

        # Explore neighbors
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Check bounds and validity
            if (0 <= nr < height and 0 <= nc < width and
                (nr, nc) not in visited and
                grid[nr][nc] in walkable_chars):

                visited.add((nr, nc))
                queue.append((nr, nc))
                parent[(nr, nc)] = current

    if not found_finish:
        raise ValueError("Maze is unsolvable - no path from start to finish.")

    # Reconstruct path from finish back to start
    path = []
    current = finish
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)  # Include start position
    path.reverse()      # Path now goes start → finish

    return path

def print_maze(grid: List[List[str]]) -> None:
    """Print maze grid to stdout

    Args:
        grid: 2D list representing maze
    """
    for row in grid:
        print(''.join(row))

def animate_solve(grid: List[List[str]], path: List[Tuple[int, int]]) -> None:
    """Animate the solution path by showing step-by-step progress

    Args:
        grid: Maze grid (will be modified with '*' path markers)
        path: List of (row, col) positions representing the solution
    """
    if not path:
        print("No path to animate.")
        return

    print("\n🎬 Animating solution path (press Ctrl+C to stop)...")
    print("Solution length:", len(path), "steps")
    print("-" * 50)

    # Show initial maze with S and F marked
    temp_grid = [row[:] for row in grid]  # Work on copy to preserve original
    print_maze(temp_grid)
    print("-" * 50)

    # Animate path construction
    for i, (r, c) in enumerate(path):
        if i > 0:  # Don't clear screen for first position (start)
            # ANSI escape codes to clear screen and move cursor to top
            print('\033[2J\033[H', end='')

        # Mark current position with '*'
        temp_grid[r][c] = '*'

        # Print current state
        print_maze(temp_grid)

        # Brief pause between steps (except final position)
        if i < len(path) - 1:
            time.sleep(0.1)  # 100ms delay

    print("\n✅ Solution complete! Path shown with '*' markers.")
    print(f"Total steps: {len(path)}")

def validate_maze(grid: List[List[str]], height: int, width: int) -> Tuple[Tuple[int,int], Tuple[int,int]]:
    """Perform comprehensive maze validation

    Args:
        grid: 2D maze grid
        height: Number of rows
        width: Number of columns

    Returns:
        Tuple of (start_position, finish_position)

    Raises:
        ValueError: If validation fails
    """
    # Find start and finish positions
    start = None
    finish = None

    for i in range(height):
        for j in range(width):
            char = grid[i][j]
            if char == 'S':
                if start:
                    raise ValueError("Multiple start positions ('S') found.")
                start = (i, j)
            elif char == 'F':
                if finish:
                    raise ValueError("Multiple finish positions ('F') found.")
                finish = (i, j)

    if not start:
        raise ValueError("No start position ('S') found in maze.")
    if not finish:
        raise ValueError("No finish position ('F') found in maze.")

    # Basic connectivity check (can we reach F from S?)
    try:
        path = solve_maze(grid, start, finish, height, width)
        if len(path) < 2:  # Minimum path length should be at least 2 (S to F)
            raise ValueError("Invalid path length - maze appears malformed.")
    except ValueError as e:
        raise ValueError(f"Maze validation failed: {e}")

    return start, finish

def main():
    """Main command-line interface for solver.py

    Usage: ./solver.py <maze_file>

    Args:
        sys.argv[1]: Path to maze file (.txt)

    Returns:
        Exit code 0 on success, 1 on error
    """
    if len(sys.argv) != 2:
        print("Usage: ./solver.py <maze_file>")
        print("Example: ./solver.py mymaze.txt")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        print(f"Loading maze from '{filename}'")
        print()

        # Read and validate maze file
        grid, height, width = read_maze(filename)

        print(f"✅ Maze loaded successfully")
        print(f"📏 Dimensions: {height}x{width} characters")
        print(f"🔍 Validating structure...")

        # Validate maze and get start/finish positions
        start, finish = validate_maze(grid, height, width)

        print(f"✅ Maze validation passed")
        print(f"🚀 Start at ({start[0]}, {start[1]}), Finish at ({finish[0]}, {finish[1]})")
        print("-" * 50)

        # Solve the maze
        print("🧠 Solving maze using BFS (shortest path)...")
        path = solve_maze(grid, start, finish, height, width)

        print(f"✅ Solution found!")
        print(f"📐 Path length: {len(path)} steps")
        print(f"⏱️  Efficiency: {len(path) / (height * width) * 100:.1f}% of grid explored")
        print("-" * 50)

        # Animate the solution
        animate_solve(grid, path)

        # Save solved maze
        base_name = os.path.splitext(os.path.basename(filename))[0]
        solved_filename = f"solved_{base_name}.txt"

        with open(solved_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(''.join(row) for row in grid))

        print(f"\n💾 Solved maze saved to '{solved_filename}'")
        print(f"📁 Original: {filename} → Solved: {solved_filename}")
        print("\n🎉 Maze solving complete!")

    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        print(f"Make sure '{filename}' exists and is readable.")
        sys.exit(1)

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        print("The maze file appears to be invalid or unsolvable.")
        print("Generate a new maze using: ./maze.py 10 10 maze.txt")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("An unexpected error occurred during maze solving.")
        print("Check the file format and try again.")
        sys.exit(1)

# Make functions importable as library for GUI.py
if __name__ == "__main__":
    main()
else:
    __all__ = ['read_maze', 'solve_maze', 'print_maze', 'animate_solve', 'validate_maze']
