class Expectimax:

    @staticmethod
    def search(state, depth, maximizing):

        expanded = 0

        def expectimax(node, depth, maximizing):

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
                    # Ưu tiên thắng ngay
                    if move == node.diamond:
                        return 100000, move
                    value, _ = expectimax(
                        child,
                        depth - 1,
                        False
                    )

                    if value > best_value:
                        best_value = value
                        best_move = move

                return best_value, best_move

            else:

                moves = node.get_zombie_moves()

                if len(moves) == 0:
                    return node.evaluate(), None

                total = 0

                for move in moves:

                    child = node.copy()
                    child.move_zombie(move)

                    score, _ = expectimax(
                        child,
                        depth - 1,
                        True
                    )

                    total += score

                average = total / len(moves)

                return average, None

        value, move = expectimax(
            state,
            depth,
            maximizing
        )

        return value, move, expanded