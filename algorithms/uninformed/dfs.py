class DFS:

    @staticmethod
    def search(grid, start, goal):

        def is_walkable(r, c):
            return grid[r][c] != 4

        stack = [(start, [start])]
        visited = {start}

        expanded = 0

        while stack:

            (r, c), path = stack.pop()
            expanded += 1

            if (r, c) == goal:
                return path, expanded


            directions = [
                (-1, 0),  # Lên
                (1, 0),   # Xuống
                (0, -1),  # Trái
                (0, 1)    # Phải
            ]

            for dr, dc in directions:

                nr, nc = r + dr, c + dc

                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):

                    if is_walkable(nr, nc):

                        nxt = (nr, nc)

                        if nxt not in visited:
                            visited.add(nxt)
                            stack.append((nxt, path + [nxt]))

        return None, expanded