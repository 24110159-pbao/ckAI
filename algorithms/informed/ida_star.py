from algorithms.informed.heuristic import Heuristic


class IDAStar:

    @staticmethod
    def search(grid, start, goal):

        expanded = [0]

        threshold = Heuristic.manhattan(start, goal)

        path = [start]

        while True:

            visited = {start}

            result = IDAStar.dfs(
                grid,
                path,
                0,
                threshold,
                goal,
                visited,
                expanded
            )

            if isinstance(result, list):
                return result, expanded[0]

            if result == float("inf"):
                return None, expanded[0]

            threshold = result

    @staticmethod
    def dfs(
        grid,
        path,
        g,
        threshold,
        goal,
        visited,
        expanded
    ):

        current = path[-1]

        expanded[0] += 1

        f = g + Heuristic.manhattan(current, goal)

        if f > threshold:
            return f

        if current == goal:
            return path.copy()

        minimum = float("inf")

        r, c = current

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        for dr, dc in directions:

            nr = r + dr
            nc = c + dc

            # Kiểm tra biên
            if not (0 <= nr < len(grid) and 0 <= nc < len(grid[0])):
                continue

            # Ô chướng ngại
            if grid[nr][nc] == 4:
                continue

            nxt = (nr, nc)

            # Tránh lặp trên đường đi hiện tại
            if nxt in visited:
                continue

            # Xác định chi phí di chuyển
            if grid[nr][nc] == 2:
                move_cost = 3
            elif grid[nr][nc] in (1,1.5):
                move_cost = 2
            else:
                move_cost = 1

            visited.add(nxt)
            path.append(nxt)

            result = IDAStar.dfs(
                grid,
                path,
                g + move_cost,
                threshold,
                goal,
                visited,
                expanded
            )

            if isinstance(result, list):
                return result

            if result < minimum:
                minimum = result

            path.pop()
            visited.remove(nxt)

        return minimum