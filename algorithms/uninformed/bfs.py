from collections import deque


class BFS:

    @staticmethod
    def search(grid, start, goal):

        def is_walkable(r, c):
            return grid[r][c] != 4

        queue = deque([(start, [start])])
        visited = {start}

        expanded = 0   # tính luôn node gốc

        while queue:

            (r, c), path = queue.popleft()
            expanded += 1
            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            ]

            for dr, dc in directions:

                nr, nc = r + dr, c + dc

                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):

                    if is_walkable(nr, nc):

                        nxt = (nr, nc)

                        if nxt not in visited:

                            # Nếu node con là goal thì dừng ngay
                            if nxt == goal:
                                return path + [nxt], expanded

                            visited.add(nxt)
                            queue.append((nxt, path + [nxt]))

        return None, expanded