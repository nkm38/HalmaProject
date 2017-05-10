

def alphabeta_search(game, d=3, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state, game.active_player)
        v = -float("inf")
        for (a, s) in game.successors(game.active_player):
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
        for (a, s) in game.successors(op_player):
            v = min(v, max_value(s, alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    cutoff_test = lambda state, depth: depth > d or game.win_check()
    eval_fn = eval_fn or game.heuristic
    action, state = argmax(game.successors(game.active_player),
                           lambda move: min_value(move[1], -float("inf"), float("inf"), 0))
    return action


def argmin(seq, fn):
    """Return an element with lowest fn(seq[i]) score; tie goes to first one.
    >>> argmin(['one', 'to', 'three'], len)
    'to'
    """
    best = seq[0]
    best_score = fn(best)
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score
    return best


def argmax(seq, fn):
    """Return an element with highest fn(seq[i]) score; tie goes to first one.
    >>> argmax(['one', 'to', 'three'], len)
    'three'
    """
    return argmin(seq, lambda x: -fn(x))
