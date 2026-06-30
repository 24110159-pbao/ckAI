from algorithms.informed.heuristic import Heuristic


class AStar:

    @staticmethod
    def search(grid, start, goal):

        rows = len(grid)
        cols = len(grid[0])

        # (f, g, node, path)
        pq = [(
            Heuristic.manhattan(start, goal),
            0,
            start,
            [start]
        )]

        g_score = {start: 0}
        expanded = 0

        while pq:

            # Lấy phần tử có f nhỏ nhất.
            # Nếu f bằng nhau thì lấy g nhỏ hơn.
            # Nếu f và g đều bằng nhau thì giữ phần tử được thêm trước
            best_index = 0

            for i in range(1, len(pq)):
                if pq[i][0] < pq[best_index][0]:
                    best_index = i
                elif pq[i][0] == pq[best_index][0]:
                    if pq[i][1] < pq[best_index][1]:
                        best_index = i

            f, g, current, path = pq.pop(best_index)

            expanded += 1

            if current == goal:
                return path, expanded

            r, c = current

            # Lên -> Xuống -> Trái -> Phải
            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            ]

            for dr, dc in directions:

                nr = r + dr
                nc = c + dc

                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue

                if grid[nr][nc] == 4:
                    continue

                nxt = (nr, nc)
                if grid[nr][nc] == 2:
                    move_cost = 3
                elif grid[nr][nc] in (1, 1.5):
                    move_cost = 2
                else:
                    move_cost = 1
                new_g = g + move_cost

                if nxt not in g_score or new_g < g_score[nxt]:

                    g_score[nxt] = new_g

                    h = Heuristic.manhattan(nxt, goal)
                    new_f = new_g + h

                    pq.append((
                        new_f,
                        new_g,
                        nxt,
                        path + [nxt]
                    ))

        return None, expanded