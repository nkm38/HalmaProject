import copy


def alphabeta_search(game, d=3, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state, game.active_player)
        v = -float("inf")
        succs = game.successors(game.active_player)
        for (a, s) in succs:
            v = max(v, min_value(s, alpha, beta, depth+1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        op_player = 1
        if game.active_player == 1:
            op_player = 2
        if cutoff_test(state, depth):
            return eval_fn(state, game.active_player)
        v = float("inf")
        succs = game.successors(op_player)
        for (a, s) in succs:
            v = min(v, max_value(s, alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    cutoff_test = lambda state, depth: depth > d or game.win_check(state)
    eval_fn = eval_fn or game.heuristic
    seq = game.successors(game.active_player)
    best = seq[0]
    best_score = min_value(best[1], -float("inf"), float("inf"), 0)
    for x in seq[1:]:
        x_score = min_value(x[1], -float("inf"), float("inf"), 0)
        if x_score > best_score:
            best, best_score = x, x_score

    return best[0]
