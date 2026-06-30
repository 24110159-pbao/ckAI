from algorithms.informed.heuristic import Heuristic

class Greedy:

    @staticmethod
    def search(grid, start, goal):

        # (h, node, path)
        pq = [(Heuristic.manhattan(start, goal), start, [start])]

        visited = {start}
        expanded = 0

        while pq:

            # Tìm phần tử có heuristic nhỏ nhất
            best_index = 0
            best_h = pq[0][0]

            for i in range(1, len(pq)):
                if pq[i][0] < best_h:
                    best_h = pq[i][0]
                    best_index = i

            h, current, path = pq.pop(best_index)


            expanded += 1

            if current == goal:
                return path, expanded

            r, c = current

            # Thứ tự: Lên -> Xuống -> Trái -> Phải
            directions = [
                (-1, 0),  # Up
                (1, 0),   # Down
                (0, -1),  # Left
                (0, 1)    # Right
            ]

            for dr, dc in directions:

                nr, nc = r + dr, c + dc

                if not (0 <= nr < len(grid) and 0 <= nc < len(grid[0])):
                    continue

                if grid[nr][nc] == 4:
                    continue

                nxt = (nr, nc)

                if nxt not in visited:
                    visited.add(nxt)
                    pq.append(
                        (
                            Heuristic.manhattan(nxt, goal),
                            nxt,
                            path + [nxt]
                        )
                    )

        return None, expanded