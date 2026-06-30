class AlphaBeta:

    @staticmethod
    def search(state, depth, maximizing):

        expanded = 0

        def alphabeta(node, depth, alpha, beta, maximizing):

            nonlocal expanded

            expanded += 1

            if depth == 0 or node.is_terminal():
                return node.evaluate(), None

            if maximizing:

                best_move = None
                value = float("-inf")

                for move in node.get_steve_moves():

                    child = node.copy()
                    child.move_steve(move)

                    # Ưu tiên thắng ngay
                    if move == node.diamond:
                        return 100000, move
                    
                    score, _ = alphabeta(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        False
                    )

                    if score > value:
                        value = score
                        best_move = move

                    alpha = max(alpha, value)

                    if beta <= alpha:
                        break

                return value, best_move

            else:

                best_move = None
                value = float("inf")

                for move in node.get_zombie_moves():

                    child = node.copy()
                    child.move_zombie(move)

                    score, _ = alphabeta(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        True
                    )

                    if score < value:
                        value = score
                        best_move = move

                    beta = min(beta, value)

                    if beta <= alpha:
                        break

                return value, best_move

        value, move = alphabeta(
            state,
            depth,
            float("-inf"),
            float("inf"),
            maximizing
        )

        return value, move, expanded