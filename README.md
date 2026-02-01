 # MazeMaker

A Python application for generating, solving, and visualizing mazes with a GUI interface.

## Features

- **Maze Generation**: Creates random mazes of various sizes
- **Pathfinding**: Uses BFS algorithm to solve mazes
- **GUI Interface**: Interactive graphical interface built with Tkinter
- **File I/O**: Save/load mazes to/from text files
- **Visualization**: Displays maze generation and solving process

## Project Structure

mazemaker/
├── maze.py# Core maze generation and representation
├── solver.py# BFS pathfinding algorithm
├── GUI.py # Tkinter-based graphical interface
├── mazemaker_AI.txt # AI development best practices
├── test_maze.txt# Sample test maze
├── aaron.txt# Sample maze file
├── dawson.txt # Sample maze file
└── README.md# This file 
 
## Installation
 
1. Clone the repository: 
 ```bash 
 git clone https://github.com/YOUR_USERNAME/mazemaker.git
 cd mazemaker
 
2. No external dependencies required - uses only Python standard library 
3. Run the GUI:
python3 GUI.py 
 
Usage
 
1. Generate New Maze: Use the GUI to create mazes of different sizes 
2. Load Existing Maze: Open .txt files with maze data
3. Solve Maze: Click "Solve" to see the pathfinding algorithm in action
4. Save Results: Export solved mazes to text files 
 
Maze Format
 
Mazes are stored as text files where:
- # = Wall 
- . = Open path
- S = Start position 
- E = End position 
 
Development
 
See mazemaker_AI.txt for AI-assisted development best practices and troubleshooting tips.
 
License
 
This project is licensed under the MIT License - see the LICENSE file for details. 
