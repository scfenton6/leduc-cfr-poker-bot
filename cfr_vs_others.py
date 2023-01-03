import json
import matplotlib.pyplot as plt
from numpy.random import choice
import numpy as np
import game_utils as gu
import leduc_game

with open('leduc_strats.json') as f:
    leduc_strats = json.load(f)

def cfr_strat_as_function(history, card, flop=None):
    '''Function that, given a history, a pocket hand and possibly a flop, chooses a 
    move according to the weighted probability vector that is the value corresponding 
    to the key formed by the given cards and history in the leduc_strats dictionary'''
    if flop:
        return choice(gu.valid_actions(history), p = leduc_strats[card+flop+" "+history])
    else:
        return choice(gu.valid_actions(history), p = leduc_strats[card+" "+history])

def random_strat(history, card, flop=None):
    '''Strategy corresponding to a player whose actions are totally random'''
    valid_actions = gu.valid_actions(history)
    return choice(valid_actions)

def honest_strat(history, card, flop=None):
    '''Strategy corresponding to an honest player, in the sense 
    that they play aggressively when they have a good enough hand, 
    passively when they have a medium hand, and pass/fold when they 
    have a bad hand'''
    def passive_move(history):
        if not history or history[-1]=='x' or history[-1]=='d':
            return 'x'
        elif history[-1] == 'b':
            return 'c'
        else:
            return 'f'

    def get_preflop_action(history, card):
        val_act = gu.valid_actions(history)
        if card == "J":
            return val_act[0]
        elif card == "K":
            return val_act[-1]
        elif card == "Q":
            return passive_move(history)

    def get_postflop_action(history, card, flop):
        val_act = gu.valid_actions(history)
        hand_rank = gu.rank(card+flop)
        if 1 <= hand_rank <=3:
            return val_act[-1]
        elif 4 <= hand_rank <=5:
            return passive_move(history)
        else:
            return val_act[-1]

    if flop:
        return get_postflop_action(history, card, flop)
    else:
        return get_preflop_action(history, card)

n_rounds = 10000

accum_utils_vs_honest = leduc_game.simulate_poker_game(
    cfr_strat_as_function, 
    honest_strat,
    n_rounds
    )

accum_utils_vs_random = leduc_game.simulate_poker_game(
    cfr_strat_as_function, 
    random_strat,
    n_rounds
    )

xx = np.arange(0, n_rounds, dtype=int)
plt.plot(xx, accum_utils_vs_honest, label='CFR vs honest')
plt.plot(xx, accum_utils_vs_random, label='CFR vs random')
plt.legend(fontsize=7)
plt.show()
