import heapq
from settings import *

# 4-direction movement (no diagonals)
DIRS = [(1,0), (-1,0), (0,1), (0,-1)]


def heuristic(a, b):
    """ Manhattan distance heuristic """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid, start, goal):
    """
    A* pathfinding
    grid  = 2D array (0 = empty, 1 = wall)
    start = (tile_x, tile_y)
    goal  = (tile_x, tile_y)

    RETURNS: list of tile positions [(x,y), (x,y), ...]
    """

    if start == goal:
        return [start]

    rows = len(grid)
    cols = len(grid[0])

    # priority queue
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        current_priority, current = heapq.heappop(open_set)

        # reached target
        if current == goal:
            return reconstruct_path(came_from, current)

        cx, cy = current

        for dx, dy in DIRS:
            nx = cx + dx
            ny = cy + dy

            if nx < 0 or ny < 0 or nx >= cols or ny >= rows:
                continue

            if grid[ny][nx] != 0:  # not walkable
                continue

            tentative_g = g_score[current] + 1

            if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                g_score[(nx, ny)] = tentative_g
                f_score = tentative_g + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (f_score, (nx, ny)))
                came_from[(nx, ny)] = current

    return []  # no path found


def reconstruct_path(came_from, current):
    """ Reconstruct final A* path """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
