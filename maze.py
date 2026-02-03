#!/usr/bin/env python3
import sys
import random
from typing import List, Tuple
from collections import deque

def generate_maze(rows: int, cols: int) -> List[List[str]]:
    """Generate a perfect maze using randomized recursive backtracking

    Args:
        rows: Number of cells vertically (1-50 recommended)
        cols: Number of cells horizontally (1-50 recommended)

    Returns:
        2D list representing the maze grid (2N+1 x 2M+1 characters)

    Raises:
        ValueError: Invalid dimensions (< 1)
    """
    if rows < 1 or cols < 1:
        raise ValueError("Maze dimensions must be positive integers.")

    # Initialize grid with walls
    height = 2 * rows + 1
    width = 2 * cols + 1
    grid = [['#' for _ in range(width)] for _ in range(height)]

    # Set horizontal borders (top and bottom rows)
    for j in range(width):
        grid[0][j] = '-'
        grid[height - 1][j] = '-'
    grid[0][0] = grid[0][width - 1] = grid[height - 1][0] = grid[height - 1][width - 1] = '.'

    # Set vertical borders (left and right columns)
    for i in range(height):
        grid[i][0] = '|'
        grid[i][width - 1] = '|'

    # Cells are at odd indices; walls at even indices
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]  # Up, Down, Left, Right
    visited = set()
    stack = []

    # Start from a random cell (odd indices only)
    start_cell_r = random.choice(range(1, height, 2))
    start_cell_c = random.choice(range(1, width, 2))
    stack.append((start_cell_r, start_cell_c))
    visited.add((start_cell_r, start_cell_c))
    grid[start_cell_r][start_cell_c] = ' '

    # Recursive backtracking to carve paths
    while stack:
        cr, cc = stack[-1]
        random.shuffle(directions)
        carved = False

        for dr, dc in directions:
            nr, nc = cr + dr, cc + dc
            if (1 <= nr < height - 1 and 1 <= nc < width - 1 and
                (nr, nc) not in visited and grid[nr][nc] == '#'):

                # Calculate wall position between cells
                wall_r = (cr + nr) // 2
                wall_c = (cc + nc) // 2

                # Carve through the wall and open the new cell
                grid[wall_r][wall_c] = ' '
                grid[nr][nc] = ' '

                stack.append((nr, nc))
                visited.add((nr, nc))
                carved = True
                break

        if not carved:
            stack.pop()

    # Replace remaining '#' with proper wall characters
    for i in range(height):
        for j in range(width):
            if grid[i][j] == '#':
                if i % 2 == 0 and j % 2 == 0:
                    # Junctions/corners - use '.' per specification
                    grid[i][j] = '.'
                elif i % 2 == 0:
                    # Horizontal wall positions
                    grid[i][j] = '-'
                else:
                    # Vertical wall positions
                    grid[i][j] = '|'

    # Place 'S' on a random edge position (border opening)
    possible_starts = []
    # Top and bottom edges (odd columns)
    for j in range(1, width, 2):
        if grid[1][j] == ' ':
            possible_starts.append((1, j))
        if grid[height - 2][j] == ' ':
            possible_starts.append((height - 2, j))
    # Left and right edges (odd rows)
    for i in range(1, height, 2):
        if grid[i][1] == ' ':
            possible_starts.append((i, 1))
        if grid[i][width - 2] == ' ':
            possible_starts.append((i, width - 2))

    if not possible_starts:
        # Fallback: force open a border position
        possible_starts = [(1, 1), (height - 2, 1), (1, width - 2), (height - 2, width - 2)]
        for r, c in possible_starts:
            if 1 <= r < height and 1 <= c < width:
                grid[r][c] = ' '
                break

    sr, sc = random.choice(possible_starts)
    grid[sr][sc] = 'S'

    # Place 'F' in a random internal open cell (not S position)
    possible_fins = []
    for i in range(1, height, 2):
        for j in range(1, width, 2):
            if grid[i][j] == ' ' and (i, j) != (sr, sc):
                possible_fins.append((i, j))

    if not possible_fins:
        raise ValueError("No valid position for finish after generation")

    fr, fc = random.choice(possible_fins)
    grid[fr][fc] = 'F'

    # Final validation: ensure maze is solvable (BFS from S to F)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N,S,W,E
    visited = set()
    queue = deque([(sr, sc)])
    visited.add((sr, sc))
    found_finish = False

    while queue:
        r, c = queue.popleft()
        if r == fr and c == fc:
            found_finish = True
            break
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if (0 <= nr < height and 0 <= nc < width and
                (nr, nc) not in visited and
                grid[nr][nc] in ' SF'):
                visited.add((nr, nc))
                queue.append((nr, nc))

    if not found_finish:
        raise ValueError("Generated maze is not solvable; please try again")

    return grid

def print_maze(grid: List[List[str]]) -> None:
    """Print maze grid to stdout in readable ASCII format

    Args:
        grid: 2D list representing maze
    """
    for row in grid:
        print(''.join(row))

def main():
    """Main command-line interface for maze.py

    Usage: ./maze.py <rows> <cols> [output_file]

    Args from sys.argv:
        sys.argv[1]: rows (int) - Number of rows
        sys.argv[2]: cols (int) - Number of columns
        sys.argv[3]: output_file (str, optional) - File to save maze

    Returns:
        Exit code 0 on success, 1 on error
    """
    if len(sys.argv) < 3:
        print("Usage: ./maze.py <rows> <cols> [output_file]")
        print("Example: ./maze.py 10 10 mymaze.maze")
        sys.exit(1)

    try:
        # Parse command line arguments
        rows = int(sys.argv[1])
        cols = int(sys.argv[2])
    except (ValueError, IndexError):
        print("Usage: ./maze.py <rows> <cols> [output_file]")
        print("Error: Rows and columns must be positive integers.")
        print("Example: ./maze.py 10 10 mymaze.maze")
        sys.exit(1)

    try:
        # Generate the maze
        print(f"Generating {rows}x{cols} maze...")
        grid = generate_maze(rows, cols)

        # Prepare output
        maze_str = '\n'.join(''.join(row) for row in grid)
        output_file = sys.argv[3] if len(sys.argv) > 3 else None

        if output_file:
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(maze_str)
            print(f"✅ Maze successfully saved to '{output_file}'")
            print(f"📏 Dimensions: {rows}x{cols} cells ({len(grid)}x{len(grid[0])} characters)")
        else:
            # Print to stdout
            print("\n" + "="*50)
            print(f"GENERATED {rows}x{cols} MAZE")
            print("="*50)
            print_maze(grid)
            print("="*50)

    except ValueError as e:
        print(f"❌ Generation Error: {e}")
        print("Please try different dimensions (1-50 recommended).")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("Maze generation failed. Please check your input and try again.")
        sys.exit(1)

# Make functions importable as library
if __name__ == "__main__":
    main()
else:
    __all__ = ['generate_maze', 'print_maze']
