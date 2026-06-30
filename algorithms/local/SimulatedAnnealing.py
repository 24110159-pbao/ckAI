import random
import math


class SimulatedAnnealing:

    @staticmethod
    def cost(grid, pos):
        v = grid[pos[0]][pos[1]]

        if v == 3:
            return 4
        if v == 2:
            return 3
        if v in (1, 1.5):
            return 2
        return 1

    @staticmethod
    def search(grid, start, goal):

        def h(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

        def neighbors(r, c):
            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            res = []

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc

                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if grid[nr][nc] != 4:
                        res.append((nr, nc))

            return res

        current = start
        path = [start]

        T = 100
        cooling = 0.95

        expanded = 0

        while T > 1 and current != goal:

            r, c = current
            nb_list = neighbors(r, c)

            expanded += len(nb_list)

            if not nb_list:
                break

            nxt = random.choice(nb_list)

            delta = (
                h(nxt) + SimulatedAnnealing.cost(grid, nxt)
                - h(current) - SimulatedAnnealing.cost(grid, current)
            )

            if delta < 0 or random.random() < math.exp(-delta / T):
                current = nxt
                path.append(nxt)

            T *= cooling

        return path, expanded, (current == goal)