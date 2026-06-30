class IDS:

    @staticmethod
    def dls(grid, node, goal, depth, path, visited, expanded):

        expanded[0] += 1

        if node == goal:
            return path

        if depth == 0:
            return None

        r, c = node

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        for dr, dc in directions:

            nr, nc = r + dr, c + dc

            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):

                if grid[nr][nc] != 4:

                    nxt = (nr, nc)

                    if nxt not in visited:

                        visited.add(nxt)

                        result = IDS.dls(
                            grid,
                            nxt,
                            goal,
                            depth - 1,
                            path + [nxt],
                            visited,
                            expanded
                        )
                        visited.remove(nxt)
                        if result:
                            return result

        return None

    @staticmethod
    def search(grid, start, goal):

        expanded = [0]

        for depth in range(100):

            visited = set([start])

            result = IDS.dls(
                grid,
                start,
                goal,
                depth,
                [start],
                visited,
                expanded
            )

            if result:
                return result, expanded[0]

        return None, expanded[0]