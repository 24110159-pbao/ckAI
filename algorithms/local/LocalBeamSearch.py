class LocalBeamSearch:

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
    def search(grid, start, goal, beam_width=3):

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

        beams = [(start, [start])]
        expanded = 0

        while beams:

            all_next = []

            for node, path in beams:

                r, c = node

                for nb in neighbors(r, c):

                    if nb in path:
                        continue

                    score = h(nb) + LocalBeamSearch.cost(grid, nb)
                    all_next.append((score, nb, path + [nb]))

            expanded += len(all_next)

            if not all_next:
                break

            all_next.sort(key=lambda x: x[0])

            beams = [(node, path) for _, node, path in all_next[:beam_width]]

            for node, path in beams:
                if node == goal:
                    return path, expanded, True

        if beams:
            return beams[0][1], expanded, False

        return [], expanded, False