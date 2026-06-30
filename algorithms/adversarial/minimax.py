class Minimax:

    @staticmethod
    def search(state, depth, maximizing):

        expanded = 0

        def minimax(node, depth, maximizing):
            nonlocal expanded

            expanded += 1

            if depth == 0 or node.is_terminal():
                return node.evaluate(), None

            if maximizing:

                best_value = float("-inf")
                best_move = None

                for move in node.get_steve_moves():

                    child = node.copy()
                    child.move_steve(move)

                    # Nếu đi tới Diamond thì chọn luôn
                    if move == node.diamond:
                        return 100000, move

                    value, _ = minimax(child, depth-1, False)

                    if value > best_value:
                        best_value = value
                        best_move = move

                return best_value, best_move

            else:

                best_value = float("inf")
                best_move = None

                for move in node.get_zombie_moves():

                    child = node.copy()
                    child.move_zombie(move)

                    value, _ = minimax(
                        child,
                        depth - 1,
                        True
                    )

                    if value < best_value:
                        best_value = value
                        best_move = move

                return best_value, best_move

        value, move = minimax(
            state,
            depth,
            maximizing
        )

        return value, move, expanded