from info_set import InformationSet

chance_nodes = {'bc','xx', 'xbc', 'brc', 'xbrc'}

def rank(cards):
    ranks = {
        'KK': 1,
        'QQ': 2,
        'JJ': 3,
        'KQ': 4, 'QK': 4,
        'KJ': 5, 'JK': 5,
        'QJ': 6, 'JQ': 6
    }
    return ranks[cards]

def is_terminal(history):
    return history[-1:] == 'f' or ('d' in history and history.split('d')[1] in chance_nodes)

def is_chance_node(history):
    return history in chance_nodes

def terminal_util(history, card_player, card_opponent, card_flop):
    '''Return player's utility when we arrive at a terminal node'''
    ante = 1
    # ante is 1$, bet is 2$, raise is 4$
    payoffs = {'xx':0, 'bf':0, 'xbf':0, 'brf':2, 'xbrf':2, 'bc':2, 'xbc':2, 'brc':4, 'xbrc':4}
    if 'd' not in history:  # if there was a fold pre-flop
        return ante + payoffs[history]
    else:  # if there was a fold post-flop or if we went to showdown 
        payoffs = {'xx':0, 'bf':0, 'xbf':0, 'brf':2, 'xbrf':2, 'bc':2, 'xbc':2, 'brc':4, 'xbrc':4}
        preflop, flop = history.split('d')
        pot = ante + payoffs[preflop] + payoffs[flop]
        if history[-1:] == 'f':
            return pot
        else:  # showdown
            # hand_player = card_str(card_player) + card_str(card_flop)
            hand_player = card_player + card_flop

            # hand_opponent = card_str(card_opponent) + card_str(card_flop)
            hand_opponent = card_opponent + card_flop

            if rank(hand_player) < rank(hand_opponent):
                return pot
            elif rank(hand_player) > rank(hand_opponent):
                return -pot
            else:
                return 0

def valid_actions(history):
    '''card dealt: d, check: x, fold: f, call: c, bet: b, raise: r'''
    if history[-1:] == '' or history[-1] == 'd' or history[-1] == 'x':
        return ['x', 'b']
    elif history[-1] == 'b':
        return ['f', 'c', 'r']
    elif history[-1] == 'r':
        return ['f', 'c']

def get_active_player(history):
    if 'd' not in history:
        return len(history) % 2
    else:  # after flop is dealt player with index 0 is the first to play
        return len(history.split('d')[1]) % 2

