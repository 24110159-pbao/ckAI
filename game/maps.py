import random

class Maps:

    LEVEL_1 = [
        ["S", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    ]
    LEVEL_2 = [
        ["S",0,0,0,0,0,0,0,0,0,0,0],
        [1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [4,4,4,4,4,4,4,4,4,4,4,4]
    ]
    LEVEL_6 = [
        ["S", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    ]
    LEVEL_3_INNER = [
        [2, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1],
        [1, 2, 1, 2, 1, 3, 2, 1, 1, 2, 1, 1],
        [1, 1, 1, 2, 3, 2, 1, 1, 2, 1, 1, 1],
        [1, 2, 1, 1, 1, 1, 2, 1, 1, 3, 2, 1],
        [1, 1, 3, 2, 1, 1, 1, 2, 1, 2, 1, 1],
        [1, 2, 1, 1, 2, 1, 3, 1, 2, 1, 1, 1],
        [1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
        [1, 1, 2, 1, 1, 1, 1, 3, 1, 2, 1, 1],
        [1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1],
    ]

    LEVEL_4_INNER = [
        [1, 2, 1, 1, 3, 1, 2, 1, 1, 2, 1, 1],
        [1, 1, 2, 4, 1, 1, 1, 3, 1, 1, 2, 1],
        [2, 1, 1, 1, 2, 3, 1, 1, 4, 1, 1, 1],
        [1, 3, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
        [1, 1, 4, 1, 3, 2, 1, 1, 2, 1, 1, 1],
        [2, 1, 1, 1, 1, 1, 4, 1, 3, 1, 2, 1],
        [1, 1, 2, 3, 1, 2, 1, 1, 1, 2, 1, 1],
        [1, 2, 1, 1, 1, 3, 1, 2, 1, 1, 1, 3],
        [1, 1, 1, 2, 1, 1, 1, 3, 2, 1, 1, 1],
    ]

    LEVEL_5_INNER = [
        [1, 2, 1, 3, 1, 1, 2, 1, 3, 1, 1, 2],
        [1, 1, 2, 1, 4, 1, 1, 2, 1, 1, 3, 1],
        [2, 1, 3, 1, 1, 2, 1, 1, 4, 1, 2, 1],
        [1, 1, 1, 2, 3, 1, 4, 1, 1, 2, 1, 1],
        [3, 2, 1, 1, 1, 1, 2, 3, 1, 1, 1, 2],
        [1, 1, 4, 1, 2, 3, 1, 1, 2, 1, 3, 1],
        [2, 1, 1, 3, 1, 1, 2, 1, 1, 4, 1, 1],
        [1, 3, 2, 1, 1, 2, 1, 3, 1, 1, 2, 1],
        [1, 1, 1, 2, 3, 1, 1, 2, 1, 3, 1, 1],
    ]
    @staticmethod
    def _build_level_like_level1(inner_rows, random_goal=True):
        grid = [
            ["S", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
            *[row[:] for row in inner_rows],
            [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        ]

        if random_goal:
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c] == "D":
                        grid[r][c] = 1

            positions = []
            for r in range(2, len(grid) - 1):
                for c in range(len(grid[0])):
                    if grid[r][c] == 1:
                        positions.append((r, c))

            if positions:
                r, c = random.choice(positions)
                grid[r][c] = "D"

        return grid
    @staticmethod
    def get_level(level):
        if level == 1:
            grid = [row[:] for row in Maps.LEVEL_1]

            # Lấy tất cả vị trí có giá trị 1
            positions = []
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c] == 1:
                        positions.append((r, c))

            # Chọn ngẫu nhiên một vị trí
            r, c = random.choice(positions)
            grid[r][c] = "D"

            return grid
        if level == 2:

            grid = [row[:] for row in Maps.LEVEL_2]

            # Các vị trí có thể đặt Stone hoặc Diamond
            positions = []

            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c] == 1:
                        positions.append((r, c))

            # -----------------------
            # Random 12 viên đá
            # -----------------------
            stone_positions = random.sample(positions, 12)

            for r, c in stone_positions:
                grid[r][c] = 2
                positions.remove((r, c))

            # -----------------------
            # Random Diamond
            # -----------------------
            dr, dc = random.choice(positions)
            grid[dr][dc] = "D"

            return grid
        
        if level == 6:
            grid = [row[:] for row in Maps.LEVEL_6]

            positions = []

            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c] == 1:
                        positions.append((r, c))

            # Diamond
            dr, dc = random.choice(positions)
            grid[dr][dc] = "D"
            positions.remove((dr, dc))

            # Zombie
            zr, zc = random.choice(positions)
            grid[zr][zc] = "Z"

            return grid
        if level == 3:
            return Maps._build_level_like_level1(Maps.LEVEL_3_INNER, random_goal=True)

        if level == 4:
            return Maps._build_level_like_level1(Maps.LEVEL_4_INNER, random_goal=True)

        if level == 5:
            return Maps._build_level_like_level1(Maps.LEVEL_5_INNER, random_goal=True)
    
        return None