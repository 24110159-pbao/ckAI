class HillClimbing:

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
        expanded = 0

        while current != goal:

            r, c = current
            candidates = []

            current_score = h(current) + HillClimbing.cost(grid, current)

            for nb in neighbors(r, c):

                if nb in path:
                    continue

                score = h(nb) + HillClimbing.cost(grid, nb)
                candidates.append((score, nb))

            expanded += len(candidates)

            if not candidates:
                break

            better = [(s, n) for s, n in candidates if s <= current_score]

            if not better:
                break

            current = min(better, key=lambda x: x[0])[1]
            path.append(current)

        return path, expanded, (current == goal)