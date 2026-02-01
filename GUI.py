#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
from typing import List, Tuple
import math
import time
import threading

# Import from local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maze import generate_maze
from solver import read_maze, solve_maze

class MazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Creator and Solver")
        self.root.geometry("1000x800")

        self.maze_grid = None
        self.solved_grid = None
        self.height = 0
        self.width = 0
        self.path = None
        self.animating = False
        self.cell_size = 0
        self.canvas_width = 700
        self.canvas_height = 600

        self.setup_ui()

    def setup_ui(self):
        # Menu buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), columnspan=2)

        ttk.Button(button_frame, text="a) Create New Maze", command=self.create_maze).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="b) Solve a Maze", command=self.solve_maze).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="c) List Mazes", command=self.list_mazes).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="d) Display Maze/Solution", command=self.display_maze).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="e) Quit", command=self.root.quit).grid(row=0, column=4, padx=5)

        # Canvas for drawing (larger for better scaling)
        self.canvas = tk.Canvas(self.root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Bind resize event
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # Status label
        self.status = ttk.Label(self.root, text="Ready")
        self.status.grid(row=2, column=0, pady=5)

        # Info frame for maze details
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W), padx=10, pady=10)

        self.info_label = ttk.Label(self.info_frame, text="Maze Info", font=('Arial', 10, 'bold'))
        self.info_label.pack(anchor=tk.W)

        self.size_label = ttk.Label(self.info_frame, text="Size: --")
        self.size_label.pack(anchor=tk.W)

        self.path_label = ttk.Label(self.info_frame, text="Path Length: --")
        self.path_label.pack(anchor=tk.W)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        if self.maze_grid:
            self.draw_maze(self.maze_grid, solved=False)
        elif self.solved_grid:
            self.draw_maze(self.solved_grid, solved=True)

    def calculate_scaling(self):
        """Calculate optimal cell size and centering for the maze"""
        if not self.maze_grid or self.height == 0 or self.width == 0:
            return 10, 20, 20, 0, 0  # Default values

        # Calculate required space (each character is one unit)
        maze_width_chars = self.width
        maze_height_chars = self.height

        # Available space (leave 20px margin on each side)
        available_width = self.canvas_width - 40
        available_height = self.canvas_height - 40

        # Calculate cell size based on limiting dimension
        if maze_width_chars > 0:
            cell_size_x = available_width / maze_width_chars
        else:
            cell_size_x = 10

        if maze_height_chars > 0:
            cell_size_y = available_height / maze_height_chars
        else:
            cell_size_y = 10

        # Choose the smaller dimension to maintain aspect ratio
        # Cap at 25px max, floor at 8px min for readability
        self.cell_size = max(8, min(cell_size_x, cell_size_y, 25))

        # Calculate total maze dimensions with scaling
        scaled_width = maze_width_chars * self.cell_size
        scaled_height = maze_height_chars * self.cell_size

        # Calculate centering offsets
        offset_x = (self.canvas_width - scaled_width) / 2
        offset_y = (self.canvas_height - scaled_height) / 2

        # Ensure offsets are non-negative
        offset_x = max(0, offset_x)
        offset_y = max(0, offset_y)

        return self.cell_size, offset_x, offset_y, scaled_width, scaled_height

    def create_maze(self):
        size_str = simpledialog.askstring("Create Maze", "Enter dimensions (rows cols, e.g., 10 10):")
        if not size_str:
            return
        try:
            rows, cols = map(int, size_str.split())
            if rows < 1 or cols < 1:
                raise ValueError("Dimensions must be positive integers")

            filename = simpledialog.askstring("Save Maze", "Enter filename (e.g., mymaze.txt):")
            if not filename:
                return
            if not filename.endswith('.txt'):
                filename += '.txt'

            # Generate maze
            self.maze_grid = generate_maze(rows, cols)
            self.height, self.width = len(self.maze_grid), len(self.maze_grid[0])

            # Update info
            self.size_label.config(text=f"Size: {rows}x{cols} cells ({self.height}x{self.width} chars)")
            self.path_label.config(text="Path Length: --")

            # Save file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(''.join(row) for row in self.maze_grid))

            self.status.config(text=f"Maze created and saved to {filename}")
            self.draw_maze(self.maze_grid, solved=False)
            messagebox.showinfo("Success", f"Created {rows}x{cols} maze and saved to {filename}")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            self.status.config(text="Error creating maze")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create maze: {str(e)}")
            self.status.config(text="Error creating maze")

    def solve_maze(self):
        filename = filedialog.askopenfilename(
            title="Select Maze File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            self.maze_grid, self.height, self.width = read_maze(filename)

            # Find start and finish
            start = next((i,j) for i in range(self.height) for j in range(self.width) if self.maze_grid[i][j] == 'S')
            finish = next((i,j) for i in range(self.height) for j in range(self.width) if self.maze_grid[i][j] == 'F')

            self.path = solve_maze(self.maze_grid, start, finish, self.height, self.width)

            # Update info
            self.size_label.config(text=f"Size: {self.height//2}x{self.width//2} cells ({self.height}x{self.width} chars)")
            self.path_label.config(text=f"Path Length: {len(self.path)} steps")

            # Animate solving
            self.animate_solve()

            # Save solved
            base_name = os.path.basename(filename)
            solved_filename = f"solved_{base_name}"
            self.solved_grid = [row[:] for row in self.maze_grid]
            for r, c in self.path:
                self.solved_grid[r][c] = '*'

            with open(solved_filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(''.join(row) for row in self.solved_grid))

            self.draw_maze(self.solved_grid, solved=True)
            self.status.config(text=f"Solved and saved to {solved_filename}")
            messagebox.showinfo("Success", f"Solved maze with {len(self.path)} steps. Saved to {solved_filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to solve maze: {str(e)}")
            self.status.config(text="Error solving maze")

    def animate_solve(self):
        if not self.path or self.animating:
            return

        self.animating = True
        self.status.config(text="Animating solution...")

        def run_animation():
            try:
                cell_size, offset_x, offset_y, scaled_width, scaled_height = self.calculate_scaling()

                # Clear path dots
                self.canvas.delete("path_dot")

                # Draw initial maze
                self.root.after(0, lambda: self.draw_maze(self.maze_grid, solved=False))

                # Wait a moment for redraw
                self.root.after(500, lambda: None)

                for idx, (r, c) in enumerate(self.path):
                    if not self.animating:
                        break

                    # Calculate position using scaling
                    x = offset_x + c * cell_size + cell_size / 2
                    y = offset_y + r * cell_size + cell_size / 2

                    # Remove previous dot
                    self.canvas.delete("path_dot")

                    # Draw new position (blue dot following path)
                    dot = self.canvas.create_oval(
                        x-6, y-6, x+6, y+6,
                        fill='blue', outline='blue',
                        tags="path_dot",
                        width=2
                    )

                    # Ensure dot stays on top
                    self.canvas.tag_raise(dot)

                    # Update display
                    self.root.update()
                    time.sleep(0.2)

                # Final update - show complete solved maze
                self.root.after(0, lambda: self.draw_maze(self.solved_grid, solved=True))
                self.root.after(0, lambda: self.status.config(text="Animation complete"))
                self.animating = False

            except Exception as e:
                print(f"Animation error: {e}")
                self.root.after(0, lambda: self.status.config(text="Animation error"))
                self.animating = False

        thread = threading.Thread(target=run_animation, daemon=True)
        thread.start()

    def list_mazes(self):
        try:
            files = [f for f in os.listdir('.') if f.endswith('.txt')]
            solved_files = [f for f in files if f.startswith('solved_')]
            maze_files = [f for f in files if not f.startswith('solved_')]

            text = f"Total maze files: {len(files)}\n"
            text += f"Solved mazes: {len(solved_files)}\n\n"

            if maze_files:
                text += "Maze files (unsolved):\n"
                for f in sorted(maze_files):
                    text += f"  📄 {f}\n"
                text += "\n"

            if solved_files:
                text += "Solved mazes:\n"
                for f in sorted(solved_files):
                    text += f"  ⭐ {f}\n"

            list_window = tk.Toplevel(self.root)
            list_window.title("Mazes on Disk")
            list_window.geometry("500x400")
            list_window.transient(self.root)
            list_window.grab_set()

            # Create scrollable text area
            text_widget = tk.Text(list_window, wrap=tk.WORD, font=('Courier', 10))
            scrollbar = ttk.Scrollbar(list_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget.insert(tk.END, text)

            # Highlight solved files
            for solved in solved_files:
                start = text_widget.search(solved, 1.0, stopindex=tk.END)
                while start:
                    end = f"{start}+1l"
                    text_widget.tag_add("highlight", start, end)
                    start = text_widget.search(solved, end, stopindex=tk.END)

            text_widget.tag_config("highlight", background="lightyellow", foreground="darkgreen")
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {str(e)}")

    def display_maze(self):
        filename = filedialog.askopenfilename(
            title="Select Maze File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            self.solved_grid, self.height, self.width = read_maze(filename)

            # Update info
            rows, cols = self.height // 2, self.width // 2
            self.size_label.config(text=f"Size: {rows}x{cols} cells ({self.height}x{self.width} chars)")

            is_solved = any('*' in ''.join(row) for row in self.solved_grid)
            self.path_label.config(text="Solved: Yes" if is_solved else "Solved: No")

            self.draw_maze(self.solved_grid, solved=is_solved)
            self.status.config(text=f"Displaying {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"Loaded and displayed {os.path.basename(filename)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maze: {str(e)}")
            self.status.config(text="Error loading maze")

    def draw_maze(self, grid: List[List[str]], solved: bool = False):
        """Draw maze with proper scaling and centering"""
        if not grid:
            return

        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

        # Calculate scaling and positioning (now returns 5 values)
        cell_size, offset_x, offset_y, scaled_width, scaled_height = self.calculate_scaling()

        # Clear canvas
        self.canvas.delete("all")

        # Draw background
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                   fill='white', outline='white')

        # Draw maze elements
        for i in range(self.height):
            for j in range(self.width):
                char = grid[i][j]
                x = offset_x + j * cell_size
                y = offset_y + i * cell_size

                # Draw walls
                if char == '-':  # Horizontal wall
                    self.canvas.create_line(
                        x, y, x + cell_size, y,
                        width=max(2, int(cell_size // 8)),
                        fill='black', capstyle=tk.ROUND, tags="wall"
                    )
                elif char == '|':  # Vertical wall
                    self.canvas.create_line(
                        x, y, x, y + cell_size,
                        width=max(2, int(cell_size // 8)),
                        fill='black', capstyle=tk.ROUND, tags="wall"
                    )
                elif char == '.':  # Junction
                    cx = x + cell_size / 2
                    cy = y + cell_size / 2
                    radius = max(2, int(cell_size // 12))
                    self.canvas.create_oval(
                        cx - radius, cy - radius, cx + radius, cy + radius,
                        fill='black', outline='black', tags="wall"
                    )
                elif char == ' ':  # Path space
                    # Draw path background
                    self.canvas.create_rectangle(
                        x + 1, y + 1, x + cell_size - 1, y + cell_size - 1,
                        fill='lightgreen', outline='', tags="path"
                    )

        # Draw special markers (S, F, *)
        for i in range(self.height):
            for j in range(self.width):
                char = grid[i][j]
                if char in 'SF*':
                    cx = offset_x + j * cell_size + cell_size / 2
                    cy = offset_y + i * cell_size + cell_size / 2

                    marker_size = cell_size * 0.4  # 40% of cell size
                    outline_width = max(1, int(marker_size // 8))

                    if char == 'S':
                        # Green start marker
                        self.canvas.create_oval(
                            cx - marker_size/2, cy - marker_size/2,
                            cx + marker_size/2, cy + marker_size/2,
                            fill='limegreen', outline='darkgreen',
                            width=outline_width, tags="marker"
                        )
                        # Add S label
                        self.canvas.create_text(
                            cx, cy, text="S", font=('Arial', max(8, int(marker_size/4)), 'bold'),
                            fill='white', tags="marker"
                        )
                    elif char == 'F':
                        # Red finish marker
                        self.canvas.create_oval(
                            cx - marker_size/2, cy - marker_size/2,
                            cx + marker_size/2, cy + marker_size/2,
                            fill='red', outline='darkred',
                            width=outline_width, tags="marker"
                        )
                        # Add F label
                        self.canvas.create_text(
                            cx, cy, text="F", font=('Arial', max(8, int(marker_size/4)), 'bold'),
                            fill='white', tags="marker"
                        )
                    elif char == '*' and solved:
                        # Blue path marker
                        self.canvas.create_oval(
                            cx - marker_size/3, cy - marker_size/3,
                            cx + marker_size/3, cy + marker_size/3,
                            fill='royalblue', outline='navy',
                            width=outline_width, tags="path_marker"
                        )

        # Add border around the maze
        border_x1 = offset_x - 5
        border_y1 = offset_y - 5
        border_x2 = offset_x + scaled_width + 5
        border_y2 = offset_y + scaled_height + 5

        self.canvas.create_rectangle(
            border_x1, border_y1, border_x2, border_y2,
            outline='gray', width=2, tags="border"
        )

        # Add info overlay
        info_text = f"Scale: {cell_size:.1f}px/char | Size: {self.height//2}x{self.width//2}"
        if solved and self.path:
            info_text += f" | Path: {len(self.path)} steps"

        self.canvas.create_text(
            10, 20, text=info_text, anchor='nw',
            font=('Arial', 9), fill='darkgray', tags="info"
        )

        # Ensure proper layer ordering
        self.canvas.tag_lower("wall")
        self.canvas.tag_raise("path")
        self.canvas.tag_raise("marker")
        self.canvas.tag_raise("path_marker")
        self.canvas.tag_raise("border")
        self.canvas.tag_raise("info")

    def stop_animation(self):
        """Stop current animation"""
        self.animating = False

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGUI(root)

    # Handle window close
    def on_closing():
        app.stop_animation()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
